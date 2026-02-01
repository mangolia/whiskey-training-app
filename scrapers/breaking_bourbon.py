"""
Breaking Bourbon Scraper
========================

Scrapes whiskey reviews from Breaking Bourbon.

Site: https://www.breakingbourbon.com
Reviews Index: https://www.breakingbourbon.com/bourbon-reviews

HTML Structure Notes (as of December 2025):
- Whiskey name: <h1 class="bold-page-title review">
- Bottle info: <div class="bottleinfo w-richtext"> with labeled <p> tags
- Tasting notes: <div class="section-headers"> followed by <div class="desktoptext">
- Review text: <div class="sumitup w-richtext"> with <p> tags
- Review date: <div class="text-block-5">

Fields extracted:
- whiskey_name, classification, company, distillery, release_date
- proof, age (raw string), age_months (normalized), mashbill, color, price
- nose, palate, finish (pipe-delimited tasting notes)
- review_text (full written review with paragraph breaks preserved)
- review_date (parsed to ISO format)
"""

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

# Import from our package
from scrapers.base_scraper import BaseScraper

# Import our utility functions
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import normalize_url, parse_date, get_current_timestamp, parse_age


class BreakingBourbonScraper(BaseScraper):
    """Scraper for Breaking Bourbon whiskey reviews."""
    
    SOURCE_NAME = "Breaking Bourbon"
    BASE_URL = "https://www.breakingbourbon.com"
    REVIEWS_INDEX_URL = "https://www.breakingbourbon.com/bourbon-rye-whiskey-reviews-sort-by-review-date"
    
    # Field mapping: Breaking Bourbon label -> our database field
    FIELD_MAP = {
        'Classification': 'classification',
        'Company': 'company',
        'Distillery': 'distillery',
        'Release Date': 'release_date',
        'Proof': 'proof',
        'Age': 'age',
        'Mashbill': 'mashbill',
        'Color': 'color',
        'SRP': 'price',
        'MSRP': 'price'  # Some pages use MSRP instead of SRP
    }
    
    def scrape_review(self, url: str) -> Optional[Dict]:
        """
        Scrape a single review from Breaking Bourbon.
        
        Args:
            url: Full URL to the review page
            
        Returns:
            Dictionary with all review data, or None if failed
        """
        html = self.fetch_page(url)
        if not html:
            return None
        
        return self.parse_review_html(html, url)
    
    def parse_review_html(self, html: str, url: str) -> Optional[Dict]:
        """
        Parse review data from HTML content.
        
        Useful for testing with cached HTML without making network requests.
        
        Args:
            html: Raw HTML string
            url: Source URL for the review
            
        Returns:
            Dictionary with all review data, or None if failed
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Build the review data dictionary
            data = {
                'source_site': self.SOURCE_NAME,
                'source_url': url,
                'normalized_url': normalize_url(url),
                'date_scraped': get_current_timestamp(),
            }
            
            # Extract whiskey name (required field)
            whiskey_name = self._extract_name(soup)
            if not whiskey_name:
                print(f"  WARNING: Could not extract whiskey name")
                return None
            
            # Map to 'name' for database compatibility
            data['name'] = whiskey_name
            
            # Extract bottle info (proof, age, distillery, etc.)
            bottle_info = self._extract_bottle_info(soup)
            data.update(bottle_info)
            
            # Process age field specially - parse into raw + normalized months
            if 'age' in data and data['age']:
                raw_age, age_months = parse_age(data['age'])
                data['age'] = raw_age  # Keep the raw string
                data['age_months'] = age_months  # Add normalized value
            
            # Extract tasting notes and review text
            tasting_notes = self._extract_tasting_notes(soup)
            data.update(tasting_notes)
            
            # Map review_text to overall_notes for database compatibility
            if 'review_text' in data:
                data['overall_notes'] = data.pop('review_text')
            
            # Extract and parse review date
            raw_date = self._extract_review_date(soup)
            data['review_date'] = parse_date(raw_date) if raw_date else None
            
            return data
            
        except Exception as e:
            print(f"  ERROR parsing {url}: {e}")
            return None
    
    def find_review_urls(self, days_back: int = None, start_date: datetime = None, end_date: datetime = None) -> List[str]:
        """
        Find URLs of reviews within a date range.
        
        Scrapes the date-sorted reviews page to find review URLs.
        
        Args:
            days_back: Number of days to look back from today (backward compatibility)
            start_date: Start date for date range (inclusive)
            end_date: End date for date range (inclusive, defaults to today)
            
        Returns:
            List of full review URLs
        """
        # Use the date-sorted reviews page
        reviews_url = f"{self.BASE_URL}/bourbon-rye-whiskey-reviews-sort-by-review-date"
        print(f"Checking reviews index: {reviews_url}")
        
        html = self.fetch_page(reviews_url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        urls = []
        
        # Determine date range
        # Priority: days_back (backward compatibility) > date range
        if days_back is not None:
            # Backward compatibility mode
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
        elif start_date is None:
            # Default: last 2 days if nothing specified
            end_date = datetime.now()
            start_date = end_date - timedelta(days=2)
        else:
            # Date range mode
            if end_date is None:
                end_date = datetime.now()
            # Ensure dates are at start/end of day for proper comparison
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Find all review items (they're in divs with role="listitem")
        review_items = soup.find_all('div', role='listitem', class_='collection-item-52')
        
        for item in review_items:
            # Extract the review date
            date_elem = item.find('div', class_='text-block-90')
            if not date_elem:
                continue
            
            date_text = date_elem.get_text(strip=True)
            if not date_text:
                continue
            
            # Parse the date (format: "December 30, 2025")
            try:
                review_date = datetime.strptime(date_text, "%B %d, %Y")
            except ValueError:
                # Try alternative format if needed
                try:
                    review_date = datetime.strptime(date_text, "%b %d, %Y")
                except ValueError:
                    print(f"  WARNING: Could not parse date '{date_text}', skipping")
                    continue
            
            # Check if review is within date range
            review_date_only = review_date.date()
            start_date_only = start_date.date()
            end_date_only = end_date.date()
            
            # If review is before start date, we can stop (reviews are sorted by date, newest first)
            if review_date_only < start_date_only:
                break
            
            # Only include reviews within the date range
            if start_date_only <= review_date_only <= end_date_only:
                # Extract the review URL
                link = item.find('a', href=True)
                if link and '/review/' in link.get('href', ''):
                    href = link['href']
                    # Make sure it's a full URL
                    if href.startswith('/'):
                        full_url = f"{self.BASE_URL}{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = f"{self.BASE_URL}/{href}"
                    
                    urls.append(full_url)
            elif review_date_only > end_date_only:
                # Review is after end date, continue (might be newer reviews before older ones in list)
                continue
        
        # Format date range for display
        if days_back is not None:
            print(f"  Found {len(urls)} review(s) from the last {days_back} day(s)")
        else:
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            print(f"  Found {len(urls)} review(s) from {start_str} to {end_str}")
        
        return urls
    
    def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract whiskey name from page header.
        
        HTML: <h1 class="bold-page-title review">Whiskey Name</h1>
        """
        element = soup.find('h1', class_='bold-page-title')
        if element:
            text = element.get_text(strip=True)
            return self._normalize_text(text)
        
        # Fallback: try any h1
        element = soup.find('h1')
        if element:
            text = element.get_text(strip=True)
            return self._normalize_text(text)
        return None
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text to fix encoding issues and smart quotes.
        
        Converts smart quotes to regular quotes and fixes common encoding errors.
        """
        if not text:
            return text
        
        # Try to fix double-encoded UTF-8 by attempting to decode as Latin-1 then re-encode
        # This handles cases where UTF-8 bytes were stored as if they were Latin-1
        try:
            # If text contains bytes that look like double-encoded UTF-8, try to fix it
            if isinstance(text, str) and any(ord(c) > 127 for c in text):
                # Try decoding as if it was incorrectly encoded
                # First, encode to bytes if it's a string with problematic characters
                text_bytes = text.encode('latin-1', errors='ignore')
                # Then try to decode as UTF-8
                try:
                    text = text_bytes.decode('utf-8', errors='ignore')
                except (UnicodeDecodeError, UnicodeError):
                    pass
        except Exception:
            pass
        
        # Replace Unicode smart quote characters with regular ones
        replacements = {
            '\u2018': "'",  # Left single quotation mark
            '\u2019': "'",  # Right single quotation mark (apostrophe)
            '\u201C': '"',  # Left double quotation mark
            '\u201D': '"',  # Right double quotation mark
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2026': '...', # Ellipsis
            '\u00A0': ' ',  # Non-breaking space
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Fix double-encoded UTF-8 patterns (like â\x80\x99)
        # These patterns occur when UTF-8 bytes are interpreted as Latin-1
        text = text.replace('â\x80\x99', "'")   # Right single quotation mark
        text = text.replace('â\x80\x9c', '"')   # Left double quotation mark  
        text = text.replace('â\x80\x9d', '"')   # Right double quotation mark
        text = text.replace('â\x80\x93', '-')    # En dash
        text = text.replace('â\x80\x94', '--')  # Em dash
        text = text.replace('â\x80¦', '...')     # Ellipsis (if present)
        
        # Fix common patterns where 'â' appears (often from encoding issues)
        # Pattern: "â" followed by something that should be an apostrophe
        import re
        # Fix "â's" -> "'s" (apostrophe-s)
        text = re.sub(r"â's", "'s", text)
        # Fix "â'N" -> "'N" (apostrophe-N)
        text = re.sub(r"â'N", "'N", text)
        # Fix "â" followed by common patterns
        text = re.sub(r"â([A-Z])", r"'\1", text)  # "âA" -> "'A"
        
        # Ensure proper UTF-8 encoding
        try:
            # Clean up any remaining encoding issues
            text = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        except (UnicodeEncodeError, UnicodeDecodeError):
            # If that fails, just return what we have
            pass
        
        return text
    
    def _extract_bottle_info(self, soup: BeautifulSoup) -> Dict:
        """
        Extract labeled fields from bottle info section.
        
        HTML Structure:
            <div class="bottleinfo w-richtext">
                <p><strong>Classification:</strong> Straight Bourbon</p>
                <p><strong>Proof:</strong> 90</p>
                ...
            </div>
            
        Preserves raw values including "Sourced from..." in distillery field.
        """
        data = {}
        
        bottle_info = soup.find('div', class_='bottleinfo')
        if not bottle_info:
            # Try alternate class name
            bottle_info = soup.find('div', class_='w-richtext')
        
        if not bottle_info:
            return data
        
        # Extract each labeled field
        for p in bottle_info.find_all('p'):
            strong = p.find('strong')
            if strong:
                # Get the label (remove colon)
                label = strong.text.strip().rstrip(':')
                
                # Get the value (everything after the label)
                value = p.text.replace(strong.text, '').strip()
                # Normalize text to fix encoding issues
                value = self._normalize_text(value) if value else None
                
                # Map to our field name if we recognize this label
                if label in self.FIELD_MAP:
                    field_name = self.FIELD_MAP[label]
                    data[field_name] = value
        
        return data
    
    def _extract_tasting_notes(self, soup: BeautifulSoup) -> Dict:
        """
        Extract tasting notes (Nose, Palate, Finish) and full review text.
        
        HTML Structure (as of Dec 2025):
            <div class="section-headers">NOSE</div>
            <div class="desktoptext w-richtext">Tasting notes here...</div>
            <div class="section-headers">palate</div>
            <div class="desktoptext w-richtext">More notes...</div>
            <div class="section-headers">OVERALL</div>
            <div class="sumitup w-richtext"><p>Full review...</p></div>
        """
        notes = {
            'nose': None,
            'palate': None,
            'finish': None,
            'review_text': None
        }
        
        # Find all section-headers divs
        section_headers = soup.find_all('div', class_='section-headers')
        
        for header in section_headers:
            section_name = header.get_text(strip=True).upper()
            
            # Find the next sibling that contains actual content
            next_div = header.find_next_sibling('div')
            
            if next_div and 'desktoptext' in next_div.get('class', []):
                content = next_div.get_text(strip=True)
                # Normalize text to fix encoding issues
                content = self._normalize_text(content) if content else None
                # Only save if there's actual content (not empty)
                if content:
                    if section_name == 'NOSE':
                        notes['nose'] = content
                    elif section_name == 'PALATE':
                        notes['palate'] = content
                    elif section_name == 'FINISH':
                        notes['finish'] = content
        
        # Fallback: regex on page text if section-headers method failed
        if not notes['nose']:
            page_text = soup.get_text()
            
            nose_match = re.search(r'NOSE\s*\n+([^\n]+(?:\|[^\n]+)*)', page_text, re.IGNORECASE)
            if nose_match:
                notes['nose'] = self._normalize_text(nose_match.group(1).strip())
            
            palate_match = re.search(r'palate\s*\n+([^\n]+(?:\|[^\n]+)*)', page_text, re.IGNORECASE)
            if palate_match:
                notes['palate'] = self._normalize_text(palate_match.group(1).strip())
            
            finish_match = re.search(r'finish\s*\n+([^\n]+(?:\|[^\n]+)*)', page_text, re.IGNORECASE)
            if finish_match:
                notes['finish'] = self._normalize_text(finish_match.group(1).strip())
        
        # Extract full review text with paragraph breaks preserved
        notes['review_text'] = self._extract_review_text(soup)
        
        return notes
    
    def _extract_review_text(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract the full written review text with paragraph breaks.
        
        The review text can appear in multiple locations:
        1. sumitup div (sometimes just has first paragraph)
        2. w-richtext divs (full review is usually in the longest one)
        
        Preserves paragraph structure with double newlines.
        """
        # Find the longest w-richtext div (likely contains full review)
        # This is more reliable than sumitup which sometimes only has a snippet
        richtext_divs = soup.find_all('div', class_='w-richtext')
        longest_text = None
        longest_len = 0
        
        for div in richtext_divs:
            # Skip bottleinfo divs
            if 'bottleinfo' in div.get('class', []):
                continue
            
            text = div.get_text(strip=True)
            
            # desktoptext divs can contain tasting notes OR full review
            # Tasting notes are usually < 500 chars, full review is usually > 800 chars
            # So we'll include desktoptext divs if they're long enough
            if len(text) > 800 and len(text) > longest_len:
                longest_text = text
                longest_len = len(text)
            elif 'desktoptext' not in div.get('class', []):
                # For non-desktoptext divs, use lower threshold
                if len(text) > 500 and len(text) > longest_len:
                    longest_text = text
                    longest_len = len(text)
        
        # Also check sumitup div
        sumitup = soup.find('div', class_='sumitup')
        sumitup_text = None
        if sumitup:
            paragraphs = sumitup.find_all('p')
            if paragraphs:
                # Get all paragraphs from sumitup
                sumitup_text = '\n\n'.join(
                    p.get_text(strip=True) 
                    for p in paragraphs 
                    if p.get_text(strip=True)
                )
            else:
                # Fallback: get all text from sumitup
                sumitup_text = sumitup.get_text(strip=True)
        
        # Prefer the longest text (full review), but combine if sumitup adds content
        if longest_text:
            # If sumitup has content not in longest_text, prepend it
            if sumitup_text and sumitup_text not in longest_text and len(sumitup_text) > 50:
                # Check if sumitup is actually the beginning of longest_text
                if not longest_text.startswith(sumitup_text[:50]):
                    # They're different, combine them
                    combined = f"{sumitup_text}\n\n{longest_text}"
                    return self._normalize_text(combined)
            # Return the longest text (should contain full review)
            return self._normalize_text(longest_text)
        elif sumitup_text:
            return self._normalize_text(sumitup_text)
        
        return None
    
    def _extract_review_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract review publication date.
        
        HTML: <div class="text-block-5">October 22, 2025</div>
        """
        element = soup.find('div', class_='text-block-5')
        if element:
            return element.text.strip()
        
        # Fallback: look for date pattern near "Written By"
        page_text = soup.get_text()
        date_match = re.search(r'Written By:.*?([A-Z][a-z]+ \d{1,2}, \d{4})', page_text, re.DOTALL)
        if date_match:
            return date_match.group(1)
        
        return None


# ============================================================
# Test code - runs when you execute this file directly
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Breaking Bourbon Scraper - Test Run")
    print("="*60)
    
    # Create scraper instance
    scraper = BreakingBourbonScraper()
    
    # Test URL - a known review
    test_url = "https://www.breakingbourbon.com/review/heaven-hill-grain-to-glass-rye-2025"
    
    print(f"\nTest URL: {test_url}")
    print("-"*60)
    
    # Scrape the review
    data = scraper.scrape_review(test_url)
    
    if data:
        print("\n✓ Successfully scraped review!\n")
        
        # Display extracted data
        print("EXTRACTED DATA:")
        print("-"*40)
        print(f"Whiskey Name:   {data.get('whiskey_name', 'N/A')}")
        print(f"Classification: {data.get('classification', 'N/A')}")
        print(f"Company:        {data.get('company', 'N/A')}")
        print(f"Distillery:     {data.get('distillery', 'N/A')}")
        print(f"Proof:          {data.get('proof', 'N/A')}")
        print(f"Age:            {data.get('age', 'N/A')}")
        print(f"Age (months):   {data.get('age_months', 'N/A')}")
        print(f"Mashbill:       {data.get('mashbill', 'N/A')}")
        print(f"Price:          {data.get('price', 'N/A')}")
        print(f"Review Date:    {data.get('review_date', 'N/A')}")
        print(f"Date Scraped:   {data.get('date_scraped', 'N/A')}")
        
        print("\nTASTING NOTES:")
        print("-"*40)
        
        nose = data.get('nose', 'N/A')
        print(f"Nose:   {nose[:80]}..." if nose and len(nose) > 80 else f"Nose:   {nose}")
        
        palate = data.get('palate', 'N/A')
        print(f"Palate: {palate[:80]}..." if palate and len(palate) > 80 else f"Palate: {palate}")
        
        finish = data.get('finish', 'N/A')
        print(f"Finish: {finish[:80]}..." if finish and len(finish) > 80 else f"Finish: {finish}")
        
        review_text = data.get('review_text', '')
        if review_text:
            print(f"\nREVIEW TEXT: ({len(review_text)} chars)")
            print("-"*40)
            print(review_text[:300] + "..." if len(review_text) > 300 else review_text)
        
    else:
        print("\n✗ Failed to scrape review")
        print("Check the URL and HTML structure")
    
    print("\n" + "="*60)
