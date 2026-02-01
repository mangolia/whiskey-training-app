#!/usr/bin/env python3
"""
Task 5: Manual Descriptor Tagging Interface
Interactive script for tagging reviews with descriptors
"""

import sqlite3
from pathlib import Path
import json

# Use relative path to find database in same directory as script
DB_PATH = Path(__file__).parent / "whiskey_mvp.db"

def get_descriptors_by_category():
    """Get all descriptors organized by category"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT descriptor_id, descriptor_name, category, applicable_sections
        FROM descriptor_vocabulary
        ORDER BY category, descriptor_name
    """)

    descriptors = cursor.fetchall()
    conn.close()

    # Organize by category
    by_category = {}
    for desc_id, name, category, sections in descriptors:
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((desc_id, name, sections))

    return by_category

def get_next_untagged_review():
    """Get the next review that hasn't been fully tagged"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Find reviews that don't have tags yet (or are incomplete)
    cursor.execute("""
        SELECT
            r.review_id,
            r.whiskey_id,
            w.name as whiskey_name,
            r.nose,
            r.palate,
            r.finish
        FROM reviews r
        JOIN whiskeys w ON r.whiskey_id = w.whiskey_id
        WHERE r.review_id NOT IN (
            SELECT DISTINCT review_id
            FROM review_descriptors
        )
        ORDER BY r.review_id
        LIMIT 1
    """)

    review = cursor.fetchone()
    conn.close()

    return review

def get_applicable_descriptors(section, descriptors_by_category):
    """Filter descriptors applicable to this section"""
    applicable = {}

    for category, desc_list in descriptors_by_category.items():
        applicable_in_category = []
        for desc_id, name, sections_json in desc_list:
            sections = json.loads(sections_json)
            if section in sections:
                applicable_in_category.append((desc_id, name))

        if applicable_in_category:
            applicable[category] = applicable_in_category

    return applicable

def display_descriptors(descriptors_by_category, section):
    """Display descriptors organized by category for a specific section"""
    print("\n" + "=" * 80)
    print(f"AVAILABLE DESCRIPTORS FOR {section.upper()}")
    print("=" * 80)

    applicable = get_applicable_descriptors(section, descriptors_by_category)

    for category in sorted(applicable.keys()):
        print(f"\n{category.upper()}:")
        desc_list = applicable[category]

        # Print in columns for readability
        for i in range(0, len(desc_list), 3):
            row = desc_list[i:i+3]
            row_str = "  ".join([f"[{d[0]:>2}] {d[1]:<20}" for d in row])
            print(f"  {row_str}")

    print("\n" + "=" * 80)

def tag_section(review_id, whiskey_name, section, text, descriptors_by_category):
    """Tag one section (nose, palate, or finish)"""
    print("\n" + "=" * 80)
    print(f"TAGGING: {whiskey_name} - {section.upper()}")
    print("=" * 80)

    if not text or text.strip() == "":
        print(f"\n⚠️  No {section} text available - skipping")
        return []

    print(f"\n{section.upper()} TEXT:")
    print(f'"{text}"')

    display_descriptors(descriptors_by_category, section)

    print(f"\nEnter descriptor IDs for {section} (comma-separated, or 's' to skip):")
    print("Example: 1, 39, 31, 48")

    user_input = input("> ").strip()

    if user_input.lower() == 's':
        print(f"⏭️  Skipped {section}")
        return []

    if not user_input:
        print(f"⚠️  No descriptors entered for {section}")
        return []

    # Parse descriptor IDs
    try:
        descriptor_ids = [int(x.strip()) for x in user_input.split(',')]
    except ValueError:
        print("❌ Invalid input. Please enter numbers separated by commas.")
        return tag_section(review_id, whiskey_name, section, text, descriptors_by_category)

    # Validate IDs
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    valid_ids = []
    for desc_id in descriptor_ids:
        cursor.execute("""
            SELECT descriptor_name, applicable_sections
            FROM descriptor_vocabulary
            WHERE descriptor_id = ?
        """, (desc_id,))

        result = cursor.fetchone()
        if not result:
            print(f"⚠️  Descriptor ID {desc_id} not found - skipping")
            continue

        name, sections_json = result
        sections = json.loads(sections_json)

        if section not in sections:
            print(f"⚠️  '{name}' not applicable to {section} - skipping")
            continue

        valid_ids.append(desc_id)

    conn.close()

    print(f"\n✅ Tagged {len(valid_ids)} descriptors for {section}")
    return valid_ids

def save_tags(review_id, section, descriptor_ids):
    """Save tags to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for desc_id in descriptor_ids:
        cursor.execute("""
            INSERT INTO review_descriptors
            (review_id, descriptor_id, tasting_section, tagged_by)
            VALUES (?, ?, ?, 'manual')
        """, (review_id, desc_id, section))

    conn.commit()
    conn.close()

def get_tagging_progress():
    """Get current tagging progress"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM reviews")
    total_reviews = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT review_id)
        FROM review_descriptors
    """)
    tagged_reviews = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM review_descriptors")
    total_tags = cursor.fetchone()[0]

    conn.close()

    return total_reviews, tagged_reviews, total_tags

def main():
    """Main tagging loop"""
    print("=" * 80)
    print("TASK 5: MANUAL DESCRIPTOR TAGGING")
    print("=" * 80)

    # Get progress
    total_reviews, tagged_reviews, total_tags = get_tagging_progress()
    print(f"\n📊 Progress: {tagged_reviews}/{total_reviews} reviews tagged ({total_tags} total tags)")

    # Load descriptors
    descriptors_by_category = get_descriptors_by_category()

    # Main loop
    while True:
        review = get_next_untagged_review()

        if not review:
            print("\n" + "=" * 80)
            print("🎉 ALL REVIEWS TAGGED!")
            print("=" * 80)

            total_reviews, tagged_reviews, total_tags = get_tagging_progress()
            print(f"\nFinal stats:")
            print(f"  Reviews tagged: {tagged_reviews}")
            print(f"  Total tags: {total_tags}")
            print(f"  Average tags per review: {total_tags / tagged_reviews:.1f}")
            print(f"\n🔜 Next: Run aggregation to create aggregated_whiskey_descriptors")
            break

        review_id, whiskey_id, whiskey_name, nose, palate, finish = review

        print(f"\n{'=' * 80}")
        print(f"Review #{review_id} - {whiskey_name}")
        print(f"{'=' * 80}")

        # Tag each section
        sections = [
            ('nose', nose),
            ('palate', palate),
            ('finish', finish)
        ]

        for section_name, section_text in sections:
            descriptor_ids = tag_section(review_id, whiskey_name, section_name, section_text, descriptors_by_category)

            if descriptor_ids:
                save_tags(review_id, section_name, descriptor_ids)

        # Ask if user wants to continue
        print(f"\n{'=' * 80}")
        total_reviews, tagged_reviews, total_tags = get_tagging_progress()
        print(f"Progress: {tagged_reviews}/{total_reviews} reviews tagged")
        print(f"{'=' * 80}")

        continue_input = input("\nContinue to next review? (y/n): ").strip().lower()
        if continue_input != 'y':
            print("\n⏸️  Paused. Run this script again to continue tagging.")
            print(f"📊 Current progress: {tagged_reviews}/{total_reviews} reviews")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Interrupted. Your progress has been saved.")
        total_reviews, tagged_reviews, total_tags = get_tagging_progress()
        print(f"📊 Current progress: {tagged_reviews}/{total_reviews} reviews tagged")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
