-- MVP Database V2 Complete Schema
-- Purpose: Fresh database with all tables needed for quiz platform

PRAGMA foreign_keys = ON;

-- ============================================================================
-- Whiskeys Table
-- ============================================================================

CREATE TABLE whiskeys (
    whiskey_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    distillery TEXT,
    brand_family TEXT,
    variant_name TEXT,
    classification TEXT,
    company TEXT,
    proof TEXT,
    age TEXT,
    mashbill TEXT,
    price TEXT,
    image_url TEXT,
    attributes TEXT,  -- JSON field
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_whiskeys_name ON whiskeys(name);
CREATE INDEX idx_whiskeys_distillery ON whiskeys(distillery);
CREATE INDEX idx_whiskeys_brand_family ON whiskeys(brand_family);
CREATE INDEX idx_whiskeys_classification ON whiskeys(classification);

-- ============================================================================
-- Reviews Table
-- ============================================================================

CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    whiskey_id INTEGER NOT NULL,
    source_site TEXT,
    source_url TEXT,
    normalized_url TEXT,
    review_date TEXT,
    date_scraped TEXT NOT NULL DEFAULT (datetime('now')),
    classification TEXT,
    company TEXT,
    proof TEXT,
    age TEXT,
    mashbill TEXT,
    color TEXT,
    price TEXT,
    nose TEXT,  -- Review text for nose
    palate TEXT,  -- Review text for palate
    finish TEXT,  -- Review text for finish
    rating TEXT,
    overall_notes TEXT,
    additional_data TEXT,
    nose_text TEXT,  -- Duplicate columns for future migration compatibility
    palate_text TEXT,
    finish_text TEXT,

    FOREIGN KEY (whiskey_id) REFERENCES whiskeys(whiskey_id) ON DELETE CASCADE
);

CREATE INDEX idx_reviews_whiskey_id ON reviews(whiskey_id);
CREATE INDEX idx_reviews_source ON reviews(source_site);

-- ============================================================================
-- Descriptor Vocabulary Table
-- ============================================================================

CREATE TABLE descriptor_vocabulary (
    descriptor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    descriptor_name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,  -- fruity, spicy, woody, floral, grain, sweet, bitter, savory, smoky, mouthfeel, nutty
    applicable_sections TEXT NOT NULL,  -- JSON: ["nose", "palate", "finish"]
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    is_active INTEGER DEFAULT 1
);

CREATE INDEX idx_descriptor_vocabulary_name ON descriptor_vocabulary(descriptor_name);
CREATE INDEX idx_descriptor_vocabulary_category ON descriptor_vocabulary(category);

-- ============================================================================
-- Review Descriptors Table (Many-to-Many)
-- ============================================================================

CREATE TABLE review_descriptors (
    review_descriptor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    descriptor_id INTEGER NOT NULL,
    tasting_section TEXT NOT NULL,  -- 'nose', 'palate', or 'finish'
    tagged_at TEXT NOT NULL DEFAULT (datetime('now')),
    tagged_by TEXT DEFAULT 'automated',

    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE,
    FOREIGN KEY (descriptor_id) REFERENCES descriptor_vocabulary(descriptor_id) ON DELETE CASCADE,
    UNIQUE(review_id, descriptor_id, tasting_section)
);

CREATE INDEX idx_review_descriptors_review_id ON review_descriptors(review_id);
CREATE INDEX idx_review_descriptors_descriptor_id ON review_descriptors(descriptor_id);
CREATE INDEX idx_review_descriptors_section ON review_descriptors(tasting_section);

-- ============================================================================
-- Aggregated Whiskey Descriptors Table (Quiz-Ready Data)
-- ============================================================================

CREATE TABLE aggregated_whiskey_descriptors (
    aggregated_descriptor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    whiskey_id INTEGER NOT NULL,
    descriptor_id INTEGER NOT NULL,
    tasting_section TEXT NOT NULL,
    source_review_ids TEXT NOT NULL,  -- JSON array: [123, 456]
    review_count INTEGER NOT NULL,
    last_updated TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (whiskey_id) REFERENCES whiskeys(whiskey_id) ON DELETE CASCADE,
    FOREIGN KEY (descriptor_id) REFERENCES descriptor_vocabulary(descriptor_id) ON DELETE CASCADE,
    UNIQUE(whiskey_id, descriptor_id, tasting_section)
);

CREATE INDEX idx_aggregated_whiskey_id ON aggregated_whiskey_descriptors(whiskey_id);
CREATE INDEX idx_aggregated_descriptor_id ON aggregated_whiskey_descriptors(descriptor_id);
CREATE INDEX idx_aggregated_section ON aggregated_whiskey_descriptors(tasting_section);

-- ============================================================================
-- Migrations Table
-- ============================================================================

CREATE TABLE migrations (
    migration_id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_name TEXT UNIQUE NOT NULL,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    description TEXT
);

INSERT INTO migrations (migration_name, description)
VALUES ('000_initial_schema', 'Initial MVP v2 schema with all quiz tables');
