#!/bin/bash

# Test script for DevMetrics AI API
# This script demonstrates the authentication and developer management endpoints

BASE_URL="http://localhost:8000"

echo "===================================="
echo "DevMetrics AI - API Test Script"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Health check
echo -e "${BLUE}[TEST 1]${NC} Health check..."
curl -s "${BASE_URL}/health" | jq '.'
echo ""

# Test 2: Register a new user (admin)
echo -e "${BLUE}[TEST 2]${NC} Register admin user..."
ADMIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@devmetrics.ai",
    "password": "admin123456",
    "full_name": "Admin User",
    "role": "admin"
  }')

echo "$ADMIN_RESPONSE" | jq '.'

# Extract admin token
ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | jq -r '.access_token')
echo -e "${GREEN}Admin token:${NC} $ADMIN_TOKEN"
echo ""

# Test 3: Register a manager
echo -e "${BLUE}[TEST 3]${NC} Register manager user..."
MANAGER_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@devmetrics.ai",
    "password": "manager123",
    "full_name": "Jane Manager",
    "role": "manager"
  }')

echo "$MANAGER_RESPONSE" | jq '.'

MANAGER_TOKEN=$(echo "$MANAGER_RESPONSE" | jq -r '.access_token')
echo -e "${GREEN}Manager token:${NC} $MANAGER_TOKEN"
echo ""

# Test 4: Register a developer
echo -e "${BLUE}[TEST 4]${NC} Register developer user..."
DEV_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@devmetrics.ai",
    "password": "alice123456",
    "full_name": "Alice Developer",
    "role": "developer"
  }')

echo "$DEV_RESPONSE" | jq '.'

DEV_USER_ID=$(echo "$DEV_RESPONSE" | jq -r '.user.id')
DEV_TOKEN=$(echo "$DEV_RESPONSE" | jq -r '.access_token')
echo -e "${GREEN}Developer User ID:${NC} $DEV_USER_ID"
echo -e "${GREEN}Developer token:${NC} $DEV_TOKEN"
echo ""

# Test 5: Get current user info
echo -e "${BLUE}[TEST 5]${NC} Get current user info (using admin token)..."
curl -s -X GET "${BASE_URL}/api/auth/me" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
echo ""

# Test 6: Login with email/password
echo -e "${BLUE}[TEST 6]${NC} Login with email/password..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@devmetrics.ai",
    "password": "alice123456"
  }')

echo "$LOGIN_RESPONSE" | jq '.'
echo ""

# Test 7: Create developer profile (as admin)
echo -e "${BLUE}[TEST 7]${NC} Create developer profile..."
PROFILE_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/developers/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $DEV_USER_ID,
    \"organization_id\": 1,
    \"role_level\": \"senior\",
    \"team\": \"backend\",
    \"job_title\": \"Senior Software Engineer\",
    \"github_username\": \"alice-dev\",
    \"jira_username\": \"alice@devmetrics.ai\",
    \"focus_areas\": [\"backend\", \"apis\", \"databases\"]
  }")

echo "$PROFILE_RESPONSE" | jq '.'

DEV_PROFILE_ID=$(echo "$PROFILE_RESPONSE" | jq -r '.id')
echo -e "${GREEN}Developer Profile ID:${NC} $DEV_PROFILE_ID"
echo ""

# Test 8: List all developers
echo -e "${BLUE}[TEST 8]${NC} List all developers..."
curl -s -X GET "${BASE_URL}/api/developers/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
echo ""

# Test 9: Get specific developer profile
echo -e "${BLUE}[TEST 9]${NC} Get developer profile by ID..."
curl -s -X GET "${BASE_URL}/api/developers/$DEV_PROFILE_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
echo ""

# Test 10: Update developer profile
echo -e "${BLUE}[TEST 10]${NC} Update developer profile..."
curl -s -X PATCH "${BASE_URL}/api/developers/$DEV_PROFILE_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "team": "platform",
    "job_title": "Staff Software Engineer"
  }' | jq '.'
echo ""

# Test 11: Filter developers by team
echo -e "${BLUE}[TEST 11]${NC} Filter developers by team..."
curl -s -X GET "${BASE_URL}/api/developers/?team=platform" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
echo ""

# Test 12: Try to access developers endpoint without auth (should fail)
echo -e "${BLUE}[TEST 12]${NC} Try to access protected endpoint without auth (should fail)..."
ERROR_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/developers/" 2>&1)
echo -e "${RED}$ERROR_RESPONSE${NC}"
echo ""

echo "===================================="
echo -e "${GREEN}✅ All tests completed!${NC}"
echo "===================================="
