"""
Conservative Prose Review Descriptor Extraction

This script extracts descriptors from prose-formatted reviews using
a conservative rule-based approach with negation handling.

Strategy:
- Exact term matching against descriptor vocabulary
- Strict negation detection (not, no, lacks, without)
- Position-based weighting (terms early in text score higher)
- Confidence scoring for manual review flagging
"""

import sqlite3
import re
from typing import List, Dict, Tuple


class ProseDescriptorExtractor:
    """Extract descriptors from prose reviews conservatively."""

    # Negation words that indicate descriptor is NOT present
    NEGATION_WORDS = [
        'not', 'no', 'without', 'lacking', 'lacks', 'absent',
        'missing', 'devoid', 'never', "doesn't", "don't", 'hardly'
    ]

    # Words that indicate weak/minimal presence (lower confidence)
    WEAK_INDICATORS = [
        'hint', 'trace', 'subtle', 'mild', 'faint', 'slight',
        'touch', 'dab', 'dash', 'bit of'
    ]

    # Words that indicate strong presence (higher confidence)
    STRONG_INDICATORS = [
        'dominant', 'prominent', 'heavy', 'rich', 'bold',
        'strong', 'intense', 'powerful', 'ample', 'plentiful'
    ]

    def __init__(self, db_path: str, vocab_db_path: str = None):
        """Initialize with database connection."""
        self.db = sqlite3.connect(db_path)
        self.cursor = self.db.cursor()

        # Use separate vocab database if provided
        if vocab_db_path:
            self.vocab_db = sqlite3.connect(vocab_db_path)
            self.vocab_cursor = self.vocab_db.cursor()
        else:
            self.vocab_db = self.db
            self.vocab_cursor = self.cursor

        self.load_descriptor_vocabulary()

    def load_descriptor_vocabulary(self):
        """Load descriptor vocabulary from database."""
        import json

        self.vocab_cursor.execute("""
            SELECT descriptor_id, descriptor_name, applicable_sections
            FROM descriptor_vocabulary
            WHERE is_active = 1
            ORDER BY LENGTH(descriptor_name) DESC
        """)

        self.descriptors = {}
        for desc_id, term, sections_json in self.vocab_cursor.fetchall():
            sections = json.loads(sections_json)
            self.descriptors[desc_id] = {
                'term': term.lower(),
                'sections': sections
            }

        print(f"Loaded {len(self.descriptors)} descriptors from vocabulary")

    def normalize_text(self, text: str) -> str:
        """Normalize text for matching."""
        if not text:
            return ""
        # Convert to lowercase, normalize whitespace
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def extract_from_section(self, text: str, section: str) -> List[Tuple[int, float]]:
        """
        Extract descriptors from a section of text.

        Returns:
            List of (descriptor_id, confidence) tuples
        """
        if not text:
            return []

        text = self.normalize_text(text)
        extracted = []

        # Track what we've already matched to avoid duplicates
        matched_spans = set()

        for desc_id, desc_info in self.descriptors.items():
            term = desc_info['term']
            sections = desc_info['sections']

            # Skip if descriptor doesn't apply to this section
            if section not in sections:
                continue

            # Look for the term in text
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = list(re.finditer(pattern, text))

            if not matches:
                continue

            # Check each match for negation and context
            for match in matches:
                start, end = match.span()

                # Skip if we already matched this span
                if any(start >= s and end <= e for s, e in matched_spans):
                    continue

                # Get context around the match (50 chars before and after)
                context_start = max(0, start - 50)
                context_end = min(len(text), end + 50)
                context = text[context_start:context_end]

                # Check for negation
                is_negated = self._is_negated(term, context)
                if is_negated:
                    continue  # Skip negated descriptors

                # Calculate confidence score
                confidence = self._calculate_confidence(term, context, text, start)

                # Conservative threshold: only include if confidence >= 0.6
                if confidence >= 0.6:
                    extracted.append((desc_id, confidence))
                    matched_spans.add((start, end))

        return extracted

    def _is_negated(self, term: str, context: str) -> bool:
        """Check if a term is negated in its context."""
        # Find where the term appears in the context
        term_pos = context.find(term)
        if term_pos == -1:
            return False

        # Get text before the term
        text_before = context[:term_pos].lower()

        # Check for clause boundaries (comma, semicolon, period, colon)
        # These break the negation scope
        clause_markers = [',', ';', '.', ':']
        last_clause_pos = max([text_before.rfind(marker) for marker in clause_markers])

        # Only look at text after the last clause marker
        if last_clause_pos > 0:
            text_before = text_before[last_clause_pos + 1:]

        # Check for negation reversal words (but, however, yet, though)
        # These reverse a previous negation
        reversal_words = ['but', 'however', 'yet', 'though', 'although']
        last_reversal_pos = max([text_before.rfind(word) for word in reversal_words])

        # Check if any negation word appears within 5 words before the term
        words_before_term = text_before.strip().split()[-5:]

        for neg_word in self.NEGATION_WORDS:
            if neg_word in words_before_term:
                # Check if there's a reversal word between the negation and the term
                neg_pos = text_before.rfind(neg_word)
                if last_reversal_pos > neg_pos:
                    # Negation was reversed (e.g., "not X, but Y")
                    return False
                return True

        return False

    def _calculate_confidence(self, term: str, context: str, full_text: str, position: int) -> float:
        """
        Calculate confidence score for a descriptor match.

        Factors:
        - Position in text (earlier = higher confidence)
        - Presence of strong/weak indicators nearby
        - Term frequency in text
        """
        confidence = 0.7  # Base confidence for exact match

        # Position bonus: terms early in text get higher score
        # First 20% of text: +0.2, gradually decreasing to 0
        position_pct = position / len(full_text)
        if position_pct < 0.2:
            confidence += 0.2
        elif position_pct < 0.5:
            confidence += 0.1

        # Check for weak indicators (lower confidence)
        for weak in self.WEAK_INDICATORS:
            if weak in context:
                confidence -= 0.2
                break

        # Check for strong indicators (higher confidence)
        for strong in self.STRONG_INDICATORS:
            if strong in context:
                confidence += 0.2
                break

        # Cap at 1.0
        return min(1.0, confidence)

    def extract_from_review(self, review_id: int, nose_text: str,
                           palate_text: str, finish_text: str) -> Dict[str, List[Tuple[int, float]]]:
        """
        Extract descriptors from all sections of a review.

        Returns:
            Dict with 'nose', 'palate', 'finish' keys, each containing
            list of (descriptor_id, confidence) tuples
        """
        results = {
            'nose': self.extract_from_section(nose_text, 'nose'),
            'palate': self.extract_from_section(palate_text, 'palate'),
            'finish': self.extract_from_section(finish_text, 'finish')
        }

        return results

    def is_prose_review(self, nose_text: str) -> bool:
        """Check if review is prose format (not pipe-delimited)."""
        if not nose_text:
            return False
        return '|' not in nose_text

    def calculate_review_confidence(self, extracted: Dict[str, List[Tuple[int, float]]]) -> float:
        """
        Calculate overall confidence score for a review's extraction.

        Used to flag reviews that may need manual review.
        Low confidence = needs human review
        High confidence = extraction is reliable
        """
        all_confidences = []

        for section in ['nose', 'palate', 'finish']:
            for desc_id, confidence in extracted[section]:
                all_confidences.append(confidence)

        if not all_confidences:
            return 0.0  # No descriptors found = low confidence

        # Average confidence across all extracted descriptors
        avg_confidence = sum(all_confidences) / len(all_confidences)

        # Penalize if very few descriptors found (expected 3-7 per section)
        total_descriptors = sum(len(extracted[s]) for s in ['nose', 'palate', 'finish'])
        if total_descriptors < 5:
            avg_confidence *= 0.8  # 20% penalty for sparse extraction

        return avg_confidence

    def process_all_prose_reviews(self, dry_run: bool = False) -> Dict:
        """
        Process all prose reviews in the database.

        Args:
            dry_run: If True, don't write to database, just return stats

        Returns:
            Dict with processing statistics
        """
        # Get all prose reviews
        self.cursor.execute("""
            SELECT
                review_id,
                whiskey_id,
                nose_text,
                palate_text,
                finish_text
            FROM reviews
            WHERE nose_text NOT LIKE '%|%'
            AND nose_text IS NOT NULL
        """)

        prose_reviews = self.cursor.fetchall()
        print(f"\nFound {len(prose_reviews)} prose reviews to process")

        stats = {
            'total_reviews': len(prose_reviews),
            'descriptors_extracted': 0,
            'low_confidence_reviews': [],  # Reviews that need manual review
            'high_confidence_reviews': 0,
            'skipped_reviews': 0
        }

        for review_id, whiskey_id, nose_text, palate_text, finish_text in prose_reviews:
            # Extract descriptors
            extracted = self.extract_from_review(review_id, nose_text, palate_text, finish_text)

            # Calculate confidence
            review_confidence = self.calculate_review_confidence(extracted)

            # Count total descriptors extracted
            total_desc = sum(len(extracted[s]) for s in ['nose', 'palate', 'finish'])

            if total_desc == 0:
                stats['skipped_reviews'] += 1
                continue

            # Flag for manual review if confidence is low
            if review_confidence < 0.7:
                stats['low_confidence_reviews'].append({
                    'review_id': review_id,
                    'whiskey_id': whiskey_id,
                    'confidence': review_confidence,
                    'descriptor_count': total_desc
                })
            else:
                stats['high_confidence_reviews'] += 1

            stats['descriptors_extracted'] += total_desc

            # Write to database if not dry run
            if not dry_run:
                for section in ['nose', 'palate', 'finish']:
                    for desc_id, confidence in extracted[section]:
                        self.cursor.execute("""
                            INSERT OR IGNORE INTO review_descriptors
                            (review_id, descriptor_id, tasting_section, confidence_score, extraction_method)
                            VALUES (?, ?, ?, ?, 'prose_conservative')
                        """, (review_id, desc_id, section, confidence))

        if not dry_run:
            self.db.commit()
            print(f"\n✅ Committed {stats['descriptors_extracted']} descriptor extractions to database")

        return stats

    def close(self):
        """Close database connection."""
        self.db.close()
        if hasattr(self, 'vocab_db') and self.vocab_db != self.db:
            self.vocab_db.close()


def main():
    """Run prose extraction with reporting."""
    print("=" * 80)
    print("CONSERVATIVE PROSE DESCRIPTOR EXTRACTION")
    print("=" * 80)

    # Use the production database
    extractor = ProseDescriptorExtractor('databases/whiskey_production.db')

    print("\nRunning in DRY RUN mode first to validate...")
    stats = extractor.process_all_prose_reviews(dry_run=True)

    print("\n" + "=" * 80)
    print("EXTRACTION STATISTICS")
    print("=" * 80)
    print(f"Total prose reviews: {stats['total_reviews']}")
    print(f"Descriptors extracted: {stats['descriptors_extracted']}")
    print(f"High confidence reviews: {stats['high_confidence_reviews']}")
    print(f"Low confidence reviews: {len(stats['low_confidence_reviews'])}")
    print(f"Skipped reviews (0 descriptors): {stats['skipped_reviews']}")

    if stats['low_confidence_reviews']:
        print(f"\n⚠️  {len(stats['low_confidence_reviews'])} reviews flagged for manual review:")
        for review in stats['low_confidence_reviews'][:10]:  # Show first 10
            print(f"  Review ID {review['review_id']}: "
                  f"{review['descriptor_count']} descriptors, "
                  f"confidence={review['confidence']:.2f}")

        if len(stats['low_confidence_reviews']) > 10:
            print(f"  ... and {len(stats['low_confidence_reviews']) - 10} more")

    # Ask user if they want to proceed
    print("\n" + "=" * 80)
    response = input("Proceed with actual extraction? (yes/no): ")

    if response.lower() == 'yes':
        print("\nProcessing for real...")
        stats = extractor.process_all_prose_reviews(dry_run=False)
        print("\n✅ Prose extraction complete!")
    else:
        print("\n❌ Extraction cancelled")

    extractor.close()


if __name__ == '__main__':
    main()
