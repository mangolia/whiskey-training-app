#!/usr/bin/env python3
"""
Flavor Cleanup Script - Hybrid Approach (Option C)
Filters extracted flavors to identify valid descriptors vs. full sentences.
"""

import json
import re
import sys
import os
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load the most recent extraction files
DATA_DIR = 'data'


def load_latest_extraction():
    """Load the most recent flavor extraction files."""
    import glob

    flavor_files = sorted(glob.glob(os.path.join(DATA_DIR, 'unique_flavors_*.json')))
    freq_files = sorted(glob.glob(os.path.join(DATA_DIR, 'flavor_frequency_*.json')))

    if not flavor_files or not freq_files:
        print("✗ No extraction files found. Run extract_flavors.py first.")
        sys.exit(1)

    with open(flavor_files[-1], 'r') as f:
        flavors = json.load(f)

    with open(freq_files[-1], 'r') as f:
        frequency = json.load(f)

    print(f"✓ Loaded {len(flavors)} flavors from: {os.path.basename(flavor_files[-1])}")
    print(f"✓ Loaded frequency data from: {os.path.basename(freq_files[-1])}")

    return flavors, frequency


def is_valid_flavor(flavor_text):
    """
    Determine if a flavor string is a valid descriptor or a sentence/paragraph.

    Returns:
        tuple: (is_valid, reason, confidence_score)
            is_valid: True if likely a valid flavor
            reason: Why it was accepted/rejected
            confidence_score: 0-100 (higher = more confident it's valid)
    """

    # Strip whitespace
    text = flavor_text.strip()

    # Reject if empty
    if not text:
        return (False, "empty", 0)

    # Character count filters
    length = len(text)
    if length > 100:
        return (False, "too_long_chars", 0)

    if length < 2:
        return (False, "too_short", 0)

    # Word count filters
    word_count = len(text.split())
    if word_count > 15:
        return (False, "too_many_words", 0)

    # Reject if starts with "&" or other connectors (likely partial sentences)
    if text.startswith(('&', 'And ', 'Or ', 'But ', 'With ', 'Without ')):
        return (False, "connector_start", 10)

    # Reject if contains multiple sentences (periods followed by capital letters)
    if re.search(r'\.\s+[A-Z]', text):
        return (False, "multiple_sentences", 0)

    # Reject if contains quotation marks (likely quoted text)
    if '"' in text or "'" in text:
        return (False, "contains_quotes", 5)

    # Reject if starts with "A " or "An " (likely start of sentence)
    if re.match(r'^An?\s+[A-Z]', text):
        return (False, "article_start", 10)

    # Reject if contains verbs that suggest it's a sentence
    sentence_verbs = [
        'is', 'are', 'was', 'were', 'has', 'have', 'had',
        'shows', 'reveals', 'delivers', 'creates', 'makes',
        'comes', 'goes', 'appears', 'seems', 'feels',
        'greets', 'provides', 'offers', 'gives'
    ]

    words_lower = text.lower().split()
    if any(verb in words_lower for verb in sentence_verbs):
        # Exception: single compound descriptors like "cream-filled" are okay
        if word_count <= 5:
            return (True, "verb_but_short", 60)
        return (False, "contains_verb", 20)

    # Reject if it looks like a full sentence (pronoun + verb patterns)
    if re.search(r'\b(it|this|that|these|those)\b', text, re.IGNORECASE):
        return (False, "pronoun_pattern", 10)

    # Accept short descriptors (1-5 words, length 3-50 chars)
    if 1 <= word_count <= 5 and 3 <= length <= 50:
        return (True, "short_descriptor", 90)

    # Accept medium descriptors (6-8 words) if they don't have sentence markers
    if 6 <= word_count <= 8 and length <= 60:
        # Check for capitalization patterns (all caps words suggest descriptors)
        cap_words = sum(1 for word in text.split() if word[0].isupper())
        if cap_words >= word_count * 0.5:  # At least 50% capitalized
            return (True, "medium_descriptor_caps", 70)
        return (False, "medium_ambiguous", 40)

    # Longer descriptors (9-15 words) are likely sentences unless they're compound descriptors
    if 9 <= word_count <= 15:
        # Check if it's a list-like structure (commas, "and", "with")
        if ',' in text or ' And ' in text or ' With ' in text:
            return (True, "compound_descriptor", 65)
        return (False, "long_ambiguous", 30)

    # Default rejection for anything else
    return (False, "default_reject", 25)


def filter_flavors(flavors, frequency):
    """
    Filter flavors into valid, invalid, and ambiguous categories.

    Returns:
        dict with 'valid', 'invalid', 'ambiguous' lists
    """

    results = {
        'valid': [],
        'invalid': [],
        'ambiguous': []
    }

    for flavor in flavors:
        freq = frequency.get(flavor, 0)
        is_valid, reason, confidence = is_valid_flavor(flavor)

        entry = {
            'flavor': flavor,
            'frequency': freq,
            'reason': reason,
            'confidence': confidence
        }

        if is_valid and confidence >= 70:
            results['valid'].append(entry)
        elif not is_valid and confidence <= 30:
            results['invalid'].append(entry)
        else:
            results['ambiguous'].append(entry)

    # Sort by frequency (most common first)
    results['valid'].sort(key=lambda x: x['frequency'], reverse=True)
    results['ambiguous'].sort(key=lambda x: x['frequency'], reverse=True)
    results['invalid'].sort(key=lambda x: x['frequency'], reverse=True)

    return results


def save_filtered_results(results, output_dir='data'):
    """Save filtered results to JSON files."""
    from datetime import datetime

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    files = {}

    # Save valid flavors
    valid_file = os.path.join(output_dir, f'valid_flavors_{timestamp}.json')
    with open(valid_file, 'w') as f:
        json.dump(results['valid'], f, indent=2)
    files['valid'] = valid_file
    print(f"✓ Valid flavors saved to: {valid_file}")

    # Save ambiguous flavors (for manual review)
    ambiguous_file = os.path.join(output_dir, f'ambiguous_flavors_{timestamp}.json')
    with open(ambiguous_file, 'w') as f:
        json.dump(results['ambiguous'], f, indent=2)
    files['ambiguous'] = ambiguous_file
    print(f"✓ Ambiguous flavors saved to: {ambiguous_file}")

    # Save invalid flavors (for reference)
    invalid_file = os.path.join(output_dir, f'invalid_flavors_{timestamp}.json')
    with open(invalid_file, 'w') as f:
        json.dump(results['invalid'], f, indent=2)
    files['invalid'] = invalid_file
    print(f"✓ Invalid flavors saved to: {invalid_file}")

    # Save summary statistics
    stats = {
        'total_flavors': len(results['valid']) + len(results['ambiguous']) + len(results['invalid']),
        'valid_count': len(results['valid']),
        'ambiguous_count': len(results['ambiguous']),
        'invalid_count': len(results['invalid']),
        'valid_percentage': len(results['valid']) / (len(results['valid']) + len(results['ambiguous']) + len(results['invalid'])) * 100,
        'timestamp': timestamp
    }

    stats_file = os.path.join(output_dir, f'cleanup_stats_{timestamp}.json')
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    files['stats'] = stats_file
    print(f"✓ Statistics saved to: {stats_file}")

    return files


def print_summary(results):
    """Print a summary of filtering results."""
    total = len(results['valid']) + len(results['ambiguous']) + len(results['invalid'])

    print("\n" + "="*80)
    print("FLAVOR CLEANUP SUMMARY")
    print("="*80)

    print(f"\nTotal flavors processed: {total}")
    print(f"\n✓ Valid flavors:      {len(results['valid']):4} ({len(results['valid'])/total*100:.1f}%)")
    print(f"? Ambiguous flavors:  {len(results['ambiguous']):4} ({len(results['ambiguous'])/total*100:.1f}%) - NEEDS REVIEW")
    print(f"✗ Invalid flavors:    {len(results['invalid']):4} ({len(results['invalid'])/total*100:.1f}%)")

    print(f"\n📋 Top 20 Valid Flavors (by frequency):")
    for i, entry in enumerate(results['valid'][:20], 1):
        print(f"  {i:2}. {entry['flavor'][:50]:50} - {entry['frequency']:4} mentions")

    print(f"\n❓ Top 20 Ambiguous Flavors (needs manual review):")
    for i, entry in enumerate(results['ambiguous'][:20], 1):
        print(f"  {i:2}. {entry['flavor'][:50]:50} - {entry['frequency']:4} mentions")

    print(f"\n✗ Sample Invalid Flavors (rejected):")
    for i, entry in enumerate(results['invalid'][:10], 1):
        reason = entry['reason'].replace('_', ' ').title()
        print(f"  {i:2}. [{reason}] {entry['flavor'][:60]}")

    print("\n" + "="*80)
    print(f"\nNext Step: Review {len(results['ambiguous'])} ambiguous flavors")
    print("Run: python scripts/review_flavors.py")
    print("="*80 + "\n")


def main():
    """Main cleanup function."""
    print("="*80)
    print("WHISKEY SCRAPER - FLAVOR CLEANUP (HYBRID APPROACH)")
    print("="*80)

    # Load extraction data
    print("\n1. Loading extraction data...")
    flavors, frequency = load_latest_extraction()

    # Filter flavors
    print("\n2. Filtering flavors into valid/invalid/ambiguous...")
    results = filter_flavors(flavors, frequency)

    # Print summary
    print_summary(results)

    # Save results
    print("3. Saving filtered results...")
    files = save_filtered_results(results)

    print("\n✓✓✓ Flavor cleanup completed! ✓✓✓")
    print(f"\nFiles created:")
    for key, path in files.items():
        print(f"  {key}: {path}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
