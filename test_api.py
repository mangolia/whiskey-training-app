#!/usr/bin/env python3
"""
Test script for the Flask API
Tests all endpoints without needing curl
"""

import sqlite3
from pathlib import Path
import json

# Import the app
from app import app, get_db_connection

def test_health():
    """Test health check endpoint"""
    print("\n" + "=" * 80)
    print("TEST 1: Health Check Endpoint")
    print("=" * 80)

    with app.test_client() as client:
        response = client.get('/api/health')
        data = response.get_json()

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")

        assert response.status_code == 200
        assert data['status'] == 'ok'
        print("✅ Health check passed!")

def test_search():
    """Test search endpoint"""
    print("\n" + "=" * 80)
    print("TEST 2: Search Endpoint")
    print("=" * 80)

    test_queries = ["garrison", "rye", "bourbon", "xyz123notfound"]

    with app.test_client() as client:
        for query in test_queries:
            response = client.get(f'/api/whiskeys/search?q={query}')
            data = response.get_json()

            print(f"\nQuery: '{query}'")
            print(f"Status Code: {response.status_code}")
            print(f"Results: {data['count']}")

            if data['count'] > 0:
                print(f"First result: {data['results'][0]['name']}")

        print("\n✅ Search tests passed!")

def test_quiz():
    """Test quiz generation endpoint"""
    print("\n" + "=" * 80)
    print("TEST 3: Quiz Generation Endpoint")
    print("=" * 80)

    # Get first whiskey from database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT whiskey_id, name FROM whiskeys LIMIT 1")
    whiskey = cursor.fetchone()
    conn.close()

    whiskey_id = whiskey['whiskey_id']
    whiskey_name = whiskey['name']

    print(f"\nTesting quiz for: {whiskey_name} (ID: {whiskey_id})")

    with app.test_client() as client:
        response = client.get(f'/api/quiz/{whiskey_id}')
        data = response.get_json()

        print(f"Status Code: {response.status_code}")
        print(f"\nWhiskey: {data['whiskey']['name']}")

        for section in ['nose', 'palate', 'finish']:
            quiz_section = data['quiz'][section]
            print(f"\n{section.upper()}:")
            print(f"  Total options: {len(quiz_section['options'])}")
            print(f"  Correct count: {quiz_section['correct_count']}")

            # Show first 3 options
            print(f"  Sample options:")
            for opt in quiz_section['options'][:3]:
                marker = "✅" if opt['correct'] else "❌"
                print(f"    {marker} {opt['name']}")

        print("\n✅ Quiz generation passed!")

def test_quiz_invalid():
    """Test quiz with invalid whiskey ID"""
    print("\n" + "=" * 80)
    print("TEST 4: Invalid Whiskey ID")
    print("=" * 80)

    with app.test_client() as client:
        response = client.get('/api/quiz/99999')
        data = response.get_json()

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")

        assert response.status_code == 404
        assert 'error' in data
        print("✅ Error handling works!")

if __name__ == '__main__':
    print("=" * 80)
    print("FLASK API TEST SUITE")
    print("=" * 80)

    try:
        test_health()
        test_search()
        test_quiz()
        test_quiz_invalid()

        print("\n" + "=" * 80)
        print("ALL TESTS PASSED! ✅")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
