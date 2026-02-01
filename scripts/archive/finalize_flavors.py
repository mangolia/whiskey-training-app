#!/usr/bin/env python3
"""
Finalize Flavors - Auto-reject remaining ambiguous entries
Since all 49 ambiguous flavors are clearly full sentences, reject them all.
"""

import json
import sys
import os
from datetime import datetime

DATA_DIR = 'data'


def load_latest_cleanup():
    """Load the most recent cleanup files."""
    import glob

    valid_files = sorted(glob.glob(os.path.join(DATA_DIR, 'valid_flavors_*.json')))
    ambiguous_files = sorted(glob.glob(os.path.join(DATA_DIR, 'ambiguous_flavors_*.json')))

    if not valid_files or not ambiguous_files:
        print("✗ No cleanup files found. Run cleanup_flavors.py first.")
        sys.exit(1)

    with open(valid_files[-1], 'r') as f:
        valid = json.load(f)

    with open(ambiguous_files[-1], 'r') as f:
        ambiguous = json.load(f)

    print(f"✓ Loaded {len(valid)} valid flavors")
    print(f"✓ Loaded {len(ambiguous)} ambiguous flavors")

    return valid, ambiguous


def main():
    """Finalize the flavor list by rejecting ambiguous entries."""
    print("="*80)
    print("FINALIZE FLAVOR LIST")
    print("="*80)

    # Load data
    print("\n1. Loading cleanup results...")
    valid, ambiguous = load_latest_cleanup()

    # Show ambiguous samples
    print(f"\n2. Reviewing {len(ambiguous)} ambiguous flavors...")
    print("\n   Sample ambiguous flavors (all appear to be sentences):")
    for i, entry in enumerate(ambiguous[:10], 1):
        print(f"   {i}. {entry['flavor'][:70]}")

    # Ask for confirmation
    print(f"\n3. Decision: Reject all {len(ambiguous)} ambiguous flavors as invalid")
    response = input("\n   Proceed? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("\n✗ Finalization cancelled.")
        print("   To review manually, run: python scripts/review_flavors.py")
        return 1

    # Finalize
    print(f"\n4. Finalizing flavor list...")
    final_valid = valid  # Keep only the valid flavors

    # Save final list
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    final_file = os.path.join(DATA_DIR, f'final_valid_flavors_{timestamp}.json')
    with open(final_file, 'w') as f:
        json.dump(final_valid, f, indent=2)

    # Extract just the flavor names for convenience
    flavor_names = [entry['flavor'] for entry in final_valid]
    flavor_names_file = os.path.join(DATA_DIR, f'flavor_names_only_{timestamp}.json')
    with open(flavor_names_file, 'w') as f:
        json.dump(sorted(flavor_names), f, indent=2)

    # Save statistics
    stats = {
        'total_valid_flavors': len(final_valid),
        'rejected_ambiguous': len(ambiguous),
        'timestamp': timestamp,
        'top_20_flavors': [
            {'flavor': e['flavor'], 'frequency': e['frequency']}
            for e in final_valid[:20]
        ]
    }

    stats_file = os.path.join(DATA_DIR, f'final_stats_{timestamp}.json')
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    # Print results
    print("\n" + "="*80)
    print("FINALIZATION COMPLETE!")
    print("="*80)

    print(f"\n✓ Final valid flavors: {len(final_valid)}")
    print(f"✓ Rejected ambiguous:  {len(ambiguous)}")

    print(f"\nTop 20 Most Common Flavors:")
    for i, entry in enumerate(final_valid[:20], 1):
        print(f"  {i:2}. {entry['flavor']:40} - {entry['frequency']:4} mentions")

    print(f"\nFiles created:")
    print(f"  Full data:    {final_file}")
    print(f"  Names only:   {flavor_names_file}")
    print(f"  Statistics:   {stats_file}")

    print(f"\n📋 Next steps:")
    print(f"  1. Categorize flavors: python scripts/categorize_flavors.py")
    print(f"  2. Populate database:  python scripts/populate_flavor_vocabulary.py")
    print("="*80 + "\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
