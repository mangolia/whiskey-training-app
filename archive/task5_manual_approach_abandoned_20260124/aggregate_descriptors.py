#!/usr/bin/env python3
"""
Task 5: Aggregate Descriptors
After manual tagging, aggregate review_descriptors to create aggregated_whiskey_descriptors
"""

import sqlite3
import json
from pathlib import Path

# Use relative path to find database in same directory as script
DB_PATH = Path(__file__).parent / "whiskey_mvp.db"

def aggregate_descriptors():
    """Aggregate review descriptors to whiskey level"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("AGGREGATING DESCRIPTORS")
    print("=" * 80)

    # Clear existing aggregated data
    cursor.execute("DELETE FROM aggregated_whiskey_descriptors")
    print("\n🗑️  Cleared existing aggregated descriptors")

    # Aggregate: For each whiskey + descriptor + section combination,
    # count how many reviews mentioned it and collect review IDs
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

    rows_inserted = cursor.rowcount
    conn.commit()

    print(f"✅ Created {rows_inserted} aggregated descriptor entries")

    # Verification
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    # Count by whiskey
    cursor.execute("""
        SELECT
            w.name,
            COUNT(*) as descriptor_count
        FROM aggregated_whiskey_descriptors awd
        JOIN whiskeys w ON awd.whiskey_id = w.whiskey_id
        GROUP BY w.whiskey_id
        ORDER BY descriptor_count DESC
        LIMIT 10
    """)

    print("\nTop 10 whiskeys by descriptor count:")
    for name, count in cursor.fetchall():
        print(f"  {name[:50]:<50} {count:>3} descriptors")

    # Sample aggregated data
    print("\n" + "=" * 80)
    print("SAMPLE AGGREGATED DATA")
    print("=" * 80)

    cursor.execute("""
        SELECT
            w.name,
            dv.descriptor_name,
            awd.tasting_section,
            awd.review_count,
            awd.source_review_ids
        FROM aggregated_whiskey_descriptors awd
        JOIN whiskeys w ON awd.whiskey_id = w.whiskey_id
        JOIN descriptor_vocabulary dv ON awd.descriptor_id = dv.descriptor_id
        ORDER BY awd.review_count DESC, w.name
        LIMIT 20
    """)

    print(f"\n{'Whiskey':<30} {'Descriptor':<15} {'Section':<8} {'Count':<6} {'Reviews'}")
    print("-" * 80)

    for whiskey, descriptor, section, count, review_ids in cursor.fetchall():
        whiskey_short = whiskey[:28]
        descriptor_short = descriptor[:13]
        review_list = json.loads(review_ids)
        review_str = str(review_list)[:20]
        print(f"{whiskey_short:<30} {descriptor_short:<15} {section:<8} {count:<6} {review_str}")

    # Stats by section
    print("\n" + "=" * 80)
    print("STATS BY SECTION")
    print("=" * 80)

    for section in ['nose', 'palate', 'finish']:
        cursor.execute("""
            SELECT COUNT(*)
            FROM aggregated_whiskey_descriptors
            WHERE tasting_section = ?
        """, (section,))

        count = cursor.fetchone()[0]
        print(f"  {section.capitalize():<8}: {count} aggregated descriptors")

    # Check for whiskeys with very few descriptors
    print("\n" + "=" * 80)
    print("QUALITY CHECK")
    print("=" * 80)

    cursor.execute("""
        SELECT
            w.whiskey_id,
            w.name,
            awd.tasting_section,
            COUNT(*) as desc_count
        FROM whiskeys w
        LEFT JOIN aggregated_whiskey_descriptors awd ON w.whiskey_id = awd.whiskey_id
        GROUP BY w.whiskey_id, awd.tasting_section
        HAVING desc_count < 3 OR desc_count IS NULL
        ORDER BY desc_count
    """)

    low_count = cursor.fetchall()
    if low_count:
        print(f"\n⚠️  Whiskeys with <3 descriptors per section:")
        for wid, name, section, count in low_count[:10]:
            section_str = section if section else "all sections"
            count_str = count if count else 0
            print(f"  [{wid}] {name[:40]:<40} {section_str:<8}: {count_str} descriptors")
    else:
        print("\n✅ All whiskeys have adequate descriptor coverage")

    conn.close()

    print("\n" + "=" * 80)
    print("✅ AGGREGATION COMPLETE")
    print("=" * 80)
    print("\n🔜 Next: Verify quiz generation works correctly")

if __name__ == "__main__":
    try:
        aggregate_descriptors()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
