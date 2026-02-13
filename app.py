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

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database path
DB_PATH = Path(__file__).parent / "databases" / "whiskey_production.db"

# ============================================================================
# Database Helper Functions
# ============================================================================

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return dict(zip(row.keys(), row))

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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM whiskeys")
        whiskey_count = cursor.fetchone()['count']
        conn.close()

        return jsonify({
            "status": "ok",
            "database": "connected",
            "whiskeys": whiskey_count
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "database": "disconnected",
            "error": str(e)
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
    limit = request.args.get('limit', 20, type=int)

    if not query:
        return jsonify({
            "error": "Query parameter 'q' is required"
        }), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Search whiskeys by name (case-insensitive LIKE)
        cursor.execute("""
            SELECT whiskey_id, name, distillery
            FROM whiskeys
            WHERE name LIKE ?
            ORDER BY name
            LIMIT ?
        """, (f"%{query}%", limit))

        results = []
        for row in cursor.fetchall():
            whiskey = dict_from_row(row)
            # Generate URL-friendly slug
            whiskey['slug'] = whiskey['name'].lower().replace(' ', '-').replace('(', '').replace(')', '')
            results.append(whiskey)

        conn.close()

        return jsonify({
            "query": query,
            "count": len(results),
            "results": results
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# ============================================================================
# Endpoint 3: Get Quiz Data
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
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get whiskey details
        cursor.execute("""
            SELECT whiskey_id, name, distillery
            FROM whiskeys
            WHERE whiskey_id = ?
        """, (whiskey_id,))

        whiskey_row = cursor.fetchone()
        if not whiskey_row:
            conn.close()
            return jsonify({
                "error": f"Whiskey with id {whiskey_id} not found"
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
                conn.close()
                return jsonify({
                    "error": f"No tasting data available for this whiskey"
                }), 404
            quiz[section] = section_data

        conn.close()

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
        return jsonify({
            "error": str(e)
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
    print("=" * 80)
    print("WHISKEY SENSORY TRAINING API")
    print("=" * 80)
    print("\nEndpoints:")
    print("  GET  /api/health")
    print("  GET  /api/whiskeys/search?q=<query>")
    print("  GET  /api/quiz/<whiskey_id>")
    print("\nServer starting on http://localhost:5001")
    print("=" * 80)

    app.run(debug=True, port=5001, host='0.0.0.0')
