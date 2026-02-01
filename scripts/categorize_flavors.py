#!/usr/bin/env python3
"""
Categorize Flavors - AI-Assisted Auto-Categorization
Assigns categories to 485 flavors using keyword matching + smart heuristics.
"""

import json
import sys
import os
from datetime import datetime
from collections import defaultdict

DATA_DIR = 'data'


def load_filtered_flavors():
    """Load the most recent filtered flavors."""
    import glob
    flavor_files = sorted(glob.glob(os.path.join(DATA_DIR, 'filtered_flavors_strategy_c_*.json')))

    if not flavor_files:
        print("✗ No filtered flavor files found. Run filter_and_consolidate.py first.")
        sys.exit(1)

    with open(flavor_files[-1], 'r') as f:
        flavors = json.load(f)

    print(f"✓ Loaded {len(flavors)} filtered flavors")
    return flavors


def categorize_flavor(flavor_name):
    """
    Categorize a flavor using keyword matching.

    Returns:
        tuple: (category, confidence_score)
            category: one of sweet, spicy, woody, fruity, grain, floral, savory, bitter, smoky, other
            confidence_score: 0-100
    """

    flavor_lower = flavor_name.lower()

    # Define category keywords with confidence weights
    categories = {
        'sweet': {
            'high': ['caramel', 'vanilla', 'honey', 'sugar', 'molasses', 'butterscotch', 'toffee', 'maple', 'candy'],
            'medium': ['syrup', 'sweet', 'cream', 'custard', 'frosting', 'fudge', 'taffy', 'nougat'],
            'low': []
        },
        'spicy': {
            'high': ['pepper', 'spice', 'cinnamon', 'nutmeg', 'clove', 'allspice', 'cardamom'],
            'medium': ['ginger', 'chili', 'cayenne', 'paprika', 'anise', 'licorice'],
            'low': ['spicy', 'hot', 'heat']
        },
        'woody': {
            'high': ['oak', 'wood', 'barrel', 'char', 'cedar', 'pine', 'mahogany'],
            'medium': ['timber', 'sawdust', 'lumber', 'toasted', 'charred'],
            'low': []
        },
        'fruity': {
            'high': ['cherry', 'apple', 'apricot', 'peach', 'plum', 'berry', 'strawberry', 'raspberry', 'blackberry', 'blueberry'],
            'medium': ['orange', 'lemon', 'lime', 'citrus', 'grape', 'banana', 'pear', 'fig', 'date', 'prune', 'raisin'],
            'low': ['fruit', 'fruity']
        },
        'grain': {
            'high': ['corn', 'wheat', 'rye grain', 'malt', 'barley', 'oat'],
            'medium': ['grain', 'cereal', 'bread', 'dough', 'bran'],
            'low': []
        },
        'floral': {
            'high': ['floral', 'rose', 'lavender', 'jasmine', 'hibiscus', 'chamomile'],
            'medium': ['flower', 'blossom', 'perfume', 'honeysuckle'],
            'low': []
        },
        'savory': {
            'high': ['leather', 'tobacco', 'earthy', 'mushroom', 'walnut', 'almond', 'pecan', 'hazelnut'],
            'medium': ['tea', 'coffee', 'espresso', 'nuts', 'peanut', 'cigar', 'smoke'],
            'low': ['savory', 'umami']
        },
        'bitter': {
            'high': ['bitter', 'cocoa', 'chocolate', 'coffee', 'espresso'],
            'medium': ['mocha', 'dark chocolate', 'baking chocolate'],
            'low': []
        },
        'smoky': {
            'high': ['smoke', 'smoky', 'ash', 'burnt', 'charcoal', 'campfire'],
            'medium': ['peat', 'smoked', 'fire'],
            'low': []
        }
    }

    # Score each category
    scores = {}

    for category, keyword_groups in categories.items():
        score = 0

        # High confidence keywords
        for keyword in keyword_groups['high']:
            if keyword in flavor_lower:
                score += 100
                break  # Don't double-count

        # Medium confidence keywords
        if score == 0:
            for keyword in keyword_groups['medium']:
                if keyword in flavor_lower:
                    score += 70
                    break

        # Low confidence keywords
        if score == 0:
            for keyword in keyword_groups['low']:
                if keyword in flavor_lower:
                    score += 40
                    break

        if score > 0:
            scores[category] = score

    # Determine best category
    if not scores:
        return ('other', 50)

    best_category = max(scores, key=scores.get)
    confidence = scores[best_category]

    # Handle special cases for compound flavors
    # If chocolate + fruit, prefer bitter
    if 'chocolate' in flavor_lower and 'fruity' in scores and 'bitter' in scores:
        return ('bitter', 90)

    # If oak + sweet, prefer woody
    if 'oak' in flavor_lower and 'sweet' in scores and 'woody' in scores:
        return ('woody', 95)

    return (best_category, confidence)


def determine_applicable_sections(flavor_name):
    """
    Determine which sections (nose, palate, finish) a flavor typically appears in.

    Most flavors appear in all three, but some are section-specific.
    """

    flavor_lower = flavor_name.lower()

    # Section-specific hints
    finish_only = ['lingering', 'aftertaste', 'tail']
    nose_only = ['aromatic', 'aroma', 'scent']

    if any(word in flavor_lower for word in finish_only):
        return ['finish']
    elif any(word in flavor_lower for word in nose_only):
        return ['nose']
    else:
        # Default: all sections
        return ['nose', 'palate', 'finish']


def categorize_all_flavors(flavors):
    """Categorize all flavors."""
    categorized = []
    category_counts = defaultdict(int)
    low_confidence = []

    print("\nCategorizing 485 flavors...")

    for i, flavor in enumerate(flavors):
        category, confidence = categorize_flavor(flavor['flavor'])
        sections = determine_applicable_sections(flavor['flavor'])

        categorized_entry = {
            'flavor': flavor['flavor'],
            'frequency': flavor['frequency'],
            'category': category,
            'confidence': confidence,
            'applicable_sections': sections
        }

        categorized.append(categorized_entry)
        category_counts[category] += 1

        if confidence < 70:
            low_confidence.append(categorized_entry)

        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/485 flavors...")

    print(f"  Processed 485/485 flavors... Done!")

    return categorized, category_counts, low_confidence


def save_categorized_flavors(flavors, category_counts, low_confidence, output_dir='data'):
    """Save categorized flavors."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save main categorized file
    output_file = os.path.join(output_dir, f'categorized_flavors_{timestamp}.json')
    with open(output_file, 'w') as f:
        json.dump(flavors, f, indent=2)

    # Save low confidence flavors for review
    if low_confidence:
        review_file = os.path.join(output_dir, f'low_confidence_flavors_{timestamp}.json')
        with open(review_file, 'w') as f:
            json.dump(low_confidence, f, indent=2)

    # Save statistics
    stats = {
        'total_flavors': len(flavors),
        'category_distribution': dict(category_counts),
        'low_confidence_count': len(low_confidence),
        'timestamp': timestamp
    }

    stats_file = os.path.join(output_dir, f'categorization_stats_{timestamp}.json')
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\nFiles saved:")
    print(f"  Categorized flavors: {output_file}")
    if low_confidence:
        print(f"  Low confidence (review): {review_file}")
    print(f"  Statistics: {stats_file}")

    return output_file, stats_file


def print_summary(flavors, category_counts, low_confidence):
    """Print categorization summary."""
    print("\n" + "="*80)
    print("CATEGORIZATION COMPLETE")
    print("="*80)

    print(f"\n✓ Categorized: {len(flavors)} flavors")
    print(f"  Low confidence (may need review): {len(low_confidence)} flavors")

    print(f"\n  Category Distribution:")
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    for category, count in sorted_categories:
        pct = count / len(flavors) * 100
        print(f"    {category:12} - {count:3} flavors ({pct:5.1f}%)")

    # Show samples from each category
    print(f"\n  Sample Flavors by Category:")
    for category, _ in sorted_categories:
        category_flavors = [f for f in flavors if f['category'] == category]
        print(f"\n  {category.upper()}:")
        for entry in category_flavors[:5]:
            print(f"    • {entry['flavor']:40} ({entry['frequency']} mentions)")

    if low_confidence:
        print(f"\n  Low Confidence Flavors (review recommended):")
        for entry in low_confidence[:10]:
            print(f"    • {entry['flavor']:40} - {entry['category']} ({entry['confidence']} confidence)")

    print("\n" + "="*80)
    print("NEXT STEP: Populate Database")
    print("="*80)
    print(f"\nRun: python scripts/populate_flavor_vocabulary.py")
    print(f"\nThis will insert {len(flavors)} flavors into the flavor_vocabulary table")
    print("="*80 + "\n")


def main():
    """Main categorization function."""
    print("="*80)
    print("CATEGORIZE FLAVORS - AI-ASSISTED AUTO-CATEGORIZATION")
    print("="*80)

    # Load flavors
    flavors = load_filtered_flavors()

    # Categorize
    categorized, category_counts, low_confidence = categorize_all_flavors(flavors)

    # Save results
    files = save_categorized_flavors(categorized, category_counts, low_confidence)

    # Print summary
    print_summary(categorized, category_counts, low_confidence)

    return 0


if __name__ == '__main__':
    sys.exit(main())
