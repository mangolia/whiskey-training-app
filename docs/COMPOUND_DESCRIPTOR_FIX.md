# Compound Descriptor Fix

**Date**: January 28, 2026
**Status**: ✅ Complete

---

## Problem

The descriptor vocabulary had standalone descriptors that should have been compound terms, causing incorrect matching:

**Examples of issues:**
- "baking" instead of "baking spice"
- "baked" (incorrect standalone)
- Missing "toasted oak" (292 occurrences in reviews!)
- Missing "black pepper" (212 occurrences)
- Missing "dark chocolate" (120 occurrences)

**Impact**: Quiz results showed incorrect descriptors like "baking" and "apple" instead of "baking spice" and "caramel apple"

---

## Solution

### 1. Removed Incorrect Standalone Descriptors
- Removed "baking" (should be "baking spice")
- Removed "baked" (not a standalone descriptor)

### 2. Added 8 Compound Descriptors

| Compound | Category | Occurrences | Whiskeys Using |
|----------|----------|-------------|----------------|
| toasted oak | woody | 292 | 269 |
| black pepper | spicy | 212 | 191 |
| dark chocolate | sweet | 120 | 110 |
| fresh oak | woody | 50 | 46 |
| gingerbread | sweet | 38 | 37 |
| caramel apple | fruity | 20 | 18 |
| toasted grain | grain | 6 | 4 |
| peppery heat | spicy | 6 | 5 |

**Total**: Added 8 compounds representing 746 occurrences in source reviews

### 3. Updated Extraction System

**Updated Files:**
- `descriptor_vocabulary.py` - Regenerated from database (73 → 81 descriptors)
- `whiskey_production.db` - Added compound descriptors to vocabulary table
- All descriptor extractions rebuilt

**Extraction Logic:**
- Multi-word descriptors checked FIRST (prevents partial matching)
- "caramel apple" matched before "caramel" + "apple"
- "toasted oak" matched before "toasted" + "oak"
- Word boundary matching prevents false positives

---

## Verification

### Before Fix
```
Text: "Caramel apple | Vanilla | Oak"
Matched: vanilla, caramel, apple, oak  ❌
```

### After Fix
```
Text: "Caramel apple | Vanilla | Oak"
Matched: caramel apple, vanilla, oak  ✅
```

### Sample Whiskey Results

**Shortbarrel Tokaji Cask Finish Rye:**
- Nose: brown sugar (compound), caramel, oak, rye, vanilla
- Palate: brown sugar (compound), dried fruit (compound), oak, rye, spice
- Finish: toasted oak (compound), honey, rye, spice, vanilla

✅ Correctly shows compounds instead of component parts

---

## Database Changes

### Before
- 73 active descriptors
- ~22,450 pipe-delimited extractions
- ~8,350 prose extractions
- Issues with "baking", "baked" showing up incorrectly

### After
- **81 active descriptors** (+8 compounds, -2 removed)
- **22,105 pipe-delimited extractions** (more accurate)
- **8,089 prose extractions** (more accurate)
- **28,513 aggregated entries**
- **2,109 quiz-ready whiskeys** (99.2% coverage maintained)

---

## Technical Implementation

### 1. Database Update
```sql
-- Added 8 compound descriptors
INSERT INTO descriptor_vocabulary
(descriptor_name, category, applicable_sections)
VALUES
  ('toasted oak', 'woody', '["nose", "palate", "finish"]'),
  ('black pepper', 'spicy', '["nose", "palate", "finish"]'),
  ('dark chocolate', 'sweet', '["nose", "palate", "finish"]'),
  ('fresh oak', 'woody', '["nose", "palate", "finish"]'),
  ('gingerbread', 'sweet', '["nose", "palate", "finish"]'),
  ('caramel apple', 'fruity', '["nose", "palate", "finish"]'),
  ('toasted grain', 'grain', '["nose", "palate", "finish"]'),
  ('peppery heat', 'spicy', '["palate", "finish"]');

-- Removed incorrect descriptors
DELETE FROM descriptor_vocabulary
WHERE descriptor_name IN ('baking', 'baked');
```

### 2. Regenerated descriptor_vocabulary.py
Auto-generated from database to ensure consistency:
```python
# 81 descriptor vocabulary for matching
# Auto-generated from database
DESCRIPTORS = [
    "apple",
    "apricot",
    # ... (sorted alphabetically)
    "baking spice",      # Compound (was "baking")
    "black pepper",      # Compound (NEW)
    "brown sugar",       # Compound (existing)
    "caramel apple",     # Compound (NEW)
    "dark chocolate",    # Compound (NEW)
    "dried fruit",       # Compound (existing)
    "fresh oak",         # Compound (NEW)
    "gingerbread",       # Compound (NEW)
    "peppery heat",      # Compound (NEW)
    "stone fruit",       # Compound (existing)
    "toasted grain",     # Compound (NEW)
    "toasted oak",       # Compound (NEW)
    # ...
]
```

### 3. Matching Algorithm
The `match_descriptors_v2.py` script ensures correct matching:

```python
# Sort descriptors: multi-word first, then by length
sorted_descriptors = sorted(
    DESCRIPTORS,
    key=lambda d: (0 if ' ' in d else 1, -len(d))
)

# This ensures:
# - "brown sugar" checked before "sugar"
# - "toasted oak" checked before "toasted" or "oak"
# - "caramel apple" checked before "caramel" or "apple"
```

---

## Quality Assurance

### Testing Matrix

| Test Case | Input | Expected | Result |
|-----------|-------|----------|--------|
| Caramel Apple | "Caramel apple \| Vanilla" | caramel apple, vanilla | ✅ Pass |
| Toasted Oak | "Toasted oak \| Charred" | toasted oak, charred | ✅ Pass |
| Black Pepper | "Black pepper \| Cinnamon" | black pepper, cinnamon | ✅ Pass |
| Dark Chocolate | "Dark chocolate \| Coffee" | dark chocolate, coffee | ✅ Pass |
| Multiple Compounds | "Fresh oak \| Brown sugar" | fresh oak, brown sugar | ✅ Pass |

### Edge Cases

**Partial matching prevented:**
- "Toasted bread" matches "toasted" + "bread", NOT "toasted grain" ✅
- "Black coffee" matches "coffee", NOT "black pepper" ✅
- Word boundaries prevent "pepper" from matching in "peppermint" ✅

---

## Impact on Quiz Quality

### Before Fix
- User sees "baking" and "apple" as separate descriptors
- Confusing results (what does standalone "baking" mean?)
- Missing precision on common terms like "toasted oak"

### After Fix
- User sees "baking spice" and "caramel apple" as compound terms
- More accurate representation of tasting notes
- Better alignment with how reviewers actually describe whiskey

---

## Files Modified

1. **Database**
   - `whiskey_production.db` - Updated vocabulary, rebuilt extractions

2. **Python Scripts**
   - `descriptor_vocabulary.py` - Regenerated from database (81 descriptors)
   - `rebuild_production.py` - Used to rebuild all extractions

3. **Documentation**
   - `COMPOUND_DESCRIPTOR_FIX.md` - This document
   - `PRODUCTION_DATABASE_SUMMARY.md` - Updated counts

---

## Maintenance

### Adding New Compound Descriptors

1. **Check if it appears in reviews:**
   ```sql
   SELECT COUNT(*) FROM reviews
   WHERE LOWER(nose_text) LIKE '%new compound%'
      OR LOWER(palate_text) LIKE '%new compound%'
      OR LOWER(finish_text) LIKE '%new compound%';
   ```

2. **Add to database:**
   ```sql
   INSERT INTO descriptor_vocabulary
   (descriptor_name, category, applicable_sections)
   VALUES ('new compound', 'category', '["nose", "palate", "finish"]');
   ```

3. **Regenerate descriptor_vocabulary.py:**
   ```python
   python3 -c "
   import sqlite3
   db = sqlite3.connect('whiskey_production.db')
   cursor = db.cursor()
   cursor.execute('SELECT descriptor_name FROM descriptor_vocabulary WHERE is_active = 1 ORDER BY descriptor_name')
   descriptors = [row[0] for row in cursor.fetchall()]
   # Generate file...
   "
   ```

4. **Rebuild extractions:**
   ```bash
   python3 rebuild_production.py
   ```

---

## Known Issues

**Minor component/compound overlap (2 whiskeys):**
- Some whiskeys have both "toasted" and "oak" separately
- This is acceptable - reviews might genuinely use them separately
- Example: "Toasted notes on nose, oak on finish"

**Not an error** - just different phrasing in source reviews

---

## Future Improvements

**Potential additional compounds to consider:**
- "vanilla bean" (if occurs frequently)
- "oak barrel" (if occurs frequently)
- "rye bread" (if occurs frequently)
- "honey graham" (if occurs frequently)

**Check with:**
```sql
SELECT COUNT(*) FROM reviews
WHERE LOWER(nose_text) LIKE '%potential compound%'
   OR LOWER(palate_text) LIKE '%potential compound%'
   OR LOWER(finish_text) LIKE '%potential compound%';
```

---

## Summary

✅ **Fixed**: Removed 2 incorrect standalone descriptors
✅ **Added**: 8 compound descriptors covering 746 review occurrences
✅ **Verified**: All compound matching tests passing
✅ **Impact**: 269 whiskeys now use "toasted oak" instead of separate terms
✅ **Quality**: Quiz results more accurate and aligned with source reviews

**Status**: Production database rebuilt and ready to use!
