"""
Base Scraper Module
===================

Shared utilities and base class for all whiskey review scrapers.
All site-specific scrapers inherit from this.

Created: November 2025
"""

import requests
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime


class BaseScraper(ABC):
    """
    Abstract base class for all whiskey review scrapers.
    
    All site-specific scrapers should inherit from this class
    and implement the required abstract methods.
    
    Attributes:
        SOURCE_NAME: Human-readable name of the source site
        BASE_URL: Root URL of the website
        RATE_LIMIT_SECONDS: Delay between requests (be polite!)
    """
    
    SOURCE_NAME: str = "Unknown"
    BASE_URL: str = ""
    RATE_LIMIT_SECONDS: float = 2.0  # Wait 2 seconds between requests
    
    def __init__(self):
        """Initialize the scraper with a configured session."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WhiskeyReviewBot/1.0 (Educational Project)'
        })
        self._last_request_time = 0
    
    def _rate_limit(self):
        """
        Enforce rate limiting between requests.
        
        Waits if necessary to maintain polite scraping behavior.
        """
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_SECONDS:
            wait_time = self.RATE_LIMIT_SECONDS - elapsed
            print(f"  Rate limiting: waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        self._last_request_time = time.time()
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a web page with rate limiting and error handling.
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string, or None if request failed
        """
        self._rate_limit()
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Ensure proper UTF-8 encoding
            # Set encoding explicitly if not detected
            if response.encoding is None:
                response.encoding = response.apparent_encoding or 'utf-8'
            
            # Get text and ensure it's properly decoded
            text = response.text
            
            # If there are encoding issues, try to fix them
            if text:
                # Replace common encoding errors
                text = text.encode('utf-8', errors='ignore').decode('utf-8')
            
            return text
            
        except requests.exceptions.Timeout:
            print(f"  ERROR: Timeout fetching {url}")
            return None
            
        except requests.exceptions.HTTPError as e:
            print(f"  ERROR: HTTP {e.response.status_code} for {url}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"  ERROR: Request failed for {url}: {e}")
            return None
    
    @abstractmethod
    def scrape_review(self, url: str) -> Optional[Dict]:
        """
        Scrape a single review page.
        
        Args:
            url: Full URL to the review page
            
        Returns:
            Dictionary with review data, or None if scraping failed
            
        Must be implemented by each site-specific scraper.
        """
        pass
    
    @abstractmethod
    def find_review_urls(self, days_back: int = 2) -> List[str]:
        """
        Find URLs of reviews published in the last N days.
        
        Args:
            days_back: Number of days to look back (default: 2)
            
        Returns:
            List of review URLs to scrape
            
        Must be implemented by each site-specific scraper.
        """
        pass
    
    def scrape_all_new(self, days_back: int = 2) -> List[Dict]:
        """
        Find and scrape all new reviews.
        
        This is the main entry point for running a scraper.
        
        Args:
            days_back: Number of days to look back for new reviews
            
        Returns:
            List of review data dictionaries
        """
        print(f"\n{'='*50}")
        print(f"Scraping: {self.SOURCE_NAME}")
        print(f"Looking back: {days_back} days")
        print(f"{'='*50}")
        
        # Find review URLs
        urls = self.find_review_urls(days_back)
        print(f"Found {len(urls)} review URLs")
        
        # Scrape each review
        reviews = []
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Scraping: {url}")
            
            data = self.scrape_review(url)
            if data:
                reviews.append(data)
                print(f"  ✓ Success: {data.get('whiskey_name', 'Unknown')}")
            else:
                print(f"  ✗ Failed to scrape")
        
        print(f"\n{'='*50}")
        print(f"Completed: {len(reviews)}/{len(urls)} reviews scraped")
        print(f"{'='*50}\n")
        
        return reviews