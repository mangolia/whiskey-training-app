#!/usr/bin/env python3
"""
Build MVP Database v2 - Auto-extracted from pipe-delimited reviews
Replaces the manual tagging approach
"""

import sqlite3
from pathlib import Path
import json
from descriptor_vocabulary import DESCRIPTORS
from match_descriptors_v2 import match_descriptors_in_text

SOURCE_DB = Path("databases/whiskey_reviews.db")
TARGET_DB = Path("archive/databases/whiskey_mvp_v2.db")

def create_mvp_database():
    """Create fresh MVP database with schema"""
    if TARGET_DB.exists():
        TARGET_DB.unlink()

    conn = sqlite3.connect(TARGET_DB)
    cursor = conn.cursor()

    # Read and execute the schema
    with open('schema_mvp_v2.sql', 'r') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)

    conn.commit()
    conn.close()
    print(f"✅ Created {TARGET_DB}")

def populate_descriptor_vocabulary():
    """Populate descriptor_vocabulary table"""
    # First, get the full descriptor data from old database
    old_conn = sqlite3.connect('archive/task5_manual_approach_abandoned_20260124/whiskey_mvp.db')
    old_cursor = old_conn.cursor()

    old_cursor.execute("""
        SELECT descriptor_id, descriptor_name, category, applicable_sections
        FROM descriptor_vocabulary
        ORDER BY descriptor_id
    """)
    descriptors = old_cursor.fetchall()
    old_conn.close()

    # Insert into new database
    conn = sqlite3.connect(TARGET_DB)
    cursor = conn.cursor()

    for desc_id, name, category, sections in descriptors:
        cursor.execute("""
            INSERT INTO descriptor_vocabulary
            (descriptor_id, descriptor_name, category, applicable_sections)
            VALUES (?, ?, ?, ?)
        """, (desc_id, name, category, sections))

    conn.commit()
    conn.close()
    print(f"✅ Populated descriptor_vocabulary with {len(descriptors)} descriptors")

def select_mvp_whiskeys():
    """
    Select 30 diverse whiskeys with pipe-delimited reviews
    Prioritize:
    - Whiskeys with 2 reviews (for consensus)
    - Popular/well-known whiskeys
    - Variety of types
    """
    conn = sqlite3.connect(SOURCE_DB)
    cursor = conn.cursor()

    # Get whiskeys with 2 pipe-delimited reviews
    cursor.execute("""
        SELECT w.whiskey_id, w.name, w.distillery, w.proof,
               w.age, w.mashbill, COUNT(r.review_id) as review_count
        FROM whiskeys w
        JOIN reviews r ON w.whiskey_id = r.whiskey_id
        WHERE r.nose LIKE '%|%'
          AND r.palate LIKE '%|%'
          AND r.finish LIKE '%|%'
        GROUP BY w.whiskey_id
        HAVING review_count >= 2
        ORDER BY w.name
        LIMIT 30
    """)

    whiskeys = cursor.fetchall()
    conn.close()

    print(f"\n✅ Selected {len(whiskeys)} whiskeys with 2+ pipe-delimited reviews:")
    for w in whiskeys:
        print(f"  - {w[1]} ({w[6]} reviews)")

    return whiskeys

def copy_whiskey_and_reviews(whiskey_ids):
    """Copy selected whiskeys and their reviews to MVP database"""
    source_conn = sqlite3.connect(SOURCE_DB)
    target_conn = sqlite3.connect(TARGET_DB)

    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    # Copy whiskeys (only columns that exist in source)
    placeholders = ','.join(['?' for _ in whiskey_ids])
    source_cursor.execute(f"""
        SELECT whiskey_id, name, distillery, proof, age, mashbill
        FROM whiskeys
        WHERE whiskey_id IN ({placeholders})
    """, whiskey_ids)

    whiskeys = source_cursor.fetchall()
    for w in whiskeys:
        target_cursor.execute("""
            INSERT INTO whiskeys
            (whiskey_id, name, distillery, proof, age, mashbill)
            VALUES (?, ?, ?, ?, ?, ?)
        """, w)

    # Copy reviews (only pipe-delimited ones)
    source_cursor.execute(f"""
        SELECT review_id, whiskey_id, source_site, source_url,
               nose, palate, finish, rating
        FROM reviews
        WHERE whiskey_id IN ({placeholders})
          AND nose LIKE '%|%'
          AND palate LIKE '%|%'
          AND finish LIKE '%|%'
    """, whiskey_ids)

    reviews = source_cursor.fetchall()
    for r in reviews:
        target_cursor.execute("""
            INSERT INTO reviews
            (review_id, whiskey_id, source_site, source_url,
             nose, palate, finish, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, r)

    target_conn.commit()
    source_conn.close()
    target_conn.close()

    print(f"✅ Copied {len(whiskeys)} whiskeys and {len(reviews)} reviews")
    return len(reviews)

def auto_tag_reviews():
    """Auto-extract descriptors from pipe-delimited reviews"""
    conn = sqlite3.connect(TARGET_DB)
    cursor = conn.cursor()

    # Get descriptor name to ID mapping
    cursor.execute("SELECT descriptor_id, descriptor_name FROM descriptor_vocabulary")
    descriptor_map = {name: desc_id for desc_id, name in cursor.fetchall()}

    # Get all reviews
    cursor.execute("SELECT review_id, nose, palate, finish FROM reviews")
    reviews = cursor.fetchall()

    total_tags = 0

    for review_id, nose, palate, finish in reviews:
        # Match descriptors in each section
        nose_descriptors = match_descriptors_in_text(nose)
        palate_descriptors = match_descriptors_in_text(palate)
        finish_descriptors = match_descriptors_in_text(finish)

        # Insert nose tags
        for desc_name in nose_descriptors:
            if desc_name in descriptor_map:
                cursor.execute("""
                    INSERT INTO review_descriptors
                    (review_id, descriptor_id, tasting_section)
                    VALUES (?, ?, 'nose')
                """, (review_id, descriptor_map[desc_name]))
                total_tags += 1

        # Insert palate tags
        for desc_name in palate_descriptors:
            if desc_name in descriptor_map:
                cursor.execute("""
                    INSERT INTO review_descriptors
                    (review_id, descriptor_id, tasting_section)
                    VALUES (?, ?, 'palate')
                """, (review_id, descriptor_map[desc_name]))
                total_tags += 1

        # Insert finish tags
        for desc_name in finish_descriptors:
            if desc_name in descriptor_map:
                cursor.execute("""
                    INSERT INTO review_descriptors
                    (review_id, descriptor_id, tasting_section)
                    VALUES (?, ?, 'finish')
                """, (review_id, descriptor_map[desc_name]))
                total_tags += 1

    conn.commit()
    conn.close()

    print(f"✅ Auto-tagged {total_tags} descriptors across {len(reviews)} reviews")
    print(f"   Average: {total_tags/len(reviews):.1f} tags per review")

def aggregate_descriptors():
    """Create aggregated_whiskey_descriptors table"""
    conn = sqlite3.connect(TARGET_DB)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO aggregated_whiskey_descriptors
        (whiskey_id, descriptor_id, tasting_section, source_review_ids, review_count)
        SELECT
            r.whiskey_id,
            rd.descriptor_id,
            rd.tasting_section,
            json_group_array(rd.review_id) as source_review_ids,
            COUNT(DISTINCT rd.review_id) as review_count
        FROM review_descriptors rd
        JOIN reviews r ON rd.review_id = r.review_id
        GROUP BY r.whiskey_id, rd.descriptor_id, rd.tasting_section
        HAVING review_count >= 1
    """)

    aggregated = cursor.rowcount
    conn.commit()
    conn.close()

    print(f"✅ Created {aggregated} aggregated descriptor entries")

def verify_data():
    """Verify the MVP database is ready for quiz generation"""
    conn = sqlite3.connect(TARGET_DB)
    cursor = conn.cursor()

    # Count everything
    cursor.execute("SELECT COUNT(*) FROM whiskeys")
    whiskey_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reviews")
    review_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM descriptor_vocabulary")
    descriptor_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM review_descriptors")
    tag_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM aggregated_whiskey_descriptors")
    agg_count = cursor.fetchone()[0]

    # Sample quiz data
    cursor.execute("""
        SELECT w.name, dv.descriptor_name, awd.tasting_section, awd.review_count
        FROM aggregated_whiskey_descriptors awd
        JOIN whiskeys w ON awd.whiskey_id = w.whiskey_id
        JOIN descriptor_vocabulary dv ON awd.descriptor_id = dv.descriptor_id
        WHERE w.whiskey_id = (SELECT MIN(whiskey_id) FROM whiskeys)
        ORDER BY awd.tasting_section, dv.descriptor_name
        LIMIT 10
    """)

    sample = cursor.fetchall()

    print("\n" + "=" * 80)
    print("MVP DATABASE V2 VERIFICATION:")
    print("=" * 80)
    print(f"✅ Whiskeys: {whiskey_count}")
    print(f"✅ Reviews: {review_count}")
    print(f"✅ Descriptors: {descriptor_count}")
    print(f"✅ Review tags: {tag_count}")
    print(f"✅ Aggregated entries: {agg_count}")

    if sample:
        print(f"\nSample quiz data for '{sample[0][0]}':")
        for row in sample:
            print(f"  {row[2]}: {row[1]} (mentioned in {row[3]} review(s))")

    conn.close()

if __name__ == "__main__":
    print("=" * 80)
    print("BUILDING MVP DATABASE V2 - AUTO-EXTRACTED")
    print("=" * 80)

    print("\n1. Creating database schema...")
    create_mvp_database()

    print("\n2. Populating descriptor vocabulary...")
    populate_descriptor_vocabulary()

    print("\n3. Selecting MVP whiskeys...")
    whiskeys = select_mvp_whiskeys()
    whiskey_ids = [w[0] for w in whiskeys]

    print("\n4. Copying whiskeys and reviews...")
    review_count = copy_whiskey_and_reviews(whiskey_ids)

    print("\n5. Auto-tagging descriptors...")
    auto_tag_reviews()

    print("\n6. Aggregating descriptors...")
    aggregate_descriptors()

    print("\n7. Verifying data...")
    verify_data()

    print("\n" + "=" * 80)
    print("✅ MVP DATABASE V2 COMPLETE!")
    print("=" * 80)
    print(f"Database: {TARGET_DB}")
    print("Ready for quiz generation")
