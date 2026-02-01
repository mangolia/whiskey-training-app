# Cleanup and Documentation Plan

**Date**: January 28, 2026
**Purpose**: Organize project files, remove redundancies, update documentation

---

## Files to Archive/Remove

### Redundant Database Files
- ❌ `whiskey_mvp_v2.db` (88KB) - Replaced by `whiskey_production.db`
  - **Action**: Move to `archive/databases/`
  - **Reason**: MVP database superseded by production version

### Redundant Python Scripts
- ❌ `match_descriptors.py` - Old version, replaced by `match_descriptors_v2.py`
  - **Action**: Move to `archive/scripts/`
- ❌ `extract_pipe_delimited_descriptors.py` - Functionality now in `rebuild_production.py`
  - **Action**: Move to `archive/scripts/`
- ⚠️ `build_mvp_v2.py` - May still be useful for reference
  - **Action**: Keep but add comment that it's superseded by `rebuild_production.py`

### Redundant Documentation (Root Level)
These are duplicates of files in `docs/`:
- ❌ `CLEANUP_RECOMMENDATIONS.md`
- ❌ `CLEANUP_SUMMARY.md`
- ❌ `FINAL_CLEANUP_REPORT.md`
- ❌ `FLASK_EXPLANATION.md`
- ❌ `FLAVOR_CATEGORIZATION_REVIEW.md`
- ❌ `QUICK_START_TASK7.md`
- ❌ `SESSION_HANDOFF.md`
- ❌ `WHISKEY_CATEGORIZATION_MASTER_GUIDE.md`
- ❌ `Whiskey_Sensory_Framework.md`
- ⚠️ `DESCRIPTOR_USAGE_REPORT.md` - Keep (useful reference)
- ⚠️ `PROGRESS.md` - Update or archive
- **Action**: Move to `archive/old-docs/` or delete if truly redundant

---

## Documentation to Update

### 1. Main README.md (MISSING!)
**Status**: ❌ Does not exist
**Priority**: HIGH
**Content needed**:
- Project overview
- Quick start guide
- Prerequisites
- Installation instructions
- Running the app (backend + frontend)
- Project structure overview
- Links to detailed docs

### 2. API_DOCUMENTATION.md
**Status**: ⚠️ Needs verification
**Action**: Verify it references `whiskey_production.db` not MVP

### 3. docs/MVP_BUILD_TASKS.md
**Status**: ⚠️ Outdated
**Current**: Says "Task 7 Next"
**Reality**: Tasks 1-7 complete, production database built
**Action**: Update to reflect current status

### 4. docs/PROJECT_STATUS.md
**Status**: ⚠️ Needs update
**Action**: Update with production database completion

### 5. frontend/README.md
**Status**: ⚠️ Needs verification
**Action**: Ensure it has correct setup instructions

---

## Documentation to Create

### 1. Main Project README.md
```markdown
# Whiskey Sensory Training App

Modern web app for training your whiskey tasting palate...

## Quick Start
## Features
## Tech Stack
## Project Structure
## Development
## Deployment
## Documentation
```

### 2. DEPLOYMENT.md
**Content**:
- Production database setup
- Backend deployment (Railway)
- Frontend deployment (Vercel)
- Environment variables
- Domain configuration

### 3. CONTRIBUTING.md (Optional)
**Content**:
- How to add whiskeys
- How to add descriptors
- Code style guide
- PR process

### 4. CHANGELOG.md
**Content**:
- Version history
- Major changes log
- Breaking changes

---

## Project Structure Review

### Current Structure (Needs Organization)

```
whiskey-scraper/
├── *.db (3 database files - consolidate!)
├── *.md (13+ markdown files at root - move to docs!)
├── *.py (20+ Python scripts - organize!)
├── app.py (backend API)
├── requirements.txt
├── archive/ (good!)
├── backups/ (good!)
├── docs/ (good!)
├── frontend/ (good!)
├── migrations/ (good!)
├── scrapers/ (good!)
└── scripts/ (good!)
```

### Recommended Structure

```
whiskey-scraper/
├── README.md ⭐ CREATE
├── INSTALLATION.md (already exists)
├── CHANGELOG.md ⭐ CREATE
├── app.py (backend)
├── requirements.txt
├── descriptor_vocabulary.py (keep - used by matching)
├── rebuild_production.py (keep - maintenance script)
├── extract_prose_descriptors.py (keep - maintenance script)
│
├── databases/ ⭐ CREATE
│   ├── whiskey_production.db (active)
│   ├── whiskey_reviews.db (source data)
│   └── archive/
│       └── whiskey_mvp_v2.db
│
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA.md
│   ├── DESIGN_SYSTEM.md
│   ├── PRD.md
│   ├── PRODUCTION_DATABASE_SUMMARY.md
│   ├── DESCRIPTOR_USAGE_REPORT.md
│   ├── COMPOUND_DESCRIPTOR_FIX.md
│   ├── FEATURE_SOURCE_REVIEWS.md
│   ├── DEPLOYMENT.md ⭐ CREATE
│   └── archive/ (for old docs)
│
├── scripts/
│   ├── (current scripts)
│   └── archive/ (old versions)
│
├── frontend/ (React app)
├── scrapers/ (web scrapers)
├── migrations/ (DB migrations)
├── archive/ (historical files)
└── backups/ (DB backups)
```

---

## Immediate Actions (Tonight)

### 1. Create Main README.md ⭐
- Overview of project
- Quick start guide
- Link to detailed docs

### 2. Update MVP_BUILD_TASKS.md
- Mark Tasks 1-7 as complete
- Update overall progress to 39% → 50%+
- Note production database completion

### 3. Create CHANGELOG.md
- Document major milestones
- Note compound descriptor fix
- Note production database creation

### 4. Consolidate Databases
- Create `databases/` folder
- Move `whiskey_production.db` and `whiskey_reviews.db` there
- Archive `whiskey_mvp_v2.db`
- Update all scripts to reference new paths

### 5. Clean Root Directory
- Move redundant docs to `archive/old-docs/`
- Keep only essential files at root level

---

## File-by-File Review

### Keep (Essential)
- ✅ `app.py` - Backend API
- ✅ `requirements.txt` - Dependencies
- ✅ `descriptor_vocabulary.py` - Used by matching logic
- ✅ `rebuild_production.py` - Maintenance script
- ✅ `extract_prose_descriptors.py` - Maintenance script
- ✅ `match_descriptors_v2.py` - Active matching logic
- ✅ `whiskey_production.db` - Production database
- ✅ `whiskey_reviews.db` - Source data
- ✅ `INSTALLATION.md` - Setup guide
- ✅ `DESCRIPTOR_USAGE_REPORT.md` - Useful reference

### Archive (Old Versions)
- 📦 `whiskey_mvp_v2.db` → `archive/databases/`
- 📦 `match_descriptors.py` → `archive/scripts/`
- 📦 `extract_pipe_delimited_descriptors.py` → `archive/scripts/`
- 📦 Root-level redundant docs → `archive/old-docs/`

### Review (Unsure)
- ❓ `build_mvp_v2.py` - May be useful for reference?
- ❓ `database.py` - Is this used?
- ❓ `test_*.py` files - Are these still relevant?
- ❓ `utils.py` - What's in here?
- ❓ `verify_extractions.py` - Still needed?
- ❓ `PROGRESS.md` - Update or archive?

### Delete (If Truly Redundant)
- ❌ Old cleanup reports (already in docs/)
- ❌ Duplicate documentation
- ❌ Unused test files

---

## Documentation Standards

### Markdown File Headers
Every doc should have:
```markdown
# Title

**Date**: YYYY-MM-DD
**Status**: Active/Archive/Draft
**Purpose**: One-line description

---
```

### File Naming Convention
- `UPPERCASE.md` for root-level important docs (README, CHANGELOG)
- `Title_Case.md` for docs in `/docs/` folder
- `lowercase_with_underscores.py` for Python scripts

### Required Sections in Docs
1. **Overview** - What is this?
2. **Quick Start** - How to use immediately
3. **Details** - In-depth information
4. **Examples** - Practical usage
5. **Troubleshooting** - Common issues

---

## Documentation Index

### For Users
- README.md - Start here
- INSTALLATION.md - Setup guide
- docs/DESIGN_SYSTEM.md - UI/UX guidelines
- docs/PRD.md - Product requirements

### For Developers
- docs/API_DOCUMENTATION.md - API reference
- docs/DATABASE_SCHEMA.md - DB structure
- docs/PRODUCTION_DATABASE_SUMMARY.md - DB details
- docs/COMPOUND_DESCRIPTOR_FIX.md - Technical decisions

### For Deployment
- DEPLOYMENT.md (to create) - Deploy guide
- requirements.txt - Python dependencies
- frontend/package.json - Frontend dependencies

### For QA/Review
- docs/DESCRIPTOR_USAGE_REPORT.md - Descriptor stats
- docs/FEATURE_SOURCE_REVIEWS.md - Source links feature

---

## Next Session Tasks

1. ✅ Create main README.md
2. ✅ Update MVP_BUILD_TASKS.md
3. ✅ Create CHANGELOG.md
4. ✅ Create databases/ folder and reorganize
5. ✅ Archive redundant files
6. ⏳ Create DEPLOYMENT.md
7. ⏳ Review and update API_DOCUMENTATION.md
8. ⏳ Clean up root directory
9. ⏳ Verify all docs have proper headers
10. ⏳ Create documentation index page

---

## Quality Checklist

### Documentation
- [ ] Every Python script has docstring at top
- [ ] Every MD file has date and status
- [ ] No broken links between docs
- [ ] All paths reference correct locations
- [ ] Code examples are up-to-date
- [ ] Screenshots/examples match current UI

### Code
- [ ] No unused imports
- [ ] No commented-out code blocks
- [ ] Consistent naming conventions
- [ ] All database paths updated
- [ ] All scripts have error handling

### Project
- [ ] No redundant files in root
- [ ] Clear folder structure
- [ ] Archive has old versions
- [ ] README explains everything
- [ ] New contributors can set up easily

---

**Status**: Plan created, ready to execute
**Estimated Time**: 2-3 hours for cleanup + documentation
**Priority**: High - Project is functional but needs organization
