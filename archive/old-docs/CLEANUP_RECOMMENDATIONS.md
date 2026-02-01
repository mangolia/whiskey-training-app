# Project Cleanup Recommendations

**Date:** January 19, 2026
**Status:** Awaiting approval before deletion

---

## Overview

This document identifies files that may be candidates for cleanup, archiving, or consolidation based on:
- Superseded documentation
- Redundant/obsolete scripts
- Old test files
- Temporary data files
- Deprecated functionality

**⚠️ NOTHING WILL BE DELETED WITHOUT YOUR APPROVAL ⚠️**

---

## Category 1: Superseded Documentation Files

### 🔴 HIGH CONFIDENCE - Likely Safe to Remove/Archive

| File | Reason | Recommendation |
|------|--------|----------------|
| `AUTOMATION_PLAN.md` | Planning doc, work is complete | **ARCHIVE** - Move to `/docs/archive/` or delete |
| `AUTOMATION_SUMMARY.md` | Summary of completed work | **ARCHIVE** - Keep as historical record |
| `PAUSE_POINT_SUMMARY.md` | Temporary checkpoint doc | **DELETE** - No longer needed |
| `FLAVOR_REVIEW_RECOMMENDATIONS.md` | Superseded by `WHISKEY_CATEGORIZATION_MASTER_GUIDE.md` | **DELETE** - Consolidated into master guide |
| `FLAVOR_EXTRACTION_SUMMARY.md` | Process summary, work complete | **ARCHIVE** or **DELETE** |
| `historical_scraper_instructions.md` | Instructions for one-time task | **ARCHIVE** - Keep as reference |
| `breaking-bourbon-data-map.md` | Initial mapping document | **KEEP** or **MOVE TO DOCS** - May be useful reference |

### 📊 Current Documentation Structure

**Keep These (Core Docs):**
- ✅ `WHISKEY_CATEGORIZATION_MASTER_GUIDE.md` - Master reference
- ✅ `Whiskey_Sensory_Framework.md` - Theoretical framework
- ✅ `FLAVOR_CATEGORIZATION_REVIEW.md` - Current 624 flavor review
- ✅ `PROGRESS.md` - Active project progress
- ✅ `INSTALLATION.md` - Setup instructions
- ✅ `/docs/PRD.md` - Product requirements
- ✅ `/docs/DATABASE_SCHEMA.md` - Schema documentation

---

## Category 2: Test Files

### 🟡 MEDIUM CONFIDENCE - Review Usage

| File | Purpose | Last Modified | Recommendation |
|------|---------|---------------|----------------|
| `test_bb_homepage.py` | Test Breaking Bourbon homepage scraping | Oct 25 | **DELETE** - If scraper is working |
| `test_scraper.py` | Initial scraper tests | Oct 25 | **DELETE** - If main scraper works |
| `test_real_review.py` | Real review parsing test | Oct 25 | **DELETE** - If scraper works |
| `test_database.py` | Database connectivity test | Nov 30 | **KEEP** - Useful for debugging |
| `test_database_ops.py` | Database operations test | Nov 30 | **CONSOLIDATE** - Merge with test_database.py? |
| `test_utils.py` | Utility function tests | Nov 30 | **KEEP** - If utils.py is active |

**Recommendation:** If your main scrapers and database operations are stable, the old test files from Oct/Nov can likely be deleted. Keep the more recent ones for debugging.

---

## Category 3: Temporary/Duplicate Scripts

### 🟡 MEDIUM CONFIDENCE

| File | Purpose | Recommendation |
|------|---------|----------------|
| `fix_encoding.py` (root) | Encoding fix utility | **CHECK DUPLICATE** - Also exists in `/scripts/fix_encoding.py` |
| `scripts/fix_encoding.py` | Same as above | **KEEP ONE** - Delete duplicate |
| `scripts/update_review_text.py` | One-time update script? | **ARCHIVE** - If task is complete |

---

## Category 4: Data Files (Intermediate Processing)

### 🔴 HIGH CONFIDENCE - Safe to Delete (After Verification)

All files in `/data/` appear to be intermediate processing files from the flavor extraction/categorization pipeline that ran on Jan 15-16, 2026. These are timestamped snapshots.

**Files that can likely be deleted (22 files):**

```
data/
├── ambiguous_flavors_20260115_232841.json               (7.3K)
├── categorization_stats_20260115_233711.json            (297B)
├── categorization_stats_20260115_234723.json            (297B)
├── categorized_flavors_20260115_233711.json             (88K)
├── categorized_flavors_20260115_234723.json             (88K)
├── categorized_flavors_624_20260115_234759.json         (114K)
├── cleanup_stats_20260115_232841.json                   (174B)
├── extraction_stats_20260115_232327.json                (144B)
├── filtered_flavor_names_20260115_233626.json           (8.2K)
├── filtered_flavors_strategy_c_20260115_233626.json     (79K)
├── filtered_stats_20260115_233626.json                  (1.5K)
├── final_valid_flavors_20260115_232914.json             (580K)
├── flavor_frequency_20260115_232327.json                (838K)
├── flavor_names_only_20260115_232914.json               (115K)
├── flavor_sections_20260115_232327.json                 (969K)
├── flavors_for_categorization_624.json                  (70K)
├── invalid_flavors_20260115_232841.json                 (882K)
├── low_confidence_flavors_20260115_233711.json          (29K)
├── low_confidence_flavors_20260115_234723.json          (29K)
├── section_frequency_20260115_232327.json               (887K)
├── unique_flavors_20260115_232327.json                  (817K)
└── valid_flavors_20260115_232841.json                   (580K)

Total: ~6.1MB
```

**Recommendation:**
- ✅ **KEEP ONLY:** `categorized_flavors_624_20260115_234759.json` (final output with 624 categorized flavors)
- ❌ **DELETE:** All other timestamped processing files
- 💾 **OPTIONAL:** Compress into archive if you want historical record

---

## Category 5: Obsolete/Superseded Files

### 🔴 HIGH CONFIDENCE

| File | Issue | Recommendation |
|------|-------|----------------|
| `spirits.db` (72KB, Jan 9) | Old/test database? | **DELETE** - Main DB is `whiskey_reviews.db` (10MB) |
| `sample-review.html` (50KB, Oct 27) | Sample for initial testing | **ARCHIVE** or **DELETE** |
| `flavor_review.html` (11KB, Jan 16) | Generated review HTML | **CHECK** - Is this still used? |
| `flavor_review_embedded.html` (483KB, Jan 16) | Embedded version | **CHECK** - Is this still used? |
| `flavor_review_fixed.html` (11KB, Jan 16) | Fixed version | **CHECK** - Can consolidate? |
| `cola_images/` directory | Purpose unclear | **CHECK** - What is this? |

---

## Category 6: One-Time Use Scripts

### 🟡 MEDIUM CONFIDENCE - Archive After Verification

| File | Purpose | Recommendation |
|------|---------|----------------|
| `historical_scraper.py` | One-time historical scrape | **ARCHIVE** - If backfill is complete |
| `backfill_missed_days.py` | Backfill missing review days | **KEEP** - May need again |
| `scripts/extract_flavors.py` | Initial flavor extraction | **ARCHIVE** - Pipeline complete |
| `scripts/cleanup_flavors.py` | Flavor cleanup step | **ARCHIVE** - Pipeline complete |
| `scripts/filter_and_consolidate.py` | Consolidation step | **ARCHIVE** - Pipeline complete |
| `scripts/categorize_flavors.py` | Categorization step | **ARCHIVE** - May need for updates |
| `scripts/finalize_flavors.py` | Finalization step | **ARCHIVE** - Pipeline complete |
| `scripts/review_flavors.py` | Manual review tool | **KEEP** - May need for validation |

---

## Category 7: Keep As-Is (Core Functionality)

### ✅ DEFINITELY KEEP

**Core Application:**
- `app.py` - Flask application
- `database.py` - Database operations
- `utils.py` - Utility functions
- `config.yaml` - Configuration
- `requirements.txt` - Dependencies

**Automation:**
- `automated_daily_check.py` - Daily scraper
- `setup_automation.sh` - Automation setup
- `com.whiskey-scraper.daily.plist` - Cron config

**Data:**
- `whiskey_reviews.db` - Main database (10MB)
- `discovered_urls.json` - URL tracking
- `historical_scrape_progress.json` - Progress tracking

**Scrapers:**
- `scrapers/` directory - All scraper modules

**Migrations:**
- `migrations/` directory - Database migrations

**Static/Templates:**
- `static/` directory
- `templates/` directory

**Logs:**
- `logs/` directory - Keep for debugging

**Backups:**
- `backups/` directory - Keep for safety

---

## Recommended Cleanup Actions

### Phase 1: Low-Risk Deletions (Immediate)

```bash
# Delete intermediate processing files (after confirming final output is good)
rm /sessions/gracious-modest-davinci/mnt/whiskey-scraper/data/*20260115*.json

# Keep only the final categorized output
# (manually move categorized_flavors_624_20260115_234759.json to a permanent location first)

# Delete temporary summary docs
rm /sessions/gracious-modest-davinci/mnt/whiskey-scraper/PAUSE_POINT_SUMMARY.md
rm /sessions/gracious-modest-davinci/mnt/whiskey-scraper/FLAVOR_REVIEW_RECOMMENDATIONS.md
rm /sessions/gracious-modest-davinci/mnt/whiskey-scraper/FLAVOR_EXTRACTION_SUMMARY.md
```

**Estimated space saved:** ~6MB

### Phase 2: Archive Old Documentation

```bash
# Create archive directory
mkdir -p /sessions/gracious-modest-davinci/mnt/whiskey-scraper/docs/archive

# Move planning/historical docs
mv /sessions/gracious-modest-davinci/mnt/whiskey-scraper/AUTOMATION_PLAN.md docs/archive/
mv /sessions/gracious-modest-davinci/mnt/whiskey-scraper/AUTOMATION_SUMMARY.md docs/archive/
mv /sessions/gracious-modest-davinci/mnt/whiskey-scraper/historical_scraper_instructions.md docs/archive/
```

### Phase 3: Cleanup Old Test Files

```bash
# Delete obsolete test files (if scrapers are working)
rm /sessions/gracious-modest-davinci/mnt/whiskey-scraper/test_bb_homepage.py
rm /sessions/gracious-modest-davinci/mnt/whiskey-scraper/test_scraper.py
rm /sessions/gracious-modest-davinci/mnt/whiskey-scraper/test_real_review.py
```

### Phase 4: Remove Duplicate/Old DBs

```bash
# Delete old test database (after confirming main DB is good)
rm /sessions/gracious-modest-davinci/mnt/whiskey-scraper/spirits.db
```

### Phase 5: Archive One-Time Scripts

```bash
# Create scripts archive
mkdir -p /sessions/gracious-modest-davinci/mnt/whiskey-scraper/scripts/archive

# Move one-time processing scripts
mv scripts/extract_flavors.py scripts/archive/
mv scripts/cleanup_flavors.py scripts/archive/
mv scripts/filter_and_consolidate.py scripts/archive/
mv scripts/finalize_flavors.py scripts/archive/
```

---

## Questions Before Proceeding

Before I execute any deletions, please confirm:

1. **Data files:** Are you okay with deleting all the intermediate processing files in `/data/` (keeping only the final `categorized_flavors_624` file)?

2. **Test files:** Are your scrapers working reliably? If yes, can we delete the old Oct/Nov test files?

3. **Documentation:** Do you want to ARCHIVE (keep in `/docs/archive/`) or fully DELETE the superseded planning documents?

4. **spirits.db:** Is this an old test database? Can we delete it?

5. **HTML files:** What are `flavor_review.html`, `flavor_review_embedded.html`, and `flavor_review_fixed.html` used for? Still needed?

6. **cola_images/:** What's in this directory? Can it be removed?

7. **One-time scripts:** The flavor extraction pipeline scripts - archive or delete?

8. **Sample files:** `sample-review.html` - still needed for reference?

---

## Summary

**Total files identified for potential cleanup:** ~40+ files
**Estimated disk space that could be freed:** ~6-7 MB (mostly from `/data/`)

**Conservative approach:**
1. Delete only intermediate processing files (timestamps show they're snapshots)
2. Archive (don't delete) documentation and one-time scripts
3. Keep all core functionality, databases, logs, backups

**Aggressive approach:**
1. Delete all intermediate files + old tests + obsolete docs
2. Archive one-time scripts
3. Clean up duplicate files

**Your call!** Let me know which approach you prefer and if you have any questions about specific files.
