# Daily Scraper Automation Plan

## Overview
Automate the Breaking Bourbon scraper to run daily at 11pm EST, with error handling, logging, and dashboard integration.

---

## 1. Scheduling: macOS launchd

### What is launchd?
`launchd` is macOS's system and service management framework. It's the modern replacement for cron and handles:
- **Launch Agents**: Run for logged-in users (what we need)
- **Launch Daemons**: Run as system services (root level)

**Advantages over cron:**
- ✅ Better integration with macOS (sleep/wake handling)
- ✅ Automatic retry on failure
- ✅ Can wake computer from sleep
- ✅ Better logging integration
- ✅ More reliable scheduling

**How it works:**
- Create a `.plist` (property list) file describing the job
- Place it in `~/Library/LaunchAgents/`
- Load it with `launchctl load`
- The system manages execution automatically

**Wake from sleep:**
- `launchd` can wake the Mac from sleep to run scheduled tasks
- Requires `StartCalendarInterval` with `Wake` key
- Mac must be plugged into power (battery limitation)
- May need "Prevent automatic sleeping" setting

---

## 2. Time Zone: 11pm EST

**Decision:** Schedule for 11pm Eastern Standard Time (EST)

**Implementation:**
- Use `StartCalendarInterval` with hour=23 (11pm)
- Handle EST/EDT automatically (EST = UTC-5, EDT = UTC-4)
- Consider: Should we use system timezone or hardcode EST?

**Open Question:**
- Do you want it to automatically adjust for Daylight Saving Time (EDT in summer)?
  - Option A: Always 11pm EST (UTC-5) - doesn't change with DST
  - Option B: Always 11pm local Eastern time (EST/EDT) - adjusts with DST
  - **Recommendation:** Option B (11pm Eastern time, adjusts for DST)
  - **Decision** Use option B

---

## 3. Wake from Sleep

**Decision:** Enable wake-from-sleep functionality

**Requirements:**
- Mac must be plugged into power (Apple limitation)
- `Wake` key in launchd plist
- May need to adjust Energy Saver settings

**Implementation:**
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>23</integer>
    <key>Minute</key>
    <integer>0</integer>
    <key>Wake</key>
    <true/>
</dict>
```

**Open Questions:**
1. What should happen if Mac is on battery when 11pm arrives?
   - Skip the run?
   - Wait until plugged in?
   - Run anyway (won't wake from sleep, but will run when awake)?
   - **Decision** don't run, log a notification on the dashboard and allow manual run when the conputer wakes from the dashboard

2. Should we add a "maximum delay" - if Mac wakes up late, should it still run?
   - Example: If Mac wakes at 11:30pm, should it run or skip?
   - **Decision** no create the notification for a manual run

---

## 4. Dashboard Error Section

**Decision:** Add error tracking section to dashboard

**Recommended Statuses to Track:**

### Error Status Categories:
1. **Success** ✅
   - Scraper ran successfully
   - All reviews processed

2. **Partial Success** ⚠️
   - Scraper ran but some reviews failed
   - Some errors encountered

3. **Failed** ❌
   - Scraper failed to run
   - Network errors, site down, etc.

4. **Skipped** ⊘
   - Run skipped (battery, system issue, etc.)

### Error Details to Show:
- **Error Type**: Network error, parsing error, database error, etc.
- **Error Message**: Specific error description
- **Affected Reviews**: Which reviews failed (if partial)
- **Retry Status**: How many retries attempted
- **Timestamp**: When error occurred

**Open Questions:**
1. How far back should we show errors?
   - Last 7 days?
   - Last 30 days?
   - All time?
   - **Decision** last 30 days

2. Should we show a "trend" (errors increasing/decreasing)?
 - **Decision** no trending

3. Do you want error notifications separate from the dashboard?
   - Email alerts for critical errors?
   - Desktop notifications?
   - **Decision** no separate notifications 

---

## 5. Retry Logic: 3 Attempts

**Decision:** Retry failed runs up to 3 times before logging error

**Implementation Strategy:**
- Attempt 1: Initial run
- Attempt 2: Wait 5 minutes, retry
- Attempt 3: Wait 10 minutes, retry
- After 3 failures: Log error, mark as failed

**Open Questions:**
1. **Retry delay strategy:**
   - Fixed delays (5 min, 10 min)?
   - Exponential backoff (5 min, 15 min, 30 min)?
   - **Decision** Exponential backoff

2. **What constitutes a "failure" to retry?**
   - Network timeout? (yes, retry)
   - Site returns 404? (no, don't retry - permanent error)
   - Parsing error? (maybe - could be temporary HTML change)
   - Database error? (yes, retry)

3. **Should retries happen within the same "run" or as separate scheduled runs?**
   - **Decision** Within same run (retry immediately, not next day)

---

## 6. Logging Strategy

**Decision:** Log both successes and errors

**Recommended Log Structure:**

### Log Files:
1. **`logs/scraper.log`** - Main activity log (all runs)
   - Format: Timestamp, Level, Message
   - Rotate daily or when > 10MB

2. **`logs/errors.log`** - Error-only log
   - Only errors and warnings
   - Easier to review issues

3. **`logs/daily_summary.log`** - Daily summary
   - One entry per day
   - Quick overview

### Log Levels:
- **INFO**: Normal operations (run started, reviews found, etc.)
- **SUCCESS**: Successful completion
- **WARNING**: Non-critical issues (duplicates, minor errors)
- **ERROR**: Failures that need attention
- **CRITICAL**: System-level failures

**Open Questions:**
1. **Log retention:**
   - Keep logs for how long? (30 days? 90 days? Forever?)
   - **Decision:** 90 days, archive older ✅

2. **Log rotation:**
   - Daily rotation? (`scraper-2025-12-30.log`)
   - Size-based rotation? (when file > 10MB)
   - **Decision:** Daily rotation ✅

3. **Log format:**
   - Plain text?
   - JSON (easier to parse later)?
   - **Decision:** Plain text with structured format ✅

---

## 7. Dashboard Architecture

**Decision:** Build a mini web application instead of regenerating HTML

### Current Approach (Regenerate HTML):
- ❌ Static file, must regenerate
- ❌ No real-time updates
- ❌ No interactivity

### Proposed Approach (Web App):

**Option A: Simple Flask App** (Recommended for start)
- Lightweight Python web framework
- Serves dashboard from database
- Can add API endpoints later
- Easy to run locally

**Option B: Static Site Generator**
- Generate HTML from template + data
- Still static but more maintainable
- Could add auto-refresh JavaScript

**Option C: Full Web Framework**
- Overkill for now, but scalable

**Decision:** Start with **Option A (Flask)** - simple, flexible, can expand

**Open Questions:**
1. **How should the web app run?**
   - Manual start (`python app.py`)?
   - Auto-start with system?
   - Always running in background?
   - **Need Decision**

2. **What port?**
   - Default Flask (5000)?
   - Custom port (8080, 3000)?
   - **Suggestion:** Use default 5000, make configurable

3. **Access:**
   - Localhost only (127.0.0.1)?
   - Network accessible?
   - **Decision:** Localhost only for security ✅

4. **Features needed:**
   - Real-time updates (auto-refresh)?
   - Filtering/search?
   - Export data?
   - Historical charts?
   - **Suggestion:** Start with auto-refresh, add others later

---

## 8. Virtual Environment Handling

**Decision:** Auto-activate venv in the launchd script

**Implementation:**
- Use full path to venv's Python: `/Users/michaelangolia/whiskey-scraper/venv/bin/python`
- Or create wrapper script that activates venv

**Open Questions:**
1. **Which approach?**
   - Direct venv Python path (simpler)
   - Wrapper script (more flexible)
   - **Decision:** Direct path (simpler, more reliable)

2. **What if venv path changes?**
   - Use relative paths?
   - Use environment variables?
   - **Decision:** Use absolute path in config file

---

## 9. Dependency Checking

**Decision:** Ensure dependencies are installed before running

**Implementation Options:**
1. **Check on each run:**
   - Quick import test
   - Install if missing (slow)

2. **Check on setup:**
   - Verify during installation
   - Fail fast if missing

3. **Hybrid:**
   - Check on setup
   - Verify on each run (don't auto-install, just warn)

**Decision:** Hybrid - verify on each run, log warning if missing, don't auto-install (security)

**Open Questions:**
1. Should we auto-install missing dependencies?
   - **Decision** No - log error, require manual install

2. Which dependencies to check?
   - All in requirements.txt?
   - Just critical ones (requests, beautifulsoup4)?
   - **Decision** check all requirements

---

## 10. Daily Summary

**Decision:** Generate daily summary and add to dashboard

**Summary Content:**
- Date
- Total reviews found
- Reviews added
- Duplicates found
- Errors encountered
- Execution time
- Source sites checked

**Open Questions:**
1. **Where to store summaries?**
   - Database table (`daily_summaries`)?
   - JSON file?
   - **Decision:** Database table (queryable, persistent)

2. **Summary format:**
   - Text summary?
   - Structured data (JSON)?
   - **Decision:** Both\

3. **Dashboard display:**
   - Show last 7 days?
   - Last 30 days?
   - All time with pagination?
   - **Suggestion:** Last 30 days with option to view more

---

## 11. Multi-Site Support

**Decision:** Plan for multiple scrapers, same schedule

**Architecture:**
- Config file lists enabled scrapers
- Runner script iterates through all enabled scrapers
- Each scraper runs sequentially (or parallel?)
- Unified logging and reporting

**Open Questions:**
1. **Execution:**
   - Run scrapers sequentially (one after another)?
   - Run in parallel?
   - **Decision** Sequential (simpler, less resource intensive, easier to debug)

2. **Error handling:**
   - If one scraper fails, continue with others?
   - **Decision** Yes, continue with others

3. **Timing:**
   - All at 11pm?
   - Staggered (11pm, 11:15pm, 11:30pm)?
   - **Decision** All at 11pm (simpler)

---

## 12. Configuration File

**Decision:** Create config file for settings

**Config Structure:**
```yaml
# config.yaml
schedule:
  hour: 23
  minute: 0
  timezone: "America/New_York"  # Handles EST/EDT automatically
  
scrapers:
  enabled:
    - breaking_bourbon
  # Future: - whiskey_advocate
  # Future: - bourbon_banter

logging:
  level: "INFO"
  retention_days: 90
  log_dir: "logs"

retry:
  max_attempts: 3
  delay_seconds: [300, 900, 1800]  # 5min, 15min, 30min

dashboard:
  port: 5000
  host: "127.0.0.1"
```

**Open Questions:**
1. **Config format:**
   - YAML (human-readable)?
   - JSON (simple)?
   - INI (simple)?
   - **Decision** YAML (most readable)

2. **Config location:**
   - `config.yaml` in project root?
   - `~/.whiskey-scraper/config.yaml`?
   - **Decision** Project root (easier to version control)

3. **Default values:**
   - Provide defaults if config missing?
   - Fail if config missing?
   - **Decision** Sensible defaults, warn if config missing

---

## Implementation Phases

### Phase 1: Core Automation
- [ ] Create config file
- [ ] Create wrapper script for daily_check.py
- [ ] Create launchd plist
- [ ] Test scheduling

### Phase 2: Error Handling & Logging
- [ ] Implement retry logic
- [ ] Set up logging system
- [ ] Create error tracking

### Phase 3: Dashboard Enhancement
- [ ] Convert to Flask web app
- [ ] Add error section
- [ ] Add daily summary section
- [ ] Real-time updates

### Phase 4: Multi-Site Support
- [ ] Refactor for multiple scrapers
- [ ] Update config structure
- [ ] Test with multiple sites

---

## Open Questions Summary

**Need Your Input:**
1. EST/EDT handling - auto-adjust for DST? (Recommendation: Yes)
2. Battery behavior - skip or wait? (Recommendation: Skip, log warning)
3. Error history - how many days? (Recommendation: 30 days)
4. Dashboard - Flask app or keep static? (Recommendation: Flask)
5. Dashboard access - localhost only? (Recommendation: Yes)
6. Log retention - how long? (Recommendation: 90 days)
7. Scraper execution - sequential or parallel? (Recommendation: Sequential)

---

## Decisions Summary

All decisions have been made and are marked with ✅ throughout this document. Key decisions:

1. ✅ **Time Zone:** Use Option B - 11pm Eastern time (auto-adjusts for DST)
2. ✅ **Battery Behavior:** Don't run on battery, log notification, allow manual run from dashboard
3. ✅ **Late Wake:** Don't auto-run if late, create notification for manual run
4. ✅ **Error History:** Show last 30 days
5. ✅ **Error Trending:** No trending display
6. ✅ **Error Notifications:** No separate notifications (dashboard only)
7. ✅ **Retry Strategy:** Exponential backoff (5min, 15min, 30min)
8. ✅ **Retry Timing:** Within same run (immediate retries)
9. ✅ **Dashboard:** Flask web application
10. ✅ **Venv Handling:** Direct venv Python path (absolute path in config)
11. ✅ **Dependency Checking:** Hybrid - verify on each run, warn if missing, don't auto-install
12. ✅ **Daily Summary:** Store in database table, both text and structured format
13. ✅ **Multi-Site Execution:** Sequential (one after another)
14. ✅ **Multi-Site Error Handling:** Continue with other scrapers if one fails
15. ✅ **Multi-Site Timing:** All at 11pm
16. ✅ **Config Format:** YAML
17. ✅ **Config Location:** Project root
18. ✅ **Config Defaults:** Sensible defaults, warn if config missing
19. ✅ **Log Retention:** 90 days, archive older
20. ✅ **Log Rotation:** Daily rotation
21. ✅ **Log Format:** Plain text with structured format
22. ✅ **Dashboard Access:** Localhost only (127.0.0.1)

---

## Remaining Open Questions & Suggestions

### 1. Flask Dashboard - How to Run? ⚠️
**Question:** How should the Flask web app run?
- **Option A:** Manual start (`python app.py`) - User starts when needed
- **Option B:** Auto-start with system (via launchd) - Always available
- **Option C:** Always running in background - Most convenient

**Suggestion:** 
- Start with **Option A** (manual start) for simplicity
- Can upgrade to Option B later if desired
- Option C might be overkill for local-only dashboard

**Decision** Option A - manual start is fine for a local dashboard

---

### 2. Flask Dashboard - Port Selection
**Question:** What port should Flask use?
- Default Flask port: 5000
- Alternative: 8080, 3000, or custom

**Suggestion:** 
- Use default port 5000 (standard Flask port)
- Make it configurable in `config.yaml` so it can be changed if needed
- Check if port is in use and suggest alternative if conflict

**Decision** Port 5000, configurable ✅

---

### 3. Flask Dashboard - Features Priority
**Question:** Which features should be implemented first?
- Auto-refresh (dashboard updates every 30 seconds)
- Manual "Run Scraper Now" button
- Filtering/search functionality
- Export data (CSV/JSON)
- Historical charts/graphs

**Suggestion:**
- **Phase 1 (MVP):** Auto-refresh + Manual run button
- **Phase 2:** Error section with details
- **Phase 3:** Filtering and search
- **Phase 4:** Charts and export

**Decision** Start with Phase 1, add features incrementally

---

### 4. Daily Summary - Dashboard Display
**Question:** How should daily summaries be displayed on dashboard?
- Show last 7 days?
- Show last 30 days?
- All time with pagination?
- Date range selector?

**Suggestion:**
- Default: Last 30 days (matches error history)
- Add "Show More" button to view older summaries
- Consider date range picker for Phase 2

**Decision** Last 30 days default, expandable ✅

---

### 5. Retry Logic - Failure Types
**Question:** What types of failures should trigger retries?
- Network timeout? → **Retry** ✅
- Site returns 404? → **Don't retry** (permanent error)
- Parsing error? → **Maybe retry** (could be temporary HTML change)
- Database error? → **Retry** ✅

**Suggestion:**
- **Retry:** Network errors, timeouts, database errors
- **Don't Retry:** 404 errors, authentication errors, invalid URLs
- **Maybe Retry:** Parsing errors (retry once, then log as warning)

**Decision** Implement smart retry logic based on error type

---

### 6. Battery Detection & Notification
**Question:** How should we detect battery state and create notifications?
- Use macOS `pmset` command to check battery/AC power?
- Create notification in database for dashboard display?
- Format for manual run button?

**Suggestion:**
- Check power state before scheduled run
- If on battery: Skip run, log to `scraper_runs` with status="skipped"
- Add notification to dashboard: "Scheduled run skipped (on battery) - Click to run manually"
- Manual run button should work regardless of battery state

**Decision** Implement battery check, skip gracefully, enable manual override

---

### 7. Manual Run from Dashboard
**Question:** How should manual run work from Flask dashboard?
- Run synchronously (user waits for completion)?
- Run asynchronously (background job, show progress)?
- Show real-time updates?

**Decision**
- Start with synchronous (simpler)
- Show progress messages in real-time using Flask's streaming response
- Can upgrade to async/background jobs later if needed

---

### 8. Error Details - What to Show
**Question:** What level of error detail should be displayed?
- Full stack traces?
- User-friendly error messages?
- Both (collapsible details)?

**Suggestion:**
- User-friendly message by default
- "Show Details" button to expand full error/stack trace
- Keep technical details available but not overwhelming

**Decison** User-friendly with expandable details

---

## Ready to Proceed? ✅

All major decisions have been made. The remaining questions are implementation details that can be decided during development or have reasonable defaults.

**Suggested Approach:**
1. Start with sensible defaults for open questions
2. Implement core functionality first
3. Refine based on usage and feedback

**Next Steps:**
1. Create config.yaml with all decided settings
2. Implement Phase 1: Core Automation
3. Build Flask dashboard with basic features
4. Add error handling and logging
5. Test and refine

**Ready to begin implementation!** 🚀
