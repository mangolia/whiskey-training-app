# Whiskey Scraper Project Progress

**Last Updated:** 2025-12-30 (Code cleanup session)  
**Project Status:** ✅ Core Features Complete, Automation Ready

---

## 📝 How to Update This File

After each working session, update the following sections:

1. **Update "Last Updated" date** at the top
2. **Add to "Completed Features"** - Check off any new items
3. **Add to "Key Decisions"** - Document any new decisions made
4. **Add to "Session Notes"** - Create new entry with:
   - Date
   - What was accomplished
   - Key learnings or issues encountered
5. **Update "Current Statistics"** - Refresh numbers if relevant
6. **Update "Next Steps"** - Mark completed items, add new ones

**Quick Update Template:**
```markdown
### Session X: [Topic] ([Date])
- Accomplished: [What was done]
- Decisions: [Any decisions made]
- Issues: [Problems encountered and solutions]
- Next: [What to do next]
```

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Completed Features](#completed-features)
3. [Key Decisions](#key-decisions)
4. [Architecture & Design](#architecture--design)
5. [File Structure](#file-structure)
6. [Configuration](#configuration)
7. [Database Schema](#database-schema)
8. [Known Issues & Solutions](#known-issues--solutions)
9. [Future Enhancements](#future-enhancements)
10. [Session Notes](#session-notes)

---

## Project Overview

**Goal:** Automated daily scraping of whiskey reviews from Breaking Bourbon (and future sites), with a web dashboard for monitoring and data analysis.

**Current Status:**
- ✅ Core scraper functional
- ✅ Database schema complete
- ✅ Daily automation ready
- ✅ Flask dashboard operational
- ✅ Error handling & logging implemented
- ✅ Character encoding fixed

---

## Completed Features

### ✅ Phase 1: Core Scraping (COMPLETE)
- [x] Breaking Bourbon scraper implementation
- [x] Review data extraction (all fields)
- [x] Full review text extraction
- [x] Date-sorted review discovery
- [x] Duplicate detection via URL normalization
- [x] Field name alignment (whiskey_name → name)

### ✅ Phase 2: Database & Storage (COMPLETE)
- [x] SQLite database with proper schema
- [x] Whiskeys master table
- [x] Reviews table with all fields
- [x] Scraper runs tracking table
- [x] Daily summaries table
- [x] Database path: project root (`whiskey_reviews.db`)
- [x] UTF-8 encoding support

### ✅ Phase 3: Daily Automation (COMPLETE)
- [x] Enhanced daily check script with retry logic
- [x] Battery detection (skips on battery, allows manual)
- [x] Exponential backoff retry (3 attempts: 5min, 15min, 30min)
- [x] Smart error handling (retries network errors, not 404s)
- [x] launchd plist for macOS scheduling
- [x] Setup script for easy installation
- [x] Scheduled for 11pm EST (auto-adjusts for DST)

### ✅ Phase 4: Logging System (COMPLETE)
- [x] Daily log rotation (`logs/scraper-YYYY-MM-DD.log`)
- [x] Error-only log (`logs/errors.log`)
- [x] Structured logging with levels (INFO, WARNING, ERROR, etc.)
- [x] 90-day retention policy
- [x] Launchd output logging

### ✅ Phase 5: Flask Dashboard (COMPLETE)
- [x] Real-time statistics display
- [x] Auto-refresh every 30 seconds
- [x] Error tracking section (last 30 days)
- [x] Daily summaries section (last 30 days)
- [x] Manual "Run Scraper Now" button
- [x] Interactive error details (expandable)
- [x] Reviews by source site
- [x] Recent reviews list

### ✅ Phase 6: Character Encoding (COMPLETE)
- [x] Text normalization function
- [x] Smart quote to regular quote conversion
- [x] Double-encoded UTF-8 fix
- [x] Applied to all text extraction
- [x] Fix script for existing corrupted data

---

## Key Decisions

### Scheduling & Automation
- **Scheduler:** macOS launchd (not cron)
- **Time:** 11pm Eastern Time (auto-adjusts for DST)
- **Wake from sleep:** Enabled (requires AC power)
- **Battery behavior:** Skip scheduled run, log notification, allow manual run
- **Late wake:** Don't auto-run, create notification for manual run

### Error Handling
- **Retry strategy:** Exponential backoff (5min, 15min, 30min)
- **Max attempts:** 3
- **Retry on:** Network errors, database errors
- **Don't retry:** 404 errors, parsing errors (likely permanent)
- **Error history:** Last 30 days in dashboard
- **Notifications:** Dashboard only (no separate email/desktop)

### Dashboard
- **Technology:** Flask web application
- **Access:** Localhost only (127.0.0.1:5000)
- **Start method:** Manual start (`python app.py`)
- **Auto-refresh:** 30 seconds
- **Features:** Real-time stats, error tracking, daily summaries, manual run button

### Database
- **Location:** Project root (`whiskey_reviews.db`)
- **Encoding:** UTF-8
- **Tables:** whiskeys, reviews, scraper_runs, daily_summaries
- **Field mapping:** Scraper uses `name` (not `whiskey_name`)

### Multi-Site Support
- **Execution:** Sequential (one after another)
- **Error handling:** Continue with other scrapers if one fails
- **Timing:** All at 11pm (same schedule)
- **Configuration:** YAML config file lists enabled scrapers

### Logging
- **Retention:** 90 days, archive older
- **Rotation:** Daily rotation
- **Format:** Plain text with structured format
- **Levels:** INFO, SUCCESS, WARNING, ERROR, CRITICAL

---

## Architecture & Design

### Scraper Architecture
```
BaseScraper (abstract)
    ↓
BreakingBourbonScraper
    - find_review_urls() - Finds reviews from date-sorted page
    - scrape_review() - Scrapes single review
    - parse_review_html() - Parses HTML to extract data
    - _normalize_text() - Fixes encoding issues
```

### Data Flow
```
1. launchd triggers → automated_daily_check.py
2. Script loads config.yaml
3. Checks battery (skip if on battery, not manual)
4. Finds review URLs (last N days)
5. For each URL:
   - Check duplicate in database
   - Scrape if new
   - Store in database
6. Create daily summary
7. Log to scraper_runs table
8. Write logs to files
```

### Dashboard Architecture
```
Flask App (app.py)
    ↓
Templates (dashboard.html)
    ↓
Static Files (CSS, JS)
    ↓
Database Queries
    ↓
Real-time Updates (JavaScript auto-refresh)
```

---

## File Structure

### Core Files
```
whiskey-scraper/
├── scrapers/
│   ├── base_scraper.py          # Base class for all scrapers
│   └── breaking_bourbon.py      # Breaking Bourbon specific scraper
├── database.py                   # Database operations & schema
├── utils.py                      # Utility functions (normalize, parse_date, etc.)
├── config.yaml                   # Configuration file
└── whiskey_reviews.db            # SQLite database
```

### Automation Files
```
├── automated_daily_check.py     # Enhanced daily check with retry/battery
├── com.whiskey-scraper.daily.plist  # launchd scheduler file
├── setup_automation.sh           # Installation script
└── logs/                         # Log files directory
    ├── scraper-YYYY-MM-DD.log   # Daily logs
    └── errors.log                # Error-only log
```

### Dashboard Files
```
├── app.py                        # Flask application
├── templates/
│   └── dashboard.html           # Dashboard template
└── static/
    ├── css/
    │   └── style.css            # Dashboard styling
    └── js/
        └── dashboard.js         # Auto-refresh & interactivity
```

### Utility Scripts (in scripts/ directory)
```
├── scripts/
│   ├── fix_encoding.py          # Fix character encoding issues
│   ├── update_review_text.py    # Update existing reviews with full text
│   ├── view_todays_reviews.py   # View today's reviews
│   └── view_reports.py          # View scraper run reports
```

### Documentation
```
├── AUTOMATION_PLAN.md           # Detailed automation planning
├── FLASK_EXPLANATION.md         # Flask pros/cons explanation
├── INSTALLATION.md              # Setup and installation guide
├── AUTOMATION_SUMMARY.md        # Quick reference
├── PROGRESS.md                  # This file - project progress
└── breaking-bourbon-data-map.md # Data mapping reference
```

---

## Configuration

### config.yaml Structure
```yaml
schedule:
  hour: 23                    # 11pm
  minute: 0
  timezone: "America/New_York"  # Auto-adjusts for DST
  wake_from_sleep: true

scrapers:
  enabled:
    - breaking_bourbon

logging:
  level: "INFO"
  retention_days: 90
  log_dir: "logs"
  rotation: "daily"

retry:
  max_attempts: 3
  delay_seconds: [300, 900, 1800]  # 5min, 15min, 30min
  retry_on_network_error: true
  retry_on_database_error: true
  retry_on_parsing_error: false

power:
  skip_on_battery: true
  allow_manual_on_battery: true

dashboard:
  port: 5000
  host: "127.0.0.1"
  auto_refresh_seconds: 30

paths:
  project_root: "/Users/michaelangolia/whiskey-scraper"
  venv_python: "/Users/michaelangolia/whiskey-scraper/venv/bin/python"
  database: "/Users/michaelangolia/whiskey-scraper/whiskey_reviews.db"
```

---

## Database Schema

### Tables

**whiskeys**
- `whiskey_id` (PK)
- `name` (TEXT, NOT NULL)
- `distillery` (TEXT)
- `first_seen_date` (TEXT)
- `needs_review` (INTEGER)

**reviews**
- `review_id` (PK)
- `whiskey_id` (FK → whiskeys)
- `source_site` (TEXT, NOT NULL)
- `source_url` (TEXT, NOT NULL)
- `normalized_url` (TEXT) - for duplicate detection
- `review_date` (TEXT) - publication date
- `date_scraped` (TEXT, NOT NULL)
- `classification`, `company`, `proof`, `age`, `mashbill`, `color`, `price`
- `nose`, `palate`, `finish` - tasting notes
- `overall_notes` (TEXT) - full review text
- `rating`, `additional_data`

**scraper_runs**
- `run_id` (PK)
- `source_site` (TEXT, NOT NULL)
- `run_date` (TEXT, NOT NULL)
- `status` (TEXT) - success/partial/error/skipped
- `reviews_found` (INTEGER)
- `reviews_added` (INTEGER)
- `error_message` (TEXT)
- `execution_time` (REAL)

**daily_summaries**
- `summary_id` (PK)
- `summary_date` (TEXT, UNIQUE)
- `total_reviews_found` (INTEGER)
- `total_reviews_added` (INTEGER)
- `total_duplicates` (INTEGER)
- `total_errors` (INTEGER)
- `sites_checked` (TEXT)
- `execution_time` (REAL)
- `status` (TEXT)
- `summary_text` (TEXT)
- `created_at` (TEXT)

---

## Known Issues & Solutions

### ✅ FIXED: Character Encoding
**Issue:** Smart quotes stored as `bakerâ\x80\x99s` instead of `baker's`  
**Solution:** 
- Added `_normalize_text()` method to scraper
- Converts smart quotes to regular quotes
- Fixes double-encoded UTF-8 patterns
- Created `fix_encoding.py` to repair existing data

**To fix existing data:**
```bash
python fix_encoding.py
```

### ✅ FIXED: Field Name Mismatch
**Issue:** Scraper used `whiskey_name`, database expected `name`  
**Solution:** Scraper now maps `whiskey_name` → `name` before storing

### ✅ FIXED: Review Text Extraction
**Issue:** Only first paragraph captured (134 chars)  
**Solution:** Updated `_extract_review_text()` to find longest `w-richtext` div, handles `desktoptext` class

### Battery & Power
**Behavior:** Scheduled runs skip if on battery  
**Workaround:** Manual runs work on battery (use `--manual` flag or dashboard button)

### macOS Network Permission
**Issue:** macOS asks to allow Python to find devices on local network  
**Solution:** Click "Allow" - this is normal for Flask. Dashboard only listens on localhost.

---

## Future Enhancements

### Phase 1: Additional Scrapers
- [ ] Whiskey Advocate scraper
- [ ] Bourbon Banter scraper
- [ ] Other review sites
- [ ] Unified scraper runner

### Phase 2: Dashboard Enhancements
- [ ] Charts/graphs (reviews over time)
- [ ] Advanced filtering (by date range, site, whiskey)
- [ ] Search functionality
- [ ] Export data (CSV/JSON)
- [ ] Historical trends

### Phase 3: Data Analysis
- [ ] Price tracking over time
- [ ] Rating analysis
- [ ] Distillery statistics
- [ ] Age vs. rating correlations

### Phase 4: Advanced Features
- [ ] Email notifications for errors
- [ ] API endpoints for external access
- [ ] User authentication (if needed)
- [ ] Backup/restore functionality

---

## Session Notes

### Session 1: Initial Setup (2025-12-30)
- Created base scraper architecture
- Implemented Breaking Bourbon scraper
- Set up database schema
- Fixed field name mapping

### Session 2: Daily Automation (2025-12-30)
- Created automated daily check script
- Implemented retry logic with exponential backoff
- Added battery detection
- Created launchd plist for scheduling
- Set up logging system

### Session 3: Dashboard & Encoding (2025-12-30)
- Built Flask web dashboard
- Added error tracking section
- Added daily summaries section
- Fixed character encoding issues
- Created fix script for existing data

**Key Learnings:**
- BeautifulSoup handles encoding well, but need explicit normalization
- SQLite needs UTF-8 encoding set explicitly
- launchd is better than cron on macOS for sleep/wake handling
- Flask is simple enough for local dashboard, powerful enough to expand

### Session 4: Code Cleanup & Organization (2025-12-30)
- Removed deprecated files (daily_check.py, dashboard.py, dashboard.html)
- Organized utility scripts into scripts/ directory
- Created .gitignore for proper version control
- Updated PROGRESS.md with cleanup changes
- Fixed import paths in moved scripts

**Files Removed:**
- `daily_check.py` (replaced by `automated_daily_check.py`)
- `dashboard.py` (replaced by Flask `app.py`)
- `dashboard.html` (root, replaced by `templates/dashboard.html`)
- `README_DASHBOARD.md` (outdated, references old dashboard)
- `tests_and_such/` (empty directory)

**Files Organized:**
- Moved utility scripts to `scripts/` directory:
  - `fix_encoding.py`
  - `update_review_text.py`
  - `view_todays_reviews.py`
  - `view_reports.py`

---

## Quick Reference Commands

### Daily Operations
```bash
# Run scraper manually
python automated_daily_check.py --manual

# View today's reviews
python scripts/view_todays_reviews.py

# View scraper reports
python scripts/view_reports.py "Breaking Bourbon" 7

# Start dashboard
python app.py
# Then open: http://127.0.0.1:5000
```

### Automation Management
```bash
# Set up automation (one time)
./setup_automation.sh

# Check if automation is loaded
launchctl list | grep whiskey

# Unload automation
launchctl unload ~/Library/LaunchAgents/com.whiskey-scraper.daily.plist

# Reload automation (after changes)
launchctl unload ~/Library/LaunchAgents/com.whiskey-scraper.daily.plist
launchctl load ~/Library/LaunchAgents/com.whiskey-scraper.daily.plist
```

### Maintenance
```bash
# Fix encoding issues
python scripts/fix_encoding.py

# Update existing reviews with full text
python scripts/update_review_text.py

# View today's reviews
python scripts/view_todays_reviews.py

# View scraper reports
python scripts/view_reports.py "Breaking Bourbon" 7

# View logs
tail -f logs/scraper-$(date +%Y-%m-%d).log
tail -f logs/errors.log
```

---

## Important Notes for Future Sessions

### When Adding New Scrapers
1. Inherit from `BaseScraper`
2. Implement `scrape_review()` and `find_review_urls()`
3. Use `_normalize_text()` for all text extraction
4. Map field names to database schema (`name` not `whiskey_name`)
5. Add to `config.yaml` under `scrapers.enabled`

### When Modifying Database
1. Update schema in `database.py`
2. Run `create_database()` to apply changes
3. Update dashboard queries if needed
4. Test with existing data

### When Debugging
1. Check logs first: `logs/scraper-YYYY-MM-DD.log`
2. Check launchd logs: `logs/launchd.err`
3. Test manually: `python automated_daily_check.py --manual`
4. Check database: Use `view_todays_reviews.py` or SQLite directly

### Configuration Changes
- Edit `config.yaml` (YAML format)
- Restart dashboard if running
- Reload launchd if schedule changed
- No need to restart for most config changes (scraper reads on each run)

---

## Current Statistics

**As of Last Update:**
- Total Reviews: 11
- Total Whiskeys: 9
- Source Sites: 3 (Breaking Bourbon, Bourbon Banter, Bourbon Culture)
- Last Review Scraped: 2025-12-31 03:01:25
- Automation Status: Ready to activate

---

## Next Steps

1. ✅ **Run fix_encoding.py** to fix existing corrupted data
2. ✅ **Set up automation** with `./setup_automation.sh`
3. ✅ **Start dashboard** and verify everything works
4. ⏳ **Monitor first automated run** (will happen at 11pm EST)
5. ⏳ **Add more scrapers** as needed

---

**To Update This File:**
Add new session notes, completed features, or decisions at the top of relevant sections. Keep timestamps for tracking progress.

