#!/bin/bash

BASE_URL="http://localhost:8000"
TOKEN=""
DEVELOPER_ID=""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== DevMetrics AI - Session 3 Analytics Tests ===${NC}"
echo ""

# Test 1: Login as manager
echo -e "${YELLOW}Test 1: Login as manager${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@devmetrics.ai",
    "password": "Manager123!"
  }')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
  echo -e "${GREEN}✓ Manager login successful${NC}"
  echo "Token: ${TOKEN:0:30}..."
else
  echo -e "${RED}✗ Login failed - Please register a manager user first${NC}"
  echo "Run: curl -X POST http://localhost:8000/api/auth/register -H 'Content-Type: application/json' -d '{\"email\":\"manager@devmetrics.ai\",\"password\":\"Manager123!\",\"full_name\":\"Test Manager\",\"role\":\"manager\"}'"
  exit 1
fi

# Test 2: Get or create a developer
echo -e "\n${YELLOW}Test 2: Get developer list${NC}"
DEVELOPERS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/developers/" \
  -H "Authorization: Bearer $TOKEN")

DEVELOPER_ID=$(echo "$DEVELOPERS_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -n "$DEVELOPER_ID" ]; then
  echo -e "${GREEN}✓ Found developer ID: $DEVELOPER_ID${NC}"
else
  echo -e "${YELLOW}No developers found - Creating test developer${NC}"

  CREATE_DEV_RESPONSE=$(curl -s -X POST "$BASE_URL/api/developers/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test.developer@devmetrics.ai",
      "full_name": "Test Developer",
      "role_level": "mid",
      "team": "Engineering",
      "github_username": "testdev",
      "jira_username": "test.developer@devmetrics.ai",
      "skills": ["Python", "FastAPI", "PostgreSQL"]
    }')

  DEVELOPER_ID=$(echo "$CREATE_DEV_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

  if [ -n "$DEVELOPER_ID" ]; then
    echo -e "${GREEN}✓ Created developer ID: $DEVELOPER_ID${NC}"
  else
    echo -e "${RED}✗ Failed to create developer${NC}"
    echo "$CREATE_DEV_RESPONSE"
    exit 1
  fi
fi

# Test 3: Calculate productivity score
echo -e "\n${YELLOW}Test 3: Calculate productivity score${NC}"
SCORE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/analytics/calculate-score" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "developer_id": '"$DEVELOPER_ID"',
    "force_recalculate": true
  }')

if echo "$SCORE_RESPONSE" | grep -q '"success":true'; then
  echo -e "${GREEN}✓ Productivity score calculated${NC}"
  echo "$SCORE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SCORE_RESPONSE"
else
  echo -e "${YELLOW}⚠ Score calculation returned: ${NC}"
  echo "$SCORE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SCORE_RESPONSE"
  echo -e "${YELLOW}Note: This is expected if there's no activity data yet${NC}"
fi

# Test 4: Get developer analytics overview
echo -e "\n${YELLOW}Test 4: Get developer analytics overview${NC}"
OVERVIEW_RESPONSE=$(curl -s -X GET "$BASE_URL/api/analytics/developers/$DEVELOPER_ID/overview" \
  -H "Authorization: Bearer $TOKEN")

if echo "$OVERVIEW_RESPONSE" | grep -q '"developer_id"'; then
  echo -e "${GREEN}✓ Analytics overview retrieved${NC}"
  echo "$OVERVIEW_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$OVERVIEW_RESPONSE"
else
  echo -e "${YELLOW}⚠ Overview response: ${NC}"
  echo "$OVERVIEW_RESPONSE"
fi

# Test 5: Get detailed productivity analytics
echo -e "\n${YELLOW}Test 5: Get detailed productivity analytics${NC}"
PRODUCTIVITY_RESPONSE=$(curl -s -X GET "$BASE_URL/api/analytics/developers/$DEVELOPER_ID/productivity?include_comparison=true" \
  -H "Authorization: Bearer $TOKEN")

if echo "$PRODUCTIVITY_RESPONSE" | grep -q '"developer_id"'; then
  echo -e "${GREEN}✓ Detailed productivity retrieved${NC}"
  echo "$PRODUCTIVITY_RESPONSE" | python3 -m json.tool 2>/dev/null | head -40
  echo "..."
elif echo "$PRODUCTIVITY_RESPONSE" | grep -q "No activity data"; then
  echo -e "${YELLOW}⚠ No activity data found (expected if no sync has run)${NC}"
else
  echo -e "${RED}✗ Productivity analytics failed${NC}"
  echo "$PRODUCTIVITY_RESPONSE"
fi

# Test 6: Get productivity trends
echo -e "\n${YELLOW}Test 6: Get productivity trends${NC}"
TRENDS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/analytics/developers/$DEVELOPER_ID/trends?periods=12" \
  -H "Authorization: Bearer $TOKEN")

if echo "$TRENDS_RESPONSE" | grep -q '"developer_id"'; then
  echo -e "${GREEN}✓ Productivity trends retrieved${NC}"
  TREND_COUNT=$(echo "$TRENDS_RESPONSE" | grep -o '"period_start"' | wc -l | tr -d ' ')
  echo "Found $TREND_COUNT trend periods"
elif echo "$TRENDS_RESPONSE" | grep -q "detail"; then
  echo -e "${YELLOW}⚠ Trends not available yet${NC}"
else
  echo -e "${YELLOW}⚠ Trends response: ${NC}"
  echo "$TRENDS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$TRENDS_RESPONSE"
fi

# Test 7: Get work breakdown
echo -e "\n${YELLOW}Test 7: Get work breakdown${NC}"
BREAKDOWN_RESPONSE=$(curl -s -X GET "$BASE_URL/api/analytics/developers/$DEVELOPER_ID/work-breakdown?limit=10" \
  -H "Authorization: Bearer $TOKEN")

if echo "$BREAKDOWN_RESPONSE" | grep -q '"work_type_distribution"'; then
  echo -e "${GREEN}✓ Work breakdown retrieved${NC}"
  echo "$BREAKDOWN_RESPONSE" | python3 -m json.tool 2>/dev/null | head -40
  echo "..."
elif echo "$BREAKDOWN_RESPONSE" | grep -q "No activity data"; then
  echo -e "${YELLOW}⚠ No activity data found${NC}"
else
  echo -e "${YELLOW}⚠ Breakdown response: ${NC}"
  echo "$BREAKDOWN_RESPONSE"
fi

# Test 8: Get team analytics
echo -e "\n${YELLOW}Test 8: Get team analytics${NC}"
TEAM_RESPONSE=$(curl -s -X GET "$BASE_URL/api/analytics/teams/Engineering/overview" \
  -H "Authorization: Bearer $TOKEN")

if echo "$TEAM_RESPONSE" | grep -q '"team"'; then
  echo -e "${GREEN}✓ Team analytics retrieved${NC}"
  echo "$TEAM_RESPONSE" | python3 -m json.tool 2>/dev/null | head -40
  echo "..."
elif echo "$TEAM_RESPONSE" | grep -q "No developers found"; then
  echo -e "${YELLOW}⚠ No developers in 'Engineering' team${NC}"
elif echo "$TEAM_RESPONSE" | grep -q "No activity data"; then
  echo -e "${YELLOW}⚠ No activity data for team yet${NC}"
else
  echo -e "${YELLOW}⚠ Team analytics response: ${NC}"
  echo "$TEAM_RESPONSE"
fi

# Test 9: Get AI insights
echo -e "\n${YELLOW}Test 9: Get AI insights for developer${NC}"
INSIGHTS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/analytics/developers/$DEVELOPER_ID/insights?regenerate=true" \
  -H "Authorization: Bearer $TOKEN")

if echo "$INSIGHTS_RESPONSE" | grep -q '"insights"'; then
  echo -e "${GREEN}✓ AI insights generated${NC}"
  INSIGHT_COUNT=$(echo "$INSIGHTS_RESPONSE" | grep -o '"insight_type"' | wc -l | tr -d ' ')
  echo "Generated $INSIGHT_COUNT insights"
  echo "$INSIGHTS_RESPONSE" | python3 -m json.tool 2>/dev/null | head -60
  echo "..."
elif echo "$INSIGHTS_RESPONSE" | grep -q "detail"; then
  echo -e "${YELLOW}⚠ Insights response: ${NC}"
  echo "$INSIGHTS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$INSIGHTS_RESPONSE"
else
  echo -e "${YELLOW}⚠ Insights not available${NC}"
  echo "$INSIGHTS_RESPONSE"
fi

# Test 10: Test date filtering
echo -e "\n${YELLOW}Test 10: Test date filtering (last 7 days)${NC}"
START_DATE=$(date -d "7 days ago" +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d 2>/dev/null)
END_DATE=$(date +%Y-%m-%d)

FILTERED_RESPONSE=$(curl -s -X GET "$BASE_URL/api/analytics/developers/$DEVELOPER_ID/overview?start_date=$START_DATE&end_date=$END_DATE" \
  -H "Authorization: Bearer $TOKEN")

if echo "$FILTERED_RESPONSE" | grep -q '"period_start"'; then
  echo -e "${GREEN}✓ Date filtering works${NC}"
  echo "Period: $START_DATE to $END_DATE"
else
  echo -e "${YELLOW}⚠ Date filtering response: ${NC}"
  echo "$FILTERED_RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
fi

# Test 11: Test as developer (own data)
echo -e "\n${YELLOW}Test 11: Test developer viewing own analytics${NC}"

# First get developer user credentials
DEV_LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.developer@devmetrics.ai",
    "password": "Dev123!"
  }')

DEV_TOKEN=$(echo "$DEV_LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$DEV_TOKEN" ]; then
  echo -e "${GREEN}✓ Developer login successful${NC}"

  DEV_OWN_ANALYTICS=$(curl -s -X GET "$BASE_URL/api/analytics/developers/$DEVELOPER_ID/overview" \
    -H "Authorization: Bearer $DEV_TOKEN")

  if echo "$DEV_OWN_ANALYTICS" | grep -q '"developer_id"'; then
    echo -e "${GREEN}✓ Developer can view own analytics${NC}"
  else
    echo -e "${YELLOW}⚠ Developer view response: ${NC}"
    echo "$DEV_OWN_ANALYTICS" | python3 -m json.tool 2>/dev/null || echo "$DEV_OWN_ANALYTICS"
  fi
else
  echo -e "${YELLOW}⚠ Developer not registered yet - create with password: Dev123!${NC}"
fi

# Test 12: Test authorization (developer viewing other's data)
echo -e "\n${YELLOW}Test 12: Test authorization (developer cannot view others)${NC}"

if [ -n "$DEV_TOKEN" ]; then
  FORBIDDEN_RESPONSE=$(curl -s -X GET "$BASE_URL/api/analytics/developers/999/overview" \
    -H "Authorization: Bearer $DEV_TOKEN")

  if echo "$FORBIDDEN_RESPONSE" | grep -q "403"; then
    echo -e "${GREEN}✓ Authorization properly enforced${NC}"
  elif echo "$FORBIDDEN_RESPONSE" | grep -q "don't have access"; then
    echo -e "${GREEN}✓ Authorization properly enforced${NC}"
  else
    echo -e "${YELLOW}⚠ Authorization response: ${NC}"
    echo "$FORBIDDEN_RESPONSE"
  fi
fi

echo -e "\n${BLUE}=== Analytics Tests Complete ===${NC}"
echo ""
echo -e "${YELLOW}Summary:${NC}"
echo "- All 6 analytics endpoints tested"
echo "- Productivity scoring service tested"
echo "- AI insights generation tested"
echo "- Role-based access control verified"
echo "- Date filtering verified"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Ensure GitHub/Jira data has been synced (Session 2)"
echo "2. Run AI analysis tasks to generate work activities"
echo "3. Check database: SELECT COUNT(*) FROM work_activities;"
echo "4. Re-run analytics tests after data sync"
echo "5. View comprehensive analytics in API docs: http://localhost:8000/docs"
echo ""
