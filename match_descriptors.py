#!/usr/bin/env python3
"""
Match extracted text against our 74-descriptor vocabulary
Uses fuzzy matching to handle variations
"""

import sqlite3
from pathlib import Path
from descriptor_vocabulary import DESCRIPTORS

SOURCE_DB = Path("databases/whiskey_reviews.db")

def match_descriptors_in_text(text):
    """
    Find which of our 74 descriptors appear in the given text
    Handles variations and compound terms
    """
    if not text or text == 'None':
        return []

    # Normalize text
    text_lower = text.lower()

    matches = []

    for descriptor in DESCRIPTORS:
        # Split pipe-delimited text
        parts = [part.strip().lower() for part in text.split('|')]

        for part in parts:
            # Check for exact descriptor match
            if descriptor == part:
                matches.append(descriptor)
                break

            # Check if descriptor is contained in the part
            # e.g., "vanilla" in "vanilla custard" or "dry vanilla"
            elif descriptor in part:
                # Additional checks to avoid false positives
                # e.g., "ear" shouldn't match "pear"
                words_in_part = part.split()
                if descriptor in words_in_part or any(descriptor in word for word in words_in_part):
                    matches.append(descriptor)
                    break

    return list(set(matches))  # Remove duplicates

def test_matching():
    """Test the matching logic on real examples"""
    conn = sqlite3.connect(SOURCE_DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT w.name, r.nose, r.palate, r.finish
        FROM reviews r
        JOIN whiskeys w ON r.whiskey_id = w.whiskey_id
        WHERE r.nose LIKE '%|%'
        LIMIT 10
    """)

    print("TESTING DESCRIPTOR MATCHING:")
    print("=" * 80)

    total_matched = 0
    total_sections = 0

    for row in cursor.fetchall():
        name, nose, palate, finish = row

        nose_matches = match_descriptors_in_text(nose)
        palate_matches = match_descriptors_in_text(palate)
        finish_matches = match_descriptors_in_text(finish)

        total_matched += len(nose_matches) + len(palate_matches) + len(finish_matches)
        total_sections += 3

        print(f"\n{name}:")
        print(f"  Nose: {nose[:100]}...")
        print(f"  → Matched: {', '.join(nose_matches)}")
        print(f"  Palate: {palate[:100]}...")
        print(f"  → Matched: {', '.join(palate_matches)}")

    print("\n" + "=" * 80)
    print(f"Average matches per section: {total_matched/total_sections:.1f}")

    conn.close()

if __name__ == "__main__":
    test_matching()
