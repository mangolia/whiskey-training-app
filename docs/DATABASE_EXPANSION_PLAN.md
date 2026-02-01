# Database Expansion Plan

**Date**: January 26, 2026
**Current Status**: MVP with 30 whiskeys
**Goal**: Expand to full production database with all eligible whiskeys

---

## Current State

### MVP Database (whiskey_mvp_v2.db)
- **Whiskeys**: 30
- **Reviews**: 60 (2 per whiskey)
- **Descriptor tags**: 1,020
- **Format**: 71.5% pipe-delimited (auto-extracted)
- **Status**: ✅ Working perfectly in frontend

### Original Database (whiskey_reviews.db)
- **Total whiskeys**: 2,123
- **Total reviews**: 2,162
- **Whiskeys with 2+ reviews**: 39 (eligible for quiz)
- **Pipe-delimited reviews**: 1,530 (70.8%)
- **Prose reviews**: 617 (28.5%)
- **Missing reviews**: 15 (0.7%)

---

## Expansion Opportunity

### Phase 1: Add Remaining Eligible Whiskeys
**Opportunity**: 9 additional whiskeys with 2+ reviews
- Current: 30 whiskeys
- Available: 39 whiskeys with 2+ reviews
- **Target: 39 whiskeys (100% of eligible)**

### Phase 2: Build Prose Review Extraction
**Opportunity**: Extract descriptors from 28.5% prose reviews
- Current: Only pipe-delimited reviews processed
- Remaining: 617 prose reviews untapped
- **Impact**: Better quiz coverage, more accurate descriptors

---

## Implementation Plan

### Task 1: Identify Missing Whiskeys
**Action**: Find which 9 whiskeys are in original but not in MVP
- Query original database for all whiskeys with 2+ reviews
- Compare with MVP whiskeys
- Generate list of 9 whiskeys to add

**Output**: List of whiskey IDs to add

---

### Task 2: Add Missing Whiskeys to MVP
**Action**: Copy 9 whiskeys + their reviews to MVP database
- Use same process as original MVP build
- Copy whiskey records
- Copy review records
- Verify data integrity

**Output**: MVP expanded to 39 whiskeys (78 reviews)

---

### Task 3: Extract Descriptors for New Whiskeys
**Action**: Run auto-extraction on new reviews
- Use existing `match_descriptors_v2.py` script
- Extract from pipe-delimited reviews
- Populate `review_descriptors` table
- Aggregate to `aggregated_whiskey_descriptors` table

**Output**: All 39 whiskeys have quiz data

---

### Task 4: Build Prose Review Extraction
**Action**: Create NLP system for prose reviews
- Parse natural language review text
- Extract descriptors using pattern matching
- Handle negations ("not sweet", "lacks oak")
- Weight by sentiment intensity
- Validate against descriptor vocabulary

**Approach Options**:
1. **Rule-based**: Pattern matching with spaCy
2. **Semantic**: Embedding similarity (descriptor vocab → review text)
3. **Hybrid**: Patterns + embeddings

**Output**: Script that extracts descriptors from prose reviews

---

### Task 5: Process All Prose Reviews
**Action**: Run prose extraction on all 617 prose reviews
- Extract descriptors from prose reviews
- Compare with pipe-delimited extraction quality
- Adjust thresholds for accuracy
- Populate `review_descriptors` table

**Impact**:
- More whiskeys become eligible (those with 1 pipe + 1 prose)
- Better quiz coverage for existing whiskeys
- More diverse descriptor distribution

---

### Task 6: Rebuild Aggregated Data
**Action**: Regenerate quiz data with all reviews
- Drop and recreate `aggregated_whiskey_descriptors`
- Run aggregation query across all reviews
- Verify each whiskey has 3-5 descriptors per section
- Test quiz generation for all whiskeys

**Output**: Production-ready database

---

### Task 7: Test Frontend with Expanded Database
**Action**: Verify frontend works with all whiskeys
- Test search for all 39+ whiskeys
- Generate quiz for random sample
- Verify results page accuracy
- Check for edge cases

**Output**: Confirmed working with expanded data

---

## Data Quality Considerations

### Review Format Analysis

**Pipe-Delimited (70.8%)**:
- ✅ Easy to parse automatically
- ✅ Consistent format
- ✅ High extraction accuracy
- ✅ Already implemented

**Prose (28.5%)**:
- ⚠️ Requires NLP extraction
- ⚠️ Variable writing styles
- ⚠️ Needs negation handling
- ⚠️ Lower extraction confidence

**Missing (0.7%)**:
- ❌ Cannot extract descriptors
- ❌ Reviews with null nose/palate/finish text
- ❌ Skip these for now

### Classification Cleanup Needed

**Issue**: Inconsistent classification formatting
```
"Straight Bourbon": 582 whiskeys
": Straight Bourbon": 175 whiskeys  ← leading colon/space
" Straight Bourbon": 98 whiskeys   ← leading space
```

**Fix**: Normalize all classifications
- Trim whitespace
- Remove leading colons
- Standardize casing
- Update original database

---

## Prose Extraction Strategy

### Option 1: Rule-Based Pattern Matching ⭐ RECOMMENDED
**Approach**:
- Use descriptor vocabulary as search terms
- Match exact terms in review text
- Handle negations with simple rules
- Weight by position and frequency

**Pros**:
- Simple to implement
- Fast execution
- Predictable results
- No external dependencies

**Cons**:
- May miss synonyms
- Limited semantic understanding

**Example**:
```python
def extract_from_prose(review_text, section, descriptor_vocab):
    descriptors = []
    text_lower = review_text.lower()

    for descriptor in descriptor_vocab:
        if section in descriptor['applicable_sections']:
            term = descriptor['term'].lower()

            # Check for presence
            if term in text_lower:
                # Check for negation
                negation_words = ['not', 'no', 'lacking', 'without']
                is_negated = any(f"{neg} {term}" in text_lower
                                for neg in negation_words)

                if not is_negated:
                    descriptors.append(descriptor['descriptor_id'])

    return descriptors
```

### Option 2: Semantic Similarity (Advanced)
**Approach**:
- Use sentence embeddings (e.g., sentence-transformers)
- Compare review text to descriptor terms
- Threshold for similarity score
- More sophisticated negation handling

**Pros**:
- Catches synonyms ("charred" = "burnt")
- Better semantic understanding
- Handles paraphrasing

**Cons**:
- Requires external library
- Slower processing
- Less predictable
- Need to tune thresholds

### Option 3: Hybrid (Best of Both)
**Approach**:
- Start with exact matching (Option 1)
- Fall back to embeddings for unmatched text
- Use embeddings to validate matches

**Pros**:
- Best accuracy
- Catches edge cases

**Cons**:
- More complex
- Longer implementation time

---

## Implementation Priority

### Phase 1: Quick Wins (Today) ⚡
1. ✅ Analyze database scope
2. Add 9 missing whiskeys to MVP
3. Extract descriptors from their pipe-delimited reviews
4. Test frontend with 39 whiskeys
5. Polish frontend UI/UX

**Result**: 39 whiskeys, ~78 reviews, production-ready MVP

### Phase 2: Prose Extraction (Next Session) 🔬
1. Build rule-based prose extractor
2. Test on sample of prose reviews
3. Validate extraction quality
4. Process all 617 prose reviews
5. Rebuild aggregated quiz data

**Result**: All reviews utilized, better quiz coverage

### Phase 3: Polish & Deploy (After Prose) 🚀
1. Clean up classification data
2. Add more whiskeys (1 pipe + 1 prose = eligible)
3. Final testing across all whiskeys
4. Deploy to production

**Result**: Maximum whiskey coverage, deployed app

---

## Expected Outcomes

### After Phase 1 (39 Whiskeys)
- 30% more whiskeys available
- More diverse whiskey selection
- Better representation of different types
- Production-ready for initial launch

### After Phase 2 (Prose Extraction)
- ~50-100 additional whiskeys eligible
- Better quiz quality for existing whiskeys
- More comprehensive descriptor coverage
- Increased user engagement potential

### After Phase 3 (Full Production)
- 100+ whiskeys available
- Complete utilization of review data
- Professional, polished app
- Ready for public beta testing

---

## Success Metrics

### Data Quality
- ✅ Each whiskey has 2+ reviews
- ✅ Each whiskey has 4-6 descriptors per section
- ✅ Quiz generation works for all whiskeys
- ✅ No duplicate or invalid data

### Frontend Performance
- ✅ Search returns results in <500ms
- ✅ Quiz loads in <1s
- ✅ All whiskeys searchable by name
- ✅ Mobile-responsive on all devices

### User Experience
- ✅ Clear error messages
- ✅ Loading states for all async operations
- ✅ Smooth transitions between sections
- ✅ Intuitive quiz interface

---

## Next Steps

**Immediate (This Session)**:
1. Find 9 missing whiskeys
2. Add them to MVP database
3. Extract their descriptors
4. Test with frontend
5. Polish UI/UX

**Short Term (Next Session)**:
1. Build prose extractor
2. Process prose reviews
3. Expand whiskey count to 50+

**Long Term (Pre-Launch)**:
1. Deploy to production
2. Set up analytics
3. Beta test with users
4. Iterate based on feedback

---

## Questions to Consider

1. **Should we expand to 39 whiskeys before building prose extractor?**
   - ✅ Yes - quick win, more content immediately

2. **Should we prioritize prose extraction over frontend polish?**
   - ⚠️ Depends on launch timeline
   - Polish first if launching soon
   - Prose extraction if building long-term dataset

3. **Should we clean up classification data now or later?**
   - Later - doesn't affect core functionality
   - Can be a separate maintenance task

4. **Should we aim for 50+ whiskeys or stick with 39?**
   - Start with 39 (all pipe-delimited)
   - Add prose-based whiskeys after extraction works

---

**Status**: Plan finalized, ready to execute Phase 1
**Next Action**: Identify and add 9 missing whiskeys to MVP
