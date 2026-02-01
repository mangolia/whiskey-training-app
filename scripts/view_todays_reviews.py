"""
View Today's Reviews
===================

Quick script to view reviews scraped today from the database.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3

# Add project root to path (scripts/ is one level down)
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import DB_PATH, get_connection
from datetime import timezone


def view_todays_reviews():
    """Display all reviews scraped today (in UTC)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get today's date range in UTC (since database stores UTC)
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start.replace(hour=23, minute=59, second=59)
    today_start_str = today_start.strftime('%Y-%m-%d %H:%M:%S')
    today_end_str = today_end.strftime('%Y-%m-%d %H:%M:%S')
    today_display = today_start.strftime('%Y-%m-%d')
    
    print("\n" + "="*80)
    print(f"REVIEWS SCRAPED TODAY ({today_display} UTC)")
    print("="*80 + "\n")
    
    # Query reviews scraped today
    cursor.execute("""
        SELECT 
            r.review_id,
            w.name as whiskey_name,
            w.distillery,
            r.source_url,
            r.review_date,
            r.classification,
            r.proof,
            r.age,
            r.price,
            r.nose,
            r.palate,
            r.finish,
            r.overall_notes,
            r.date_scraped
        FROM reviews r
        JOIN whiskeys w ON r.whiskey_id = w.whiskey_id
        WHERE r.date_scraped >= ? AND r.date_scraped <= ?
        ORDER BY r.date_scraped DESC
    """, (today_start_str, today_end_str))
    
    reviews = cursor.fetchall()
    
    if not reviews:
        print("No reviews found for today.")
        conn.close()
        return
    
    print(f"Found {len(reviews)} review(s) scraped today:\n")
    
    for i, review in enumerate(reviews, 1):
        review_id, whiskey_name, distillery, source_url, review_date, \
        classification, proof, age, price, nose, palate, finish, overall_notes, date_scraped = review
        
        print(f"{'='*80}")
        print(f"Review #{i}: {whiskey_name}")
        print(f"{'='*80}")
        print(f"Review ID:      {review_id}")
        print(f"Scraped:        {date_scraped}")
        print(f"Whiskey:        {whiskey_name}")
        if distillery:
            print(f"Distillery:     {distillery}")
        if classification:
            print(f"Classification: {classification}")
        if proof:
            print(f"Proof:          {proof}")
        if age:
            print(f"Age:            {age}")
        if price:
            print(f"Price:          {price}")
        if review_date:
            print(f"Review Date:    {review_date}")
        print(f"Source URL:     {source_url}")
        
        if nose:
            print(f"\nNose:")
            print(f"  {nose[:200]}{'...' if len(nose) > 200 else ''}")
        
        if palate:
            print(f"\nPalate:")
            print(f"  {palate[:200]}{'...' if len(palate) > 200 else ''}")
        
        if finish:
            print(f"\nFinish:")
            print(f"  {finish[:200]}{'...' if len(finish) > 200 else ''}")
        
        if overall_notes:
            print(f"\nFull Review Text:")
            print(f"  {overall_notes}")
        
        print()
    
    conn.close()


if __name__ == "__main__":
    view_todays_reviews()

