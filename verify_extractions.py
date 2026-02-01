#!/usr/bin/env python3
"""
Verification script to review auto-extracted descriptors
Shows original review text alongside matched descriptors
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("whiskey_mvp_v2.db")

def verify_single_whiskey(whiskey_name=None):
    """Show detailed extraction for a specific whiskey"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get whiskey ID
    if whiskey_name:
        cursor.execute("SELECT whiskey_id, name FROM whiskeys WHERE name LIKE ?", (f"%{whiskey_name}%",))
    else:
        cursor.execute("SELECT whiskey_id, name FROM whiskeys LIMIT 1")

    result = cursor.fetchone()
    if not result:
        print(f"Whiskey not found: {whiskey_name}")
        return

    whiskey_id, name = result

    print("=" * 80)
    print(f"VERIFICATION: {name}")
    print("=" * 80)

    # Get reviews for this whiskey
    cursor.execute("""
        SELECT review_id, source_site, nose, palate, finish
        FROM reviews
        WHERE whiskey_id = ?
        ORDER BY review_id
    """, (whiskey_id,))

    reviews = cursor.fetchall()

    for review_id, source, nose, palate, finish in reviews:
        print(f"\nReview #{review_id} from {source}")
        print("-" * 80)

        # Get extracted descriptors for each section
        for section, text in [("nose", nose), ("palate", palate), ("finish", finish)]:
            print(f"\n{section.upper()}:")
            print(f'  Original: "{text}"')

            cursor.execute("""
                SELECT dv.descriptor_name
                FROM review_descriptors rd
                JOIN descriptor_vocabulary dv ON rd.descriptor_id = dv.descriptor_id
                WHERE rd.review_id = ? AND rd.tasting_section = ?
                ORDER BY dv.descriptor_name
            """, (review_id, section))

            descriptors = [row[0] for row in cursor.fetchall()]
            print(f'  Extracted ({len(descriptors)}): {", ".join(descriptors)}')

    # Show aggregated data
    print("\n" + "=" * 80)
    print("AGGREGATED QUIZ DATA:")
    print("=" * 80)

    for section in ["nose", "palate", "finish"]:
        cursor.execute("""
            SELECT dv.descriptor_name, awd.review_count
            FROM aggregated_whiskey_descriptors awd
            JOIN descriptor_vocabulary dv ON awd.descriptor_id = dv.descriptor_id
            WHERE awd.whiskey_id = ? AND awd.tasting_section = ?
            ORDER BY awd.review_count DESC, dv.descriptor_name
        """, (whiskey_id, section))

        descriptors = cursor.fetchall()
        print(f"\n{section.upper()} ({len(descriptors)} descriptors):")
        for desc, count in descriptors:
            marker = "✅✅" if count == 2 else "✅"
            print(f"  {marker} {desc} ({count}/2 reviews)")

    conn.close()

def show_extraction_stats():
    """Show overall extraction statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("EXTRACTION STATISTICS")
    print("=" * 80)

    # Descriptors per section
    cursor.execute("""
        SELECT tasting_section, COUNT(*) as tag_count
        FROM review_descriptors
        GROUP BY tasting_section
        ORDER BY tasting_section
    """)

    print("\nDescriptor tags by section:")
    for section, count in cursor.fetchall():
        print(f"  {section}: {count} tags")

    # Average descriptors per review
    cursor.execute("""
        SELECT r.review_id, COUNT(rd.descriptor_id) as desc_count
        FROM reviews r
        LEFT JOIN review_descriptors rd ON r.review_id = rd.review_id
        GROUP BY r.review_id
    """)

    counts = [row[1] for row in cursor.fetchall()]
    avg = sum(counts) / len(counts) if counts else 0
    print(f"\nAverage descriptors per review: {avg:.1f}")
    print(f"Range: {min(counts)} - {max(counts)}")

    # Most common descriptors
    cursor.execute("""
        SELECT dv.descriptor_name, COUNT(*) as frequency
        FROM review_descriptors rd
        JOIN descriptor_vocabulary dv ON rd.descriptor_id = dv.descriptor_id
        GROUP BY dv.descriptor_name
        ORDER BY frequency DESC
        LIMIT 15
    """)

    print("\nMost frequently extracted descriptors:")
    for desc, freq in cursor.fetchall():
        print(f"  {desc}: {freq} times")

    # Descriptors never extracted
    cursor.execute("""
        SELECT descriptor_name
        FROM descriptor_vocabulary
        WHERE descriptor_id NOT IN (
            SELECT DISTINCT descriptor_id FROM review_descriptors
        )
        ORDER BY descriptor_name
    """)

    unused = [row[0] for row in cursor.fetchall()]
    if unused:
        print(f"\nDescriptors not found in any review ({len(unused)}):")
        print(f"  {', '.join(unused)}")

    conn.close()

def list_all_whiskeys():
    """List all whiskeys in MVP database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT w.whiskey_id, w.name, COUNT(r.review_id) as review_count
        FROM whiskeys w
        LEFT JOIN reviews r ON w.whiskey_id = r.whiskey_id
        GROUP BY w.whiskey_id
        ORDER BY w.name
    """)

    print("=" * 80)
    print("ALL WHISKEYS IN MVP DATABASE")
    print("=" * 80)

    for wid, name, count in cursor.fetchall():
        print(f"{wid:3d}. {name} ({count} reviews)")

    conn.close()

def check_matching_quality():
    """Check for potential matching issues"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("MATCHING QUALITY CHECK")
    print("=" * 80)

    # Find reviews with very few descriptors (potential under-matching)
    cursor.execute("""
        SELECT w.name, r.review_id, r.nose, COUNT(rd.descriptor_id) as desc_count
        FROM reviews r
        JOIN whiskeys w ON r.whiskey_id = w.whiskey_id
        LEFT JOIN review_descriptors rd ON r.review_id = rd.review_id
        WHERE rd.tasting_section = 'nose'
        GROUP BY r.review_id
        HAVING desc_count < 3
        ORDER BY desc_count
    """)

    low_matches = cursor.fetchall()
    if low_matches:
        print(f"\nReviews with <3 nose descriptors (potential under-matching):")
        for name, rid, nose, count in low_matches[:5]:
            print(f"  Review {rid} ({name}): {count} descriptors")
            print(f'    Nose text: "{nose[:80]}..."')

    # Find reviews with very many descriptors (potential over-matching)
    cursor.execute("""
        SELECT w.name, r.review_id, r.nose, COUNT(rd.descriptor_id) as desc_count
        FROM reviews r
        JOIN whiskeys w ON r.whiskey_id = w.whiskey_id
        LEFT JOIN review_descriptors rd ON r.review_id = rd.review_id
        WHERE rd.tasting_section = 'nose'
        GROUP BY r.review_id
        HAVING desc_count > 10
        ORDER BY desc_count DESC
    """)

    high_matches = cursor.fetchall()
    if high_matches:
        print(f"\nReviews with >10 nose descriptors (potential over-matching):")
        for name, rid, nose, count in high_matches[:5]:
            print(f"  Review {rid} ({name}): {count} descriptors")
            print(f'    Nose text: "{nose[:80]}..."')

    conn.close()

def main():
    """Main verification menu"""
    import sys

    if len(sys.argv) > 1:
        # Verify specific whiskey from command line
        whiskey_name = ' '.join(sys.argv[1:])
        verify_single_whiskey(whiskey_name)
    else:
        # Interactive menu
        while True:
            print("\n" + "=" * 80)
            print("EXTRACTION VERIFICATION MENU")
            print("=" * 80)
            print("1. Show extraction statistics")
            print("2. List all whiskeys")
            print("3. Verify specific whiskey")
            print("4. Check matching quality")
            print("5. Exit")
            print()

            choice = input("Select option (1-5): ").strip()

            if choice == "1":
                show_extraction_stats()
            elif choice == "2":
                list_all_whiskeys()
            elif choice == "3":
                name = input("Enter whiskey name (partial match OK): ").strip()
                verify_single_whiskey(name)
            elif choice == "4":
                check_matching_quality()
            elif choice == "5":
                break
            else:
                print("Invalid choice")

if __name__ == "__main__":
    main()
