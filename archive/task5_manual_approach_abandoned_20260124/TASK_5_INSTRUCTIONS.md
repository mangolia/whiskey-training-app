# Task 5: Manual Descriptor Tagging - Instructions

**Estimated Time**: 6-8 hours (manual work, can be done in multiple sessions)
**Goal**: Tag all 60 reviews with descriptors to create the "correct answers" for quizzes

---

## Overview

You'll be reading each review and selecting 3-7 descriptors per section (nose/palate/finish) that match what the reviewer described. This creates the foundation for quiz generation.

---

## The Tagging Interface

### How to Start

```bash
cd /sessions/practical-fervent-hopper/mnt/whiskey-scraper
python3 tag_reviews.py
```

### What You'll See

For each review, the script will show:

1. **Whiskey name** (e.g., "Eagle Rare 10 Year")
2. **Section** (nose, palate, or finish)
3. **Review text** (the actual tasting notes)
4. **Available descriptors** organized by category

**Example**:
```
================================================================================
TAGGING: Eagle Rare 10 Year - NOSE
================================================================================

NOSE TEXT:
"Caramel, vanilla, oak and a hint of dried fruit. Sweet and inviting."

================================================================================
AVAILABLE DESCRIPTORS FOR NOSE
================================================================================

FRUITY:
  [ 14] fruit                 [ 15] raisin               [ 16] plum
  [ 17] apple                 [ 18] orange               [ 19] cherry
  [ 24] grape                 [ 25] lemon                [ 26] citrus
  [ 27] tropical

SPICY:
  [ 30] spice                 [ 31] cinnamon             [ 32] pepper
  [ 33] mint                  [ 36] nutmeg               [ 39] baking

SWEET:
  [  1] vanilla               [  2] caramel              [  3] honey
  [  4] brown sugar           [  5] sugar                [  6] chocolate
  [  7] molasses              [  8] cocoa                [ 12] sweet
  [ 13] cream

WOODY:
  [ 40] oak                   [ 41] char                 [ 42] charred
  [ 43] toasted               [ 44] barrel               [ 45] pine
  [ 46] cedar

================================================================================

Enter descriptor IDs for nose (comma-separated, or 's' to skip):
Example: 1, 39, 31, 48
>
```

### How to Tag

Based on the review text above, you'd enter:
```
> 2, 1, 40, 22
```

This means:
- 2 = caramel
- 1 = vanilla
- 40 = oak
- 22 = dried fruit (ID 22 from fruity category)

**The script will validate**:
- IDs exist
- Descriptors are applicable to that section
- Saves tags to database

---

## Tagging Guidelines

### How Many to Tag?

**Target**: 3-7 descriptors per section

**Too few** (1-2):
- Not enough variety for quiz
- User might get all correct by guessing

**Too many** (8+):
- Makes quiz too easy
- Every nuance becomes a "correct" answer

**Just right** (3-7):
- Captures the descriptors YOU detect in the review
- Leaves room for difficulty
- Remember: Sensory perception is subjective - what one reviewer detects is valid even if another doesn't mention it

### What to Tag?

✅ **Tag if**:
- Explicitly mentioned in review ("vanilla", "oak", "caramel")
- Implied but clear ("sweet corn" → tag "corn" and "sweet")
- Part of a compound ("baking spices" → tag "baking")

❌ **Don't tag if**:
- Not mentioned at all
- Only mentioned negatively ("lacks vanilla")
- Too much of a stretch

### Handling Ambiguity

**"Fruity notes"** → Tag "fruit" (generic is OK!)

**"Dark chocolate"** → Tag "chocolate" (we don't have "dark chocolate")

**"Toasted oak"** → Tag both "toasted" AND "oak"

**"Rye spice"** → Tag "rye" and "spice"

**"Charred barrel"** → Tag "char" and "barrel" (or "charred" and "barrel")

### Pro Tips

1. **Read the whole review first** before tagging any section
2. **Be consistent** across reviews (if you tag "sweet" for one, tag it similarly for others)
3. **When in doubt, include it** (more data is better than less)
4. **Don't overthink** (first instinct is usually right)
5. **Take breaks** (this is tedious work!)

---

## The Workflow

### Session 1: Tag 10-15 reviews (1-2 hours)

**Start**:
```bash
python3 tag_reviews.py
```

**Tag reviews**, one at a time

**Pause** when you need a break:
- Press Ctrl+C or enter 'n' when asked to continue
- Progress is saved automatically

### Session 2: Tag next 10-15 reviews (1-2 hours)

**Resume** where you left off:
```bash
python3 tag_reviews.py
```

Script picks up from where you stopped

### Continue until complete (6-8 hours total)

### Final Step: Run Aggregation

**After ALL 60 reviews are tagged**:
```bash
python3 aggregate_descriptors.py
```

This will:
1. Combine tags from all reviews
2. Create `aggregated_whiskey_descriptors` table
3. Show you stats and verification

---

## Example Tagging Session

**Review**: Eagle Rare 10 Year - Nose
**Text**: "Caramel, vanilla, oak and a hint of dried fruit. Sweet and inviting."

**My tags**: 2 (caramel), 1 (vanilla), 40 (oak), 22 (dried fruit), 12 (sweet)
**Count**: 5 descriptors ✅ Good!

**Review**: Eagle Rare 10 Year - Palate
**Text**: "Sweet corn, butterscotch, oak spice, hints of dark chocolate and cinnamon."

**My tags**: 49 (corn), 11 (butterscotch), 40 (oak), 30 (spice), 6 (chocolate), 31 (cinnamon)
**Count**: 6 descriptors ✅ Good!

**Review**: Eagle Rare 10 Year - Finish
**Text**: "Long and smooth, oak and vanilla linger with a touch of black pepper."

**My tags**: 40 (oak), 1 (vanilla), 32 (pepper), 69 (smooth)
**Count**: 4 descriptors ✅ Good!

**Total for this review**: 15 tags across 3 sections

---

## Troubleshooting

### "Descriptor ID X not found"
- You entered an invalid number
- Check the displayed list for valid IDs

### "Not applicable to this section"
- You tried to tag a descriptor that doesn't apply
- Example: "heat" only applies to finish, not nose
- The script will skip it automatically

### "No descriptors entered"
- You hit Enter without typing anything
- Review will be incomplete
- You can re-run the script and it will show this review again

### Script crashes
- Your progress is saved!
- Just run `python3 tag_reviews.py` again
- It will resume from the next untagged review

---

## Progress Tracking

The script shows:
```
Progress: 15/60 reviews tagged (127 total tags)
```

**To check progress manually**:
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('whiskey_mvp.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(DISTINCT review_id) FROM review_descriptors')
print(f'Tagged: {cursor.fetchone()[0]}/60 reviews')
"
```

---

## After Tagging is Complete

### Step 1: Run Aggregation

```bash
python3 aggregate_descriptors.py
```

**Expected output**:
- "Created X aggregated descriptor entries"
- Stats showing descriptor distribution
- Quality check for whiskeys with too few descriptors

### Step 2: Verify Data

Check that whiskeys have enough descriptors:
- Each whiskey should have 3-5+ descriptors per section
- If some have <3, you may need to tag more

### Step 3: Test Quiz Generation (Optional)

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('whiskey_mvp.db')
cursor = conn.cursor()

# Get correct descriptors for whiskey #1, nose section
cursor.execute('''
    SELECT dv.descriptor_name, awd.review_count
    FROM aggregated_whiskey_descriptors awd
    JOIN descriptor_vocabulary dv ON awd.descriptor_id = dv.descriptor_id
    WHERE awd.whiskey_id = 1 AND awd.tasting_section = \"nose\"
    ORDER BY awd.review_count DESC
''')

print('Correct answers for Whiskey #1 - Nose:')
for name, count in cursor.fetchall():
    print(f'  {name} ({count}/2 reviews)')
"
```

---

## Time Estimates

**Per review**: ~5 minutes
- 1 min: Read all three sections
- 1 min: Tag nose
- 1 min: Tag palate
- 1 min: Tag finish
- 1 min: Buffer (thinking, corrections)

**Total time**:
- 60 reviews × 5 minutes = **5 hours**
- Add breaks and thinking time = **6-8 hours**

**Recommended approach**:
- Session 1: 15 reviews (1.5 hours)
- Session 2: 15 reviews (1.5 hours)
- Session 3: 15 reviews (1.5 hours)
- Session 4: 15 reviews (1.5 hours)

---

## What Happens Next (Task 6)

After Task 5 is complete, the database will be ready for backend API development:

**You'll have**:
- `review_descriptors`: ~1,000 individual tags
- `aggregated_whiskey_descriptors`: ~400 aggregated entries
- Quiz data ready for API to consume

**Task 6 will**:
- Build Flask API
- Create `/api/quiz/:id` endpoint
- Use aggregated data to generate quizzes

---

## Questions?

**Before starting**:
- Review the example tagging session above
- Try tagging 1-2 reviews to get comfortable
- Ask if anything is unclear

**During tagging**:
- Be consistent but don't stress perfection
- When unsure, go with your instinct
- Take breaks when needed

**Good luck! This is the most tedious task but also the most important for data quality.**
