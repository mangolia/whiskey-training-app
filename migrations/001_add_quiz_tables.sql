-- Migration 001: Add Quiz Platform Tables
-- Date: 2025-01-15
-- Purpose: Add descriptor_vocabulary, review_descriptors, and aggregated_whiskey_descriptors tables
--          Add brand_family, variant_name, attributes to whiskeys table
--          Rename nose/palate/finish to nose_text/palate_text/finish_text for consistency

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================================================
-- PART 1: Extend whiskeys table
-- ============================================================================

-- Add new columns to whiskeys table
ALTER TABLE whiskeys ADD COLUMN brand_family TEXT;
ALTER TABLE whiskeys ADD COLUMN variant_name TEXT;
ALTER TABLE whiskeys ADD COLUMN attributes TEXT; -- JSON field
ALTER TABLE whiskeys ADD COLUMN classification TEXT;
ALTER TABLE whiskeys ADD COLUMN proof TEXT;
ALTER TABLE whiskeys ADD COLUMN age TEXT;
ALTER TABLE whiskeys ADD COLUMN mashbill TEXT;
ALTER TABLE whiskeys ADD COLUMN price TEXT;
ALTER TABLE whiskeys ADD COLUMN image_url TEXT;

-- Add indexes for new fields
CREATE INDEX idx_whiskeys_brand_family ON whiskeys(brand_family);
CREATE INDEX idx_whiskeys_classification ON whiskeys(classification);

-- ============================================================================
-- PART 2: Rename reviews columns for consistency
-- ============================================================================

-- SQLite doesn't support RENAME COLUMN directly in older versions
-- So we'll create new columns and copy data

ALTER TABLE reviews ADD COLUMN nose_text TEXT;
ALTER TABLE reviews ADD COLUMN palate_text TEXT;
ALTER TABLE reviews ADD COLUMN finish_text TEXT;

-- Copy data from old columns to new columns
UPDATE reviews SET nose_text = nose WHERE nose IS NOT NULL;
UPDATE reviews SET palate_text = palate WHERE palate IS NOT NULL;
UPDATE reviews SET finish_text = finish WHERE finish IS NOT NULL;

-- Note: We'll keep the old columns for now to ensure data safety
-- You can drop them later after verifying the migration worked:
-- ALTER TABLE reviews DROP COLUMN nose;
-- ALTER TABLE reviews DROP COLUMN palate;
-- ALTER TABLE reviews DROP COLUMN finish;

-- ============================================================================
-- PART 3: Create descriptor_vocabulary table
-- ============================================================================

CREATE TABLE descriptor_vocabulary (
    descriptor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    descriptor_name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,  -- fruity, spicy, woody, floral, grain, sweet, bitter, savory, smoky
    applicable_sections TEXT NOT NULL,  -- JSON: ["nose", "palate", "finish"]
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    is_active INTEGER DEFAULT 1  -- Boolean: allow deprecating descriptors
);

-- Indexes for descriptor_vocabulary
CREATE INDEX idx_descriptor_vocabulary_name ON descriptor_vocabulary(descriptor_name);
CREATE INDEX idx_descriptor_vocabulary_category ON descriptor_vocabulary(category);

-- ============================================================================
-- PART 4: Create review_descriptors table (many-to-many relationship)
-- ============================================================================

CREATE TABLE review_descriptors (
    review_descriptor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    descriptor_id INTEGER NOT NULL,
    tasting_section TEXT NOT NULL,  -- 'nose', 'palate', or 'finish'
    tagged_at TEXT NOT NULL DEFAULT (datetime('now')),
    tagged_by TEXT DEFAULT 'automated',  -- 'manual', 'automated', or admin_user_id (future)

    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE,
    FOREIGN KEY (descriptor_id) REFERENCES descriptor_vocabulary(descriptor_id) ON DELETE CASCADE,
    UNIQUE(review_id, descriptor_id, tasting_section)  -- Prevent duplicate tags
);

-- Indexes for review_descriptors
CREATE INDEX idx_review_descriptors_review_id ON review_descriptors(review_id);
CREATE INDEX idx_review_descriptors_descriptor_id ON review_descriptors(descriptor_id);
CREATE INDEX idx_review_descriptors_section ON review_descriptors(tasting_section);

-- ============================================================================
-- PART 5: Create aggregated_whiskey_descriptors table
-- ============================================================================

CREATE TABLE aggregated_whiskey_descriptors (
    aggregated_descriptor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    whiskey_id INTEGER NOT NULL,
    descriptor_id INTEGER NOT NULL,
    tasting_section TEXT NOT NULL,  -- 'nose', 'palate', or 'finish'
    source_review_ids TEXT NOT NULL,  -- JSON array: [123, 456, 789]
    review_count INTEGER NOT NULL,  -- How many reviews mentioned this descriptor
    last_updated TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (whiskey_id) REFERENCES whiskeys(whiskey_id) ON DELETE CASCADE,
    FOREIGN KEY (descriptor_id) REFERENCES descriptor_vocabulary(descriptor_id) ON DELETE CASCADE,
    UNIQUE(whiskey_id, descriptor_id, tasting_section)
);

-- Indexes for aggregated_whiskey_descriptors
CREATE INDEX idx_aggregated_whiskey_id ON aggregated_whiskey_descriptors(whiskey_id);
CREATE INDEX idx_aggregated_descriptor_id ON aggregated_whiskey_descriptors(descriptor_id);
CREATE INDEX idx_aggregated_section ON aggregated_whiskey_descriptors(tasting_section);

-- ============================================================================
-- PART 6: Create migration tracking table (for future migrations)
-- ============================================================================

CREATE TABLE IF NOT EXISTS migrations (
    migration_id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_name TEXT UNIQUE NOT NULL,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    description TEXT
);

-- Record this migration
INSERT INTO migrations (migration_name, description)
VALUES ('001_add_quiz_tables', 'Add descriptor_vocabulary, review_descriptors, aggregated_whiskey_descriptors tables and extend whiskeys/reviews tables');

-- ============================================================================
-- Verification Queries (run these after migration to verify)
-- ============================================================================

-- Check new tables exist:
-- SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

-- Check new columns in whiskeys:
-- PRAGMA table_info(whiskeys);

-- Check new columns in reviews:
-- PRAGMA table_info(reviews);

-- Check data was copied:
-- SELECT COUNT(*) FROM reviews WHERE nose_text IS NOT NULL;
-- SELECT COUNT(*) FROM reviews WHERE palate_text IS NOT NULL;
-- SELECT COUNT(*) FROM reviews WHERE finish_text IS NOT NULL;
