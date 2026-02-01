#!/usr/bin/env python3
"""
Auto-extract descriptors from pipe-delimited reviews
Replaces manual tagging approach for Type A reviews
"""

import sqlite3
from pathlib import Path
import re

SOURCE_DB = Path("databases/whiskey_reviews.db")
TARGET_DB = Path("archive/databases/whiskey_mvp_v2.db")

def clean_descriptor(text):
    """Clean and normalize a descriptor string"""
    # Remove whitespace
    text = text.strip()

    # Convert to lowercase
    text = text.lower()

    # Remove trailing punctuation
    text = re.sub(r'[.,;:!?]+$', '', text)

    # Handle common variations
    # "hints of X" -> "X"
    text = re.sub(r'^hints? of\s+', '', text)
    text = re.sub(r'^touch of\s+', '', text)
    text = re.sub(r'^dab of\s+', '', text)
    text = re.sub(r'^light\s+', '', text)
    text = re.sub(r'^heavy\s+', '', text)
    text = re.sub(r'^faint\s+', '', text)

    return text

def extract_descriptors_from_text(text):
    """Extract list of descriptors from pipe-delimited text"""
    if not text or text == 'None':
        return []

    # Split by pipe
    parts = text.split('|')

    # Clean each descriptor
    descriptors = [clean_descriptor(part) for part in parts]

    # Filter out empty strings and very long phrases (likely sentences, not descriptors)
    descriptors = [d for d in descriptors if d and len(d) < 50]

    return descriptors

def analyze_extraction():
    """Analyze what descriptors we can extract"""
    conn = sqlite3.connect(SOURCE_DB)
    cursor = conn.cursor()

    # Get all pipe-delimited reviews
    cursor.execute("""
        SELECT w.whiskey_id, w.name, r.nose, r.palate, r.finish
        FROM reviews r
        JOIN whiskeys w ON r.whiskey_id = w.whiskey_id
        WHERE r.nose LIKE '%|%'
          AND r.palate LIKE '%|%'
          AND r.finish LIKE '%|%'
    """)

    all_descriptors = set()
    whiskey_count = 0
    total_extractions = 0

    print("ANALYZING PIPE-DELIMITED REVIEWS:")
    print("=" * 80)

    for row in cursor.fetchall():
        whiskey_id, name, nose, palate, finish = row
        whiskey_count += 1

        nose_descriptors = extract_descriptors_from_text(nose)
        palate_descriptors = extract_descriptors_from_text(palate)
        finish_descriptors = extract_descriptors_from_text(finish)

        all_descriptors.update(nose_descriptors)
        all_descriptors.update(palate_descriptors)
        all_descriptors.update(finish_descriptors)

        total_extractions += len(nose_descriptors) + len(palate_descriptors) + len(finish_descriptors)

        if whiskey_count <= 3:
            print(f"\n{name}:")
            print(f"  Nose ({len(nose_descriptors)}): {', '.join(nose_descriptors[:5])}...")
            print(f"  Palate ({len(palate_descriptors)}): {', '.join(palate_descriptors[:5])}...")
            print(f"  Finish ({len(finish_descriptors)}): {', '.join(finish_descriptors[:5])}...")

    print("\n" + "=" * 80)
    print(f"Total whiskeys with pipe-delimited reviews: {whiskey_count}")
    print(f"Total descriptors extracted: {total_extractions}")
    print(f"Unique descriptors found: {len(all_descriptors)}")
    print(f"Average descriptors per whiskey: {total_extractions/whiskey_count:.1f}")

    # Show top 30 most common descriptor terms (alphabetically)
    print("\nSample unique descriptors (first 30 alphabetically):")
    for desc in sorted(all_descriptors)[:30]:
        print(f"  - {desc}")

    conn.close()

    return whiskey_count, len(all_descriptors)

def find_whiskeys_with_most_reviews():
    """Find whiskeys that have multiple pipe-delimited reviews"""
    conn = sqlite3.connect(SOURCE_DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT w.whiskey_id, w.name, w.distillery, COUNT(r.review_id) as review_count
        FROM whiskeys w
        JOIN reviews r ON w.whiskey_id = r.whiskey_id
        WHERE r.nose LIKE '%|%'
          AND r.palate LIKE '%|%'
          AND r.finish LIKE '%|%'
        GROUP BY w.whiskey_id
        ORDER BY review_count DESC, w.name
        LIMIT 50
    """)

    print("\n" + "=" * 80)
    print("WHISKEYS WITH PIPE-DELIMITED REVIEWS (showing top 50):")
    print("=" * 80)

    results = cursor.fetchall()
    for row in results[:30]:
        print(f"{row[1]}: {row[3]} review(s)")

    conn.close()
    return results

if __name__ == "__main__":
    print("STEP 1: Analyzing pipe-delimited review format")
    print("=" * 80)

    whiskey_count, descriptor_count = analyze_extraction()

    print("\n\nSTEP 2: Finding best whiskeys for MVP")
    print("=" * 80)

    whiskeys = find_whiskeys_with_most_reviews()

    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print(f"✅ {whiskey_count} whiskeys with auto-extractable reviews")
    print(f"✅ {descriptor_count} unique descriptors found")
    print(f"✅ Can select 30 whiskeys with 1+ reviews each")
    print(f"✅ Extraction can be done in minutes, not hours")
    print("\nNext: Select 30 diverse whiskeys and build MVP database v2")
