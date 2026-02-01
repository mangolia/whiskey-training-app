"""
Automated Daily Review Check Script
===================================

Enhanced version with retry logic, battery detection, logging, and config support.
Designed to run via launchd scheduler.

Usage:
    python automated_daily_check.py [days_back]
"""

import sys
import time
import yaml
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from database import (
    get_connection,
    create_database,
    insert_review,
    check_duplicate_review,
    log_scraper_run,
    insert_daily_summary,
    normalize_url,
    detect_missed_days
)
from scrapers.breaking_bourbon import BreakingBourbonScraper


# ============================================================================
# Configuration Loading
# ============================================================================

def load_config() -> Dict:
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent / "config.yaml"
    
    if not config_path.exists():
        # Use sensible defaults
        logging.warning(f"Config file not found at {config_path}, using defaults")
        return {
            'schedule': {'hour': 23, 'minute': 0, 'timezone': 'America/New_York'},
            'scrapers': {'enabled': ['breaking_bourbon']},
            'logging': {'level': 'INFO', 'retention_days': 90, 'log_dir': 'logs'},
            'retry': {'max_attempts': 3, 'delay_seconds': [300, 900, 1800]},
            'power': {'skip_on_battery': True, 'allow_manual_on_battery': True},
            'paths': {'project_root': str(Path(__file__).parent)}
        }
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(config: Dict):
    """Set up logging system with rotation."""
    log_dir = Path(config['logging']['log_dir'])
    log_dir.mkdir(exist_ok=True)
    
    log_level = getattr(logging, config['logging'].get('level', 'INFO'))
    
    # Main log file
    log_file = log_dir / f"scraper-{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Error log file
    error_log_file = log_dir / "errors.log"
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # File handler for all logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Error-only file handler
    error_handler = logging.FileHandler(error_log_file)
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


# ============================================================================
# Battery Detection
# ============================================================================

def check_battery_power() -> bool:
    """
    Check if Mac is on battery power.
    
    Returns:
        True if on battery, False if on AC power
    """
    try:
        result = subprocess.run(
            ['pmset', '-g', 'batt'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Check if "AC Power" is in output
        if 'AC Power' in result.stdout or 'charging' in result.stdout.lower():
            return False  # On AC power
        else:
            return True   # On battery
    except Exception as e:
        logging.warning(f"Could not check battery status: {e}")
        return False  # Assume AC power if check fails


# ============================================================================
# Retry Logic
# ============================================================================

def should_retry_error(error: Exception, config: Dict) -> bool:
    """
    Determine if an error should trigger a retry.
    
    Args:
        error: The exception that occurred
        config: Configuration dictionary
        
    Returns:
        True if should retry, False otherwise
    """
    error_str = str(error).lower()
    error_type = type(error).__name__
    
    # Network errors - retry
    if 'timeout' in error_str or 'connection' in error_str:
        return config['retry'].get('retry_on_network_error', True)
    
    # Database errors - retry
    if 'database' in error_str or 'sqlite' in error_str:
        return config['retry'].get('retry_on_database_error', True)
    
    # HTTP 404 - don't retry (permanent error)
    if '404' in error_str or 'not found' in error_str:
        return False
    
    # Parsing errors - don't retry (likely permanent HTML change)
    if 'parsing' in error_str or 'parse' in error_str:
        return config['retry'].get('retry_on_parsing_error', False)
    
    # Default: retry for unknown errors
    return True


# ============================================================================
# Main Scraper Function with Retry
# ============================================================================

def run_scraper_with_retry(config: Dict, days_back: int = 1, is_manual: bool = False) -> Dict:
    """
    Run scraper with retry logic.
    
    Args:
        config: Configuration dictionary
        days_back: Number of days to look back
        is_manual: True if manually triggered (bypasses battery check)
        
    Returns:
        dict: Summary of the run
    """
    logger = logging.getLogger(__name__)
    start_time = time.time()
    
    # Check battery if not manual run
    if not is_manual and config['power'].get('skip_on_battery', True):
        if check_battery_power():
            logger.warning("Mac is on battery power - skipping scheduled run")
            execution_time = time.time() - start_time
            
            # Log skipped run
            conn = get_connection()
            log_scraper_run(
                conn, "Breaking Bourbon", "skipped",
                reviews_found=0, reviews_added=0,
                error_message="Skipped: Mac on battery power",
                execution_time=execution_time
            )
            conn.close()
            
            return {
                'status': 'skipped',
                'reason': 'battery',
                'reviews_found': 0,
                'reviews_added': 0,
                'duplicates': 0,
                'errors': [],
                'execution_time': execution_time
            }
    
    # Initialize scraper
    scraper = BreakingBourbonScraper()
    source_site = scraper.SOURCE_NAME
    
    logger.info(f"Starting scraper run for {source_site}")
    logger.info(f"Checking reviews from last {days_back} day(s)")
    
    max_attempts = config['retry'].get('max_attempts', 3)
    delays = config['retry'].get('delay_seconds', [300, 900, 1800])
    
    last_error = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Attempt {attempt}/{max_attempts}")
            
            # Run the scraper
            result = check_reviews_for_date_internal(scraper, days_back, logger)
            
            # Success - return result
            logger.info(f"Scraper completed successfully on attempt {attempt}")
            return result
            
        except Exception as e:
            last_error = e
            error_type = type(e).__name__
            error_msg = str(e)
            
            logger.warning(f"Attempt {attempt} failed: {error_type} - {error_msg}")
            
            # Check if we should retry
            if attempt < max_attempts and should_retry_error(e, config):
                delay = delays[min(attempt - 1, len(delays) - 1)]
                logger.info(f"Retrying in {delay} seconds (exponential backoff)...")
                time.sleep(delay)
            else:
                # Don't retry - log error and fail
                logger.error(f"Scraper failed after {attempt} attempts: {error_msg}")
                break
    
    # All attempts failed
    execution_time = time.time() - start_time
    error_message = f"Failed after {max_attempts} attempts: {str(last_error)}"
    
    # Log failed run
    conn = get_connection()
    log_scraper_run(
        conn, source_site, "error",
        reviews_found=0, reviews_added=0,
        error_message=error_message,
        execution_time=execution_time
    )
    conn.close()
    
    return {
        'status': 'error',
        'reviews_found': 0,
        'reviews_added': 0,
        'duplicates': 0,
        'errors': [error_message],
        'execution_time': execution_time
    }


def check_reviews_for_date_internal(scraper, days_back: int, logger) -> Dict:
    """
    Internal function to check reviews (called by retry logic).
    
    Args:
        scraper: Scraper instance
        days_back: Number of days to look back
        logger: Logger instance
        
    Returns:
        dict: Summary of the run
    """
    start_time = time.time()
    source_site = scraper.SOURCE_NAME
    
    # Ensure database exists
    create_database()
    conn = get_connection()
    
    # Find review URLs
    review_urls = scraper.find_review_urls(days_back=days_back)
    
    if not review_urls:
        logger.info("No reviews found for the specified date range")
        execution_time = time.time() - start_time
        log_scraper_run(
            conn, source_site, 'success',
            reviews_found=0, reviews_added=0,
            execution_time=execution_time
        )
        conn.close()
        return {
            'status': 'success',
            'reviews_found': 0,
            'reviews_added': 0,
            'duplicates': 0,
            'errors': [],
            'execution_time': execution_time
        }
    
    logger.info(f"Found {len(review_urls)} review(s) to process")
    
    # Process each review
    reviews_added = 0
    duplicates = 0
    errors = []
    
    for i, url in enumerate(review_urls, 1):
        logger.info(f"Processing [{i}/{len(review_urls)}]: {url}")
        
        # Check if already in database
        normalized_url = normalize_url(url)
        if check_duplicate_review(conn, source_site, normalized_url):
            logger.info(f"  Duplicate - already in database")
            duplicates += 1
            continue
        
        # Scrape the review
        try:
            review_data = scraper.scrape_review(url)
            
            if not review_data:
                error_msg = f"Failed to scrape review data"
                logger.warning(f"  {error_msg}")
                errors.append(f"{url}: {error_msg}")
                continue
            
            # Insert into database
            review_id = insert_review(conn, review_data)
            
            if review_id:
                reviews_added += 1
                logger.info(f"  Successfully added: {review_data.get('name', 'Unknown')}")
            else:
                duplicates += 1
                logger.info(f"  Duplicate detected during insertion")
                
        except Exception as e:
            error_msg = f"Error processing review: {str(e)}"
            logger.error(f"  {error_msg}")
            errors.append(f"{url}: {error_msg}")
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Determine status
    if errors and reviews_added == 0:
        status = 'error'
    elif errors:
        status = 'partial'
    else:
        status = 'success'
    
    # Log the run
    error_message = '; '.join(errors) if errors else None
    log_scraper_run(
        conn, source_site, status,
        reviews_found=len(review_urls),
        reviews_added=reviews_added,
        error_message=error_message,
        execution_time=execution_time
    )
    
    # Create daily summary
    today = datetime.now().strftime('%Y-%m-%d')
    summary_text = f"Found {len(review_urls)} review(s), added {reviews_added}, {duplicates} duplicate(s)"
    if errors:
        summary_text += f", {len(errors)} error(s)"
    
    insert_daily_summary(
        conn, today,
        total_reviews_found=len(review_urls),
        total_reviews_added=reviews_added,
        total_duplicates=duplicates,
        total_errors=len(errors),
        sites_checked=source_site,
        execution_time=execution_time,
        status=status,
        summary_text=summary_text
    )
    
    logger.info(f"Run completed: {status}")
    logger.info(f"  Reviews found: {len(review_urls)}")
    logger.info(f"  Reviews added: {reviews_added}")
    logger.info(f"  Duplicates: {duplicates}")
    logger.info(f"  Errors: {len(errors)}")
    logger.info(f"  Execution time: {execution_time:.2f}s")
    
    conn.close()
    
    return {
        'status': status,
        'reviews_found': len(review_urls),
        'reviews_added': reviews_added,
        'duplicates': duplicates,
        'errors': errors,
        'execution_time': execution_time
    }


# ============================================================================
# Backfill Functions
# ============================================================================

def check_reviews_for_specific_date(scraper, target_date: datetime, logger, is_backfill: bool = False) -> Dict:
    """
    Check reviews for a specific date (used for backfilling).
    
    Args:
        scraper: Scraper instance
        target_date: Date to check (datetime object)
        logger: Logger instance
        is_backfill: True if this is a backfill operation
        
    Returns:
        dict: Summary of the run
    """
    start_time = time.time()
    source_site = scraper.SOURCE_NAME
    date_str = target_date.strftime('%Y-%m-%d')
    
    # Ensure database exists
    create_database()
    conn = get_connection()
    
    # Find review URLs for this specific date
    review_urls = scraper.find_review_urls(start_date=target_date, end_date=target_date)
    
    # Always create a summary entry, even if no reviews found
    if not review_urls:
        logger.info(f"No reviews found for {date_str}")
        execution_time = time.time() - start_time
        
        # Create summary entry with zero reviews (marks date as checked)
        summary_text = "No reviews published on this date"
        if is_backfill:
            summary_text += f" (backfilled on {datetime.now().strftime('%Y-%m-%d')})"
        
        insert_daily_summary(
            conn, date_str,
            total_reviews_found=0,
            total_reviews_added=0,
            total_duplicates=0,
            total_errors=0,
            sites_checked=source_site,
            execution_time=execution_time,
            status='success',
            summary_text=summary_text
        )
        
        # Log the run
        log_scraper_run(
            conn, source_site, 'success',
            reviews_found=0, reviews_added=0,
            execution_time=execution_time
        )
        
        conn.close()
        return {
            'status': 'success',
            'reviews_found': 0,
            'reviews_added': 0,
            'duplicates': 0,
            'errors': [],
            'execution_time': execution_time,
            'date': date_str
        }
    
    logger.info(f"Found {len(review_urls)} review(s) for {date_str}")
    
    # Process each review
    reviews_added = 0
    duplicates = 0
    errors = []
    
    for i, url in enumerate(review_urls, 1):
        logger.info(f"Processing [{i}/{len(review_urls)}]: {url}")
        
        # Check if already in database
        normalized_url = normalize_url(url)
        if check_duplicate_review(conn, source_site, normalized_url):
            logger.info(f"  Duplicate - already in database")
            duplicates += 1
            continue
        
        # Scrape the review
        try:
            review_data = scraper.scrape_review(url)
            
            if not review_data:
                error_msg = f"Failed to scrape review data"
                logger.warning(f"  {error_msg}")
                errors.append(f"{url}: {error_msg}")
                continue
            
            # Insert into database
            review_id = insert_review(conn, review_data)
            
            if review_id:
                reviews_added += 1
                logger.info(f"  Successfully added: {review_data.get('name', 'Unknown')}")
            else:
                duplicates += 1
                logger.info(f"  Duplicate detected during insertion")
                
        except Exception as e:
            error_msg = f"Error processing review: {str(e)}"
            logger.error(f"  {error_msg}")
            errors.append(f"{url}: {error_msg}")
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Determine status
    if errors and reviews_added == 0:
        status = 'error'
    elif errors:
        status = 'partial'
    else:
        status = 'success'
    
    # Log the run
    error_message = '; '.join(errors) if errors else None
    log_scraper_run(
        conn, source_site, status,
        reviews_found=len(review_urls),
        reviews_added=reviews_added,
        error_message=error_message,
        execution_time=execution_time
    )
    
    # Create daily summary for this date
    summary_text = f"Found {len(review_urls)} review(s), added {reviews_added}, {duplicates} duplicate(s)"
    if errors:
        summary_text += f", {len(errors)} error(s)"
    if is_backfill:
        summary_text += f" (backfilled on {datetime.now().strftime('%Y-%m-%d')})"
    
    insert_daily_summary(
        conn, date_str,
        total_reviews_found=len(review_urls),
        total_reviews_added=reviews_added,
        total_duplicates=duplicates,
        total_errors=len(errors),
        sites_checked=source_site,
        execution_time=execution_time,
        status=status,
        summary_text=summary_text
    )
    
    logger.info(f"Run completed for {date_str}: {status}")
    logger.info(f"  Reviews found: {len(review_urls)}")
    logger.info(f"  Reviews added: {reviews_added}")
    logger.info(f"  Duplicates: {duplicates}")
    logger.info(f"  Errors: {len(errors)}")
    logger.info(f"  Execution time: {execution_time:.2f}s")
    
    conn.close()
    
    return {
        'status': status,
        'reviews_found': len(review_urls),
        'reviews_added': reviews_added,
        'duplicates': duplicates,
        'errors': errors,
        'execution_time': execution_time,
        'date': date_str
    }


def auto_backfill_missed_days(config: Dict, max_days_back: int = 7) -> Dict:
    """
    Automatically detect and backfill missed days.
    
    Args:
        config: Configuration dictionary
        max_days_back: Maximum days to look back for missed days (default: 7)
    
    Returns:
        Summary dictionary of backfill operation
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting automatic backfill of missed days")
    
    # Get backfill settings from config
    backfill_config = config.get('backfill', {})
    lookback_days = backfill_config.get('lookback_window_days', 30)
    max_days_to_backfill = backfill_config.get('max_days_to_backfill', max_days_back)
    
    # Limit lookback to max_days_back
    lookback_days = min(lookback_days, max_days_to_backfill)
    
    # Get database connection
    conn = get_connection()
    
    # Detect missed days
    missed_dates = detect_missed_days(conn, lookback_days=lookback_days)
    conn.close()
    
    if not missed_dates:
        logger.info("No missed days detected")
        return {
            'status': 'success',
            'dates_backfilled': 0,
            'dates_with_reviews': 0,
            'dates_with_zero_reviews': 0,
            'total_reviews_added': 0,
            'errors': []
        }
    
    # Limit to max_days_to_backfill
    missed_dates = missed_dates[:max_days_to_backfill]
    
    logger.info(f"Found {len(missed_dates)} missed day(s) to backfill: {', '.join(missed_dates)}")
    
    # Initialize scraper
    scraper = BreakingBourbonScraper()
    
    # Backfill each missed date
    dates_with_reviews = 0
    dates_with_zero_reviews = 0
    total_reviews_added = 0
    errors = []
    
    for date_str in missed_dates:
        try:
            # Parse the date
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            logger.info(f"Backfilling {date_str}...")
            
            # Check reviews for this date
            result = check_reviews_for_specific_date(scraper, target_date, logger, is_backfill=True)
            
            if result['reviews_found'] > 0:
                dates_with_reviews += 1
                total_reviews_added += result['reviews_added']
            else:
                dates_with_zero_reviews += 1
            
            if result['status'] == 'error':
                errors.append(f"{date_str}: {result.get('errors', ['Unknown error'])}")
            
        except Exception as e:
            error_msg = f"Error backfilling {date_str}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            continue
    
    # Summary
    logger.info(f"Backfill complete: {len(missed_dates)} dates processed")
    logger.info(f"  Dates with reviews: {dates_with_reviews}")
    logger.info(f"  Dates with zero reviews: {dates_with_zero_reviews}")
    logger.info(f"  Total reviews added: {total_reviews_added}")
    if errors:
        logger.warning(f"  Errors: {len(errors)}")
    
    return {
        'status': 'success' if not errors else 'partial',
        'dates_backfilled': len(missed_dates),
        'dates_with_reviews': dates_with_reviews,
        'dates_with_zero_reviews': dates_with_zero_reviews,
        'total_reviews_added': total_reviews_added,
        'errors': errors
    }


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the script."""
    # Load configuration
    config = load_config()
    
    # Set up logging
    logger = setup_logging(config)
    
    # Parse command line arguments
    days_back = 1
    is_manual = False
    auto_backfill_enabled = True
    no_backfill = False
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--manual':
            is_manual = True
            days_back = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            # Check for additional flags
            if '--no-backfill' in sys.argv:
                no_backfill = True
            elif '--backfill-days' in sys.argv:
                idx = sys.argv.index('--backfill-days')
                if idx + 1 < len(sys.argv):
                    try:
                        max_backfill_days = int(sys.argv[idx + 1])
                        config.setdefault('backfill', {})['max_days_to_backfill'] = max_backfill_days
                    except ValueError:
                        logger.warning(f"Invalid backfill-days value, using default")
        elif sys.argv[1] == '--no-backfill':
            no_backfill = True
            if len(sys.argv) > 2:
                try:
                    days_back = int(sys.argv[2])
                except ValueError:
                    logger.error(f"Invalid days_back value: {sys.argv[2]}")
                    sys.exit(1)
        else:
            try:
                days_back = int(sys.argv[1])
            except ValueError:
                logger.error(f"Invalid days_back value: {sys.argv[1]}")
                sys.exit(1)
    
    # Check if auto-backfill should run
    backfill_config = config.get('backfill', {})
    auto_backfill_enabled = backfill_config.get('auto_detect_on_startup', True) and not no_backfill
    
    # Run auto-backfill if enabled (and not manual run, or if explicitly requested)
    if auto_backfill_enabled and not is_manual:
        logger.info("Checking for missed days to backfill...")
        backfill_result = auto_backfill_missed_days(config)
        if backfill_result['dates_backfilled'] > 0:
            logger.info(f"Backfilled {backfill_result['dates_backfilled']} missed day(s)")
    
    # Run scraper with retry logic
    result = run_scraper_with_retry(config, days_back=days_back, is_manual=is_manual)
    
    # Exit with appropriate code
    if result['status'] == 'error':
        sys.exit(1)
    elif result['status'] == 'partial':
        sys.exit(2)
    elif result['status'] == 'skipped':
        sys.exit(3)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

