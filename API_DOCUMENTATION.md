# Whiskey Sensory Training API Documentation

## Overview

REST API for the Whiskey Sensory Training App. Provides endpoints for searching whiskeys and generating quiz data.

**Base URL (Development):** `http://localhost:5001`

**Base URL (Production):** `https://api.yourapp.com` (Railway deployment)

**Database:** Production database with 2,125 whiskeys (2,109 quiz-ready)

---

## Endpoints

### 1. Health Check

**GET** `/api/health`

Check API status and database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "whiskeys": 2125,
  "quiz_ready_whiskeys": 2109,
  "reviews": 2164,
  "descriptors": 81
}
```

**Status Codes:**
- `200 OK` - API is healthy
- `500 Internal Server Error` - Database connection failed

---

### 2. Search Whiskeys

**GET** `/api/whiskeys/search?q=<query>&limit=<limit>`

Search for whiskeys by name.

**Query Parameters:**
- `q` (required) - Search query string
- `limit` (optional) - Maximum results to return (default: 20)

**Example Request:**
```bash
GET /api/whiskeys/search?q=garrison
```

**Response:**
```json
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
```

**Status Codes:**
- `200 OK` - Search successful
- `400 Bad Request` - Missing query parameter
- `500 Internal Server Error` - Server error

---

### 3. Get Quiz Data

**GET** `/api/quiz/<whiskey_id>`

Generate quiz data for a specific whiskey.

**Path Parameters:**
- `whiskey_id` (integer) - ID of the whiskey

**Example Request:**
```bash
GET /api/quiz/4
```

**Response:**
```json
{
  "whiskey": {
    "id": 4,
    "name": "garrison brothers cowboy bourbon (2025)",
    "distillery": "Garrison Brothers"
  },
  "quiz": {
    "nose": {
      "options": [
        {"id": 39, "name": "oak", "correct": true},
        {"id": 31, "name": "cinnamon", "correct": true},
        {"id": 1, "name": "vanilla", "correct": false},
        {"id": 48, "name": "chocolate", "correct": true},
        {"id": 32, "name": "pepper", "correct": true},
        {"id": 7, "name": "molasses", "correct": true},
        {"id": 15, "name": "smoke", "correct": false},
        {"id": 26, "name": "tropical", "correct": false},
        {"id": 2, "name": "caramel", "correct": false}
      ],
      "correct_count": 5
    },
    "palate": {
      "options": [...],
      "correct_count": 6
    },
    "finish": {
      "options": [...],
      "correct_count": 5
    }
  },
  "source_reviews": [
    {
      "site": "Breaking Bourbon",
      "url": "https://www.breakingbourbon.com/review/garrison-brothers-cowboy-bourbon-2025"
    }
  ]
}
```

**Quiz Logic:**
- Each section (nose/palate/finish) has **9 options**
- **4-6 correct** descriptors from this whiskey's reviews
- **3-5 incorrect** descriptors from other whiskeys
- Options are **shuffled randomly**
- `correct_count` tells user how many to find (hint)
- `source_reviews` provides URLs to original reviews for QA verification

**Status Codes:**
- `200 OK` - Quiz generated successfully
- `404 Not Found` - Whiskey ID doesn't exist
- `500 Internal Server Error` - Server error

---

## Running the API

### Development (Local)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the server:**
```bash
python3 app.py
```

3. **Test endpoints:**
```bash
# Health check
curl http://localhost:5001/api/health

# Search
curl http://localhost:5001/api/whiskeys/search?q=garrison

# Quiz
curl http://localhost:5001/api/quiz/4
```

### Production (Railway)

See deployment documentation (Task 13-16).

---

## CORS Configuration

CORS is enabled for all origins in development. In production, configure to only allow requests from your frontend domain:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://whiskey-training.vercel.app"]
    }
})
```

---

## Error Handling

All endpoints return JSON error messages:

```json
{
  "error": "Whiskey with id 99999 not found"
}
```

Common error codes:
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server-side error

---

## Database Schema

The API queries these tables:
- `whiskeys` - Whiskey metadata
- `descriptor_vocabulary` - 74 sensory descriptors
- `aggregated_whiskey_descriptors` - Pre-computed quiz data

See `DATABASE_SCHEMA.md` for full schema documentation.

---

## Frontend Integration

**React example:**

```javascript
// Search whiskeys
const searchWhiskeys = async (query) => {
  const response = await fetch(`http://localhost:5001/api/whiskeys/search?q=${query}`);
  const data = await response.json();
  return data.results;
};

// Get quiz
const getQuiz = async (whiskeyId) => {
  const response = await fetch(`http://localhost:5001/api/quiz/${whiskeyId}`);
  const data = await response.json();
  return data;
};
```

---

## Testing

Run the test suite:

```bash
python3 test_api.py
```

This tests all endpoints and validates responses.

---

## Limitations (MVP)

- No user authentication
- No rate limiting
- No caching
- Quiz generation is randomized (not seeded)
- Single database connection (no connection pooling)

These will be addressed in post-MVP iterations.
