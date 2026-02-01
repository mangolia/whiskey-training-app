#!/bin/bash

# ============================================================================
# Deployment Verification Script
# ============================================================================
# This script tests all critical functionality after deployment
# Run this after deploying to production to ensure everything works
#
# Usage:
#   ./scripts/verify_deployment.sh [API_URL] [FRONTEND_URL]
#
# Examples:
#   ./scripts/verify_deployment.sh https://api.yourapp.com https://yourapp.com
#   ./scripts/verify_deployment.sh  # Uses localhost defaults
# ============================================================================

set -e  # Exit on error

# ============================================================================
# Configuration
# ============================================================================

API_URL="${1:-http://localhost:5001}"
FRONTEND_URL="${2:-http://localhost:3000}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_test() {
    echo -e "${YELLOW}Testing:${NC} $1"
}

pass_test() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${GREEN}✓ PASS${NC} $1"
}

fail_test() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${RED}✗ FAIL${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        echo "Please install $1 to run this verification script"
        exit 1
    fi
}

# ============================================================================
# Pre-flight Checks
# ============================================================================

print_header "PRE-FLIGHT CHECKS"

check_command curl
check_command jq

echo -e "${GREEN}✓${NC} All required commands available"
echo
echo "API URL:      $API_URL"
echo "Frontend URL: $FRONTEND_URL"

# ============================================================================
# Backend Tests
# ============================================================================

print_header "BACKEND API TESTS"

# Test 1: Health Check Endpoint
print_test "Health check endpoint (GET /api/health)"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/health" 2>/dev/null || echo "000")
HEALTH_CODE=$(echo "$HEALTH_RESPONSE" | tail -n 1)
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

if [ "$HEALTH_CODE" = "200" ]; then
    # Verify response structure
    STATUS=$(echo "$HEALTH_BODY" | jq -r '.status' 2>/dev/null)
    WHISKEY_COUNT=$(echo "$HEALTH_BODY" | jq -r '.whiskeys' 2>/dev/null)

    if [ "$STATUS" = "healthy" ] && [ "$WHISKEY_COUNT" -gt "0" ]; then
        pass_test "Health endpoint returns 200 with valid data ($WHISKEY_COUNT whiskeys)"
    else
        fail_test "Health endpoint returns 200 but invalid response structure"
        echo "       Response: $HEALTH_BODY"
    fi
else
    fail_test "Health endpoint returned HTTP $HEALTH_CODE (expected 200)"
fi

# Test 2: Search Endpoint - Valid Query
print_test "Search endpoint with valid query (GET /api/whiskeys/search?q=eagle)"
SEARCH_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/whiskeys/search?q=eagle" 2>/dev/null || echo "000")
SEARCH_CODE=$(echo "$SEARCH_RESPONSE" | tail -n 1)
SEARCH_BODY=$(echo "$SEARCH_RESPONSE" | sed '$d')

if [ "$SEARCH_CODE" = "200" ]; then
    RESULT_COUNT=$(echo "$SEARCH_BODY" | jq -r '.count' 2>/dev/null)
    if [ "$RESULT_COUNT" -gt "0" ]; then
        pass_test "Search returns results (found $RESULT_COUNT whiskeys)"
    else
        fail_test "Search returns 200 but no results"
    fi
else
    fail_test "Search endpoint returned HTTP $SEARCH_CODE (expected 200)"
fi

# Test 3: Search Endpoint - Empty Query
print_test "Search endpoint handles missing query parameter"
SEARCH_EMPTY=$(curl -s -w "\n%{http_code}" "$API_URL/api/whiskeys/search" 2>/dev/null || echo "000")
SEARCH_EMPTY_CODE=$(echo "$SEARCH_EMPTY" | tail -n 1)

if [ "$SEARCH_EMPTY_CODE" = "400" ]; then
    pass_test "Search correctly rejects missing query (HTTP 400)"
else
    fail_test "Search should return 400 for missing query, got $SEARCH_EMPTY_CODE"
fi

# Test 4: Quiz Endpoint - Valid Whiskey
print_test "Quiz generation for valid whiskey (GET /api/quiz/1)"
QUIZ_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/api/quiz/1" 2>/dev/null || echo "000")
QUIZ_CODE=$(echo "$QUIZ_RESPONSE" | tail -n 1)
QUIZ_BODY=$(echo "$QUIZ_RESPONSE" | sed '$d')

if [ "$QUIZ_CODE" = "200" ]; then
    # Verify quiz structure
    NOSE_OPTIONS=$(echo "$QUIZ_BODY" | jq -r '.quiz.nose.options | length' 2>/dev/null)
    PALATE_OPTIONS=$(echo "$QUIZ_BODY" | jq -r '.quiz.palate.options | length' 2>/dev/null)
    FINISH_OPTIONS=$(echo "$QUIZ_BODY" | jq -r '.quiz.finish.options | length' 2>/dev/null)

    if [ "$NOSE_OPTIONS" = "9" ] && [ "$PALATE_OPTIONS" = "9" ] && [ "$FINISH_OPTIONS" = "9" ]; then
        pass_test "Quiz generates correct structure (9 options per section)"
    else
        fail_test "Quiz has incorrect option counts (nose:$NOSE_OPTIONS palate:$PALATE_OPTIONS finish:$FINISH_OPTIONS)"
    fi
else
    fail_test "Quiz endpoint returned HTTP $QUIZ_CODE (expected 200)"
fi

# Test 5: Quiz Endpoint - Invalid Whiskey
print_test "Quiz endpoint handles invalid whiskey ID"
QUIZ_INVALID=$(curl -s -w "\n%{http_code}" "$API_URL/api/quiz/99999" 2>/dev/null || echo "000")
QUIZ_INVALID_CODE=$(echo "$QUIZ_INVALID" | tail -n 1)

if [ "$QUIZ_INVALID_CODE" = "404" ]; then
    pass_test "Quiz correctly rejects invalid whiskey ID (HTTP 404)"
else
    fail_test "Quiz should return 404 for invalid ID, got $QUIZ_INVALID_CODE"
fi

# Test 6: Response Time
print_test "API response time is acceptable"
START_TIME=$(date +%s%N)
curl -s "$API_URL/api/health" > /dev/null
END_TIME=$(date +%s%N)
RESPONSE_TIME=$((($END_TIME - $START_TIME) / 1000000))  # Convert to milliseconds

if [ "$RESPONSE_TIME" -lt "1000" ]; then
    pass_test "Health endpoint responds in ${RESPONSE_TIME}ms (< 1000ms)"
elif [ "$RESPONSE_TIME" -lt "3000" ]; then
    pass_test "Health endpoint responds in ${RESPONSE_TIME}ms (acceptable, but could be faster)"
else
    fail_test "Health endpoint too slow: ${RESPONSE_TIME}ms (> 3000ms)"
fi

# Test 7: CORS Headers (if production)
if [[ "$API_URL" != *"localhost"* ]]; then
    print_test "CORS headers are configured"
    CORS_HEADERS=$(curl -s -I "$API_URL/api/health" | grep -i "access-control")
    if [ -n "$CORS_HEADERS" ]; then
        pass_test "CORS headers present"
    else
        fail_test "CORS headers missing (frontend may not work)"
    fi
fi

# ============================================================================
# Frontend Tests
# ============================================================================

print_header "FRONTEND TESTS"

# Test 8: Frontend Accessibility
print_test "Frontend homepage loads"
FRONTEND_RESPONSE=$(curl -s -w "\n%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "000")
FRONTEND_CODE=$(echo "$FRONTEND_RESPONSE" | tail -n 1)

if [ "$FRONTEND_CODE" = "200" ]; then
    pass_test "Frontend homepage returns HTTP 200"
else
    fail_test "Frontend homepage returned HTTP $FRONTEND_CODE (expected 200)"
fi

# Test 9: Frontend Response Time
print_test "Frontend response time"
START_TIME=$(date +%s%N)
curl -s "$FRONTEND_URL" > /dev/null
END_TIME=$(date +%s%N)
FRONTEND_TIME=$((($END_TIME - $START_TIME) / 1000000))

if [ "$FRONTEND_TIME" -lt "2000" ]; then
    pass_test "Frontend responds in ${FRONTEND_TIME}ms (< 2000ms)"
else
    fail_test "Frontend too slow: ${FRONTEND_TIME}ms (> 2000ms)"
fi

# Test 10: HTTPS (if production)
if [[ "$FRONTEND_URL" == "https://"* ]]; then
    print_test "HTTPS certificate is valid"
    SSL_CHECK=$(curl -s -I "$FRONTEND_URL" 2>&1)
    if [[ $SSL_CHECK != *"SSL"* ]] && [[ $SSL_CHECK != *"certificate"* ]]; then
        pass_test "HTTPS certificate valid"
    else
        fail_test "HTTPS certificate issue detected"
    fi
fi

# ============================================================================
# Database Tests
# ============================================================================

print_header "DATABASE TESTS"

# Test 11: Database Statistics
print_test "Database has expected number of whiskeys"
if [ "$WHISKEY_COUNT" -ge "2000" ]; then
    pass_test "Database contains $WHISKEY_COUNT whiskeys (expected >= 2000)"
elif [ "$WHISKEY_COUNT" -ge "30" ]; then
    pass_test "Database contains $WHISKEY_COUNT whiskeys (MVP mode)"
else
    fail_test "Database only has $WHISKEY_COUNT whiskeys (expected more)"
fi

# Test 12: Quiz-Ready Whiskeys
QUIZ_READY=$(echo "$HEALTH_BODY" | jq -r '.quiz_ready_whiskeys' 2>/dev/null)
if [ -n "$QUIZ_READY" ] && [ "$QUIZ_READY" != "null" ]; then
    COVERAGE=$(echo "scale=1; $QUIZ_READY * 100 / $WHISKEY_COUNT" | bc)
    if (( $(echo "$COVERAGE >= 95" | bc -l) )); then
        pass_test "Quiz coverage is ${COVERAGE}% ($QUIZ_READY/$WHISKEY_COUNT)"
    else
        fail_test "Quiz coverage only ${COVERAGE}% (expected >= 95%)"
    fi
fi

# ============================================================================
# Integration Tests
# ============================================================================

print_header "INTEGRATION TESTS"

# Test 13: Full User Flow
print_test "Complete user flow (search → quiz → results)"

# Step 1: Search
SEARCH_RESULT=$(curl -s "$API_URL/api/whiskeys/search?q=eagle" | jq -r '.results[0].whiskey_id' 2>/dev/null)

if [ -n "$SEARCH_RESULT" ] && [ "$SEARCH_RESULT" != "null" ]; then
    # Step 2: Get Quiz
    QUIZ_TEST=$(curl -s "$API_URL/api/quiz/$SEARCH_RESULT")
    QUIZ_VALID=$(echo "$QUIZ_TEST" | jq -r '.quiz.nose.options | length' 2>/dev/null)

    if [ "$QUIZ_VALID" = "9" ]; then
        pass_test "Full flow works (search → quiz generation)"
    else
        fail_test "Quiz generation failed in integration test"
    fi
else
    fail_test "Search failed in integration test"
fi

# Test 14: Source Reviews Present
print_test "Source review links are present"
SOURCE_REVIEWS=$(echo "$QUIZ_TEST" | jq -r '.source_reviews | length' 2>/dev/null)

if [ -n "$SOURCE_REVIEWS" ] && [ "$SOURCE_REVIEWS" != "null" ] && [ "$SOURCE_REVIEWS" -gt "0" ]; then
    pass_test "Source reviews present ($SOURCE_REVIEWS links)"
else
    fail_test "Source reviews missing or empty"
fi

# ============================================================================
# Results Summary
# ============================================================================

print_header "TEST RESULTS SUMMARY"

echo
echo "Tests Passed:  ${GREEN}$TESTS_PASSED${NC}"
echo "Tests Failed:  ${RED}$TESTS_FAILED${NC}"
echo "Total Tests:   $TESTS_TOTAL"
echo

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ ALL TESTS PASSED - Deployment Verified!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo "Your application is ready for production! 🎉"
    echo
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ SOME TESTS FAILED - Review errors above${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo "Please fix the failing tests before deploying to production."
    echo
    exit 1
fi
