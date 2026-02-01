"""
Update existing reviews with full review text.

This script re-scrapes reviews that are missing full review text.
"""

import sys
from pathlib import Path
from database import get_connection, normalize_url
from scrapers.breaking_bourbon import BreakingBourbonScraper
import sqlite3

# Add project root to path (scripts/ is one level down)
sys.path.insert(0, str(Path(__file__).parent.parent))

def update_review_text(review_url):
    """Update a single review with full text."""
    scraper = BreakingBourbonScraper()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Scrape the review
    print(f"Scraping: {review_url}")
    review_data = scraper.scrape_review(review_url)
    
    if not review_data:
        print("  ✗ Failed to scrape review")
        conn.close()
        return False
    
    # Get the normalized URL
    normalized_url = normalize_url(review_url)
    
    # Find the review in database
    cursor.execute("""
        SELECT review_id FROM reviews 
        WHERE source_site = ? AND normalized_url = ?
    """, (scraper.SOURCE_NAME, normalized_url))
    
    result = cursor.fetchone()
    if not result:
        print("  ✗ Review not found in database")
        conn.close()
        return False
    
    review_id = result[0]
    
    # Update the review with full text
    overall_notes = review_data.get('overall_notes', '')
    cursor.execute("""
        UPDATE reviews 
        SET overall_notes = ?
        WHERE review_id = ?
    """, (overall_notes, review_id))
    
    conn.commit()
    print(f"  ✓ Updated review #{review_id} with {len(overall_notes)} characters of review text")
    conn.close()
    return True


def update_all_missing_text():
    """Update all reviews that are missing full review text."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Find reviews with missing or short review text
    cursor.execute("""
        SELECT r.review_id, r.source_url, w.name
        FROM reviews r
        JOIN whiskeys w ON r.whiskey_id = w.whiskey_id
        WHERE r.source_site = 'Breaking Bourbon'
        AND (r.overall_notes IS NULL OR LENGTH(r.overall_notes) < 500)
        ORDER BY r.review_id DESC
    """)
    
    reviews = cursor.fetchall()
    
    if not reviews:
        print("No reviews need updating.")
        conn.close()
        return
    
    print(f"Found {len(reviews)} review(s) that need updating.\n")
    
    for review_id, source_url, whiskey_name in reviews:
        print(f"[{review_id}] {whiskey_name}")
        update_review_text(source_url)
        print()
    
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Update specific review
        url = sys.argv[1]
        update_review_text(url)
    else:
        # Update all reviews missing text
        update_all_missing_text()

