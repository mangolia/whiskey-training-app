#!/usr/bin/env python3
"""
Filter and Consolidate Flavors - Strategy C Implementation
Applies 5+ mention threshold and consolidates duplicates.
"""

import json
import sys
import os
from datetime import datetime
from collections import defaultdict

DATA_DIR = 'data'


def load_flavors():
    """Load the final valid flavors."""
    import glob
    flavor_files = sorted(glob.glob(os.path.join(DATA_DIR, 'final_valid_flavors_*.json')))

    if not flavor_files:
        print("✗ No flavor files found.")
        sys.exit(1)

    with open(flavor_files[-1], 'r') as f:
        flavors = json.load(f)

    print(f"✓ Loaded {len(flavors)} flavors")
    return flavors


def apply_frequency_filter(flavors, min_frequency=5):
    """Keep only flavors with minimum frequency."""
    filtered = [f for f in flavors if f['frequency'] >= min_frequency]
    print(f"\n1. Applied frequency filter (>= {min_frequency} mentions)")
    print(f"   Before: {len(flavors)} flavors")
    print(f"   After:  {len(filtered)} flavors")
    print(f"   Removed: {len(flavors) - len(filtered)} flavors")
    return filtered


def remove_descriptors(flavors):
    """Remove standalone descriptors that aren't actual flavors."""
    descriptors = [
        'long', 'short', 'medium length', 'medium', 'rich', 'dry',
        'light', 'bold', 'heavy', 'thick', 'thin', 'strong', 'mild',
        'lingering', 'faint', 'subtle', 'intense', 'smooth', 'rough',
        'creamy', 'oily', 'watery', 'syrupy', 'viscous'
    ]

    # Remove ONLY if it's a standalone descriptor (not part of compound)
    removed = []
    kept = []

    for flavor in flavors:
        flavor_lower = flavor['flavor'].lower()
        words = flavor_lower.split()

        # If it's a single word and matches descriptor, remove
        if len(words) == 1 and flavor_lower in descriptors:
            removed.append(flavor)
        # If it's 2 words and first word is descriptor + "mouthfeel" or "length", remove
        elif len(words) == 2 and words[0] in descriptors and words[1] in ['mouthfeel', 'length']:
            removed.append(flavor)
        else:
            kept.append(flavor)

    print(f"\n2. Removed standalone descriptors")
    print(f"   Before: {len(flavors)} flavors")
    print(f"   After:  {len(kept)} flavors")
    print(f"   Removed: {len(removed)} flavors")

    if removed:
        print(f"   Sample removed:")
        for entry in removed[:10]:
            print(f"     • {entry['flavor']}")

    return kept


def consolidate_duplicates(flavors):
    """Consolidate obvious duplicates (plural/singular, spacing, etc.)."""
    # Build consolidation map
    consolidation_map = {}
    flavor_dict = {}  # normalized -> original entry

    for flavor in flavors:
        original = flavor['flavor']
        normalized = original.lower().strip()

        # Handle plural/singular
        singular = normalized.rstrip('s') if normalized.endswith('s') and not normalized.endswith('ss') else normalized

        if singular in flavor_dict:
            # Found a duplicate, map this to the existing one
            existing = flavor_dict[singular]
            consolidation_map[original] = existing['flavor']
        elif normalized in flavor_dict:
            existing = flavor_dict[normalized]
            consolidation_map[original] = existing['flavor']
        else:
            # First time seeing this, store it
            flavor_dict[singular] = flavor
            flavor_dict[normalized] = flavor

    # Apply consolidations
    consolidated_flavors = {}

    for flavor in flavors:
        target_name = consolidation_map.get(flavor['flavor'], flavor['flavor'])

        if target_name not in consolidated_flavors:
            consolidated_flavors[target_name] = {
                'flavor': target_name,
                'frequency': flavor['frequency'],
                'reason': flavor.get('reason', 'short_descriptor'),
                'confidence': flavor.get('confidence', 90),
                'variants': [flavor['flavor']]
            }
        else:
            # Add frequency to existing
            consolidated_flavors[target_name]['frequency'] += flavor['frequency']
            consolidated_flavors[target_name]['variants'].append(flavor['flavor'])

    result = list(consolidated_flavors.values())
    result.sort(key=lambda x: x['frequency'], reverse=True)

    merged_count = len(flavors) - len(result)

    print(f"\n3. Consolidated duplicates (plural/singular)")
    print(f"   Before: {len(flavors)} flavors")
    print(f"   After:  {len(result)} flavors")
    print(f"   Merged: {merged_count} duplicates")

    # Show examples of merged
    merged_examples = [f for f in result if len(f.get('variants', [])) > 1]
    if merged_examples:
        print(f"   Sample consolidations:")
        for entry in merged_examples[:10]:
            variants_str = ' + '.join(entry['variants'])
            print(f"     • {entry['flavor']} ← {variants_str}")

    return result


def handle_variants(flavors):
    """
    Consolidate rare variants to base flavors.
    Keep major variants (100+ mentions), merge rare ones.
    """
    # Define base flavors and their variants
    variant_groups = {
        'oak': ['oak'],
        'vanilla': ['vanilla'],
        'cinnamon': ['cinnamon'],
        'caramel': ['caramel'],
        'cherry': ['cherry'],
        'chocolate': ['chocolate'],
        'pepper': ['pepper'],
        'leather': ['leather'],
    }

    # Build variant map
    variant_map = {}
    kept_variants = []
    merged = []

    for flavor in flavors:
        flavor_lower = flavor['flavor'].lower()
        base_found = None

        # Check if this is a variant of a base flavor
        for base, keywords in variant_groups.items():
            if any(keyword in flavor_lower for keyword in keywords):
                base_found = base
                break

        if base_found:
            # Check if this is THE base flavor or a significant variant
            if flavor_lower == base_found:
                # This IS the base flavor
                kept_variants.append(flavor)
            elif flavor['frequency'] >= 20:  # Keep significant variants
                kept_variants.append(flavor)
            else:
                # Merge into base
                variant_map[flavor['flavor']] = base_found
                merged.append(flavor)
        else:
            # Not a variant, keep as-is
            kept_variants.append(flavor)

    # Apply variant consolidations
    consolidated = {}

    for flavor in kept_variants:
        name = flavor['flavor']
        if name not in consolidated:
            consolidated[name] = flavor.copy()
        else:
            consolidated[name]['frequency'] += flavor['frequency']

    # Add frequencies from merged variants to base flavors
    for merged_flavor in merged:
        # Find the base flavor name (capitalize properly)
        base_name_lower = variant_map[merged_flavor['flavor']]

        # Find the actual base flavor entry (case-sensitive)
        base_entry = None
        for name, entry in consolidated.items():
            if name.lower() == base_name_lower:
                base_entry = entry
                break

        if base_entry:
            base_entry['frequency'] += merged_flavor['frequency']
            if 'merged_variants' not in base_entry:
                base_entry['merged_variants'] = []
            base_entry['merged_variants'].append(merged_flavor['flavor'])

    result = list(consolidated.values())
    result.sort(key=lambda x: x['frequency'], reverse=True)

    print(f"\n4. Consolidated rare variants")
    print(f"   Before: {len(flavors)} flavors")
    print(f"   After:  {len(result)} flavors")
    print(f"   Merged: {len(merged)} rare variants to base flavors")

    # Show examples
    with_merged = [f for f in result if 'merged_variants' in f and f['merged_variants']]
    if with_merged:
        print(f"   Sample variant consolidations:")
        for entry in with_merged[:10]:
            merged_str = ', '.join(entry['merged_variants'][:3])
            if len(entry['merged_variants']) > 3:
                merged_str += f" + {len(entry['merged_variants']) - 3} more"
            print(f"     • {entry['flavor']} ← {merged_str}")

    return result


def save_filtered_flavors(flavors, output_dir='data'):
    """Save filtered and consolidated flavors."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    output_file = os.path.join(output_dir, f'filtered_flavors_strategy_c_{timestamp}.json')
    with open(output_file, 'w') as f:
        json.dump(flavors, f, indent=2)

    # Also save just the names
    names_file = os.path.join(output_dir, f'filtered_flavor_names_{timestamp}.json')
    flavor_names = sorted([f['flavor'] for f in flavors])
    with open(names_file, 'w') as f:
        json.dump(flavor_names, f, indent=2)

    # Save statistics
    stats = {
        'total_flavors': len(flavors),
        'min_frequency': min(f['frequency'] for f in flavors),
        'max_frequency': max(f['frequency'] for f in flavors),
        'total_mentions': sum(f['frequency'] for f in flavors),
        'timestamp': timestamp,
        'strategy': 'C - Hybrid (5+ mentions)',
        'top_20': [
            {'flavor': f['flavor'], 'frequency': f['frequency']}
            for f in flavors[:20]
        ]
    }

    stats_file = os.path.join(output_dir, f'filtered_stats_{timestamp}.json')
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\n5. Saved filtered results")
    print(f"   Full data: {output_file}")
    print(f"   Names only: {names_file}")
    print(f"   Statistics: {stats_file}")

    return output_file, names_file, stats_file


def print_summary(flavors):
    """Print summary of filtered flavors."""
    print("\n" + "="*80)
    print("FILTERING COMPLETE - STRATEGY C (HYBRID)")
    print("="*80)

    print(f"\n✓ Final count: {len(flavors)} flavors")
    print(f"  Total mentions: {sum(f['frequency'] for f in flavors):,}")
    print(f"  Frequency range: {min(f['frequency'] for f in flavors)} - {max(f['frequency'] for f in flavors)}")

    # Frequency distribution
    ranges = [
        (500, float('inf'), 'Very Common (500+)'),
        (100, 499, 'Common (100-499)'),
        (50, 99, 'Moderate (50-99)'),
        (20, 49, 'Occasional (20-49)'),
        (10, 19, 'Rare (10-19)'),
        (5, 9, 'Very Rare (5-9)')
    ]

    print(f"\n  Frequency distribution:")
    for min_freq, max_freq, label in ranges:
        count = len([f for f in flavors if min_freq <= f['frequency'] <= max_freq])
        if count > 0:
            print(f"    {label:30} - {count:3} flavors")

    print(f"\n  Top 20 flavors:")
    for i, entry in enumerate(flavors[:20], 1):
        print(f"    {i:2}. {entry['flavor']:45} - {entry['frequency']:4} mentions")

    print("\n" + "="*80)
    print("NEXT STEP: Categorization")
    print("="*80)
    print(f"\nRun: python scripts/categorize_flavors.py")
    print(f"\nThis will assign categories (sweet, spicy, woody, etc.) to {len(flavors)} flavors")
    print("="*80 + "\n")


def main():
    """Main filtering and consolidation."""
    print("="*80)
    print("FILTER & CONSOLIDATE - STRATEGY C (HYBRID)")
    print("="*80)

    # Load flavors
    print("\nLoading flavors...")
    flavors = load_flavors()

    # Step 1: Apply frequency filter (5+ mentions)
    flavors = apply_frequency_filter(flavors, min_frequency=5)

    # Step 2: Remove standalone descriptors
    flavors = remove_descriptors(flavors)

    # Step 3: Consolidate duplicates
    flavors = consolidate_duplicates(flavors)

    # Step 4: Handle variants (merge rare variants to base)
    flavors = handle_variants(flavors)

    # Save results
    files = save_filtered_flavors(flavors)

    # Print summary
    print_summary(flavors)

    return 0


if __name__ == '__main__':
    sys.exit(main())
