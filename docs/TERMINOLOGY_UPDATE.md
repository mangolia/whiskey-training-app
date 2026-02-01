# Terminology Update: "Flavor" → "Descriptor"

## Date: January 2026
## Status: Completed

---

## Overview

The project has been updated to use consistent terminology throughout all documentation and database schemas. The term **"descriptor"** is now used instead of **"flavor"** when referring to sensory characteristics in the database and technical documentation.

## Rationale

- **Clarity**: "Descriptor" more accurately represents the technical concept of sensory attributes stored in the database
- **Consistency**: Aligns with industry terminology for sensory analysis
- **Distinction**: Separates the technical/database concept from the sensory experience concept (flavors and aromas)

## Terminology Guidelines

### ✅ Use "Descriptor"
- Database table names
- Column names
- API endpoints
- Technical documentation
- Variable names in code

### ✅ Use "Flavor" or "Aroma"
- User-facing text describing the sensory experience
- Marketing copy
- General descriptions of whiskey tasting
- When discussing the actual taste or smell of whiskey

### Examples

**Good - Technical Context:**
- "The `descriptor_vocabulary` table stores all sensory descriptors"
- "Query the `aggregated_whiskey_descriptors` for quiz generation"
- "Each descriptor has a category (fruity, spicy, woody)"

**Good - User-Facing Context:**
- "Identify flavors in whiskey's nose, palate, and finish"
- "Test your ability to detect aromas and flavors"
- "Compare your tasting notes against professional reviews"

---

## Database Schema Changes

### Table Names

| Old Name | New Name | Status |
|----------|----------|--------|
| `flavor_vocabulary` | `descriptor_vocabulary` | ✅ Updated |
| `review_flavors` | `review_descriptors` | ✅ Updated |
| `aggregated_whiskey_flavors` | `aggregated_whiskey_descriptors` | ✅ Updated |

### Column Names

| Old Name | New Name | Table | Status |
|----------|----------|-------|--------|
| `flavor_id` | `descriptor_id` | descriptor_vocabulary | ✅ Updated |
| `flavor_name` | `descriptor_name` | descriptor_vocabulary | ✅ Updated |
| `flavor_id` (FK) | `descriptor_id` (FK) | review_descriptors | ✅ Updated |
| `review_flavor_id` | `review_descriptor_id` | review_descriptors | ✅ Updated |
| `aggregated_flavor_id` | `aggregated_descriptor_id` | aggregated_whiskey_descriptors | ✅ Updated |
| `flavor_id` (FK) | `descriptor_id` (FK) | aggregated_whiskey_descriptors | ✅ Updated |

### Index Names

| Old Name | New Name | Status |
|----------|----------|--------|
| `idx_flavor_vocabulary_name` | `idx_descriptor_vocabulary_name` | ✅ Updated |
| `idx_flavor_vocabulary_category` | `idx_descriptor_vocabulary_category` | ✅ Updated |
| `idx_review_flavors_review_id` | `idx_review_descriptors_review_id` | ✅ Updated |
| `idx_review_flavors_flavor_id` | `idx_review_descriptors_descriptor_id` | ✅ Updated |
| `idx_review_flavors_section` | `idx_review_descriptors_section` | ✅ Updated |
| `idx_aggregated_whiskey_id` | `idx_aggregated_whiskey_id` | No change |
| `idx_aggregated_flavor_id` | `idx_aggregated_descriptor_id` | ✅ Updated |
| `idx_aggregated_section` | `idx_aggregated_section` | No change |

---

## Files Updated

### Core Documentation
- ✅ `/docs/DATABASE_SCHEMA.md` - All table definitions, queries, and examples
- ✅ `/docs/PRD.md` - User stories, database implications, and workflows
- ✅ `/migrations/001_add_quiz_tables.sql` - Migration script

### Files NOT Updated (Intentionally)
These files contain historical data or are archived scripts that reference the old terminology. They have been left as-is for historical accuracy:

- `FLAVOR_CATEGORIZATION_REVIEW.md` - Historical documentation
- `WHISKEY_CATEGORIZATION_MASTER_GUIDE.md` - Reference guide
- `Whiskey_Sensory_Framework.md` - Framework document
- `data/categorized_flavors_*.json` - Data files (will be migrated separately)
- `scripts/categorize_flavors.py` - Script (will be updated when needed)
- `scripts/review_flavors.py` - Script (will be updated when needed)
- HTML review files - Frontend templates (will be updated with new frontend)

---

## Migration Strategy

### Phase 1: Documentation (✅ Completed)
- Updated PRD.md
- Updated DATABASE_SCHEMA.md
- Updated migration SQL file
- Created this terminology guide

### Phase 2: Database Migration (Pending)
- Create new migration script to rename existing tables
- Test migration on development database
- Apply to production when ready

### Phase 3: Code Updates (Pending)
- Update `database.py` with new table/column names
- Update Python scripts in `scripts/` folder
- Update any API endpoints
- Update frontend code

### Phase 4: Data Migration (Pending)
- Migrate existing data files
- Update JSON data structures
- Test data integrity

---

## SQL Migration Template

When ready to migrate the actual database, use this template:

```sql
-- Migration: Rename flavor tables to descriptor tables
-- This will be a new migration file (e.g., 002_rename_flavor_to_descriptor.sql)

PRAGMA foreign_keys = OFF;

-- Rename flavor_vocabulary to descriptor_vocabulary
ALTER TABLE flavor_vocabulary RENAME TO descriptor_vocabulary;
ALTER TABLE descriptor_vocabulary RENAME COLUMN flavor_id TO descriptor_id;
ALTER TABLE descriptor_vocabulary RENAME COLUMN flavor_name TO descriptor_name;

-- Rename review_flavors to review_descriptors
ALTER TABLE review_flavors RENAME TO review_descriptors;
ALTER TABLE review_descriptors RENAME COLUMN review_flavor_id TO review_descriptor_id;
ALTER TABLE review_descriptors RENAME COLUMN flavor_id TO descriptor_id;

-- Rename aggregated_whiskey_flavors to aggregated_whiskey_descriptors
ALTER TABLE aggregated_whiskey_flavors RENAME TO aggregated_whiskey_descriptors;
ALTER TABLE aggregated_whiskey_descriptors RENAME COLUMN aggregated_flavor_id TO aggregated_descriptor_id;
ALTER TABLE aggregated_whiskey_descriptors RENAME COLUMN flavor_id TO descriptor_id;

-- Drop old indexes
DROP INDEX IF EXISTS idx_flavor_vocabulary_name;
DROP INDEX IF EXISTS idx_flavor_vocabulary_category;
DROP INDEX IF EXISTS idx_review_flavors_review_id;
DROP INDEX IF EXISTS idx_review_flavors_flavor_id;
DROP INDEX IF EXISTS idx_review_flavors_section;
DROP INDEX IF EXISTS idx_aggregated_flavor_id;

-- Create new indexes
CREATE INDEX idx_descriptor_vocabulary_name ON descriptor_vocabulary(descriptor_name);
CREATE INDEX idx_descriptor_vocabulary_category ON descriptor_vocabulary(category);
CREATE INDEX idx_review_descriptors_review_id ON review_descriptors(review_id);
CREATE INDEX idx_review_descriptors_descriptor_id ON review_descriptors(descriptor_id);
CREATE INDEX idx_review_descriptors_section ON review_descriptors(tasting_section);
CREATE INDEX idx_aggregated_descriptor_id ON aggregated_whiskey_descriptors(descriptor_id);

PRAGMA foreign_keys = ON;
```

---

## Verification Checklist

After applying changes to any system:

- [ ] All table names use "descriptor" terminology
- [ ] All column names use "descriptor" terminology
- [ ] All indexes are properly named
- [ ] Foreign key relationships are intact
- [ ] Queries execute without errors
- [ ] Data integrity is maintained
- [ ] Documentation is consistent
- [ ] Code comments are updated

---

## Questions & Answers

**Q: Why not update the data files and scripts immediately?**
A: We're updating documentation first to establish the standard. Code and data will be updated as part of the actual implementation/migration phase.

**Q: Do we need to update the existing database?**
A: Only when you're ready to use the new structure. The documentation now reflects the correct schema, and you can create a fresh database using the updated migration scripts.

**Q: What about existing reviews and data?**
A: Historical data files are left unchanged for reference. When loading into a new database, use the updated schema and table names.

**Q: Should we rename the Python files like `categorize_flavors.py`?**
A: Not necessary immediately. The file names can reference "flavors" as they represent the user-facing concept. Internal variable names and database queries should be updated to use "descriptor" terminology.

---

## Summary

The terminology update provides clarity and consistency throughout the project. "Descriptor" is now the standard term for database and technical contexts, while "flavor" and "aroma" remain appropriate for user-facing content describing the sensory experience.

All core documentation has been updated. Database migration and code updates will occur in subsequent phases as the MVP is built.
