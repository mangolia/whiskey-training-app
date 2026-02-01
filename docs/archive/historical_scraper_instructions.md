# Historical Scraper Build Instructions

## Project Overview

**Objective:** Build a one-time historical scraper that discovers and scrapes ALL existing whiskey reviews from Breaking Bourbon, storing them in the existing database.

**Estimated runtime:** ~50 minutes (at 2-second intervals between requests)

### In Scope ✅

| Content Type | URL Pattern | Action |
|--------------|-------------|--------|
| **Full Reviews** | `/review/` | Scrape these |

### Out of Scope ❌

| Content Type | URL Pattern | Reason |
|--------------|-------------|--------|
| Articles | `/article/` | Editorial content, not structured reviews |
| Tasting Notes Tuesday | `/tnt/` | Different format, less structured |
| Single Barrel Club | `/single-barrel-club/` | Different format, exclusive picks |
| All other pages | Various | Not review content |

**IMPORTANT:** The sitemap contains many URL types. The scraper must filter to ONLY process URLs containing `/review/` in the path.

### Estimated Volume

Based on pagination analysis, there are approximately **1,500 review pages**. However, this is an estimate. The actual count should be verified when the sitemap is fetched. Do not hardcode this number - always use the actual count from the sitemap.

---

## Prerequisites

### Project Location

**Directory:** `~/whiskey-scraper/`

All work should be done in this directory. New files should be created here alongside existing code.

### Virtual Environment

**IMPORTANT:** Always activate the virtual environment before running any code:

```bash
cd ~/whiskey-scraper
source venv/bin/activate
```

### Existing Code to Use

Before building, review and understand these existing files:

| File | Purpose | How Historical Scraper Uses It |
|------|---------|-------------------------------|
| `database.py` | All database operations | Use existing functions to check for duplicates and insert reviews |
| `scrapers/breaking_bourbon.py` | Scrapes individual review pages | Instantiate `BreakingBourbonScraper` and call `scrape_review(url)` |
| `utils.py` | URL normalization, date parsing | Import `normalize_url`, `parse_date`, `get_current_timestamp`, `parse_age` |
| `config.yaml` | Settings (rate limits, user-agent) | Read settings from here, don't hardcode |

---

## Existing Code Reference

### database.py Functions to Use

```python
# Import the module
import database

# Get database connection
conn = database.get_connection()

# Check if review already exists (returns True if duplicate)
is_duplicate = database.check_duplicate_review(conn, source_site, normalized_url)

# Insert a review (handles whiskey matching/creation automatically)
# Returns review_id if inserted, None if duplicate
review_id = database.insert_review(conn, review_data)

# Log a scraper run
database.log_scraper_run(
    conn,
    source_site="Breaking Bourbon",
    status="success",  # or "error" or "partial"
    reviews_found=100,
    reviews_added=95,
    error_message=None,
    execution_time=120.5
)

# Utility functions also available in database.py:
normalized = database.normalize_url(url)
timestamp = database.get_current_timestamp()
parsed = database.parse_date(date_string)
```

### insert_review() Expected Data Format

The `insert_review()` function expects a dictionary with these keys:

```python
review_data = {
    # REQUIRED
    'name': 'Eagle Rare 10 Year',           # Whiskey name
    'source_site': 'Breaking Bourbon',       # Must be exactly this string
    'source_url': 'https://...',             # Original URL
    
    # OPTIONAL (all nullable)
    'distillery': 'Buffalo Trace',
    'classification': 'Straight Bourbon',
    'company': 'Sazerac',
    'proof': '90',                           # Stored as TEXT
    'age': '10 Years',                       # Stored as TEXT (raw string)
    'mashbill': 'Low Rye',
    'color': 'Auburn',
    'price': '$34.99',                       # Stored as TEXT
    'nose': 'Vanilla | Oak | Caramel',
    'palate': 'Honey | Spice | Leather',
    'finish': 'Long | Oaky',
    'rating': '87',                          # Stored as TEXT
    'overall_notes': 'Full review text...',
    'review_date': 'October 22, 2025',       # Will be parsed to ISO format
    'additional_data': None                  # JSON string for extras
}
```

### BreakingBourbonScraper Usage

```python
# Import the scraper
from scrapers.breaking_bourbon import BreakingBourbonScraper

# Create instance
scraper = BreakingBourbonScraper()

# Scrape a single review URL
# Returns dict with all review data, or None if failed
data = scraper.scrape_review(url)

# The returned data dict already has:
# - 'source_site': 'Breaking Bourbon'
# - 'source_url': the URL
# - 'normalized_url': normalized version
# - 'date_scraped': current timestamp
# - 'name': whiskey name (mapped from whiskey_name)
# - 'overall_notes': review text (mapped from review_text)
# - All bottle info fields (classification, company, distillery, proof, age, etc.)
# - Tasting notes (nose, palate, finish)
# - 'review_date': parsed date

# Key constants
BreakingBourbonScraper.SOURCE_NAME  # "Breaking Bourbon"
BreakingBourbonScraper.BASE_URL     # "https://www.breakingbourbon.com"
```

### BaseScraper (inherited by BreakingBourbonScraper)

The scraper inherits from `scrapers/base_scraper.py` which provides:

```python
# fetch_page() - fetches HTML with rate limiting and error handling
html = scraper.fetch_page(url)  # Returns HTML string or None on failure

# The base scraper handles:
# - User-Agent header (from config)
# - Rate limiting (from config)
# - Request timeout
# - Basic error handling
```

---

## Database Schema

**Database file:** `~/whiskey-scraper/whiskey_reviews.db`

The scraper must work with the existing schema:

```sql
-- whiskeys table (master index)
whiskey_id          INTEGER PRIMARY KEY AUTOINCREMENT
name                TEXT NOT NULL
distillery          TEXT (nullable)
first_seen_date     TEXT NOT NULL (ISO 8601)
needs_review        INTEGER DEFAULT 0

-- reviews table (all review data)
review_id           INTEGER PRIMARY KEY AUTOINCREMENT
whiskey_id          INTEGER NOT NULL (foreign key)
source_site         TEXT NOT NULL
source_url          TEXT NOT NULL
normalized_url      TEXT
review_date         TEXT (ISO 8601)
date_scraped        TEXT NOT NULL (ISO 8601)
classification      TEXT (nullable)
company             TEXT (nullable)
proof               TEXT (nullable)
age                 TEXT (nullable)
mashbill            TEXT (nullable)
color               TEXT (nullable)
price               TEXT (nullable)
nose                TEXT (nullable)
palate              TEXT (nullable)
finish              TEXT (nullable)
rating              TEXT (nullable)
overall_notes       TEXT (nullable)
additional_data     TEXT (JSON, nullable)

-- UNIQUE constraint on (source_site, normalized_url) prevents duplicates

-- scraper_runs table (monitoring)
run_id              INTEGER PRIMARY KEY AUTOINCREMENT
source_site         TEXT NOT NULL
run_date            TEXT NOT NULL (ISO 8601)
status              TEXT NOT NULL (success/error/partial)
reviews_found       INTEGER
reviews_added       INTEGER
error_message       TEXT (nullable)
execution_time      REAL (seconds)

-- daily_summaries table (also exists but not needed for historical scrape)
```

---

## Implementation Requirements

### Phase 1: Sitemap Discovery

**File to create:** `sitemap_parser.py`

**Functionality:**
1. Fetch the sitemap from `https://www.breakingbourbon.com/sitemap.xml`
2. Parse the XML to extract all `<loc>` URLs
3. Filter to only URLs containing `/review/`
4. Return a list of review URLs

**Requirements:**
- Use `requests` library for fetching
- Use `xml.etree.ElementTree` for parsing (standard library, no extra dependencies)
- Handle sitemap fetch failures gracefully (retry 3 times with exponential backoff)
- Log the total count of review URLs found

**Expected output:**
```python
def get_all_review_urls() -> list[str]:
    """
    Fetches Breaking Bourbon sitemap and extracts all review URLs.
    
    Returns:
        List of full URLs like ['https://breakingbourbon.com/review/...', ...]
    
    Raises:
        SitemapFetchError: If sitemap cannot be retrieved after retries
    """
```

---

### Phase 2: Duplicate Filtering

**Integration point:** Use existing `database.py` functions

**Functionality:**
1. Take the list of all review URLs from Phase 1
2. Normalize each URL using `database.normalize_url()` 
3. Check against database for existing `normalized_url` in reviews table
4. Return only URLs that are NOT already in the database

**Requirements:**
- Use `database.normalize_url()` for URL normalization
- Use `database.check_duplicate_review()` for duplicate checking
- Batch the database lookups for efficiency (don't query one at a time)

**Efficient batch lookup approach:**
```python
import database

def filter_new_urls(all_urls: list[str]) -> list[str]:
    """
    Filters out URLs that already exist in the database.
    """
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Get all existing normalized URLs for Breaking Bourbon in one query
    cursor.execute("""
        SELECT normalized_url FROM reviews 
        WHERE source_site = 'Breaking Bourbon'
    """)
    existing_urls = {row[0] for row in cursor.fetchall()}
    
    # Filter out URLs that already exist
    new_urls = []
    for url in all_urls:
        normalized = database.normalize_url(url)
        if normalized not in existing_urls:
            new_urls.append(url)
    
    conn.close()
    return new_urls
```

---

### Phase 3: Batch Scraping with Resume Capability

**File to create:** `historical_scraper.py`

**Functionality:**
1. Load list of URLs to scrape (either fresh from sitemap or from progress file)
2. For each URL:
   - Call `BreakingBourbonScraper.scrape_review(url)` to extract review data
   - Save to database using `database.insert_review()`
   - Log success/failure
   - Update progress file
   - Wait for rate limit interval
3. Handle errors gracefully (log and continue, don't stop)
4. Save progress periodically so scraping can resume if interrupted

**Main scraping loop pattern:**
```python
import time
import database
from scrapers.breaking_bourbon import BreakingBourbonScraper

scraper = BreakingBourbonScraper()
conn = database.get_connection()

for url in urls_to_scrape:
    try:
        # Scrape the review
        data = scraper.scrape_review(url)
        
        if data is None:
            # Scraper returned None (parsing failed or page not found)
            log_failure(url, "Scraper returned None")
            continue
        
        # Insert into database
        # insert_review handles duplicate checking internally
        review_id = database.insert_review(conn, data)
        
        if review_id:
            success_count += 1
        else:
            duplicate_count += 1
            
    except Exception as e:
        log_failure(url, str(e))
        
    # Rate limiting (read from config, default 2 seconds)
    time.sleep(rate_limit_seconds)
    
    # Save progress periodically
    if success_count % 10 == 0:
        save_progress()

conn.close()
```

**Requirements:**

#### Rate Limiting
- Default: 2 seconds between requests
- Read from `config.yaml` if available
- If site returns 429 (Too Many Requests): back off exponentially
  - First 429: wait 30 seconds
  - Second 429: wait 60 seconds
  - Third 429: wait 5 minutes
  - Fourth 429: stop and log error

#### Progress Tracking
- Create a progress file: `historical_scrape_progress.json`
- Structure:
```json
{
  "started_at": "2026-01-02T10:00:00Z",
  "last_updated": "2026-01-02T10:25:00Z",
  "total_urls": 1500,
  "completed_urls": 750,
  "failed_urls": ["https://...", "https://..."],
  "status": "in_progress"
}
```
- Update progress file every 10 successful scrapes
- On restart, read progress file and skip already-completed URLs

#### Error Handling

| Error Type | Behavior |
|------------|----------|
| Network timeout | Retry 3 times, then log as failed and continue |
| 404 Not Found | Log as failed (page removed), continue |
| 429 Too Many Requests | Exponential backoff (see above) |
| Parsing error (scraper returns None) | Log as failed with details, continue |
| Database error | Stop immediately (data integrity risk) |
| Keyboard interrupt (Ctrl+C) | Save progress and exit cleanly |

#### Logging
- Log to both console and file: `historical_scrape.log`
- Log levels:
  - INFO: Starting, progress updates (every 50 pages), completion
  - WARNING: Retries, skipped pages, parsing issues
  - ERROR: Failed pages, rate limit hits
- Include timestamp in all log entries

---

### Phase 4: Monitoring and Reporting

**At completion, log a summary:**
```
Historical Scrape Complete
==========================
Started: 2026-01-02 10:00:00
Finished: 2026-01-02 10:52:00
Duration: 52 minutes

URLs in sitemap: [ACTUAL COUNT]
Already in database: [ACTUAL COUNT]
Attempted to scrape: [ACTUAL COUNT]
Successfully scraped: [ACTUAL COUNT]
Failed: [ACTUAL COUNT]
  - 404 errors: [COUNT]
  - Parsing errors: [COUNT]
  - Timeout errors: [COUNT]

Failed URLs saved to: failed_urls.txt
```

**Also create `failed_urls.txt`** with one URL per line for manual review.

**Log the run to database:**
```python
database.log_scraper_run(
    conn,
    source_site="Breaking Bourbon",
    status="success",  # or "partial" if some failed
    reviews_found=total_attempted,
    reviews_added=success_count,
    error_message=None,  # or summary of errors
    execution_time=duration_seconds
)
```

---

## File Structure

After implementation, new files should be:

```
whiskey-scraper/
├── database.py                    # EXISTING - use as-is
├── utils.py                       # EXISTING - use as-is  
├── config.yaml                    # EXISTING - add historical_scrape section
├── scrapers/
│   ├── __init__.py               # EXISTING
│   ├── base_scraper.py           # EXISTING - inherited by BB scraper
│   └── breaking_bourbon.py       # EXISTING - use scrape_review() method
├── sitemap_parser.py              # NEW: Sitemap fetching and parsing
├── historical_scraper.py          # NEW: Main historical scrape orchestrator
├── historical_scrape.log          # GENERATED: Log file
├── historical_scrape_progress.json  # GENERATED: Resume capability
└── failed_urls.txt                # GENERATED: Failed URLs for review
```

---

## Testing Requirements

### Before Running Full Scrape

1. **Test sitemap parser:**
   - Verify it fetches sitemap successfully
   - Verify it extracts correct number of `/review/` URLs
   - Verify URL format is correct

2. **Test duplicate filtering:**
   - Manually add one review to database
   - Verify that URL is filtered out
   - Verify other URLs pass through

3. **Test scraper on sample URLs:**
   - Run on 5-10 different review URLs
   - Include both "IN-DEPTH REVIEW" and "CAPSULE REVIEW" types
   - Verify data is extracted correctly
   - Verify data is saved to database correctly

4. **Test resume capability:**
   - Start a scrape of 20 URLs
   - Interrupt after 10
   - Restart and verify it picks up at URL 11

5. **Test error handling:**
   - Test with a known bad URL (404)
   - Verify it logs error and continues

### Sample Test URLs

Use these for testing (mix of types and content):

```
https://www.breakingbourbon.com/review/eagle-rare-10-year-single-barrel
https://www.breakingbourbon.com/review/bookers-bourbon-2025-03-jerrys-batch
https://www.breakingbourbon.com/review/barrell-bourbon-batch-037
https://www.breakingbourbon.com/review/blantons-single-barrrel
https://www.breakingbourbon.com/review/buffalo-trace-bourbon
https://www.breakingbourbon.com/review/blackfork-farms-gordon-w-legacy-series-edition-iii
https://www.breakingbourbon.com/review/still-austin-blue-corn-bottled-in-bond-bourbon-winter-2025
https://www.breakingbourbon.com/review/remus-gatsby-reserve-bourbon-2025
https://www.breakingbourbon.com/review/rough-rider-the-big-stick-rye
https://www.breakingbourbon.com/review/barrell-bourbon-new-year-2026
```

### Test the Existing Scraper First

Before writing new code, verify the existing scraper still works:

```bash
cd ~/whiskey-scraper
source venv/bin/activate
python -m scrapers.breaking_bourbon
```

This runs the test code at the bottom of `breaking_bourbon.py` which scrapes a sample review.

---

## Success Criteria

The implementation is complete when:

- [ ] Sitemap parser successfully retrieves all `/review/` URLs (verify count matches sitemap)
- [ ] Duplicate filtering correctly identifies existing reviews
- [ ] Scraper processes all URLs with appropriate rate limiting
- [ ] Progress file enables resume after interruption
- [ ] Errors are logged but don't stop the scrape (except database errors)
- [ ] Final report shows counts of success/failure
- [ ] All successfully scraped reviews are queryable in database
- [ ] Code follows existing project patterns and conventions
- [ ] `log_scraper_run()` is called at completion

---

## Configuration

Add these settings to `config.yaml` if not already present:

```yaml
historical_scrape:
  rate_limit_seconds: 2
  max_retries: 3
  retry_backoff_base: 2  # exponential backoff multiplier
  progress_save_interval: 10  # save progress every N successful scrapes
  request_timeout: 30  # seconds
  
  # Backoff for 429 errors (in seconds)
  rate_limit_backoff:
    - 30
    - 60
    - 300
    - -1  # -1 means stop
```

---

## Ethical Scraping Reminders

- **User-Agent:** Use the project's identified user-agent string (from config.yaml)
- **robots.txt:** Breaking Bourbon's robots.txt has been checked - scraping is allowed
- **Rate limiting:** 2 seconds minimum between requests
- **Don't retry aggressively:** If the site is struggling, back off

---

## Running the Historical Scrape

### When to Run

- **Best time:** Off-peak hours (2-5 AM Eastern) to minimize impact on their servers
- **Avoid:** Evenings and weekends when site traffic is likely highest

### Preparing Your Mac

The scrape will take approximately 50 minutes. To prevent interruption:

1. **Prevent sleep:** Go to System Settings → Battery → Options → Prevent automatic sleeping on power adapter (or use `caffeinate` command)
   ```bash
   # Run this before starting the scrape to prevent sleep:
   caffeinate -i -s &
   ```

2. **Keep Terminal open:** Don't close the Terminal window running the scrape

3. **Power:** Make sure your MacBook is plugged in

4. **Network:** Use a stable internet connection (wired or strong WiFi)

### Starting the Scrape

```bash
cd ~/whiskey-scraper
source venv/bin/activate
python historical_scraper.py
```

### If Interrupted

If the scrape stops for any reason (network issue, accidental Ctrl+C, Mac sleep):

1. Check `historical_scrape_progress.json` to see progress
2. Simply re-run `python historical_scraper.py`
3. It will automatically resume from where it left off

---

## Pre-Build Checklist (All Verified ✅)

| Item | Status | Details |
|------|--------|---------|
| Existing scraper tested | ✅ | `scrapers/breaking_bourbon.py` tested on 15 different pages |
| Database location | ✅ | `~/whiskey-scraper/whiskey_reviews.db` |
| Virtual environment | ✅ | Activate with `source venv/bin/activate` |
| Config file | ✅ | `~/whiskey-scraper/config.yaml` exists |
| Scraper file location | ✅ | `scrapers/breaking_bourbon.py` (note: in scrapers subdirectory) |
| Review count | ⏳ | Verify actual count when sitemap is fetched (estimate: ~1,500) |

---

## Code Style Requirements

Match the existing code patterns:

### Imports
```python
# Standard library first
import time
import json
import logging
from datetime import datetime
from pathlib import Path

# Third-party
import requests

# Local imports
import database
from scrapers.breaking_bourbon import BreakingBourbonScraper
```

### Logging Setup
```python
import logging

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('historical_scrape.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
```

### Error Handling Pattern
```python
try:
    data = scraper.scrape_review(url)
    if data is None:
        logger.warning(f"Failed to parse: {url}")
        failed_urls.append(url)
        continue
    
    review_id = database.insert_review(conn, data)
    if review_id:
        logger.info(f"Added: {data.get('name', 'Unknown')}")
        success_count += 1
    else:
        logger.debug(f"Duplicate skipped: {url}")
        
except sqlite3.Error as e:
    # Database errors are critical - stop immediately
    logger.critical(f"Database error: {e}")
    save_progress()
    raise
    
except requests.RequestException as e:
    # Network errors - log and continue
    logger.error(f"Network error for {url}: {e}")
    failed_urls.append(url)
    continue
```

---

## Notes for the Implementing Agent

- **Read existing code first** before writing new code
- **Match existing code style** (naming conventions, error handling patterns, docstrings)
- **Don't duplicate functionality** - use existing functions from database.py and utils.py
- **Scraper is in subdirectory** - import as `from scrapers.breaking_bourbon import BreakingBourbonScraper`
- **Test incrementally** - don't run 1,500 URLs without testing on 10 first
- **The scraper's `scrape_review()` method returns data ready for `insert_review()`** - keys are already mapped correctly
- **Use `database.get_connection()`** to get database connection, not direct sqlite3 calls
