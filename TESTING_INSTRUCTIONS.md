# DevMetrics AI - Testing Instructions

## ✅ Cost-Controlled Testing Guide

This guide helps you test the system safely **without incurring any AI API costs**.

---

## Prerequisites

1. **PostgreSQL** running on localhost:5432
2. **Redis** running on localhost:6379
3. **OpenAI API Key** (but we won't use it in initial tests)
4. **Python 3.11+** and **Node.js 18+**

---

## Phase 1: Backend Testing (No AI Costs)

### Step 1: Start PostgreSQL and Redis

```bash
# macOS
brew services start postgresql
brew services start redis

# Linux
sudo systemctl start postgresql
sudo systemctl start redis

# Verify they're running
psql -U postgres -c "SELECT 1;"
redis-cli ping  # Should return "PONG"
```

### Step 2: Setup Backend

```bash
cd backend

# Install dependencies (if not already done)
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Edit .env - Add your database credentials
nano .env
```

**Minimum .env configuration:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/devmetrics
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# OpenAI (add key but we won't use it yet)
OPENAI_API_KEY=sk-your-key-here
AI_MODEL_PROVIDER=openai
AI_MODEL_NAME=gpt-4o-mini
```

### Step 3: Run Database Migrations

```bash
cd backend

# Run migrations to create tables
alembic upgrade head

# Verify tables created
psql -U postgres -d devmetrics -c "\dt"
# Should see 13 tables
```

### Step 4: Start FastAPI Server ONLY

```bash
cd backend

# Terminal 1: Start API server
uvicorn app.main:app --reload --port 8000

# You should see:
# 🚀 Starting DevMetrics AI...
# 📊 Database: localhost:5432/devmetrics
# ✅ Database initialized
```

### Step 5: Verify API is Running (No Costs)

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected: {"status":"healthy"}

# Test docs
open http://localhost:8000/docs
# Should see Swagger UI with all endpoints
```

### Step 6: Test Authentication (No Costs)

```bash
# Register admin user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Admin123!",
    "full_name": "Test Admin",
    "role": "admin"
  }'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Admin123!"
  }'

# Save the access_token from response
TOKEN="paste-token-here"

# Test authenticated endpoint
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

✅ **At this point, you have incurred ZERO AI costs**

---

## Phase 2: Celery Worker Testing (No AI Costs)

### Step 7: Start Celery Worker (Without Beat)

```bash
# Terminal 2: Start Celery worker
cd backend
celery -A app.tasks.celery_app worker --loglevel=info

# You should see:
# - Worker started
# - Registered tasks listed
# - NO "Analyzing" messages
```

⚠️ **DO NOT START CELERY BEAT YET**

### Step 8: Verify No Automatic Tasks

```bash
# Check worker logs
# Should see NO messages about:
# - "Analyzing commits"
# - "Analyzing tickets"
# - "AI analysis"
```

### Step 9: Monitor OpenAI Usage

1. Go to https://platform.openai.com/usage
2. Check today's usage
3. Should show **$0.00** if no analysis has run

✅ **Still ZERO costs at this point**

---

## Phase 3: Frontend Testing (No AI Costs)

### Step 10: Setup Frontend

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Configure environment
cp .env.example .env.local

# Edit .env.local
nano .env.local
```

**.env.local:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 11: Start Frontend

```bash
cd frontend

# Terminal 3: Start Next.js
npm run dev

# Should see:
# - Local: http://localhost:3000
# - Ready in X ms
```

### Step 12: Test Login Flow

1. Open http://localhost:3000
2. Should redirect to http://localhost:3000/login
3. Login with:
   - Email: admin@test.com
   - Password: Admin123!
4. Should redirect to /dashboard
5. Should see "No Data Available" card

✅ **Still ZERO AI costs - just viewing UI**

---

## Phase 4: Manual Integration Testing (No AI Costs Yet)

### Step 13: Create Developer Profile

```bash
# Create developer profile
curl -X POST "http://localhost:8000/api/developers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev@test.com",
    "full_name": "Test Developer",
    "role_level": "mid",
    "team": "Engineering",
    "github_username": "testdev",
    "jira_username": "test.developer@company.com",
    "skills": ["Python", "FastAPI"]
  }'
```

### Step 14: Try to View Analytics (No AI Costs)

```bash
# Get developer ID from previous response
DEV_ID=1

# Try to get overview (will return no data)
curl -X GET "http://localhost:8000/api/analytics/developers/$DEV_ID/overview" \
  -H "Authorization: Bearer $TOKEN"

# Expected: Error or empty data (no work activities yet)
```

✅ **Still ZERO AI costs - no analysis has run**

---

## Phase 5: Monitor for Accidental AI Calls

### Step 15: Monitor Logs for 10 Minutes

```bash
# Watch all terminals for 10 minutes
# Look for these keywords (should NOT appear):

# Celery worker terminal:
# ❌ Should NOT see: "Analyzing", "AI analysis", "CodeComplexityAnalyzer"
# ✅ Should see: Worker heartbeat messages only

# FastAPI terminal:
# ✅ Should see: GET/POST requests to endpoints
# ❌ Should NOT see: Any analysis-related logs
```

### Step 16: Check OpenAI Dashboard Again

1. Go to https://platform.openai.com/usage
2. Refresh the page
3. Today's usage should **STILL be $0.00**

✅ **Verified: No automatic AI calls happening**

---

## Phase 6: Test Manual AI Trigger (WILL COST MONEY)

⚠️ **WARNING: This step will incur small costs (~$0.0005)**

### Step 17: Prepare for Cost Tracking

1. Note current OpenAI usage: $X.XX
2. Have integration configured (GitHub or Jira)
3. Have some commits/tickets synced to database

### Step 18: Trigger Manual Analysis (Small Batch)

```bash
# Trigger analysis for just 10 items (very small cost)
curl -X POST "http://localhost:8000/api/analytics/developers/$DEV_ID/analyze?limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Response will show:
# - Job IDs
# - Estimated cost
# - Warning message
```

### Step 19: Monitor Analysis

```bash
# Watch Celery worker logs
# Should see:
# "Analyzing 10 commits for developer..."
# "AI analysis started"

# Wait 1-2 minutes for completion
```

### Step 20: Verify Cost

1. Go to https://platform.openai.com/usage
2. Refresh after 5 minutes
3. Should see small increase (~$0.0005 for 10 items)
4. Verify it's less than estimated

✅ **Manual trigger working, costs controlled**

---

## Verification Checklist

### Backend

- [ ] PostgreSQL running and accessible
- [ ] Redis running and accessible
- [ ] Database tables created (13 tables)
- [ ] FastAPI server starts without errors
- [ ] /docs endpoint accessible
- [ ] /health returns {"status":"healthy"}
- [ ] Celery worker starts (without Beat)
- [ ] No automatic "Analyzing" messages in logs

### Authentication

- [ ] Can register new user
- [ ] Can login and get JWT token
- [ ] Token works for authenticated endpoints
- [ ] /api/auth/me returns user data
- [ ] Role-based access control works

### Frontend

- [ ] npm install completes
- [ ] npm run dev starts without errors
- [ ] http://localhost:3000 accessible
- [ ] Login page renders
- [ ] Can login successfully
- [ ] Redirects to /dashboard after login
- [ ] Dashboard shows "No Data Available"
- [ ] "Run AI Analysis" button visible (if manager/admin)

### Cost Control

- [ ] NO automatic AI analysis running
- [ ] NO automatic sync running (unless enabled)
- [ ] OpenAI usage is $0.00 after 10 minutes
- [ ] Celery Beat is NOT running
- [ ] Manual trigger requires confirmation
- [ ] Cost estimate shown before analysis
- [ ] Can monitor usage in OpenAI dashboard

### Optional: Manual Triggers

- [ ] Can trigger GitHub sync manually
- [ ] Can trigger Jira sync manually
- [ ] Can trigger AI analysis manually
- [ ] Cost warning shown before AI analysis
- [ ] Estimated cost is accurate
- [ ] Analysis completes successfully
- [ ] Results appear in dashboard after refresh

---

## Troubleshooting

### "Connection refused" errors

**Problem:** Can't connect to database or Redis

**Solution:**
```bash
# Check PostgreSQL
psql -U postgres -c "SELECT 1;"

# Check Redis
redis-cli ping

# Start if needed
brew services start postgresql
brew services start redis
```

### "No developer profile found"

**Problem:** Dashboard shows error

**Solution:**
```bash
# Create developer profile via API
# Link user_id to developer profile
curl -X POST "http://localhost:8000/api/developers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com", ...}'
```

### Celery worker won't start

**Problem:** Import errors or connection errors

**Solution:**
```bash
# Check Redis
redis-cli ping

# Check Python path
which python
pip list | grep celery

# Reinstall if needed
pip install --force-reinstall celery[redis]
```

### Frontend build errors

**Problem:** npm errors or module not found

**Solution:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

---

## What to Check During Testing

### 1. Network Requests

Open browser DevTools → Network tab:
- All API calls should go to http://localhost:8000
- Check response status codes (200, 401, 403, etc.)
- Verify Authorization headers include "Bearer {token}"

### 2. Console Logs

Open browser DevTools → Console:
- Should see no errors
- API errors should be displayed clearly
- State updates should log correctly

### 3. Database State

```sql
-- Check users
SELECT id, email, role FROM users;

-- Check developers
SELECT id, user_id, role_level, team FROM developer_profiles;

-- Check if any commits exist
SELECT COUNT(*) FROM git_commits;

-- Check if any analyzed
SELECT COUNT(*) FROM git_commits WHERE analyzed = TRUE;

-- Check work activities
SELECT COUNT(*) FROM work_activities;
```

### 4. API Response Times

All endpoints should respond within:
- Auth endpoints: < 200ms
- Developer endpoints: < 500ms
- Analytics endpoints: < 1s

---

## Success Criteria

After completing these tests, you should have:

1. ✅ Working backend with all endpoints
2. ✅ Working frontend with login and dashboard
3. ✅ Zero unexpected AI costs
4. ✅ Manual triggers working correctly
5. ✅ Cost monitoring in place
6. ✅ All automatic tasks disabled
7. ✅ Clear understanding of cost control

---

## Next Steps

Once testing is complete:

1. **Configure Real Integrations:**
   - Add real GitHub org and token
   - Add real Jira workspace and credentials

2. **Sync Real Data:**
   - Manually trigger GitHub sync
   - Manually trigger Jira sync

3. **Run AI Analysis:**
   - Start with small batches (limit=10)
   - Monitor costs closely
   - Increase limit gradually

4. **Enable Team:**
   - Create developer profiles for team
   - Set up role assignments
   - Train managers on manual triggers

5. **Monitor Costs:**
   - Check OpenAI dashboard daily
   - Set budget alerts
   - Review usage weekly

---

**Testing Complete!** 🎉

You now have a fully functional DevMetrics AI system with complete cost control.

**Total Cost for Testing:** $0.00 (if you didn't run Phase 6)
**Total Cost with Manual Trigger:** ~$0.0005-0.001

---

*Last Updated: 2025-11-09*
