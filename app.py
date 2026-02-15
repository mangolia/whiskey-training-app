#!/usr/bin/env python3
"""
Flask API for Whiskey Sensory Training App
Provides search and quiz generation endpoints
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from pathlib import Path
import random
import re
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Determine environment
DEBUG = os.getenv('FLASK_ENV') == 'development'
IS_PRODUCTION = not DEBUG

# Configure CORS with environment-specific origins
if DEBUG:
    ALLOWED_ORIGINS = [
        'http://localhost:5173',  # Development frontend
        'http://localhost:5001',  # Local testing
        'http://localhost:3000',  # Alternative dev port
    ]
else:
    ALLOWED_ORIGINS = [
        os.getenv('FRONTEND_URL', 'https://whiskey-training-app.vercel.app'),
    ]

CORS(app, origins=ALLOWED_ORIGINS)
logger.info(f"Environment: {'Development' if DEBUG else 'Production'}")
logger.info(f"CORS enabled for origins: {ALLOWED_ORIGINS}")

# ============================================================================
# Security Headers Middleware
# ============================================================================

@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Only enforce HSTS in production
    if IS_PRODUCTION:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    return response

# Database path
DB_PATH = Path(__file__).parent / "databases" / "whiskey_production.db"

# ============================================================================
# Database Helper Functions
# ============================================================================

def get_db_connection():
    """Create database connection with context manager support"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return dict(zip(row.keys(), row))

# ============================================================================
# Utility Functions
# ============================================================================

def create_slug(name):
    """
    Create URL-safe slug from whiskey name

    Examples:
        "Jack Daniel's Old No. 7" -> "jack-daniels-old-no-7"
        "Maker's Mark 46" -> "makers-mark-46"
        "Old Forester 1920 (Prohibition Style)" -> "old-forester-1920-prohibition-style"
    """
    if not name:
        return ""

    # Convert to lowercase
    slug = name.lower()

    # Remove all non-alphanumeric characters except spaces and hyphens
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)

    # Replace multiple spaces/hyphens with single hyphen
    slug = re.sub(r'[-\s]+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    return slug

def validate_search_query(query):
    """
    Validate and sanitize search query

    Returns: (is_valid, sanitized_query, error_message)
    """
    if not query:
        return False, None, "Query parameter 'q' is required"

    # Check length
    if len(query) > 100:
        return False, None, "Query too long (max 100 characters)"

    # Sanitize: remove potentially problematic characters but keep useful ones
    # Keep: alphanumeric, spaces, hyphens, apostrophes (for Jack Daniel's etc)
    sanitized = re.sub(r'[^\w\s\'-]', '', query)

    if not sanitized.strip():
        return False, None, "Invalid search query"

    return True, sanitized.strip(), None

# ============================================================================
# Endpoint 1: Health Check
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Returns API status and database connectivity
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM whiskeys")
            whiskey_count = cursor.fetchone()['count']

        logger.info(f"Health check successful: {whiskey_count} whiskeys in database")
        return jsonify({
            "status": "ok",
            "database": "connected",
            "whiskeys": whiskey_count
        }), 200

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "database": "disconnected",
            "message": "Database connection failed"
        }), 500

# ============================================================================
# Endpoint 2: Search Whiskeys
# ============================================================================

@app.route('/api/whiskeys/search', methods=['GET'])
def search_whiskeys():
    """
    Search whiskeys by name
    Query params:
      - q: search query (required)
      - limit: max results (default: 20)

    Returns:
      {
        "query": "garrison",
        "count": 1,
        "results": [
          {
            "whiskey_id": 4,
            "name": "garrison brothers cowboy bourbon (2025)",
            "distillery": "Garrison Brothers",
            "slug": "garrison-brothers-cowboy-bourbon-2025"
          }
        ]
      }
    """
    query = request.args.get('q', '').strip()
    limit = min(request.args.get('limit', 20, type=int), 50)  # Cap at 50

    # Validate and sanitize query
    is_valid, sanitized_query, error_msg = validate_search_query(query)
    if not is_valid:
        logger.warning(f"Invalid search query: {query}")
        return jsonify({"error": error_msg}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Search whiskeys by name (case-insensitive LIKE)
            cursor.execute("""
                SELECT whiskey_id, name, distillery
                FROM whiskeys
                WHERE name LIKE ?
                ORDER BY name
                LIMIT ?
            """, (f"%{sanitized_query}%", limit))

            results = []
            for row in cursor.fetchall():
                whiskey = dict_from_row(row)
                # Generate URL-friendly slug using proper function
                whiskey['slug'] = create_slug(whiskey['name'])
                results.append(whiskey)

        logger.info(f"Search query '{sanitized_query}' returned {len(results)} results")
        return jsonify({
            "query": sanitized_query,
            "count": len(results),
            "results": results
        }), 200

    except Exception as e:
        logger.error(f"Search failed for query '{sanitized_query}': {str(e)}", exc_info=True)
        return jsonify({
            "error": "An error occurred while searching. Please try again."
        }), 500

# ============================================================================
# Endpoint 3: Get Distilleries List
# ============================================================================

@app.route('/api/distilleries', methods=['GET'])
def get_distilleries():
    """
    Get alphabetical list of all distilleries with whiskey counts

    Returns:
      {
        "distilleries": [
          {
            "name": "Buffalo Trace",
            "whiskey_count": 23
          },
          ...
        ],
        "total": 621
      }
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get distilleries with counts, ordered alphabetically
            cursor.execute("""
                SELECT
                    distillery as name,
                    COUNT(*) as whiskey_count
                FROM whiskeys
                WHERE distillery IS NOT NULL
                  AND distillery != ''
                GROUP BY distillery
                ORDER BY distillery COLLATE NOCASE
            """)

            distilleries = [dict_from_row(row) for row in cursor.fetchall()]

        logger.info(f"Distilleries list returned {len(distilleries)} distilleries")
        return jsonify({
            "distilleries": distilleries,
            "total": len(distilleries)
        }), 200

    except Exception as e:
        logger.error(f"Failed to fetch distilleries: {str(e)}", exc_info=True)
        return jsonify({
            "error": "An error occurred while fetching distilleries. Please try again."
        }), 500

# ============================================================================
# Endpoint 4: Get Quiz Data
# ============================================================================

@app.route('/api/quiz/<int:whiskey_id>', methods=['GET'])
def get_quiz(whiskey_id):
    """
    Generate quiz data for a specific whiskey

    Returns:
      {
        "whiskey": {
          "id": 4,
          "name": "garrison brothers cowboy bourbon (2025)",
          "distillery": "Garrison Brothers"
        },
        "quiz": {
          "nose": {
            "options": [...],  // 9 shuffled descriptors
            "correct_count": 5  // How many are correct
          },
          "palate": {...},
          "finish": {...}
        }
      }
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get whiskey details
            cursor.execute("""
                SELECT whiskey_id, name, distillery
                FROM whiskeys
                WHERE whiskey_id = ?
            """, (whiskey_id,))

            whiskey_row = cursor.fetchone()
            if not whiskey_row:
                logger.warning(f"Quiz requested for non-existent whiskey_id: {whiskey_id}")
                return jsonify({
                    "error": "Whiskey not found"
                }), 404

            whiskey = dict_from_row(whiskey_row)

            # Get source review URLs for this whiskey
            cursor.execute("""
                SELECT DISTINCT source_site, source_url
                FROM reviews
                WHERE whiskey_id = ?
                AND source_url IS NOT NULL
                ORDER BY source_site
            """, (whiskey_id,))

            source_reviews = [
                {
                    "site": row['source_site'],
                    "url": row['source_url']
                }
                for row in cursor.fetchall()
            ]

            # Generate quiz for each section
            quiz = {}
            for section in ['nose', 'palate', 'finish']:
                section_data = generate_quiz_section(cursor, whiskey_id, section)
                if section_data is None:
                    logger.warning(f"No tasting data for whiskey_id {whiskey_id}, section {section}")
                    return jsonify({
                        "error": "No tasting data available for this whiskey"
                    }), 404
                quiz[section] = section_data

        logger.info(f"Generated quiz for whiskey_id {whiskey_id}: {whiskey['name']}")
        return jsonify({
            "whiskey": {
                "id": whiskey['whiskey_id'],
                "name": whiskey['name'],
                "distillery": whiskey['distillery']
            },
            "quiz": quiz,
            "source_reviews": source_reviews
        }), 200

    except Exception as e:
        logger.error(f"Quiz generation failed for whiskey_id {whiskey_id}: {str(e)}", exc_info=True)
        return jsonify({
            "error": "An error occurred while generating the quiz. Please try again."
        }), 500

def generate_quiz_section(cursor, whiskey_id, section):
    """
    Generate quiz options for one section (nose/palate/finish)

    Algorithm:
    1. Get correct descriptors for this whiskey + section
    2. Get incorrect descriptors from OTHER whiskeys (same section)
    3. Mix to create 9 total options (4-6 correct, 3-5 incorrect)
    4. Shuffle randomly
    5. Return with correct_count hint
    """

    # Get CORRECT descriptors for this whiskey
    cursor.execute("""
        SELECT dv.descriptor_id, dv.descriptor_name
        FROM aggregated_whiskey_descriptors awd
        JOIN descriptor_vocabulary dv ON awd.descriptor_id = dv.descriptor_id
        WHERE awd.whiskey_id = ?
          AND awd.tasting_section = ?
        ORDER BY awd.review_count DESC, dv.descriptor_name
    """, (whiskey_id, section))

    correct_descriptors = [dict_from_row(row) for row in cursor.fetchall()]

    # Check if whiskey has any descriptors
    if len(correct_descriptors) == 0:
        return None  # Will be handled by caller

    # Get INCORRECT descriptors from OTHER whiskeys
    cursor.execute("""
        SELECT DISTINCT dv.descriptor_id, dv.descriptor_name
        FROM aggregated_whiskey_descriptors awd
        JOIN descriptor_vocabulary dv ON awd.descriptor_id = dv.descriptor_id
        WHERE awd.whiskey_id != ?
          AND awd.tasting_section = ?
          AND dv.descriptor_id NOT IN (
              SELECT descriptor_id
              FROM aggregated_whiskey_descriptors
              WHERE whiskey_id = ? AND tasting_section = ?
          )
        ORDER BY RANDOM()
        LIMIT 20
    """, (whiskey_id, section, whiskey_id, section))

    incorrect_descriptors = [dict_from_row(row) for row in cursor.fetchall()]

    # Determine how many correct vs incorrect to show
    # Goal: 9 total options, with 4-6 correct if available
    total_options = 9

    if len(correct_descriptors) >= 6:
        # Lots of correct options - sample 5-6 of them
        num_correct = min(6, len(correct_descriptors))
    elif len(correct_descriptors) >= 4:
        # Good amount - use all
        num_correct = len(correct_descriptors)
    else:
        # Few correct options - use all
        num_correct = len(correct_descriptors)

    num_incorrect = total_options - num_correct

    # Sample descriptors
    selected_correct = correct_descriptors[:num_correct]
    selected_incorrect = incorrect_descriptors[:num_incorrect]

    # Build options list
    options = []

    for desc in selected_correct:
        options.append({
            "id": desc['descriptor_id'],
            "name": desc['descriptor_name'],
            "correct": True
        })

    for desc in selected_incorrect:
        options.append({
            "id": desc['descriptor_id'],
            "name": desc['descriptor_name'],
            "correct": False
        })

    # Shuffle options (so correct answers aren't always first)
    random.shuffle(options)

    return {
        "options": options,
        "correct_count": len(selected_correct)
    }

# ============================================================================
# Run Server
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("WHISKEY SENSORY TRAINING API")
    logger.info("=" * 80)
    logger.info("Endpoints:")
    logger.info("  GET  /api/health")
    logger.info("  GET  /api/whiskeys/search?q=<query>")
    logger.info("  GET  /api/distilleries")
    logger.info("  GET  /api/quiz/<whiskey_id>")
    logger.info("=" * 80)

    # Security: Use environment-based configuration
    port = int(os.getenv('PORT', 5001))
    host = '127.0.0.1' if DEBUG else '0.0.0.0'

    logger.info(f"Server starting in {'DEBUG' if DEBUG else 'PRODUCTION'} mode")
    logger.info(f"Listening on {host}:{port}")
    logger.info("=" * 80)

    app.run(debug=DEBUG, port=port, host=host)
