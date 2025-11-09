#!/bin/bash

BASE_URL="http://localhost:8000"
TOKEN=""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== DevMetrics AI - Session 2 Integration Tests ===${NC}"
echo ""

# Test 1: Register admin user
echo -e "${YELLOW}Test 1: Register admin user${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@devmetrics.ai",
    "password": "Admin123!",
    "full_name": "Admin User",
    "role": "admin"
  }')

if echo "$REGISTER_RESPONSE" | grep -q "email"; then
  echo -e "${GREEN}✓ Admin registered${NC}"
else
  echo -e "${RED}✗ Registration failed (may already exist)${NC}"
  # Try to continue anyway
fi

# Test 2: Login as admin
echo -e "\n${YELLOW}Test 2: Login as admin${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@devmetrics.ai",
    "password": "Admin123!"
  }')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
  echo -e "${GREEN}✓ Login successful${NC}"
  echo "Token: ${TOKEN:0:30}..."
else
  echo -e "${RED}✗ Login failed${NC}"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

# Test 3: Configure GitHub integration
echo -e "\n${YELLOW}Test 3: Configure GitHub integration${NC}"
if [ -z "$GITHUB_ACCESS_TOKEN" ]; then
  echo -e "${RED}✗ GITHUB_ACCESS_TOKEN not set in environment${NC}"
  echo "Set it with: export GITHUB_ACCESS_TOKEN=your_token"
  GITHUB_SKIP=true
else
  GITHUB_RESPONSE=$(curl -s -X POST "$BASE_URL/api/integrations/github" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "organization_name": "'"${GITHUB_ORG:-your-github-org}"'",
      "access_token": "'"$GITHUB_ACCESS_TOKEN"'"
    }')

  if echo "$GITHUB_RESPONSE" | grep -q '"type":"github"'; then
    GITHUB_ID=$(echo "$GITHUB_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo -e "${GREEN}✓ GitHub integration configured (ID: $GITHUB_ID)${NC}"
  else
    echo -e "${RED}✗ GitHub integration failed${NC}"
    echo "Response: $GITHUB_RESPONSE"
  fi
fi

# Test 4: Configure Jira integration
echo -e "\n${YELLOW}Test 4: Configure Jira integration${NC}"
if [ -z "$JIRA_API_TOKEN" ]; then
  echo -e "${RED}✗ JIRA_API_TOKEN not set in environment${NC}"
  echo "Set it with: export JIRA_API_TOKEN=your_token"
  JIRA_SKIP=true
else
  JIRA_RESPONSE=$(curl -s -X POST "$BASE_URL/api/integrations/jira" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "workspace_url": "'"${JIRA_WORKSPACE_URL:-https://yourcompany.atlassian.net}"'",
      "username": "'"${JIRA_USERNAME:-your-email@company.com}"'",
      "api_token": "'"$JIRA_API_TOKEN"'",
      "project_keys": ["'"${JIRA_PROJECT_KEY:-PROJ}"'"]
    }')

  if echo "$JIRA_RESPONSE" | grep -q '"type":"jira"'; then
    JIRA_ID=$(echo "$JIRA_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo -e "${GREEN}✓ Jira integration configured (ID: $JIRA_ID)${NC}"
  else
    echo -e "${RED}✗ Jira integration failed${NC}"
    echo "Response: $JIRA_RESPONSE"
  fi
fi

# Test 5: List integrations
echo -e "\n${YELLOW}Test 5: List all integrations${NC}"
LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/api/integrations/" \
  -H "Authorization: Bearer $TOKEN")

if echo "$LIST_RESPONSE" | grep -q '"type"'; then
  COUNT=$(echo "$LIST_RESPONSE" | grep -o '"id":' | wc -l | tr -d ' ')
  echo -e "${GREEN}✓ Found $COUNT integration(s)${NC}"
  echo "$LIST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LIST_RESPONSE"
else
  echo -e "${RED}✗ List integrations failed${NC}"
  echo "Response: $LIST_RESPONSE"
fi

# Test 6: Test GitHub connection
if [ -n "$GITHUB_ID" ] && [ "$GITHUB_SKIP" != true ]; then
  echo -e "\n${YELLOW}Test 6: Test GitHub connection${NC}"
  TEST_RESPONSE=$(curl -s -X POST "$BASE_URL/api/integrations/$GITHUB_ID/test" \
    -H "Authorization: Bearer $TOKEN")

  if echo "$TEST_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ GitHub connection test passed${NC}"
  else
    echo -e "${RED}✗ GitHub connection test failed${NC}"
    echo "Response: $TEST_RESPONSE"
  fi
fi

# Test 7: Test Jira connection
if [ -n "$JIRA_ID" ] && [ "$JIRA_SKIP" != true ]; then
  echo -e "\n${YELLOW}Test 7: Test Jira connection${NC}"
  TEST_RESPONSE=$(curl -s -X POST "$BASE_URL/api/integrations/$JIRA_ID/test" \
    -H "Authorization: Bearer $TOKEN")

  if echo "$TEST_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ Jira connection test passed${NC}"
  else
    echo -e "${RED}✗ Jira connection test failed${NC}"
    echo "Response: $TEST_RESPONSE"
  fi
fi

# Test 8: Trigger GitHub sync
if [ -n "$GITHUB_ID" ] && [ "$GITHUB_SKIP" != true ]; then
  echo -e "\n${YELLOW}Test 8: Trigger GitHub sync${NC}"
  SYNC_RESPONSE=$(curl -s -X POST "$BASE_URL/api/integrations/$GITHUB_ID/sync" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "days_back": 7
    }')

  if echo "$SYNC_RESPONSE" | grep -q '"job_id"'; then
    JOB_ID=$(echo "$SYNC_RESPONSE" | grep -o '"job_id":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✓ GitHub sync triggered (Job ID: $JOB_ID)${NC}"
    echo "Check Celery worker logs to see sync progress"
  else
    echo -e "${RED}✗ Sync trigger failed${NC}"
    echo "Response: $SYNC_RESPONSE"
  fi
fi

# Test 9: Trigger Jira sync
if [ -n "$JIRA_ID" ] && [ "$JIRA_SKIP" != true ]; then
  echo -e "\n${YELLOW}Test 9: Trigger Jira sync${NC}"
  SYNC_RESPONSE=$(curl -s -X POST "$BASE_URL/api/integrations/$JIRA_ID/sync" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "days_back": 30
    }')

  if echo "$SYNC_RESPONSE" | grep -q '"job_id"'; then
    JOB_ID=$(echo "$SYNC_RESPONSE" | grep -o '"job_id":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✓ Jira sync triggered (Job ID: $JOB_ID)${NC}"
    echo "Check Celery worker logs to see sync progress"
  else
    echo -e "${RED}✗ Sync trigger failed${NC}"
    echo "Response: $SYNC_RESPONSE"
  fi
fi

# Test 10: Check sync status
if [ -n "$GITHUB_ID" ] && [ "$GITHUB_SKIP" != true ]; then
  echo -e "\n${YELLOW}Test 10: Check GitHub sync status${NC}"
  sleep 2  # Wait a bit for sync to start
  STATUS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/integrations/$GITHUB_ID/status" \
    -H "Authorization: Bearer $TOKEN")

  if echo "$STATUS_RESPONSE" | grep -q '"status"'; then
    STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✓ GitHub sync status: $STATUS${NC}"
    echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"
  else
    echo -e "${RED}✗ Status check failed${NC}"
    echo "Response: $STATUS_RESPONSE"
  fi
fi

echo -e "\n${BLUE}=== Integration Tests Complete ===${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Check Celery worker logs to see sync tasks running"
echo "2. Check database for synced data: SELECT COUNT(*) FROM git_commits;"
echo "3. Check for analyzed activities: SELECT COUNT(*) FROM work_activities;"
echo "4. Monitor with Flower: celery -A app.tasks.celery_app flower --port=5555"
echo ""
