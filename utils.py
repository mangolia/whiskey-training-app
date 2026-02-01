"""
Utility functions for the whiskey review scraper.
Shared functions used across multiple modules.
"""

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from datetime import datetime
from dateutil import parser as date_parser
from typing import Optional, Tuple
import re


def normalize_url(url):
    """
    Normalize a URL for duplicate detection.
    
    Removes tracking parameters, converts to lowercase, removes trailing slashes.
    
    Args:
        url (str): The URL to normalize
        
    Returns:
        str: Normalized URL
        
    Example:
        >>> normalize_url("https://BreakingBourbon.com/Review/Eagle-Rare/?utm_source=twitter")
        'https://breakingbourbon.com/review/eagle-rare'
    """
    if not url:
        return None
    
    # Parse the URL into components
    parsed = urlparse(url.lower())
    
    # List of tracking parameters to remove
    tracking_params = {
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'ref', 'source', 'fbclid', 'gclid', 'mc_cid', 'mc_eid'
    }
    
    # Parse query parameters and filter out tracking ones
    query_params = parse_qs(parsed.query)
    cleaned_params = {
        key: value for key, value in query_params.items() 
        if key not in tracking_params
    }
    
    # Sort parameters alphabetically for consistency
    sorted_query = urlencode(sorted(cleaned_params.items()), doseq=True)
    
    # Remove trailing slash from path
    clean_path = parsed.path.rstrip('/')
    
    # Reconstruct URL without tracking parameters
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        clean_path,
        parsed.params,
        sorted_query,
        ''  # Remove fragment
    ))
    
    return normalized


def normalize_string(text):
    """
    Normalize a string for matching (whiskey names, distillery names, etc).
    
    Converts to lowercase and removes extra whitespace.
    
    Args:
        text (str): The string to normalize
        
    Returns:
        str: Normalized string, or None if input is None/empty
        
    Example:
        >>> normalize_string("  Eagle Rare 10 Year  ")
        'eagle rare 10 year'
    """
    if not text:
        return None
    
    # Convert to lowercase and strip leading/trailing whitespace
    normalized = text.lower().strip()
    
    # Replace multiple spaces with single space
    normalized = ' '.join(normalized.split())
    
    return normalized if normalized else None


def parse_date(date_string):
    """
    Parse a date string into ISO 8601 format (YYYY-MM-DD HH:MM:SS).
    
    Handles many common date formats automatically.
    
    Args:
        date_string (str): Date in various formats
        
    Returns:
        str: Date in ISO 8601 format, or None if parsing fails
        
    Example:
        >>> parse_date("November 23, 2024")
        '2024-11-23 00:00:00'
        >>> parse_date("2024-11-23")
        '2024-11-23 00:00:00'
    """
    if not date_string:
        return None
    
    try:
        # dateutil.parser can handle most date formats automatically
        parsed_date = date_parser.parse(date_string)
        
        # Return in ISO 8601 format
        return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
    
    except (ValueError, TypeError):
        # If parsing fails, return None
        return None


def get_current_timestamp():
    """
    Get current UTC timestamp in ISO 8601 format.
    
    Used for date_scraped and run_date fields.
    
    Returns:
        str: Current timestamp in ISO 8601 format
        
    Example:
        >>> get_current_timestamp()
        '2024-11-23 15:30:45'
    """
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def parse_age(age_str: str) -> Tuple[Optional[str], Optional[float]]:
    """
    Parse whiskey age string into raw value and normalized months.
    
    Handles various formats commonly found on whiskey review sites:
    - "10 Years"
    - "8 Years (Company website states 8 years, 5 months, 2 days)"
    - "5 Years, 4 Months, 10 Days"
    - "18 months"
    - "NAS" or "No Age Statement"
    
    Args:
        age_str: Raw age string from the review
    
    Returns:
        Tuple of (raw_age_string, age_in_months)
        - raw_age_string: The original string, cleaned up
        - age_in_months: Float value in months, or None if NAS/unparseable
        
    Examples:
        >>> parse_age("10 Years")
        ('10 Years', 120.0)
        >>> parse_age("5 Years, 4 Months, 10 Days")
        ('5 Years, 4 Months, 10 Days', 64.33)
        >>> parse_age("NAS")
        ('NAS', None)
        >>> parse_age("")
        (None, None)
    """
    if not age_str:
        return (None, None)
    
    raw = age_str.strip()
    
    # Check for NAS (No Age Statement)
    nas_variants = ('NAS', 'N/A', 'NO AGE STATEMENT', 'NO AGE', 'NOT STATED')
    if raw.upper() in nas_variants:
        return (raw, None)
    
    total_months = 0.0
    found_any = False
    
    # Extract years
    years_match = re.search(r'(\d+)\s*years?', raw, re.IGNORECASE)
    if years_match:
        total_months += int(years_match.group(1)) * 12
        found_any = True
    
    # Extract months
    months_match = re.search(r'(\d+)\s*months?', raw, re.IGNORECASE)
    if months_match:
        total_months += int(months_match.group(1))
        found_any = True
    
    # Extract days (convert to fractional months, ~30 days/month)
    days_match = re.search(r'(\d+)\s*days?', raw, re.IGNORECASE)
    if days_match:
        total_months += int(days_match.group(1)) / 30.0
        found_any = True
    
    if found_any:
        return (raw, round(total_months, 2))
    
    # Couldn't parse - return raw string with None for months
    return (raw, None)


# Test the functions when running this file directly
if __name__ == "__main__":
    print("Testing utility functions...\n")
    
    # Test normalize_url
    test_url = "https://BreakingBourbon.com/Review/Eagle-Rare/?utm_source=twitter&ref=homepage"
    print(f"Original URL: {test_url}")
    print(f"Normalized:   {normalize_url(test_url)}")
    print()
    
    # Test normalize_string
    test_string = "  Eagle Rare 10 Year  "
    print(f"Original string: '{test_string}'")
    print(f"Normalized:      '{normalize_string(test_string)}'")
    print()
    
    # Test parse_date
    test_dates = [
        "November 23, 2024",
        "2024-11-23",
        "11/23/2024",
        "23 Nov 2024"
    ]
    print("Testing date parsing:")
    for date_str in test_dates:
        print(f"  {date_str:20} -> {parse_date(date_str)}")
    print()
    
    # Test parse_age
    test_ages = [
        "10 Years",
        "8 Years (Company website states 8 years, 5 months, 2 days)",
        "5 Years, 4 Months, 10 Days",
        "18 months",
        "NAS",
        "No Age Statement",
        "",
        "Aged to perfection"  # Unparseable but not NAS
    ]
    print("Testing age parsing:")
    for age_str in test_ages:
        raw, months = parse_age(age_str)
        if months:
            years = months / 12
            print(f"  '{age_str}' -> {months} months ({years:.2f} years)")
        else:
            print(f"  '{age_str}' -> {raw}, {months}")
    print()
    
    # Test get_current_timestamp
    print(f"Current timestamp: {get_current_timestamp()}")