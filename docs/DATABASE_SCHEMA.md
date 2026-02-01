# **Whiskey Quiz Platform - Database Schema**

## **Schema Overview**

This database supports a whiskey tasting quiz platform that aggregates reviews from multiple sources and generates interactive quizzes for users to test their palate.

**Database Platform:** SQLite (MVP) → PostgreSQL (Production)  
**Design Philosophy:** Moderate normalization with JSON for flexibility  
**Key Feature:** Computed aggregation of tasting notes from multiple reviews

---

## **Table Definitions**

### **1. `whiskeys` - Master Whiskey Index**

Stores unique whiskeys and their variants as separate entities.
```sql
CREATE TABLE whiskeys (
    whiskey_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    distillery TEXT,
    brand_family TEXT,
    variant_name TEXT,
    classification TEXT,  -- bourbon, rye, scotch, single malt, etc.
    proof TEXT,
    age TEXT,
    mashbill TEXT,
    price TEXT,
    attributes TEXT,  -- JSON: {batch, release_year, edition_name, release_type}
    image_url TEXT,
    first_seen_date TEXT,  -- ISO 8601 format (YYYY-MM-DD HH:MM:SS)
    needs_review INTEGER DEFAULT 0  -- Boolean flag for manual duplicate review
);

-- Indexes for search performance
CREATE INDEX idx_whiskeys_name ON whiskeys(name);
CREATE INDEX idx_whiskeys_distillery ON whiskeys(distillery);
CREATE INDEX idx_whiskeys_brand_family ON whiskeys(brand_family);
CREATE INDEX idx_whiskeys_classification ON whiskeys(classification);
```

**Key Points:**
- Each whiskey variant (different batch, edition, release) gets its own record
- `attributes` JSON field stores flexible variant metadata
- `brand_family` enables grouping related products (e.g., all Blanton's variants)

**Standard JSON Attribute Keys:**
```json
{
  "batch": "Batch 2024-A",
  "release_year": "2024",
  "edition_name": "Limited Edition",
  "release_type": "store_pick",
  "barrel_type": "single_barrel",
  "cask_finish": "sherry"
}
```

---

### **2. `reviews` - All Review Data**

Stores all reviews from all sources with both raw and structured data.
```sql
CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    whiskey_id INTEGER NOT NULL,
    source_site TEXT NOT NULL,
    source_url TEXT NOT NULL,
    normalized_url TEXT NOT NULL,
    review_date TEXT,  -- ISO 8601 format
    date_scraped TEXT NOT NULL,  -- ISO 8601 format
    
    -- Structured review fields
    classification TEXT,
    company TEXT,
    proof TEXT,
    age TEXT,
    mashbill TEXT,
    color TEXT,
    price TEXT,
    
    -- Raw tasting notes (free text)
    nose_text TEXT,
    palate_text TEXT,
    finish_text TEXT,
    
    rating TEXT,
    overall_notes TEXT,
    
    -- Flexible unstructured metadata
    additional_data TEXT,  -- JSON for site-specific fields
    
    FOREIGN KEY (whiskey_id) REFERENCES whiskeys(whiskey_id),
    UNIQUE(source_site, normalized_url)  -- Prevent duplicate reviews
);

-- Indexes
CREATE INDEX idx_reviews_whiskey_id ON reviews(whiskey_id);
CREATE INDEX idx_reviews_source_site ON reviews(source_site);
CREATE INDEX idx_reviews_normalized_url ON reviews(normalized_url);
```

**Key Points:**
- Raw tasting notes preserved in `nose_text`, `palate_text`, `finish_text`
- Structured flavor extraction happens separately via `review_flavors` table
- `UNIQUE` constraint prevents exact duplicate reviews from same source

---

### **3. `descriptor_vocabulary` - Master Descriptor List**

Comprehensive list of all possible sensory descriptors.
```sql
CREATE TABLE descriptor_vocabulary (
    descriptor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    descriptor_name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,  -- fruity, spicy, woody, floral, grain, sweet, etc.
    applicable_sections TEXT NOT NULL,  -- JSON: ["nose", "palate", "finish"]
    created_at TEXT NOT NULL,  -- ISO 8601 format
    is_active INTEGER DEFAULT 1  -- Boolean: allow deprecating descriptors
);

-- Indexes
CREATE INDEX idx_descriptor_vocabulary_name ON descriptor_vocabulary(descriptor_name);
CREATE INDEX idx_descriptor_vocabulary_category ON descriptor_vocabulary(category);
```

**Descriptor Categories:**
- `fruity` - citrus, apple, cherry, berry, stone fruit
- `spicy` - cinnamon, pepper, clove, nutmeg
- `woody` - oak, cedar, pine, charred wood
- `floral` - rose, lavender, perfume, honey
- `grain` - corn, wheat, rye, malt
- `sweet` - vanilla, caramel, butterscotch, chocolate, brown sugar
- `bitter` - coffee, dark chocolate, tobacco
- `savory` - leather, tobacco, earthy
- `smoky` - peat, campfire, charcoal

**Example Records:**
```sql
INSERT INTO descriptor_vocabulary (descriptor_name, category, applicable_sections, created_at) VALUES
('caramel', 'sweet', '["nose", "palate", "finish"]', datetime('now')),
('oak', 'woody', '["nose", "palate", "finish"]', datetime('now')),
('cherry', 'fruity', '["nose", "palate"]', datetime('now')),
('cinnamon', 'spicy', '["nose", "palate", "finish"]', datetime('now'));
```

---

### **4. `review_descriptors` - Descriptor Tags per Review**

Links specific descriptors to reviews (many-to-many relationship).
```sql
CREATE TABLE review_descriptors (
    review_descriptor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    descriptor_id INTEGER NOT NULL,
    tasting_section TEXT NOT NULL,  -- 'nose', 'palate', or 'finish'
    tagged_at TEXT NOT NULL,  -- ISO 8601 format
    tagged_by TEXT,  -- 'manual', 'scraper', or admin_user_id (future)

    FOREIGN KEY (review_id) REFERENCES reviews(review_id),
    FOREIGN KEY (descriptor_id) REFERENCES descriptor_vocabulary(descriptor_id),
    UNIQUE(review_id, descriptor_id, tasting_section)  -- Prevent duplicate tags
);

-- Indexes
CREATE INDEX idx_review_descriptors_review_id ON review_descriptors(review_id);
CREATE INDEX idx_review_descriptors_descriptor_id ON review_descriptors(descriptor_id);
CREATE INDEX idx_review_descriptors_section ON review_descriptors(tasting_section);
```

**Key Points:**
- Each row represents one descriptor detected in one section of one review
- `tagged_by` tracks whether descriptor was auto-extracted or manually tagged
- For MVP, all tagging is `'manual'` via admin interface

---

### **5. `aggregated_whiskey_descriptors` - Computed Aggregations**

Combines descriptors from all reviews for a whiskey (for quiz generation).
```sql
CREATE TABLE aggregated_whiskey_descriptors (
    aggregated_descriptor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    whiskey_id INTEGER NOT NULL,
    descriptor_id INTEGER NOT NULL,
    tasting_section TEXT NOT NULL,  -- 'nose', 'palate', or 'finish'
    source_review_ids TEXT NOT NULL,  -- JSON array: [123, 456, 789]
    review_count INTEGER NOT NULL,  -- How many reviews mentioned this descriptor
    last_updated TEXT NOT NULL,  -- ISO 8601 format

    FOREIGN KEY (whiskey_id) REFERENCES whiskeys(whiskey_id),
    FOREIGN KEY (descriptor_id) REFERENCES descriptor_vocabulary(descriptor_id),
    UNIQUE(whiskey_id, descriptor_id, tasting_section)
);

-- Indexes
CREATE INDEX idx_aggregated_whiskey_id ON aggregated_whiskey_descriptors(whiskey_id);
CREATE INDEX idx_aggregated_section ON aggregated_whiskey_descriptors(tasting_section);
```

**Key Points:**
- This is a **computed/derived table** - refreshed when reviews are added/updated
- Stores which reviews contributed each descriptor (for debugging/quality control)
- Used directly for quiz generation (fetch all correct descriptors for a whiskey)

---

### **6. `scraper_runs` - Monitoring & Logging**

Tracks scraper execution history.
```sql
CREATE TABLE scraper_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_site TEXT NOT NULL,
    run_date TEXT NOT NULL,  -- ISO 8601 format
    status TEXT NOT NULL,  -- 'success' or 'failure'
    reviews_found INTEGER,
    reviews_added INTEGER,
    error_message TEXT,
    execution_time REAL  -- seconds
);

-- Index
CREATE INDEX idx_scraper_runs_source_site ON scraper_runs(source_site);
CREATE INDEX idx_scraper_runs_date ON scraper_runs(run_date);
```

---

## **Future Tables (Design Now, Implement Later)**

### **7. `brand_families` - Brand/Distillery Hierarchy**
```sql
CREATE TABLE brand_families (
    brand_family_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    parent_company TEXT,
    distillery TEXT,
    region TEXT,  -- Kentucky, Scotland, Tennessee, etc.
    description TEXT
);
```

**Migration Path:**
- Phase 1 (MVP): Use `whiskeys.brand_family` as TEXT field
- Phase 2: Migrate to foreign key relationship with this table

---

### **8. `users` - User Accounts**
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,  -- ISO 8601 format
    preferences TEXT  -- JSON: UI preferences, quiz settings
);
```

---

### **9. `quiz_attempts` - User Quiz History**
```sql
CREATE TABLE quiz_attempts (
    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    whiskey_id INTEGER NOT NULL,
    attempted_at TEXT NOT NULL,  -- ISO 8601 format
    
    -- Accuracy metrics per section
    nose_correct INTEGER,
    nose_total INTEGER,
    palate_correct INTEGER,
    palate_total INTEGER,
    finish_correct INTEGER,
    finish_total INTEGER,
    
    selections TEXT,  -- JSON: full record of user selections and correctness
    duration_seconds INTEGER,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (whiskey_id) REFERENCES whiskeys(whiskey_id)
);
```

---

### **10. `user_tasting_notes` - User-Generated Content**
```sql
CREATE TABLE user_tasting_notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    whiskey_id INTEGER NOT NULL,
    nose_text TEXT,
    palate_text TEXT,
    finish_text TEXT,
    rating INTEGER,
    created_at TEXT NOT NULL,  -- ISO 8601 format
    is_public INTEGER DEFAULT 0,  -- Boolean
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (whiskey_id) REFERENCES whiskeys(whiskey_id)
);
```

---

## **Key Queries & Operations**

### **Query 1: Search Whiskeys by Name**
```sql
-- Simple search
SELECT whiskey_id, name, distillery, proof, classification
FROM whiskeys
WHERE LOWER(name) LIKE LOWER('%blanton%')
ORDER BY name;

-- Full-text search with ranking (SQLite FTS5)
-- Create FTS5 virtual table first:
CREATE VIRTUAL TABLE whiskeys_fts USING fts5(
    whiskey_id, name, distillery, brand_family,
    content=whiskeys
);

-- Then search with ranking:
SELECT w.whiskey_id, w.name, w.distillery, w.proof
FROM whiskeys_fts fts
JOIN whiskeys w ON fts.whiskey_id = w.whiskey_id
WHERE whiskeys_fts MATCH 'blanton OR single'
ORDER BY rank;
```

---

### **Query 2: Get Whiskey Details with Review Count**
```sql
SELECT
    w.*,
    COUNT(DISTINCT r.review_id) as review_count,
    COUNT(DISTINCT awd.descriptor_id) as total_descriptors
FROM whiskeys w
LEFT JOIN reviews r ON w.whiskey_id = r.whiskey_id
LEFT JOIN aggregated_whiskey_descriptors awd ON w.whiskey_id = awd.whiskey_id
WHERE w.whiskey_id = ?
GROUP BY w.whiskey_id;
```

---

### **Query 3: Generate Quiz Options (Correct + Incorrect Descriptors)**
```sql
-- Step 1: Get correct descriptors for whiskey + section
SELECT dv.descriptor_id, dv.descriptor_name
FROM aggregated_whiskey_descriptors awd
JOIN descriptor_vocabulary dv ON awd.descriptor_id = dv.descriptor_id
WHERE awd.whiskey_id = ? AND awd.tasting_section = ?;

-- Step 2: Get random incorrect descriptors
-- (Exclude correct descriptors, match category for plausibility)
SELECT dv.descriptor_id, dv.descriptor_name
FROM descriptor_vocabulary dv
WHERE dv.category IN (
    -- Get categories of correct descriptors
    SELECT DISTINCT dv2.category
    FROM aggregated_whiskey_descriptors awd2
    JOIN descriptor_vocabulary dv2 ON awd2.descriptor_id = dv2.descriptor_id
    WHERE awd2.whiskey_id = ? AND awd2.tasting_section = ?
)
AND dv.applicable_sections LIKE '%' || ? || '%'  -- Check section is applicable
AND dv.descriptor_id NOT IN (
    -- Exclude correct descriptors
    SELECT descriptor_id FROM aggregated_whiskey_descriptors
    WHERE whiskey_id = ? AND tasting_section = ?
)
AND dv.is_active = 1
ORDER BY RANDOM()
LIMIT ?;  -- (9 - number_of_correct_descriptors)
```

---

### **Query 4: Refresh Aggregated Descriptors for a Whiskey**
```sql
-- Delete existing aggregations for this whiskey
DELETE FROM aggregated_whiskey_descriptors WHERE whiskey_id = ?;

-- Insert fresh aggregations
INSERT INTO aggregated_whiskey_descriptors
    (whiskey_id, descriptor_id, tasting_section, source_review_ids, review_count, last_updated)
SELECT
    ? as whiskey_id,
    rd.descriptor_id,
    rd.tasting_section,
    json_group_array(DISTINCT rd.review_id) as source_review_ids,
    COUNT(DISTINCT rd.review_id) as review_count,
    datetime('now') as last_updated
FROM reviews r
JOIN review_descriptors rd ON r.review_id = rd.review_id
WHERE r.whiskey_id = ?
GROUP BY rd.descriptor_id, rd.tasting_section;
```

---

### **Query 5: Find Untagged Reviews (Need Manual Descriptor Tagging)**
```sql
SELECT
    r.review_id,
    r.source_site,
    r.source_url,
    w.name as whiskey_name,
    r.nose_text,
    r.palate_text,
    r.finish_text
FROM reviews r
JOIN whiskeys w ON r.whiskey_id = w.whiskey_id
WHERE r.review_id NOT IN (
    SELECT DISTINCT review_id FROM review_descriptors
)
ORDER BY r.date_scraped DESC;
```

---

### **Query 6: Whiskey Variant Matching**
```sql
-- Check if whiskey variant already exists
SELECT whiskey_id 
FROM whiskeys
WHERE LOWER(brand_family) = LOWER(?)
  AND LOWER(variant_name) = LOWER(?)
  AND json_extract(attributes, '$.batch') = ?  -- Match specific attributes
LIMIT 1;

-- Note: For complex attribute matching, may need to:
-- 1. Fetch all whiskeys with matching brand_family + variant_name
-- 2. Parse JSON attributes in Python to find best match
```

---

### **Query 7: Get All Descriptors for a Whiskey (Grouped by Section)**
```sql
SELECT
    awd.tasting_section,
    dv.descriptor_name,
    awd.review_count,
    awd.source_review_ids
FROM aggregated_whiskey_descriptors awd
JOIN descriptor_vocabulary dv ON awd.descriptor_id = dv.descriptor_id
WHERE awd.whiskey_id = ?
ORDER BY awd.tasting_section, dv.descriptor_name;
```

---

## **Database Constraints & Rules**

### **Uniqueness Constraints**
1. `whiskeys`: No explicit unique constraint (variants create separate records)
2. `reviews`: UNIQUE(source_site, normalized_url)
3. `descriptor_vocabulary`: UNIQUE(descriptor_name)
4. `review_descriptors`: UNIQUE(review_id, descriptor_id, tasting_section)
5. `aggregated_whiskey_descriptors`: UNIQUE(whiskey_id, descriptor_id, tasting_section)

### **Foreign Key Constraints**
- All foreign keys enforced (SQLite: `PRAGMA foreign_keys = ON;`)
- Cascading deletes configured where appropriate (future consideration)

### **Data Type Standards**
- **Dates:** TEXT in ISO 8601 format (`YYYY-MM-DD HH:MM:SS`)
- **JSON:** TEXT field with JSON validation (SQLite 3.38+)
- **Booleans:** INTEGER (0 = false, 1 = true)
- **IDs:** INTEGER PRIMARY KEY AUTOINCREMENT

---

## **Migration to PostgreSQL**

### **Changes Required:**
1. **Auto-increment:** `AUTOINCREMENT` → `SERIAL`
2. **JSON fields:** TEXT → JSONB (better performance)
3. **Boolean:** INTEGER → BOOLEAN type
4. **Full-text search:** FTS5 → PostgreSQL full-text search or pg_trgm extension
5. **JSON functions:** `json_extract()` → `jsonb_extract_path_text()`

### **Sample PostgreSQL Conversion:**
```sql
-- SQLite
CREATE TABLE whiskeys (
    whiskey_id INTEGER PRIMARY KEY AUTOINCREMENT,
    attributes TEXT  -- JSON
);

-- PostgreSQL
CREATE TABLE whiskeys (
    whiskey_id SERIAL PRIMARY KEY,
    attributes JSONB
);

CREATE INDEX idx_whiskeys_attributes ON whiskeys USING GIN (attributes);
```

---

## **Performance Considerations**

### **Indexes Created:**
- All foreign keys indexed
- Search fields indexed (name, distillery, brand_family, classification)
- Full-text search on whiskey names (via FTS5 virtual table)
- Tasting section indexed for quiz generation queries

### **Query Optimization:**
- Aggregated table denormalized for read performance
- Random flavor selection uses indexed category field
- Review deduplication uses indexed normalized_url

### **Estimated Scale:**
- 10,000+ whiskeys
- 50,000+ reviews
- 500-1,000 unique flavors
- 100,000+ review_flavor tags
- 50,000+ aggregated flavor records

---

## **Data Integrity Checks**

### **Consistency Rules:**
1. Every whiskey should have at least one review (eventually)
2. Every review should have at least one flavor tag (after manual tagging)
3. Aggregated flavors should match source review_flavors
4. No orphaned records (foreign keys enforced)

### **Validation Queries:**
```sql
-- Find whiskeys with no reviews
SELECT w.whiskey_id, w.name 
FROM whiskeys w
LEFT JOIN reviews r ON w.whiskey_id = r.whiskey_id
WHERE r.review_id IS NULL;

-- Find reviews with no descriptor tags
SELECT r.review_id, w.name, r.source_site
FROM reviews r
JOIN whiskeys w ON r.whiskey_id = w.whiskey_id
LEFT JOIN review_descriptors rd ON r.review_id = rd.review_id
WHERE rd.review_descriptor_id IS NULL;

-- Find whiskeys where aggregation is stale
SELECT DISTINCT w.whiskey_id, w.name,
    MAX(r.date_scraped) as latest_review,
    MAX(awd.last_updated) as latest_aggregation
FROM whiskeys w
JOIN reviews r ON w.whiskey_id = r.whiskey_id
LEFT JOIN aggregated_whiskey_descriptors awd ON w.whiskey_id = awd.whiskey_id
GROUP BY w.whiskey_id
HAVING latest_review > latest_aggregation OR latest_aggregation IS NULL;
```

---

## **Schema Diagram**
```
┌─────────────────────┐
│    whiskeys         │
│─────────────────────│
│ whiskey_id (PK)     │───┐
│ name                │   │
│ distillery          │   │
│ brand_family        │   │
│ variant_name        │   │
│ classification      │   │
│ proof, age, etc.    │   │
│ attributes (JSON)   │   │
└─────────────────────┘   │
                          │
                          │ 1:N
                          │
┌─────────────────────┐   │
│     reviews         │   │
│─────────────────────│   │
│ review_id (PK)      │───┤
│ whiskey_id (FK) ────┘   │
│ source_site         │   │
│ nose_text           │   │
│ palate_text         │   │
│ finish_text         │   │
│ additional_data     │   │
└─────────────────────┘   │
          │               │
          │ 1:N           │
          │               │
┌─────────────────────────┐   │
│  review_descriptors     │   │
│─────────────────────────│   │
│ review_descriptor_id(PK)│   │
│ review_id (FK) ─────────┘   │
│ descriptor_id (FK) ─────┐   │
│ tasting_section         │   │
└─────────────────────────┘   │
                              │
                              │
┌─────────────────────────┐   │
│ descriptor_vocabulary   │   │
│─────────────────────────│   │
│ descriptor_id (PK) ─────┴───┤
│ descriptor_name         │   │
│ category                │   │
│ applicable_sections     │   │
└─────────────────────────┘   │
          │                   │
          │                   │
┌─────────────────────────────┴──────┐
│ aggregated_whiskey_descriptors     │
│────────────────────────────────────│
│ aggregated_descriptor_id (PK)      │
│ whiskey_id (FK)                    │
│ descriptor_id (FK)                 │
│ tasting_section                    │
│ source_review_ids (JSON)           │
│ review_count                       │
└────────────────────────────────────┘
```

---

## **Implementation Checklist**

### **Phase 1: Core Tables (MVP)**
- [ ] Create `whiskeys` table with indexes
- [ ] Create `reviews` table with indexes
- [ ] Create `descriptor_vocabulary` table with indexes
- [ ] Create `review_descriptors` table with indexes
- [ ] Create `aggregated_whiskey_descriptors` table with indexes
- [ ] Create `scraper_runs` table
- [ ] Enable foreign key constraints (`PRAGMA foreign_keys = ON;`)
- [ ] Test all CREATE TABLE statements
- [ ] Write database initialization script

### **Phase 2: Query Functions**
- [ ] Implement whiskey search queries
- [ ] Implement quiz generation queries
- [ ] Implement aggregation refresh logic
- [ ] Implement validation queries
- [ ] Test performance with sample data

### **Phase 3: Data Quality**
- [ ] Build manual descriptor tagging interface
- [ ] Create aggregation refresh trigger/job
- [ ] Implement consistency check queries
- [ ] Set up database backup strategy

### **Phase 4: Future Preparation**
- [ ] Document future table schemas
- [ ] Plan PostgreSQL migration path
- [ ] Design user account schema
- [ ] Prepare for full-text search upgrade

---

**END OF DATABASE SCHEMA**