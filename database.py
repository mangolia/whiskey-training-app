"""
Database module for whiskey review scraper.
Handles all database operations and schema creation.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Database file location
# Use project directory for portability
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "databases" / "whiskey_reviews.db"


# ============================================================================
# UTILITY FUNCTIONS - Data Normalization
# ============================================================================

def normalize_url(url):
    """
    Normalize a URL for duplicate detection.
    
    Steps:
    1. Convert to lowercase
    2. Strip common tracking parameters
    3. Remove trailing slashes
    4. Sort remaining query parameters
    
    Args:
        url (str): The URL to normalize
        
    Returns:
        str: Normalized URL, or None if input is invalid
    """
    if not url or not isinstance(url, str):
        return None
    
    # Parse the URL into components
    parsed = urlparse(url.lower().strip())
    
    # Tracking parameters to remove
    tracking_params = {
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'ref', 'source', 'fbclid', 'gclid', 'mc_cid', 'mc_eid'
    }
    
    # Parse query parameters
    query_params = parse_qs(parsed.query)
    
    # Remove tracking parameters
    cleaned_params = {
        key: value 
        for key, value in query_params.items() 
        if key not in tracking_params
    }
    
    # Sort parameters alphabetically and rebuild query string
    if cleaned_params:
        sorted_query = urlencode(sorted(cleaned_params.items()), doseq=True)
    else:
        sorted_query = ''
    
    # Remove trailing slash from path
    clean_path = parsed.path.rstrip('/')
    
    # Rebuild URL
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        clean_path,
        parsed.params,
        sorted_query,
        ''  # Remove fragment
    ))
    
    return normalized


def normalize_string(text):
    """
    Normalize a string for consistent matching.
    
    Steps:
    1. Convert to lowercase
    2. Strip leading/trailing whitespace
    3. Collapse multiple spaces to single space
    4. Return None if empty
    
    Args:
        text (str): The string to normalize
        
    Returns:
        str or None: Normalized string, or None if empty/invalid
    """
    if not text or not isinstance(text, str):
        return None
    
    # Convert to lowercase and strip whitespace
    normalized = text.lower().strip()
    
    # Collapse multiple spaces to single space
    normalized = ' '.join(normalized.split())
    
    # Return None if empty string
    return normalized if normalized else None


def parse_date(date_string):
    """
    Parse various date formats into ISO 8601 format.
    
    Handles formats like:
    - "Nov 15, 2024"
    - "2024-11-15"
    - "15/11/2024"
    
    Args:
        date_string (str): The date string to parse
        
    Returns:
        str or None: ISO 8601 formatted date (YYYY-MM-DD HH:MM:SS), or None if parsing fails
    """
    if not date_string or not isinstance(date_string, str):
        return None
    
    try:
        # Try to parse the date (dateutil will handle multiple formats)
        # Note: We'll need to install python-dateutil package
        from dateutil import parser
        parsed_date = parser.parse(date_string)
        
        # Return in ISO 8601 format
        return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        # If parsing fails, return None
        return None


def get_current_timestamp():
    """
    Get current UTC timestamp in ISO 8601 format.
    
    Returns:
        str: Current UTC time as 'YYYY-MM-DD HH:MM:SS'
    """
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


# ============================================================================
# DATABASE OPERATION FUNCTIONS
# ============================================================================

def find_whiskey(conn, name, distillery=None):
    """
    Find a whiskey in the database by name and distillery.
    
    Uses normalized (lowercase, trimmed) matching for consistency.
    
    Args:
        conn: Database connection
        name (str): Whiskey name
        distillery (str, optional): Distillery name
        
    Returns:
        int or None: whiskey_id if found, None if not found
    """
    cursor = conn.cursor()
    
    # Normalize inputs for consistent matching
    normalized_name = normalize_string(name)
    normalized_distillery = normalize_string(distillery)
    
    if not normalized_name:
        return None
    
    # Query with normalized values
    cursor.execute("""
        SELECT whiskey_id 
        FROM whiskeys 
        WHERE LOWER(name) = ? AND LOWER(COALESCE(distillery, '')) = ?
    """, (normalized_name, normalized_distillery or ''))
    
    result = cursor.fetchone()
    return result[0] if result else None


def insert_whiskey(conn, name, distillery=None):
    """
    Insert a new whiskey into the database.
    
    Args:
        conn: Database connection
        name (str): Whiskey name (required)
        distillery (str, optional): Distillery name
        
    Returns:
        int: The whiskey_id of the newly inserted whiskey
    """
    cursor = conn.cursor()
    
    # Normalize inputs
    normalized_name = normalize_string(name)
    normalized_distillery = normalize_string(distillery)
    
    if not normalized_name:
        raise ValueError("Whiskey name cannot be empty")
    
    # Get current timestamp
    first_seen = get_current_timestamp()
    
    # Insert new whiskey
    cursor.execute("""
        INSERT INTO whiskeys (name, distillery, first_seen_date, needs_review)
        VALUES (?, ?, ?, 0)
    """, (normalized_name, normalized_distillery, first_seen))
    
    conn.commit()
    
    # Return the new whiskey_id
    return cursor.lastrowid


def check_duplicate_review(conn, source_site, normalized_url):
    """
    Check if a review already exists in the database.
    
    Args:
        conn: Database connection
        source_site (str): Name of the review website
        normalized_url (str): Normalized URL of the review
        
    Returns:
        bool: True if review exists (duplicate), False if new
    """
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT review_id 
        FROM reviews 
        WHERE source_site = ? AND normalized_url = ?
    """, (source_site, normalized_url))
    
    result = cursor.fetchone()
    return result is not None


def insert_review(conn, review_data):
    """
    Insert a new review into the database.
    
    Handles whiskey matching/creation and duplicate detection automatically.
    
    Args:
        conn: Database connection
        review_data (dict): Dictionary containing review information
            Required keys:
                - name: Whiskey name
                - source_site: Website name (e.g., "Breaking Bourbon")
                - source_url: Original review URL
            Optional keys:
                - distillery, classification, company, proof, age, mashbill,
                  color, price, nose, palate, finish, rating, overall_notes,
                  review_date, additional_data
                  
    Returns:
        int or None: review_id if inserted, None if duplicate
    """
    cursor = conn.cursor()
    
    # Extract required fields
    name = review_data.get('name')
    source_site = review_data.get('source_site')
    source_url = review_data.get('source_url')
    
    if not all([name, source_site, source_url]):
        raise ValueError("Missing required fields: name, source_site, source_url")
    
    # Normalize URL for duplicate detection
    normalized_url = normalize_url(source_url)
    
    # Check for duplicate review
    if check_duplicate_review(conn, source_site, normalized_url):
        print(f"  ⊘ Duplicate review skipped: {source_url}")
        return None
    
    # Find or create whiskey
    distillery = review_data.get('distillery')
    whiskey_id = find_whiskey(conn, name, distillery)
    
    if whiskey_id is None:
        # Whiskey doesn't exist, create it
        whiskey_id = insert_whiskey(conn, name, distillery)
        print(f"  + Created new whiskey: {name}")
    
    # Get current timestamp for date_scraped
    date_scraped = get_current_timestamp()
    
    # Parse review_date if provided
    review_date = review_data.get('review_date')
    if review_date:
        review_date = parse_date(review_date)
    
    # Insert review
    cursor.execute("""
        INSERT INTO reviews (
            whiskey_id, source_site, source_url, normalized_url,
            review_date, date_scraped,
            classification, company, proof, age, mashbill, color, price,
            nose, palate, finish, rating, overall_notes, additional_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        whiskey_id,
        source_site,
        source_url,
        normalized_url,
        review_date,
        date_scraped,
        review_data.get('classification'),
        review_data.get('company'),
        review_data.get('proof'),
        review_data.get('age'),
        review_data.get('mashbill'),
        review_data.get('color'),
        review_data.get('price'),
        review_data.get('nose'),
        review_data.get('palate'),
        review_data.get('finish'),
        review_data.get('rating'),
        review_data.get('overall_notes'),
        review_data.get('additional_data')
    ))
    
    conn.commit()
    
    print(f"  ✓ Added review: {name} from {source_site}")
    return cursor.lastrowid


def log_scraper_run(conn, source_site, status, reviews_found=0, reviews_added=0, 
                     error_message=None, execution_time=None):
    """
    Log a scraper run to the scraper_runs table.
    
    Args:
        conn: Database connection
        source_site (str): Name of the source site
        status (str): Status of the run ('success', 'error', 'partial')
        reviews_found (int): Number of reviews found
        reviews_added (int): Number of reviews successfully added
        error_message (str, optional): Error message if run failed
        execution_time (float, optional): Execution time in seconds
        
    Returns:
        int: The run_id of the logged run
    """
    cursor = conn.cursor()
    run_date = get_current_timestamp()
    
    cursor.execute("""
        INSERT INTO scraper_runs (
            source_site, run_date, status, reviews_found, reviews_added,
            error_message, execution_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (source_site, run_date, status, reviews_found, reviews_added,
          error_message, execution_time))
    
    conn.commit()
    return cursor.lastrowid


def get_daily_reports(conn, source_site=None, days=7, limit=50):
    """
    Retrieve daily scraper run reports from the database.
    
    Args:
        conn: Database connection
        source_site (str, optional): Filter by source site name
        days (int): Number of days to look back (default: 7)
        limit (int): Maximum number of records to return (default: 50)
        
    Returns:
        list: List of dictionaries with run information
    """
    cursor = conn.cursor()
    
    # Calculate cutoff date
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    
    if source_site:
        cursor.execute("""
            SELECT run_id, source_site, run_date, status, reviews_found, 
                   reviews_added, error_message, execution_time
            FROM scraper_runs
            WHERE source_site = ? AND run_date >= ?
            ORDER BY run_date DESC
            LIMIT ?
        """, (source_site, cutoff_date, limit))
    else:
        cursor.execute("""
            SELECT run_id, source_site, run_date, status, reviews_found, 
                   reviews_added, error_message, execution_time
            FROM scraper_runs
            WHERE run_date >= ?
            ORDER BY run_date DESC
            LIMIT ?
        """, (cutoff_date, limit))
    
    rows = cursor.fetchall()
    
    # Convert to list of dictionaries
    reports = []
    for row in rows:
        reports.append({
            'run_id': row[0],
            'source_site': row[1],
            'run_date': row[2],
            'status': row[3],
            'reviews_found': row[4],
            'reviews_added': row[5],
            'error_message': row[6],
            'execution_time': row[7]
        })
    
    return reports


# ============================================================================
# DATABASE SCHEMA CREATION
# ============================================================================

def get_connection():
    """
    Create and return a connection to the SQLite database.
    Creates the database file if it doesn't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    # Ensure UTF-8 encoding for text operations
    conn.execute("PRAGMA encoding = 'UTF-8'")
    return conn


def create_whiskeys_table(conn):
    """
    Create the whiskeys table (master index of all whiskeys).
    """
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS whiskeys (
            whiskey_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            distillery TEXT,
            first_seen_date TEXT NOT NULL,
            needs_review INTEGER DEFAULT 0
        )
    """)
    
    # Create index on name for fast searching
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_whiskeys_name 
        ON whiskeys(name)
    """)
    
    conn.commit()
    print("✓ Created whiskeys table")


def create_reviews_table(conn):
    """
    Create the reviews table (all review data from all sites).
    """
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            whiskey_id INTEGER NOT NULL,
            source_site TEXT NOT NULL,
            source_url TEXT NOT NULL,
            normalized_url TEXT,
            review_date TEXT,
            date_scraped TEXT NOT NULL,
            
            -- Review details (all nullable)
            classification TEXT,
            company TEXT,
            proof TEXT,
            age TEXT,
            mashbill TEXT,
            color TEXT,
            price TEXT,
            nose TEXT,
            palate TEXT,
            finish TEXT,
            rating TEXT,
            overall_notes TEXT,
            additional_data TEXT,
            
            FOREIGN KEY (whiskey_id) REFERENCES whiskeys(whiskey_id)
        )
    """)
    
    # Create indexes for performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reviews_whiskey_id 
        ON reviews(whiskey_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reviews_source_site 
        ON reviews(source_site)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reviews_normalized_url 
        ON reviews(normalized_url)
    """)
    
    # Prevent exact duplicate reviews
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_reviews_unique 
        ON reviews(source_site, normalized_url)
    """)
    
    conn.commit()
    print("✓ Created reviews table")


def create_scraper_runs_table(conn):
    """
    Create the scraper_runs table (monitoring and debugging).
    """
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraper_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_site TEXT NOT NULL,
            run_date TEXT NOT NULL,
            status TEXT NOT NULL,
            reviews_found INTEGER,
            reviews_added INTEGER,
            error_message TEXT,
            execution_time REAL
        )
    """)
    
    conn.commit()
    print("✓ Created scraper_runs table")


def create_daily_summaries_table(conn):
    """
    Create the daily_summaries table for daily run summaries.
    """
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_summaries (
            summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_date TEXT NOT NULL,
            total_reviews_found INTEGER DEFAULT 0,
            total_reviews_added INTEGER DEFAULT 0,
            total_duplicates INTEGER DEFAULT 0,
            total_errors INTEGER DEFAULT 0,
            sites_checked TEXT,
            execution_time REAL,
            status TEXT NOT NULL,
            summary_text TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(summary_date)
        )
    """)
    
    # Create index on date for fast queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_daily_summaries_date 
        ON daily_summaries(summary_date)
    """)
    
    conn.commit()
    print("✓ Created daily_summaries table")


def detect_missed_days(conn, source_site: str = "Breaking Bourbon", lookback_days: int = 30) -> List[str]:
    """
    Detect dates where scraper should have run but didn't.
    
    Checks daily_summaries table for gaps and returns list of missing dates.
    Important: A date with a summary entry (even with total_reviews_found = 0) 
    means the scraper ran - NOT a missed day. Only dates with NO summary entry 
    are considered "missed".
    
    Args:
        conn: Database connection
        source_site: Source site to check (not currently used, but kept for future multi-site support)
        lookback_days: How many days back to check (default: 30)
    
    Returns:
        List of date strings in YYYY-MM-DD format for missing days
    """
    cursor = conn.cursor()
    
    # Calculate the date range to check
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    
    # Get all dates that have summaries (any summary means scraper ran)
    cursor.execute("""
        SELECT DISTINCT summary_date 
        FROM daily_summaries 
        WHERE summary_date >= ? AND summary_date <= ?
        ORDER BY summary_date
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    existing_dates = {row[0] for row in cursor.fetchall()}
    
    # Generate list of all dates in the range
    all_dates = []
    current_date = start_date
    while current_date <= end_date:
        all_dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    # Find missing dates (dates without summaries)
    missed_dates = [date for date in all_dates if date not in existing_dates]
    
    return missed_dates


def insert_daily_summary(conn, summary_date, total_reviews_found=0, total_reviews_added=0,
                         total_duplicates=0, total_errors=0, sites_checked=None,
                         execution_time=None, status='success', summary_text=None):
    """
    Insert or update a daily summary.
    
    Args:
        conn: Database connection
        summary_date: Date string (YYYY-MM-DD)
        total_reviews_found: Total reviews found
        total_reviews_added: Total reviews added
        total_duplicates: Total duplicates
        total_errors: Total errors
        sites_checked: Comma-separated list of sites checked
        execution_time: Total execution time in seconds
        status: Overall status (success, partial, error)
        summary_text: Text summary
        
    Returns:
        int: summary_id
    """
    cursor = conn.cursor()
    created_at = get_current_timestamp()
    
    # Check if summary for this date already exists
    cursor.execute("SELECT summary_id FROM daily_summaries WHERE summary_date = ?", (summary_date,))
    existing = cursor.fetchone()
    
    if existing:
        # Update existing summary
        cursor.execute("""
            UPDATE daily_summaries 
            SET total_reviews_found = ?, total_reviews_added = ?, total_duplicates = ?,
                total_errors = ?, sites_checked = ?, execution_time = ?, status = ?,
                summary_text = ?
            WHERE summary_date = ?
        """, (total_reviews_found, total_reviews_added, total_duplicates,
              total_errors, sites_checked, execution_time, status, summary_text, summary_date))
        summary_id = existing[0]
    else:
        # Insert new summary
        cursor.execute("""
            INSERT INTO daily_summaries (
                summary_date, total_reviews_found, total_reviews_added,
                total_duplicates, total_errors, sites_checked, execution_time,
                status, summary_text, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (summary_date, total_reviews_found, total_reviews_added,
              total_duplicates, total_errors, sites_checked, execution_time,
              status, summary_text, created_at))
        summary_id = cursor.lastrowid
    
    conn.commit()
    return summary_id


def create_database():
    """
    Create the complete database schema.
    Safe to run multiple times.
    """
    print(f"Creating database at: {DB_PATH}")
    
    # Create the directory if it doesn't exist
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database (creates file if doesn't exist)
    conn = get_connection()
    
    # Create all tables
    create_whiskeys_table(conn)
    create_reviews_table(conn)
    create_scraper_runs_table(conn)
    create_daily_summaries_table(conn)
    
    # Close connection
    conn.close()
    
    print(f"\n✓ Database created successfully!")
    print(f"Location: {DB_PATH}")


if __name__ == "__main__":
    # This runs when you execute the script directly
    create_database()