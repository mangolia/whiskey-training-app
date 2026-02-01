#!/usr/bin/env python3
"""
Improved descriptor matching - avoids false positives from substring matches
"""

import re
from descriptor_vocabulary import DESCRIPTORS

def match_descriptors_in_text(text):
    """
    Find which of our 74 descriptors appear in the given text
    Uses word boundary matching to avoid false positives

    Key rules:
    - Multi-word descriptors checked FIRST (to prevent partial matches)
    - Word boundary matching (prevents "nut" matching "nutmeg")
    - After matching a multi-word descriptor, remove it from consideration
      to prevent matching its component words
    """
    if not text or text == 'None':
        return []

    # Split by pipe and normalize
    parts = [part.strip().lower() for part in text.split('|')]

    # Track which parts have been fully matched by multi-word descriptors
    parts_to_check = list(parts)

    matches = []

    # Sort descriptors: multi-word first, then by length (longest first)
    # This ensures "brown sugar" is checked before "sugar"
    # and "stone fruit" is checked before "fruit"
    sorted_descriptors = sorted(
        DESCRIPTORS,
        key=lambda d: (0 if ' ' in d else 1, -len(d))
    )

    for descriptor in sorted_descriptors:
        # Check each pipe-delimited part
        for i, part in enumerate(parts_to_check):
            if part is None:  # Already fully matched by a multi-word descriptor
                continue

            matched = False

            # Strategy 1: Exact match
            if descriptor == part:
                matches.append(descriptor)
                # If this is a multi-word descriptor, mark part as consumed
                if ' ' in descriptor:
                    parts_to_check[i] = None
                matched = True
                break

            # Strategy 2: Multi-word descriptors in compound phrases
            # e.g., "brown sugar" in "light brown sugar"
            if ' ' in descriptor and descriptor in part:
                matches.append(descriptor)
                # Remove the matched phrase to prevent component matching
                parts_to_check[i] = part.replace(descriptor, '', 1).strip()
                matched = True
                break

            # Strategy 3: Single-word with word boundaries
            # Only applies to single-word descriptors
            if ' ' not in descriptor:
                pattern = r'\b' + re.escape(descriptor) + r'\b'
                if re.search(pattern, part):
                    matches.append(descriptor)
                    matched = True
                    break

            if matched:
                break

    return list(set(matches))  # Remove duplicates

def test_specific_cases():
    """Test problematic cases to verify fixes"""
    test_cases = [
        ("Brown sugar | Nutmeg | Oak", ["brown sugar", "nutmeg", "oak"]),
        ("Nut | Brown sugar", ["nut", "brown sugar"]),
        ("Sugar | Caramel", ["sugar", "caramel"]),
        ("Brown sugar | Sugar", ["brown sugar", "sugar"]),
        ("Vanilla custard | Oak", ["vanilla", "oak"]),
        ("Cherry cordial", ["cherry"]),
        ("Stone fruit | Plum", ["stone fruit", "plum"]),
        ("Light oak | Dry oak", ["oak", "dry"]),
    ]

    print("TESTING SPECIFIC CASES:")
    print("=" * 80)

    all_passed = True

    for text, expected in test_cases:
        result = sorted(match_descriptors_in_text(text))
        expected_sorted = sorted(expected)
        passed = result == expected_sorted

        status = "✅" if passed else "❌"
        print(f"\n{status} Input: '{text}'")
        print(f"   Expected: {expected_sorted}")
        print(f"   Got:      {result}")

        if not passed:
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed - needs refinement")

    return all_passed

if __name__ == "__main__":
    test_specific_cases()
