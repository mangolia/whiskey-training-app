"""
Test script for database utility functions.
"""

from database import (
    normalize_url, 
    normalize_string, 
    parse_date, 
    get_current_timestamp
)

print("Testing Utility Functions")
print("=" * 50)

# Test normalize_url
print("\n1. Testing normalize_url():")
test_urls = [
    "https://BreakingBourbon.com/Review/Eagle-Rare/?utm_source=twitter",
    "https://site.com/review/",
    "HTTPS://SITE.COM/REVIEW",
]
for url in test_urls:
    print(f"  Input:  {url}")
    print(f"  Output: {normalize_url(url)}\n")

# Test normalize_string
print("\n2. Testing normalize_string():")
test_strings = [
    "  Eagle Rare   10 Year  ",
    "Buffalo Trace",
    "   ",
    None
]
for string in test_strings:
    print(f"  Input:  '{string}'")
    print(f"  Output: '{normalize_string(string)}'\n")

# Test parse_date
print("\n3. Testing parse_date():")
test_dates = [
    "Nov 15, 2024",
    "2024-11-15",
    "15/11/2024",
    "invalid date"
]
for date in test_dates:
    print(f"  Input:  {date}")
    print(f"  Output: {parse_date(date)}\n")

# Test get_current_timestamp
print("\n4. Testing get_current_timestamp():")
print(f"  Current UTC: {get_current_timestamp()}")