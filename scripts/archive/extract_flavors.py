#!/usr/bin/env python3
"""
Flavor Extraction Script
Parses all reviews to extract unique flavors from pipe-delimited tasting notes.
"""

import sqlite3
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = '/Users/michaelangolia/whiskey-scraper/whiskey_reviews.db'


def extract_flavors_from_text(text):
    """
    Extract individual flavors from pipe-delimited text.

    Args:
        text: String like "Caramel | Vanilla | Oak"

    Returns:
        List of cleaned flavor strings
    """
    if not text or text.strip() == '':
        return []

    # Split on pipe and clean each flavor
    flavors = []
    for flavor in text.split('|'):
        cleaned = flavor.strip()
        if cleaned and cleaned != '':
            # Remove common prefixes/suffixes for normalization
            cleaned = cleaned.replace('Dash of ', '')
            cleaned = cleaned.replace('Hint of ', '')
            cleaned = cleaned.replace('Faint ', '')
            cleaned = cleaned.replace('Light ', '')
            cleaned = cleaned.replace('Heavy ', '')
            cleaned = cleaned.replace('Strong ', '')
            cleaned = cleaned.replace('Slight ', '')
            cleaned = cleaned.replace('Muted ', '')

            # Normalize case (title case)
            cleaned = cleaned.title()

            flavors.append(cleaned)

    return flavors


def analyze_reviews(conn):
    """
    Analyze all reviews and extract unique flavors.

    Returns:
        Dictionary with extraction statistics and unique flavors
    """
    cursor = conn.cursor()

    # Determine which columns to use (old or new names)
    cursor.execute("PRAGMA table_info(reviews)")
    columns = {row[1] for row in cursor.fetchall()}

    if 'nose_text' in columns:
        nose_col = 'nose_text'
        palate_col = 'palate_text'
        finish_col = 'finish_text'
    else:
        nose_col = 'nose'
        palate_col = 'palate'
        finish_col = 'finish'

    print(f"Using columns: {nose_col}, {palate_col}, {finish_col}")

    # Fetch all reviews
    cursor.execute(f"""
        SELECT
            review_id,
            whiskey_id,
            source_site,
            {nose_col} as nose,
            {palate_col} as palate,
            {finish_col} as finish
        FROM reviews
        WHERE {nose_col} IS NOT NULL OR {palate_col} IS NOT NULL OR {finish_col} IS NOT NULL
    """)

    reviews = cursor.fetchall()

    # Track statistics
    stats = {
        'total_reviews': len(reviews),
        'reviews_with_nose': 0,
        'reviews_with_palate': 0,
        'reviews_with_finish': 0,
    }

    # Track unique flavors
    all_flavors = set()
    flavor_frequency = Counter()
    flavor_by_section = defaultdict(set)
    flavor_section_frequency = defaultdict(Counter)

    print(f"\nProcessing {len(reviews)} reviews...")

    for review_id, whiskey_id, source_site, nose, palate, finish in reviews:
        # Extract nose flavors
        if nose:
            stats['reviews_with_nose'] += 1
            nose_flavors = extract_flavors_from_text(nose)
            for flavor in nose_flavors:
                all_flavors.add(flavor)
                flavor_frequency[flavor] += 1
                flavor_by_section[flavor].add('nose')
                flavor_section_frequency['nose'][flavor] += 1

        # Extract palate flavors
        if palate:
            stats['reviews_with_palate'] += 1
            palate_flavors = extract_flavors_from_text(palate)
            for flavor in palate_flavors:
                all_flavors.add(flavor)
                flavor_frequency[flavor] += 1
                flavor_by_section[flavor].add('palate')
                flavor_section_frequency['palate'][flavor] += 1

        # Extract finish flavors
        if finish:
            stats['reviews_with_finish'] += 1
            finish_flavors = extract_flavors_from_text(finish)
            for flavor in finish_flavors:
                all_flavors.add(flavor)
                flavor_frequency[flavor] += 1
                flavor_by_section[flavor].add('finish')
                flavor_section_frequency['finish'][flavor] += 1

    stats['unique_flavors'] = len(all_flavors)

    return {
        'stats': stats,
        'all_flavors': sorted(all_flavors),
        'flavor_frequency': flavor_frequency,
        'flavor_by_section': flavor_by_section,
        'flavor_section_frequency': flavor_section_frequency,
    }


def save_results(results, output_dir='data'):
    """Save extraction results to JSON files."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save unique flavors list
    flavors_file = os.path.join(output_dir, f'unique_flavors_{timestamp}.json')
    with open(flavors_file, 'w') as f:
        json.dump(results['all_flavors'], f, indent=2)
    print(f"\n✓ Unique flavors saved to: {flavors_file}")

    # Save flavor frequency
    frequency_file = os.path.join(output_dir, f'flavor_frequency_{timestamp}.json')
    frequency_data = dict(results['flavor_frequency'].most_common())
    with open(frequency_file, 'w') as f:
        json.dump(frequency_data, f, indent=2)
    print(f"✓ Flavor frequency saved to: {frequency_file}")

    # Save flavor sections mapping
    sections_file = os.path.join(output_dir, f'flavor_sections_{timestamp}.json')
    sections_data = {
        flavor: list(sections)
        for flavor, sections in results['flavor_by_section'].items()
    }
    with open(sections_file, 'w') as f:
        json.dump(sections_data, f, indent=2)
    print(f"✓ Flavor sections mapping saved to: {sections_file}")

    # Save section-specific frequency
    section_freq_file = os.path.join(output_dir, f'section_frequency_{timestamp}.json')
    section_freq_data = {
        section: dict(counter.most_common())
        for section, counter in results['flavor_section_frequency'].items()
    }
    with open(section_freq_file, 'w') as f:
        json.dump(section_freq_data, f, indent=2)
    print(f"✓ Section-specific frequency saved to: {section_freq_file}")

    # Save summary statistics
    stats_file = os.path.join(output_dir, f'extraction_stats_{timestamp}.json')
    with open(stats_file, 'w') as f:
        json.dump(results['stats'], f, indent=2)
    print(f"✓ Statistics saved to: {stats_file}")

    return {
        'flavors': flavors_file,
        'frequency': frequency_file,
        'sections': sections_file,
        'section_frequency': section_freq_file,
        'stats': stats_file,
    }


def print_summary(results):
    """Print a summary of extraction results."""
    print("\n" + "="*80)
    print("FLAVOR EXTRACTION SUMMARY")
    print("="*80)

    stats = results['stats']
    print(f"\nReviews Analyzed:")
    print(f"  Total reviews:          {stats['total_reviews']}")
    print(f"  Reviews with nose:      {stats['reviews_with_nose']} ({stats['reviews_with_nose']/stats['total_reviews']*100:.1f}%)")
    print(f"  Reviews with palate:    {stats['reviews_with_palate']} ({stats['reviews_with_palate']/stats['total_reviews']*100:.1f}%)")
    print(f"  Reviews with finish:    {stats['reviews_with_finish']} ({stats['reviews_with_finish']/stats['total_reviews']*100:.1f}%)")

    print(f"\nFlavors Extracted:")
    print(f"  Unique flavors found:   {stats['unique_flavors']}")

    print(f"\nTop 20 Most Common Flavors:")
    for i, (flavor, count) in enumerate(results['flavor_frequency'].most_common(20), 1):
        sections = ', '.join(sorted(results['flavor_by_section'][flavor]))
        print(f"  {i:2}. {flavor:30} - {count:4} mentions ({sections})")

    print(f"\nFlavor Distribution by Section:")
    for section in ['nose', 'palate', 'finish']:
        section_flavors = results['flavor_section_frequency'][section]
        print(f"  {section.title():8} - {len(section_flavors)} unique flavors, {sum(section_flavors.values())} total mentions")

    print("\n" + "="*80 + "\n")


def main():
    """Main extraction function."""
    print("="*80)
    print("WHISKEY SCRAPER - FLAVOR EXTRACTION")
    print("="*80)

    if not os.path.exists(DB_PATH):
        print(f"✗ Database not found at: {DB_PATH}")
        return 1

    # Connect to database
    print(f"\nConnecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    try:
        # Extract flavors
        print("\nExtracting flavors from reviews...")
        results = analyze_reviews(conn)

        # Print summary
        print_summary(results)

        # Save results
        print("Saving results...")
        files = save_results(results)

        print("\n✓✓✓ Flavor extraction completed successfully! ✓✓✓\n")

        return 0

    except Exception as e:
        print(f"\n✗ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())
