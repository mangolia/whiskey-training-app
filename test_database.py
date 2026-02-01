"""
Test script for database.py
Tests all utility functions and database operations
"""

import sqlite3
from database import (
    normalize_url, normalize_string, parse_date, get_current_timestamp,
    get_connection, insert_whiskey, find_whiskey, 
    check_duplicate_review, insert_review,
    DB_PATH
)

def test_utility_functions():
    """Test all utility functions"""
    print("\n" + "="*60)
    print("TESTING UTILITY FUNCTIONS")
    print("="*60)
    
    # Test normalize_url()
    print("\n--- Testing normalize_url() ---")
    
    test_urls = [
        ("https://BreakingBourbon.com/Review/Eagle-Rare/?utm_source=twitter", 
         "https://breakingbourbon.com/review/eagle-rare"),
        ("https://example.com/path/", 
         "https://example.com/path"),
        (None, None),
        ("", None)
    ]
    
    for original, expected in test_urls:
        result = normalize_url(original)
        status = "✓" if result == expected else "✗"
        print(f"{status} normalize_url('{original}')")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
    
    # Test normalize_string()
    print("\n--- Testing normalize_string() ---")
    
    test_strings = [
        ("  Eagle  Rare  ", "eagle rare"),
        ("BUFFALO TRACE", "buffalo trace"),
        ("", None),
        (None, None),
        ("   ", None)
    ]
    
    for original, expected in test_strings:
        result = normalize_string(original)
        status = "✓" if result == expected else "✗"
        print(f"{status} normalize_string('{original}')")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
    
    # Test parse_date()
    print("\n--- Testing parse_date() ---")
    
    test_dates = [
        "Nov 15, 2024",
        "2024-11-15",
        "15/11/2024",
        "invalid date",
        None
    ]
    
    for date_str in test_dates:
        result = parse_date(date_str)
        print(f"  parse_date('{date_str}') = {result}")
    
    # Test get_current_timestamp()
    print("\n--- Testing get_current_timestamp() ---")
    timestamp = get_current_timestamp()
    print(f"  Current timestamp: {timestamp}")
    print(f"  Format looks correct: {'✓' if len(timestamp) == 19 else '✗'}")


def test_database_operations():
    """Test all database operation functions"""
    print("\n" + "="*60)
    print("TESTING DATABASE OPERATIONS")
    print("="*60)
    
    conn = get_connection()
    
    # Test 1: Insert first whiskey
    print("\n--- Test 1: Insert New Whiskey ---")
    whiskey_id_1 = insert_whiskey(conn, "Eagle Rare", "Buffalo Trace Distillery")
    print(f"  Inserted whiskey_id: {whiskey_id_1}")
    
    # Test 2: Find the whiskey we just inserted
    print("\n--- Test 2: Find Existing Whiskey ---")
    found_id = find_whiskey(conn, "eagle rare", "buffalo trace distillery")
    print(f"  Found whiskey_id: {found_id}")
    print(f"  Match: {'✓' if found_id == whiskey_id_1 else '✗'}")
    
    # Test 3: Try to find non-existent whiskey
    print("\n--- Test 3: Find Non-Existent Whiskey ---")
    not_found = find_whiskey(conn, "Pappy Van Winkle", "Buffalo Trace Distillery")
    print(f"  Found: {not_found}")
    print(f"  Correctly returns None: {'✓' if not_found is None else '✗'}")
    
    # Test 4: Insert whiskey with no distillery
    print("\n--- Test 4: Insert Whiskey Without Distillery ---")
    whiskey_id_2 = insert_whiskey(conn, "Blanton's")
    print(f"  Inserted whiskey_id: {whiskey_id_2}")
    
    # Test 5: Insert first review
    print("\n--- Test 5: Insert Complete Review ---")
    review_1 = {
        'name': 'Eagle Rare',
        'distillery': 'Buffalo Trace Distillery',
        'source_site': 'Breaking Bourbon',
        'source_url': 'https://www.breakingbourbon.com/review/eagle-rare',
        'classification': 'Straight Bourbon',
        'company': 'Sazerac',
        'proof': '90',
        'age': '10 Years',
        'mashbill': 'Buffalo Trace Mash #1',
        'price': '$30',
        'nose': 'Caramel and vanilla',
        'palate': 'Oak and spice',
        'finish': 'Long and smooth',
        'rating': '7/10',
        'review_date': 'Nov 15, 2024'
    }
    
    review_id_1 = insert_review(conn, review_1)
    print(f"  Inserted review_id: {review_id_1}")
    
    # Test 6: Try to insert duplicate review
    print("\n--- Test 6: Insert Duplicate Review (Should Skip) ---")
    review_id_duplicate = insert_review(conn, review_1)
    print(f"  Returned: {review_id_duplicate}")
    print(f"  Correctly returns None: {'✓' if review_id_duplicate is None else '✗'}")
    
    # Test 7: Insert review with minimal fields
    print("\n--- Test 7: Insert Review With Minimal Fields ---")
    review_2 = {
        'name': "Blanton's",
        'source_site': 'Bourbon Banter',
        'source_url': 'https://www.bourbonbanter.com/blantons-review',
        'rating': '8/10'
    }
    
    review_id_2 = insert_review(conn, review_2)
    print(f"  Inserted review_id: {review_id_2}")
    
    # Test 8: Insert second review for same whiskey
    print("\n--- Test 8: Insert Second Review for Same Whiskey ---")
    review_3 = {
        'name': 'Eagle Rare',
        'distillery': 'Buffalo Trace Distillery',
        'source_site': 'Bourbon Culture',
        'source_url': 'https://thebourbonculture.com/eagle-rare-review',
        'rating': '6/10'
    }
    
    review_id_3 = insert_review(conn, review_3)
    print(f"  Inserted review_id: {review_id_3}")
    
    # Test 9: Check duplicate detection
    print("\n--- Test 9: Check Duplicate Detection ---")
    normalized_url = normalize_url(review_1['source_url'])
    is_duplicate = check_duplicate_review(conn, 'Breaking Bourbon', normalized_url)
    print(f"  Is duplicate: {is_duplicate}")
    print(f"  Correctly detects duplicate: {'✓' if is_duplicate else '✗'}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
    print(f"\nDatabase location: {DB_PATH}")
    print("Next step: Open database in DB Browser for SQLite to verify data")


if __name__ == "__main__":
    print("WHISKEY DATABASE TEST SUITE")
    print("=" * 60)
    
    # Run utility function tests
    test_utility_functions()
    
    # Run database operation tests
    test_database_operations()