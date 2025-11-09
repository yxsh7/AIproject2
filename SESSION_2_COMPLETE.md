# Session 2 Complete: Integrations & Background Tasks

## Overview

Session 2 successfully implements the integration layer and background task processing system for DevMetrics AI. This session builds upon the foundation from Session 1 (Authentication & Developer Management) and adds:

- GitHub and Jira integration configuration
- Background task processing with Celery
- Automatic data synchronization from GitHub/Jira
- AI-powered analysis of commits and tickets
- Integration testing and monitoring endpoints

## What Was Built

### 1. Integration API Layer

**File:** `backend/app/schemas/integration.py`

Created comprehensive schemas for integration management:
- `GitHubIntegrationCreate` - Configure GitHub integration
- `JiraIntegrationCreate` - Configure Jira integration
- `IntegrationResponse` - Integration status and metadata
- `IntegrationSyncRequest` - Manual sync triggering
- `IntegrationSyncResponse` - Sync job information
- `SyncStatusResponse` - Real-time sync status
- `IntegrationTestResponse` - Connection test results

**File:** `backend/app/api/integrations.py`

Created 7 REST API endpoints:

1. **POST /api/integrations/github** - Configure GitHub integration
   - Tests connection before saving
   - Stores organization name and access token
   - Admin-only endpoint

2. **POST /api/integrations/jira** - Configure Jira integration
   - Tests connection before saving
   - Stores workspace URL, credentials, and project keys
   - Admin-only endpoint

3. **GET /api/integrations/** - List all integrations
   - Returns all configured integrations
   - Shows status, last sync time, errors

4. **POST /api/integrations/{id}/sync** - Trigger manual sync
   - Starts background Celery task
   - Returns job ID for tracking
   - Manager/Admin only

5. **GET /api/integrations/{id}/status** - Check sync status
   - Returns current status, last sync, errors
   - Available to all authenticated users

6. **POST /api/integrations/{id}/test** - Test connection
   - Validates credentials without syncing
   - Admin-only endpoint

7. **DELETE /api/integrations/{id}** - Remove integration
   - Deletes integration configuration
   - Admin-only endpoint

### 2. Background Task System

**File:** `backend/app/tasks/celery_app.py`

Configured Celery with Redis backend:
- Task result backend using Redis
- Broker using Redis
- Beat schedule for periodic tasks:
  - GitHub sync every 2 hours
  - Jira sync every 3 hours
  - AI analysis every 4 hours

**File:** `backend/app/tasks/sync_tasks.py`

Created data synchronization tasks:

1. **sync_integration_task(integration_id, days_back)**
   - Main orchestrator for syncing
   - Updates integration status
   - Handles errors gracefully
   - Routes to GitHub or Jira sync

2. **sync_github_integration(db, integration, days_back)**
   - Syncs commits, PRs, and code reviews
   - Processes all developers with GitHub usernames
   - Returns statistics (commits, PRs, reviews)

3. **sync_jira_integration(db, integration, days_back)**
   - Syncs tickets and comments
   - Processes all developers with Jira usernames
   - Returns statistics (tickets, comments)

4. **sync_all_github()** - Periodic task
   - Syncs all active GitHub integrations
   - Runs every 2 hours via Beat

5. **sync_all_jira()** - Periodic task
   - Syncs all active Jira integrations
   - Runs every 3 hours via Beat

**File:** `backend/app/tasks/analysis_tasks.py`

Created AI analysis tasks:

1. **analyze_git_commits(developer_id, limit)**
   - Uses CodeComplexityAnalyzer AI agent
   - Analyzes commit messages, file changes, and diffs
   - Creates WorkActivity records with scores
   - Processes in batches of 10

2. **analyze_jira_tickets(developer_id, limit)**
   - Uses WorkTypeClassifier AI agent
   - Analyzes ticket title, description, comments
   - Detects work type and complexity
   - Creates WorkActivity records

3. **analyze_all_unanalyzed()** - Periodic task
   - Triggers analysis for all developers
   - Runs every 4 hours via Beat
   - Processes up to 50 items per developer

Helper functions:
- `_map_impact_to_score()` - Maps impact level to 0-10 scale
- `_estimate_time_from_complexity()` - Estimates hours from complexity

### 3. Application Updates

**File:** `backend/app/main.py`

Updated main application:
- Imported integrations router
- Added integration routes at `/api/integrations`
- All 7 integration endpoints now accessible

## Database Models Used

Session 2 leverages these models created in Phase 1:

1. **IntegrationConfig** - Stores GitHub/Jira configuration
2. **GitCommit** - Stores synced Git commits
3. **PullRequest** - Stores synced pull requests
4. **CodeReview** - Stores code review activities
5. **JiraTicket** - Stores synced Jira tickets
6. **JiraComment** - Stores ticket comments
7. **WorkActivity** - Unified activity records from AI analysis
8. **DeveloperProfile** - Developer information with GitHub/Jira usernames

## Architecture Flow

### GitHub/Jira Sync Flow

```
1. Admin configures integration via API
   ↓
2. Connection tested immediately
   ↓
3. Integration saved with ACTIVE status
   ↓
4. Manual or automatic sync triggered
   ↓
5. Celery task fetches data from GitHub/Jira
   ↓
6. Data saved to database (commits, PRs, tickets)
   ↓
7. Integration status updated with last_sync_at
```

### AI Analysis Flow

```
1. Sync tasks create raw activity records
   ↓
2. Analysis tasks triggered (manual or scheduled)
   ↓
3. AI agents analyze unanalyzed records
   ↓
4. CodeComplexityAnalyzer processes commits
   ↓
5. WorkTypeClassifier processes tickets
   ↓
6. WorkActivity records created with scores
   ↓
7. Records marked as analyzed
```

## Testing Guide

### Prerequisites

1. **Install Redis:**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

2. **Update .env file:**
```bash
# Add to backend/.env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# GitHub/Jira credentials for testing
GITHUB_ACCESS_TOKEN=your_github_token_here
JIRA_WORKSPACE_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your_email@company.com
JIRA_API_TOKEN=your_jira_token_here
```

3. **Install Celery:**
```bash
cd backend
pip install celery[redis]
```

### Running the System

**Terminal 1: FastAPI Server**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2: Celery Worker**
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 3: Celery Beat (Scheduler)**
```bash
cd backend
celery -A app.tasks.celery_app beat --loglevel=info
```

### Testing Integration Endpoints

Create a test script `test_integrations.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
TOKEN=""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== DevMetrics AI - Session 2 Integration Tests ==="
echo ""

# Test 1: Register admin user
echo "Test 1: Register admin user"
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
  echo -e "${RED}✗ Registration failed${NC}"
  echo "$REGISTER_RESPONSE"
fi

# Test 2: Login as admin
echo -e "\nTest 2: Login as admin"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@devmetrics.ai",
    "password": "Admin123!"
  }')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
  echo -e "${GREEN}✓ Login successful${NC}"
  echo "Token: ${TOKEN:0:20}..."
else
  echo -e "${RED}✗ Login failed${NC}"
  exit 1
fi

# Test 3: Configure GitHub integration
echo -e "\nTest 3: Configure GitHub integration"
GITHUB_RESPONSE=$(curl -s -X POST "$BASE_URL/api/integrations/github" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "your-github-org",
    "access_token": "'"$GITHUB_ACCESS_TOKEN"'"
  }')

if echo "$GITHUB_RESPONSE" | grep -q '"type":"github"'; then
  GITHUB_ID=$(echo "$GITHUB_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
  echo -e "${GREEN}✓ GitHub integration configured (ID: $GITHUB_ID)${NC}"
else
  echo -e "${RED}✗ GitHub integration failed${NC}"
  echo "$GITHUB_RESPONSE"
fi

# Test 4: Configure Jira integration
echo -e "\nTest 4: Configure Jira integration"
JIRA_RESPONSE=$(curl -s -X POST "$BASE_URL/api/integrations/jira" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_url": "'"$JIRA_WORKSPACE_URL"'",
    "username": "'"$JIRA_USERNAME"'",
    "api_token": "'"$JIRA_API_TOKEN"'",
    "project_keys": ["PROJ"]
  }')

if echo "$JIRA_RESPONSE" | grep -q '"type":"jira"'; then
  JIRA_ID=$(echo "$JIRA_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
  echo -e "${GREEN}✓ Jira integration configured (ID: $JIRA_ID)${NC}"
else
  echo -e "${RED}✗ Jira integration failed${NC}"
  echo "$JIRA_RESPONSE"
fi

# Test 5: List integrations
echo -e "\nTest 5: List all integrations"
LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/api/integrations/" \
  -H "Authorization: Bearer $TOKEN")

if echo "$LIST_RESPONSE" | grep -q '"type"'; then
  COUNT=$(echo "$LIST_RESPONSE" | grep -o '"id":' | wc -l)
  echo -e "${GREEN}✓ Found $COUNT integrations${NC}"
else
  echo -e "${RED}✗ List integrations failed${NC}"
fi

# Test 6: Test GitHub connection
echo -e "\nTest 6: Test GitHub connection"
if [ -n "$GITHUB_ID" ]; then
  TEST_RESPONSE=$(curl -s -X POST "$BASE_URL/api/integrations/$GITHUB_ID/test" \
    -H "Authorization: Bearer $TOKEN")

  if echo "$TEST_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ GitHub connection test passed${NC}"
  else
    echo -e "${RED}✗ GitHub connection test failed${NC}"
    echo "$TEST_RESPONSE"
  fi
fi

# Test 7: Trigger GitHub sync
echo -e "\nTest 7: Trigger GitHub sync"
if [ -n "$GITHUB_ID" ]; then
  SYNC_RESPONSE=$(curl -s -X POST "$BASE_URL/api/integrations/$GITHUB_ID/sync" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "days_back": 7
    }')

  if echo "$SYNC_RESPONSE" | grep -q '"job_id"'; then
    JOB_ID=$(echo "$SYNC_RESPONSE" | grep -o '"job_id":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✓ Sync triggered (Job ID: $JOB_ID)${NC}"
  else
    echo -e "${RED}✗ Sync trigger failed${NC}"
    echo "$SYNC_RESPONSE"
  fi
fi

# Test 8: Check sync status
echo -e "\nTest 8: Check sync status"
if [ -n "$GITHUB_ID" ]; then
  sleep 2  # Wait a bit for sync to start
  STATUS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/integrations/$GITHUB_ID/status" \
    -H "Authorization: Bearer $TOKEN")

  if echo "$STATUS_RESPONSE" | grep -q '"status"'; then
    STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✓ Sync status: $STATUS${NC}"
  else
    echo -e "${RED}✗ Status check failed${NC}"
  fi
fi

echo -e "\n=== Integration Tests Complete ==="
```

Make it executable and run:
```bash
chmod +x test_integrations.sh
./test_integrations.sh
```

### Manual Testing with cURL

**1. Configure GitHub Integration:**
```bash
curl -X POST "http://localhost:8000/api/integrations/github" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "your-org",
    "access_token": "ghp_xxxxxxxxxxxxx"
  }'
```

**2. Configure Jira Integration:**
```bash
curl -X POST "http://localhost:8000/api/integrations/jira" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_url": "https://yourcompany.atlassian.net",
    "username": "your-email@company.com",
    "api_token": "ATATTxxxxxxxxxxxxx",
    "project_keys": ["PROJ1", "PROJ2"]
  }'
```

**3. Trigger Manual Sync:**
```bash
curl -X POST "http://localhost:8000/api/integrations/1/sync" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "days_back": 30
  }'
```

**4. Check Sync Status:**
```bash
curl -X GET "http://localhost:8000/api/integrations/1/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Testing Celery Tasks Directly

You can test Celery tasks using Python shell:

```python
from app.tasks.sync_tasks import sync_integration_task
from app.tasks.analysis_tasks import analyze_git_commits

# Trigger sync task
result = sync_integration_task.delay(integration_id=1, days_back=7)
print(f"Task ID: {result.id}")
print(f"Status: {result.status}")

# Wait for result
result.wait(timeout=60)
print(f"Result: {result.result}")

# Trigger analysis
analysis_result = analyze_git_commits.delay(developer_id=1, limit=10)
print(f"Analysis result: {analysis_result.result}")
```

### Monitoring Celery Tasks

**Using Flower (Celery monitoring tool):**
```bash
pip install flower
celery -A app.tasks.celery_app flower --port=5555
```

Open http://localhost:5555 in browser to see:
- Active workers
- Task history
- Task success/failure rates
- Real-time monitoring

## Verification Checklist

- [ ] Redis is running and accessible
- [ ] Celery worker is running
- [ ] Celery beat scheduler is running
- [ ] FastAPI server is running
- [ ] Can register admin user
- [ ] Can configure GitHub integration
- [ ] Can configure Jira integration
- [ ] GitHub connection test passes
- [ ] Jira connection test passes
- [ ] Can trigger manual sync
- [ ] Sync task appears in Celery logs
- [ ] Can check sync status
- [ ] Data appears in database after sync
- [ ] AI analysis tasks run successfully
- [ ] WorkActivity records created

## Database Verification

Check that data was synced:

```sql
-- Check integrations
SELECT * FROM integration_configs;

-- Check synced commits
SELECT COUNT(*) FROM git_commits;

-- Check synced tickets
SELECT COUNT(*) FROM jira_tickets;

-- Check analyzed activities
SELECT COUNT(*) FROM work_activities;

-- Check recent activities with AI analysis
SELECT
  developer_id,
  activity_date,
  work_type,
  complexity_score,
  impact_score,
  quality_score
FROM work_activities
ORDER BY activity_date DESC
LIMIT 10;
```

## Troubleshooting

### Redis Connection Errors
**Error:** `Error 61 connecting to localhost:6379. Connection refused.`

**Solution:**
```bash
# Start Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux

# Verify
redis-cli ping
```

### Celery Task Not Running
**Error:** Tasks stay in PENDING state

**Solution:**
1. Check worker is running: `celery -A app.tasks.celery_app worker --loglevel=info`
2. Check Redis is accessible
3. Verify task name matches exactly
4. Check worker logs for errors

### GitHub API Rate Limiting
**Error:** `API rate limit exceeded`

**Solution:**
- Use authenticated requests (access token)
- Reduce sync frequency
- Implement exponential backoff in sync tasks

### Jira Authentication Failed
**Error:** `401 Unauthorized`

**Solution:**
1. Verify Jira workspace URL is correct
2. Check API token is valid
3. Ensure username/email is correct
4. Try generating new API token

## What's Next: Session 3

Session 3 will implement:

1. **Productivity Scoring Service**
   - Calculate multi-dimensional scores
   - Role-based evaluation
   - Historical trends

2. **Analytics API**
   - Individual developer analytics
   - Team analytics
   - Comparison and benchmarking

3. **AI Insights Generation**
   - Pattern detection
   - Productivity recommendations
   - Anomaly detection

## Session 2 Summary

**Files Created/Modified:**
- `backend/app/schemas/integration.py` - NEW
- `backend/app/api/integrations.py` - NEW
- `backend/app/tasks/celery_app.py` - NEW
- `backend/app/tasks/sync_tasks.py` - NEW
- `backend/app/tasks/analysis_tasks.py` - NEW
- `backend/app/main.py` - MODIFIED (added integration routes)
- `backend/test_integrations.sh` - NEW (testing script)

**API Endpoints Added:** 7
- POST /api/integrations/github
- POST /api/integrations/jira
- GET /api/integrations/
- POST /api/integrations/{id}/sync
- GET /api/integrations/{id}/status
- POST /api/integrations/{id}/test
- DELETE /api/integrations/{id}

**Background Tasks Added:** 8
- sync_integration_task
- sync_github_integration
- sync_jira_integration
- sync_all_github (periodic)
- sync_all_jira (periodic)
- analyze_git_commits
- analyze_jira_tickets
- analyze_all_unanalyzed (periodic)

**Status:** ✅ Complete and ready for testing

---

*Generated: 2025-11-09 | Session 2 of DevMetrics AI Development*
