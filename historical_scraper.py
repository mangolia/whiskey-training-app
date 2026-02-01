"""
Historical Scraper
==================

One-time scraper to discover and scrape ALL historical whiskey reviews from
Breaking Bourbon's endless scroll reviews page.

Usage:
    python historical_scraper.py
"""

import sys
import json
import time
import logging
import sqlite3
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import yaml
from bs4 import BeautifulSoup

from database import (
    get_connection,
    create_database,
    insert_review,
    check_duplicate_review,
    log_scraper_run,
    normalize_url
)
from scrapers.breaking_bourbon import BreakingBourbonScraper


# ============================================================================
# Configuration Loading
# ============================================================================

def load_config() -> Dict:
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent / "config.yaml"
    
    if not config_path.exists():
        return {
            'historical_scrape': {
                'rate_limit_seconds': 2,
                'max_retries': 3,
                'progress_save_interval': 10,
                'request_timeout': 30,
                'use_browser_automation': False,
                'rate_limit_backoff': [30, 60, 300, -1]
            }
        }
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging():
    """Set up logging for historical scraper."""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"historical_scrape-{datetime.now().strftime('%Y-%m-%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


# ============================================================================
# Progress File Management
# ============================================================================

PROGRESS_FILE = Path(__file__).parent / "historical_scrape_progress.json"


def load_progress() -> Dict:
    """Load progress from file."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        'started_at': None,
        'last_updated': None,
        'total_urls_discovered': 0,
        'urls_to_scrape': 0,
        'completed_urls': 0,
        'successful_scrapes': 0,
        'failed_urls': [],
        'status': 'not_started'
    }


def save_progress(progress: Dict):
    """Save progress to file."""
    progress['last_updated'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


# ============================================================================
# URL Discovery
# ============================================================================

def discover_all_review_urls_sitemap(scraper: BreakingBourbonScraper, logger: logging.Logger) -> List[str]:
    """
    Discover all review URLs by fetching and parsing the sitemap.xml.
    
    This is the preferred method as it's faster, more reliable, and doesn't
    require browser automation.
    """
    logger.info("Discovering review URLs from sitemap.xml...")
    
    sitemap_url = f"{scraper.BASE_URL}/sitemap.xml"
    all_urls = []
    max_retries = 3
    
    # Fetch sitemap with retries
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Fetching sitemap (attempt {attempt}/{max_retries})...")
            html = scraper.fetch_page(sitemap_url)
            
            if not html:
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 2s, 4s, 8s
                    logger.warning(f"Failed to fetch sitemap, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error("Failed to fetch sitemap after all retries")
                    return []
            
            # Parse XML sitemap
            try:
                root = ET.fromstring(html)
            except ET.ParseError as e:
                logger.error(f"Failed to parse sitemap XML: {e}")
                if attempt < max_retries:
                    continue
                else:
                    return []
            
            # Sitemap XML namespace (usually empty or 'http://www.sitemaps.org/schemas/sitemap/0.9')
            # Handle both with and without namespace
            namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Try with namespace first
            urls = root.findall('.//sitemap:url/sitemap:loc', namespace)
            if not urls:
                # Try without namespace
                urls = root.findall('.//url/loc')
            
            if not urls:
                logger.warning("No URLs found in sitemap, trying alternative parsing...")
                # Try finding all <loc> elements directly
                urls = root.findall('.//loc')
            
            logger.info(f"Found {len(urls)} total URLs in sitemap")
            
            # Filter to only review URLs
            review_urls = []
            for url_elem in urls:
                url_text = url_elem.text
                if url_text and '/review/' in url_text:
                    # Clean up the URL (remove whitespace, ensure it's a full URL)
                    url_text = url_text.strip()
                    if not url_text.startswith('http'):
                        # If relative URL, make it absolute
                        if url_text.startswith('/'):
                            url_text = f"{scraper.BASE_URL}{url_text}"
                        else:
                            url_text = f"{scraper.BASE_URL}/{url_text}"
                    review_urls.append(url_text)
            
            logger.info(f"Found {len(review_urls)} review URLs in sitemap")
            return review_urls
            
        except Exception as e:
            logger.error(f"Error fetching/parsing sitemap (attempt {attempt}): {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                logger.error("Failed to fetch sitemap after all retries")
                return []
    
    return []


def discover_all_review_urls_api(scraper: BreakingBourbonScraper, logger: logging.Logger) -> List[str]:
    """
    Fallback method: Attempt to discover review URLs by parsing the initial page.
    This is kept as a fallback if sitemap is unavailable.
    """
    logger.info("Attempting to discover review URLs via HTML parsing (fallback method)...")
    
    reviews_url = f"{scraper.BASE_URL}/bourbon-rye-whiskey-reviews-sort-by-review-date"
    all_urls = set()
    
    # Get the initial page
    logger.info("Fetching initial page...")
    html = scraper.fetch_page(reviews_url)
    if not html:
        logger.error("Failed to fetch initial page")
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract all review URLs from initial page
    review_items = soup.find_all('div', role='listitem', class_='collection-item-52')
    for item in review_items:
        link = item.find('a', href=True)
        if link and '/review/' in link.get('href', ''):
            href = link['href']
            if href.startswith('/'):
                full_url = f"{scraper.BASE_URL}{href}"
            elif href.startswith('http'):
                full_url = href
            else:
                full_url = f"{scraper.BASE_URL}/{href}"
            all_urls.add(full_url)
    
    logger.info(f"Found {len(all_urls)} review URLs on initial page")
    logger.warning("Note: This method only gets URLs from the first page. Use sitemap method for all reviews.")
    
    return list(all_urls)


def discover_all_review_urls_browser(scraper: BreakingBourbonScraper, logger: logging.Logger) -> List[str]:
    """
    Discover all review URLs using browser automation.
    Requires Selenium or Playwright.
    """
    logger.info("Attempting to discover review URLs via browser automation...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
    except ImportError:
        logger.error("Selenium not installed. Install with: pip install selenium")
        logger.info("Falling back to API method...")
        return discover_all_review_urls_api(scraper, logger)
    
    config = load_config()
    hist_config = config.get('historical_scrape', {})
    headless = hist_config.get('browser_headless', True)
    
    # Set up browser
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        reviews_url = f"{scraper.BASE_URL}/bourbon-rye-whiskey-reviews-sort-by-review-date"
        driver.get(reviews_url)
        
        # Wait for page to load
        time.sleep(3)
        
        all_urls = set()
        max_clicks = 200  # Safety limit
        clicks = 0
        
        while clicks < max_clicks:
            # Extract all review URLs currently visible
            links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/review/"]')
            for link in links:
                href = link.get_attribute('href')
                if href and '/review/' in href:
                    all_urls.add(href)
            
            logger.info(f"Found {len(all_urls)} unique review URLs so far...")
            
            # Try to find and click "Load More" button
            try:
                load_more = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Load More')]"))
                )
                driver.execute_script("arguments[0].click();", load_more)
                time.sleep(2)  # Wait for content to load
                clicks += 1
            except (TimeoutException, NoSuchElementException):
                # No more "Load More" button, we're done
                logger.info("No more 'Load More' button found")
                break
        
        return list(all_urls)
    
    finally:
        if driver:
            driver.quit()


def discover_all_review_urls(scraper: BreakingBourbonScraper, logger: logging.Logger) -> List[str]:
    """
    Discover all review URLs from the sitemap.
    Tries sitemap method first (preferred), falls back to browser automation or API if needed.
    """
    config = load_config()
    hist_config = config.get('historical_scrape', {})
    use_browser = hist_config.get('use_browser_automation', False)
    
    # Always try sitemap first (fastest and most reliable)
    logger.info("Using sitemap method to discover URLs...")
    sitemap_urls = discover_all_review_urls_sitemap(scraper, logger)
    
    if sitemap_urls:
        return sitemap_urls
    
    # Fallback to browser automation if sitemap fails
    if use_browser:
        logger.warning("Sitemap method failed, falling back to browser automation...")
        return discover_all_review_urls_browser(scraper, logger)
    else:
        logger.warning("Sitemap method failed, falling back to HTML parsing (limited results)...")
        return discover_all_review_urls_api(scraper, logger)


# ============================================================================
# Duplicate Filtering
# ============================================================================

def filter_new_urls(all_urls: List[str], logger: logging.Logger) -> List[str]:
    """
    Filter out URLs that already exist in the database.
    Uses batch query for efficiency.
    """
    logger.info(f"Filtering {len(all_urls)} URLs against database...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all existing normalized URLs in one query
    cursor.execute("""
        SELECT normalized_url FROM reviews 
        WHERE source_site = 'Breaking Bourbon'
    """)
    existing_urls = {row[0] for row in cursor.fetchall() if row[0]}
    
    logger.info(f"Found {len(existing_urls)} existing reviews in database")
    
    # Filter
    new_urls = []
    for url in all_urls:
        normalized = normalize_url(url)
        if normalized and normalized not in existing_urls:
            new_urls.append(url)
    
    conn.close()
    
    logger.info(f"Found {len(new_urls)} new URLs to scrape (filtered out {len(all_urls) - len(new_urls)} duplicates)")
    return new_urls


# ============================================================================
# Main Scraping Loop
# ============================================================================

def scrape_reviews(urls: List[str], config: Dict, logger: logging.Logger) -> Dict:
    """
    Scrape all reviews from the provided URLs.
    
    Args:
        urls: List of review URLs to scrape
        config: Configuration dictionary
        logger: Logger instance
    
    Returns:
        Summary dictionary
    """
    hist_config = config.get('historical_scrape', {})
    rate_limit = hist_config.get('rate_limit_seconds', 2)
    max_retries = hist_config.get('max_retries', 3)
    save_interval = hist_config.get('progress_save_interval', 10)
    rate_limit_backoff = hist_config.get('rate_limit_backoff', [30, 60, 300, -1])
    
    scraper = BreakingBourbonScraper()
    conn = get_connection()
    source_site = scraper.SOURCE_NAME
    
    # Load progress
    progress = load_progress()
    if progress['status'] == 'in_progress' and progress.get('completed_urls_list'):
        completed_urls = set(progress.get('completed_urls_list', []))
        logger.info(f"Resuming from previous run. {len(completed_urls)} URLs already processed.")
    else:
        completed_urls = set()
        progress['started_at'] = datetime.now().isoformat()
        progress['status'] = 'in_progress'
        progress['total_urls_discovered'] = len(urls)
        progress['urls_to_scrape'] = len(urls)
        progress['completed_urls_list'] = []
        progress['successful_scrapes'] = 0
        progress['failed_urls'] = []
    
    successful_scrapes = progress.get('successful_scrapes', 0)
    failed_urls = progress.get('failed_urls', [])
    rate_limit_count = 0
    
    for i, url in enumerate(urls, 1):
        # Skip if already processed
        if url in completed_urls:
            logger.debug(f"Skipping already processed URL: {url}")
            continue
        
        logger.info(f"[{i}/{len(urls)}] Processing: {url}")
        
        retries = 0
        success = False
        
        while retries < max_retries:
            try:
                # Check for duplicate before scraping
                normalized_url = normalize_url(url)
                if check_duplicate_review(conn, source_site, normalized_url):
                    logger.info(f"  Duplicate - already in database")
                    successful_scrapes += 1
                    success = True
                    break
                
                # Scrape the review
                review_data = scraper.scrape_review(url)
                
                if not review_data:
                    error_msg = "Scraper returned None"
                    logger.warning(f"  {error_msg}")
                    if retries < max_retries - 1:
                        retries += 1
                        logger.info(f"  Retrying ({retries}/{max_retries})...")
                        time.sleep(rate_limit * retries)  # Exponential backoff
                        continue
                    else:
                        failed_urls.append(url)
                        break
                
                # Insert into database
                review_id = insert_review(conn, review_data)
                
                if review_id:
                    successful_scrapes += 1
                    logger.info(f"  ✓ Successfully added: {review_data.get('name', 'Unknown')}")
                    success = True
                    break
                else:
                    logger.info(f"  Duplicate detected during insertion")
                    successful_scrapes += 1
                    success = True
                    break
                    
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
                
                # Check for rate limiting
                if '429' in error_msg or 'Too Many Requests' in error_msg:
                    rate_limit_count += 1
                    if rate_limit_count <= len(rate_limit_backoff):
                        backoff_time = rate_limit_backoff[rate_limit_count - 1]
                        if backoff_time == -1:
                            logger.error("Rate limit exceeded maximum backoff, stopping")
                            conn.close()
                            progress['status'] = 'error'
                            progress['failed_urls'] = failed_urls
                            save_progress(progress)
                            return {
                                'status': 'error',
                                'reason': 'rate_limit_exceeded',
                                'successful_scrapes': successful_scrapes,
                                'failed_urls': failed_urls
                            }
                        logger.warning(f"Rate limited (429). Waiting {backoff_time} seconds...")
                        time.sleep(backoff_time)
                        retries += 1
                        continue
                
                # Database errors - stop immediately
                if isinstance(e, sqlite3.Error):
                    logger.critical(f"Database error: {error_msg}")
                    conn.close()
                    progress['status'] = 'error'
                    progress['failed_urls'] = failed_urls
                    save_progress(progress)
                    raise
                
                # Other errors - retry or log
                logger.warning(f"  Error ({error_type}): {error_msg}")
                if retries < max_retries - 1:
                    retries += 1
                    logger.info(f"  Retrying ({retries}/{max_retries})...")
                    time.sleep(rate_limit * retries)
                    continue
                else:
                    failed_urls.append(f"{url}: {error_msg}")
                    break
        
        # Mark as completed
        completed_urls.add(url)
        progress['completed_urls'] = len(completed_urls)
        progress['successful_scrapes'] = successful_scrapes
        progress['failed_urls'] = failed_urls
        progress['completed_urls_list'] = list(completed_urls)
        
        # Save progress periodically
        if i % save_interval == 0:
            save_progress(progress)
            logger.info(f"Progress saved: {len(completed_urls)}/{len(urls)} completed")
        
        # Rate limiting
        if success:
            time.sleep(rate_limit)
    
    conn.close()
    return {
        'status': 'success' if not failed_urls else 'partial',
        'successful_scrapes': successful_scrapes,
        'failed_urls': failed_urls,
        'total_processed': len(completed_urls)
    }


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for historical scraper."""
    logger = setup_logging()
    config = load_config()
    
    logger.info("=" * 60)
    logger.info("Historical Scraper - Breaking Bourbon")
    logger.info("=" * 60)
    
    # Ensure database exists
    create_database()
    
    # Load progress to check if we're resuming
    progress = load_progress()
    urls_file = Path(__file__).parent / "discovered_urls.json"
    
    # Check if we should resume or start fresh
    if progress['status'] == 'in_progress' and urls_file.exists():
        logger.info("Resuming previous scrape...")
        logger.info("Loading discovered URLs from file...")
        with open(urls_file, 'r') as f:
            all_urls = json.load(f)
        logger.info(f"Loaded {len(all_urls)} URLs from previous discovery")
    else:
        # Phase 1: Discover all review URLs
        logger.info("\nPhase 1: Discovering all review URLs...")
        scraper = BreakingBourbonScraper()
        all_urls = discover_all_review_urls(scraper, logger)
        
        if not all_urls:
            logger.error("No review URLs discovered. Exiting.")
            return
        
        # Save discovered URLs to file for resume capability
        with open(urls_file, 'w') as f:
            json.dump(all_urls, f, indent=2)
        logger.info(f"Saved {len(all_urls)} discovered URLs to {urls_file}")
    
    # Phase 2: Filter out existing reviews
    logger.info("\nPhase 2: Filtering out existing reviews...")
    new_urls = filter_new_urls(all_urls, logger)
    
    if not new_urls:
        logger.info("No new reviews to scrape. All discovered reviews already in database.")
        return
    
    # Phase 3: Scrape reviews
    logger.info(f"\nPhase 3: Scraping {len(new_urls)} reviews...")
    start_time = time.time()
    
    result = scrape_reviews(new_urls, config, logger)
    
    execution_time = time.time() - start_time
    
    # Phase 4: Final reporting
    logger.info("\n" + "=" * 60)
    logger.info("Historical Scrape Complete")
    logger.info("=" * 60)
    logger.info(f"Execution time: {execution_time/60:.1f} minutes")
    logger.info(f"URLs discovered: {len(all_urls)}")
    logger.info(f"URLs to scrape: {len(new_urls)}")
    logger.info(f"Successfully scraped: {result['successful_scrapes']}")
    logger.info(f"Failed: {len(result['failed_urls'])}")
    
    # Save failed URLs to file
    if result['failed_urls']:
        failed_file = Path(__file__).parent / "failed_urls.txt"
        with open(failed_file, 'w') as f:
            for url in result['failed_urls']:
                f.write(f"{url}\n")
        logger.info(f"Failed URLs saved to: {failed_file}")
    
    # Update final progress
    progress['status'] = 'completed'
    progress['last_updated'] = datetime.now().isoformat()
    save_progress(progress)
    
    # Log to database
    conn = get_connection()
    log_scraper_run(
        conn,
        "Breaking Bourbon",
        result['status'],
        reviews_found=len(new_urls),
        reviews_added=result['successful_scrapes'],
        error_message=f"Failed: {len(result['failed_urls'])}" if result['failed_urls'] else None,
        execution_time=execution_time
    )
    conn.close()
    
    logger.info("Historical scrape complete!")


if __name__ == "__main__":
    main()
