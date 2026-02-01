#!/usr/bin/env python3
"""
Rebuild production database descriptor extractions
Run this after vocabulary changes
"""

import sqlite3
import json
from match_descriptors_v2 import match_descriptors_in_text
from extract_prose_descriptors import ProseDescriptorExtractor

print("=" * 80)
print("REBUILDING PRODUCTION DATABASE EXTRACTIONS")
print("=" * 80)

# Step 1: Clear existing data
print("\n1. Clearing existing extractions...")
db = sqlite3.connect('databases/whiskey_production.db')
cursor = db.cursor()

cursor.execute("DELETE FROM aggregated_whiskey_descriptors")
cursor.execute("DELETE FROM review_descriptors")
db.commit()
print("   ✓ Cleared")

# Step 2: Extract pipe-delimited reviews
print("\n2. Extracting pipe-delimited reviews...")

# Load vocabulary
cursor.execute("SELECT descriptor_id, descriptor_name FROM descriptor_vocabulary WHERE is_active = 1")
vocab_map = {name.lower(): desc_id for desc_id, name in cursor.fetchall()}
print(f"   Loaded {len(vocab_map)} descriptors")

# Get pipe-delimited reviews
cursor.execute("""
    SELECT review_id, nose_text, palate_text, finish_text
    FROM reviews
    WHERE nose_text LIKE '%|%'
    AND nose_text IS NOT NULL
""")

pipe_reviews = cursor.fetchall()
print(f"   Found {len(pipe_reviews)} pipe-delimited reviews")

pipe_count = 0
for i, (review_id, nose_text, palate_text, finish_text) in enumerate(pipe_reviews, 1):
    if i % 200 == 0:
        print(f"   Processing {i}/{len(pipe_reviews)}...")

    for section_name, section_text in [('nose', nose_text), ('palate', palate_text), ('finish', finish_text)]:
        if not section_text:
            continue

        matched_descriptors = match_descriptors_in_text(section_text)

        for descriptor_name in matched_descriptors:
            if descriptor_name in vocab_map:
                desc_id = vocab_map[descriptor_name]
                cursor.execute("""
                    INSERT INTO review_descriptors
                    (review_id, descriptor_id, tasting_section, confidence_score, extraction_method)
                    VALUES (?, ?, ?, 1.0, 'pipe_delimited')
                """, (review_id, desc_id, section_name))
                pipe_count += 1

db.commit()
print(f"   ✓ Extracted {pipe_count} descriptors")

db.close()

# Step 3: Extract prose reviews
print("\n3. Extracting prose reviews...")
extractor = ProseDescriptorExtractor('whiskey_production.db')
stats = extractor.process_all_prose_reviews(dry_run=False)
extractor.close()
print(f"   ✓ Extracted {stats['descriptors_extracted']} descriptors")

# Step 4: Aggregate
print("\n4. Aggregating descriptors...")
db = sqlite3.connect('whiskey_production.db')
cursor = db.cursor()

cursor.execute("""
    SELECT
        r.whiskey_id,
        rd.descriptor_id,
        rd.tasting_section,
        GROUP_CONCAT(rd.review_id) as review_ids,
        COUNT(*) as review_count
    FROM review_descriptors rd
    JOIN reviews r ON rd.review_id = r.review_id
    GROUP BY r.whiskey_id, rd.descriptor_id, rd.tasting_section
""")

aggregations = cursor.fetchall()

for whiskey_id, descriptor_id, section, review_ids_str, review_count in aggregations:
    review_ids = [int(x) for x in review_ids_str.split(',')]
    review_ids_json = json.dumps(review_ids)

    cursor.execute("""
        INSERT INTO aggregated_whiskey_descriptors
        (whiskey_id, descriptor_id, tasting_section, source_review_ids, review_count)
        VALUES (?, ?, ?, ?, ?)
    """, (whiskey_id, descriptor_id, section, review_ids_json, review_count))

db.commit()

# Get stats
cursor.execute("SELECT COUNT(*) FROM aggregated_whiskey_descriptors")
total_agg = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT whiskey_id) FROM aggregated_whiskey_descriptors")
quiz_ready = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM whiskeys")
total_whiskeys = cursor.fetchone()[0]

db.close()

print(f"   ✓ Created {total_agg} aggregated entries")
print(f"   ✓ {quiz_ready}/{total_whiskeys} quiz-ready whiskeys ({quiz_ready/total_whiskeys*100:.1f}%)")

print("\n" + "=" * 80)
print("✅ REBUILD COMPLETE")
print("=" * 80)
