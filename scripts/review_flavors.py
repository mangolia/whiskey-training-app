#!/usr/bin/env python3
"""
Interactive Flavor Review Interface
Allows manual review of ambiguous flavors and learning from user decisions.
"""

import json
import sys
import os
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    print(f"✓ Loaded {len(ambiguous)} ambiguous flavors for review")

    return valid, ambiguous


def review_flavor(entry, index, total):
    """
    Present a single flavor for review.

    Returns:
        str: 'y' (yes/valid), 'n' (no/invalid), 's' (skip), 'q' (quit)
    """
    flavor = entry['flavor']
    freq = entry['frequency']
    reason = entry.get('reason', 'unknown').replace('_', ' ').title()
    confidence = entry.get('confidence', 0)

    print("\n" + "="*80)
    print(f"Flavor {index}/{total}")
    print("="*80)
    print(f"\nFlavor:     {flavor}")
    print(f"Frequency:  {freq} mentions")
    print(f"Auto-Score: {confidence}/100 ({reason})")
    print("\n" + "-"*80)

    while True:
        response = input("\nIs this a valid flavor? (y/n/s=skip/q=quit/h=help): ").strip().lower()

        if response in ['y', 'yes']:
            return 'y'
        elif response in ['n', 'no']:
            return 'n'
        elif response in ['s', 'skip']:
            return 's'
        elif response in ['q', 'quit', 'exit']:
            return 'q'
        elif response in ['h', 'help', '?']:
            print("\nCommands:")
            print("  y / yes  - Mark as VALID (accept as a flavor)")
            print("  n / no   - Mark as INVALID (reject, it's a sentence)")
            print("  s / skip - Skip this one (review later)")
            print("  q / quit - Save progress and exit")
            print("  h / help - Show this help")
        else:
            print("Invalid input. Type 'h' for help.")


def learn_patterns(reviewed):
    """
    Learn patterns from user decisions to auto-classify remaining flavors.

    Returns:
        dict: Learned patterns
    """
    patterns = {
        'accept_words': set(),
        'reject_words': set(),
        'accept_patterns': [],
        'reject_patterns': [],
    }

    # Analyze accepted flavors
    accepted = [r for r in reviewed if r['decision'] == 'y']
    rejected = [r for r in reviewed if r['decision'] == 'n']

    # Find common words in accepted flavors
    accept_word_freq = {}
    for entry in accepted:
        words = entry['flavor'].lower().split()
        for word in words:
            if len(word) > 3:  # Ignore short words
                accept_word_freq[word] = accept_word_freq.get(word, 0) + 1

    # Words that appear in >30% of accepted flavors
    threshold = len(accepted) * 0.3
    patterns['accept_words'] = {
        word for word, count in accept_word_freq.items()
        if count >= threshold
    }

    # Find common words in rejected flavors
    reject_word_freq = {}
    for entry in rejected:
        words = entry['flavor'].lower().split()
        for word in words:
            if len(word) > 3:
                reject_word_freq[word] = reject_word_freq.get(word, 0) + 1

    # Words that appear in >30% of rejected flavors
    threshold = len(rejected) * 0.3 if rejected else 1
    patterns['reject_words'] = {
        word for word, count in reject_word_freq.items()
        if count >= threshold
    }

    # Remove overlap (words that appear in both)
    overlap = patterns['accept_words'] & patterns['reject_words']
    patterns['accept_words'] -= overlap
    patterns['reject_words'] -= overlap

    return patterns


def auto_classify_remaining(ambiguous, reviewed_indices, patterns):
    """
    Auto-classify remaining ambiguous flavors based on learned patterns.

    Returns:
        tuple: (newly_valid, newly_invalid, still_ambiguous)
    """
    remaining = [
        entry for i, entry in enumerate(ambiguous)
        if i not in reviewed_indices
    ]

    newly_valid = []
    newly_invalid = []
    still_ambiguous = []

    for entry in remaining:
        flavor = entry['flavor']
        words = set(flavor.lower().split())

        # Check if it has accept words
        accept_score = len(words & patterns['accept_words'])

        # Check if it has reject words
        reject_score = len(words & patterns['reject_words'])

        # Decision logic
        if accept_score > 0 and reject_score == 0:
            newly_valid.append(entry)
        elif reject_score > 0 and accept_score == 0:
            newly_invalid.append(entry)
        else:
            still_ambiguous.append(entry)

    return newly_valid, newly_invalid, still_ambiguous


def save_review_results(valid, ambiguous, invalid, reviewed, patterns):
    """Save review results to files."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Combine original valid + newly accepted
    all_valid = valid + [r for r in reviewed if r['decision'] == 'y']

    # Combine original invalid + newly rejected
    reviewed_invalid = [r for r in reviewed if r['decision'] == 'n']

    # Save final valid flavors
    final_valid_file = os.path.join(DATA_DIR, f'final_valid_flavors_{timestamp}.json')
    with open(final_valid_file, 'w') as f:
        json.dump(all_valid, f, indent=2)
    print(f"✓ Final valid flavors saved: {final_valid_file}")

    # Save reviewed decisions (for audit)
    review_log_file = os.path.join(DATA_DIR, f'review_log_{timestamp}.json')
    with open(review_log_file, 'w') as f:
        json.dump({
            'reviewed': reviewed,
            'patterns': {
                'accept_words': list(patterns['accept_words']),
                'reject_words': list(patterns['reject_words'])
            },
            'timestamp': timestamp
        }, f, indent=2)
    print(f"✓ Review log saved: {review_log_file}")

    # Save remaining ambiguous
    if ambiguous:
        remaining_file = os.path.join(DATA_DIR, f'remaining_ambiguous_{timestamp}.json')
        with open(remaining_file, 'w') as f:
            json.dump(ambiguous, f, indent=2)
        print(f"✓ Remaining ambiguous flavors: {remaining_file}")

    # Save final statistics
    stats = {
        'total_valid': len(all_valid),
        'total_reviewed': len(reviewed),
        'accepted_in_review': len([r for r in reviewed if r['decision'] == 'y']),
        'rejected_in_review': len([r for r in reviewed if r['decision'] == 'n']),
        'skipped': len([r for r in reviewed if r['decision'] == 's']),
        'remaining_ambiguous': len(ambiguous),
        'learned_accept_words': len(patterns['accept_words']),
        'learned_reject_words': len(patterns['reject_words']),
        'timestamp': timestamp
    }

    stats_file = os.path.join(DATA_DIR, f'review_stats_{timestamp}.json')
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✓ Review statistics saved: {stats_file}")

    return {
        'final_valid': final_valid_file,
        'review_log': review_log_file,
        'stats': stats_file,
        'remaining': remaining_file if ambiguous else None
    }


def main():
    """Main review interface."""
    print("="*80)
    print("INTERACTIVE FLAVOR REVIEW")
    print("="*80)

    # Load cleanup results
    print("\n1. Loading cleanup results...")
    valid, ambiguous = load_latest_cleanup()

    # Limit review to top N most frequent (configurable)
    review_limit = 200
    to_review = ambiguous[:review_limit]

    print(f"\n2. You will review the top {len(to_review)} ambiguous flavors (by frequency)")
    print("   (The remaining {len(ambiguous) - len(to_review)} will be auto-classified based on your decisions)\n")

    response = input("Ready to start? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Review cancelled.")
        return 0

    # Review loop
    reviewed = []
    reviewed_indices = set()

    for i, entry in enumerate(to_review):
        decision = review_flavor(entry, i + 1, len(to_review))

        if decision == 'q':
            print("\n⚠️  Quitting early. Saving progress...")
            break

        reviewed.append({
            'flavor': entry['flavor'],
            'frequency': entry['frequency'],
            'decision': decision
        })
        reviewed_indices.add(i)

    # Learn patterns from reviewed flavors
    print("\n3. Learning patterns from your decisions...")
    patterns = learn_patterns(reviewed)

    print(f"\n✓ Learned patterns:")
    print(f"  Accept-words: {len(patterns['accept_words'])} words")
    print(f"  Reject-words: {len(patterns['reject_words'])} words")

    if patterns['accept_words']:
        print(f"\n  Common words in accepted flavors: {', '.join(list(patterns['accept_words'])[:10])}")
    if patterns['reject_words']:
        print(f"  Common words in rejected flavors: {', '.join(list(patterns['reject_words'])[:10])}")

    # Auto-classify remaining
    if len(reviewed_indices) < len(ambiguous):
        print(f"\n4. Auto-classifying {len(ambiguous) - len(reviewed_indices)} remaining flavors...")
        newly_valid, newly_invalid, still_ambiguous = auto_classify_remaining(
            ambiguous, reviewed_indices, patterns
        )

        print(f"\n✓ Auto-classification results:")
        print(f"  Newly valid:      {len(newly_valid)}")
        print(f"  Newly invalid:    {len(newly_invalid)}")
        print(f"  Still ambiguous:  {len(still_ambiguous)}")

        # Add auto-classified to reviewed
        for entry in newly_valid:
            reviewed.append({
                'flavor': entry['flavor'],
                'frequency': entry['frequency'],
                'decision': 'y_auto'
            })

        for entry in newly_invalid:
            reviewed.append({
                'flavor': entry['flavor'],
                'frequency': entry['frequency'],
                'decision': 'n_auto'
            })

        ambiguous = still_ambiguous
    else:
        ambiguous = []

    # Save results
    print("\n5. Saving review results...")
    files = save_review_results(valid, ambiguous, [], reviewed, patterns)

    print("\n" + "="*80)
    print("REVIEW COMPLETE!")
    print("="*80)
    print(f"\nFinal Statistics:")
    print(f"  Total valid flavors:  {len(valid) + len([r for r in reviewed if r['decision'].startswith('y')])}")
    print(f"  Manually reviewed:    {len([r for r in reviewed if not r['decision'].endswith('_auto')])}")
    print(f"  Auto-classified:      {len([r for r in reviewed if r['decision'].endswith('_auto')])}")
    print(f"  Still ambiguous:      {len(ambiguous)}")

    print(f"\nNext steps:")
    print(f"  1. Review results in: {files['final_valid']}")
    print(f"  2. Run categorization: python scripts/categorize_flavors.py")
    print("="*80 + "\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
