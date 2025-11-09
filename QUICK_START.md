# DevMetrics AI - Quick Start Guide

## 🚀 5-Minute Setup & Testing (Zero AI Costs Guaranteed)

This guide gets you testing the system in 5 minutes with **ZERO OpenAI API costs**.

---

## Prerequisites Check

Before starting, verify you have:

```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# PostgreSQL running
psql --version

# Redis running
redis-cli --version
```

---

## Step 1: Start Services

### Option A: All-in-One (Recommended for Testing)

```bash
# Terminal 1: Backend API
cd /home/user/AIproject2/backend
uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Option B: With Background Jobs

If you want to test integrations:

```bash
# Terminal 2: Celery Worker (ONLY worker, NO beat)
cd /home/user/AIproject2/backend
celery -A app.tasks.celery_app worker --loglevel=info
```

**Expected Output:**
```
celery@hostname ready.
```

---

## Step 2: Verify Zero AI Costs

### Check 1: Celery Logs (First 60 seconds)

Watch the Celery terminal for these messages:

❌ **Should NOT see:**
- "Analyzing commits"
- "AI analysis"
- "CodeComplexityAnalyzer"
- "WorkTypeClassifier"

✅ **Should ONLY see:**
- "celery@hostname ready"
- "Connected to redis"
- Heartbeat messages

### Check 2: OpenAI Dashboard

1. Open: https://platform.openai.com/usage
2. Check today's usage
3. **Should show: $0.00**

### Check 3: Database Query

```bash
# Check if any AI analysis happened
psql -U postgres -d devmetrics -c "SELECT COUNT(*) FROM work_activities;"

# Should return 0 or very small number
```

---

## Step 3: Test Frontend

```bash
# Terminal 3: Frontend
cd /home/user/AIproject2/frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs

---

## Step 4: Create Test Account & Verify

### 4.1 Register Admin

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@devmetrics.ai",
    "password": "Test123!",
    "full_name": "Test Admin",
    "role": "admin"
  }'
```

### 4.2 Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@devmetrics.ai",
    "password": "Test123!"
  }'
```

**Save the access_token from response!**

### 4.3 Test Protected Endpoint (No AI Cost)

```bash
TOKEN="paste-your-token-here"

curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

✅ **This should work and costs $0.00**

---

## Step 5: Verify Cost Control

### Wait 10 Minutes

After starting the system, wait 10 minutes and verify:

1. **OpenAI Dashboard:** Still shows $0.00
2. **Celery Logs:** No "Analyzing" messages
3. **Database:** `SELECT COUNT(*) FROM work_activities;` returns 0

✅ **If all three checks pass: Zero automatic AI costs confirmed!**

---

## Step 6: Test Manual Trigger (Optional - Costs ~$0.005)

⚠️ **THIS STEP WILL COST MONEY** (~$0.005)

Only do this if you want to verify the manual trigger works:

```bash
# First create a developer profile
curl -X POST "http://localhost:8000/api/developers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev@test.com",
    "full_name": "Test Dev",
    "role_level": "mid",
    "team": "Engineering",
    "github_username": "testdev",
    "skills": ["Python"]
  }'

# Get developer ID from response (e.g., 1)
DEV_ID=1

# Trigger AI analysis for 10 items (small cost ~$0.001)
curl -X POST "http://localhost:8000/api/analytics/developers/$DEV_ID/analyze?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "message": "AI analysis triggered for Test Dev",
  "warning": "This will incur AI API costs...",
  "estimated_cost_usd": 0.001,
  ...
}
```

**Verify Cost:**
1. Wait 5 minutes
2. Check https://platform.openai.com/usage
3. Should see ~$0.001 charge
4. Celery logs should show "Analyzing 10 commits"

---

## Monitoring Checklist

### Every 10 Minutes (First Hour)

- [ ] OpenAI usage dashboard shows expected amount
- [ ] No unexpected "Analyzing" messages in Celery logs
- [ ] Database query returns expected count

### Database Checks

```sql
-- Check analyzed items (these cost money)
SELECT COUNT(*) FROM git_commits WHERE analyzed = TRUE;
-- Should be 0 unless you manually triggered

-- Check work activities (created by AI analysis)
SELECT COUNT(*) FROM work_activities;
-- Should be 0 unless you manually triggered

-- Check when last activity was created
SELECT MAX(created_at) FROM work_activities;
-- Should be NULL or your manual trigger time
```

---

## Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Check database connection
psql -U postgres -d devmetrics -c "SELECT 1;"

# Check environment variables
cd backend
cat .env
```

### Frontend won't start

```bash
# Check if port 3000 is in use
lsof -i :3000

# Clear cache and reinstall
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### Celery worker errors

```bash
# Check Redis
redis-cli ping

# Check if worker is running
ps aux | grep celery

# Restart worker
pkill -f celery
celery -A app.tasks.celery_app worker --loglevel=info
```

---

## Success Criteria

After 1 hour of running:

✅ **Backend:**
- API server running on :8000
- /docs accessible
- No errors in logs

✅ **Celery:**
- Worker running
- NO "Analyzing" messages
- Only heartbeat and connection logs

✅ **Frontend:**
- Running on :3000
- Can login successfully
- Dashboard loads

✅ **Costs:**
- OpenAI dashboard: $0.00 (or only manual trigger amount)
- No automatic charges
- Full control maintained

---

## What's Safe vs What Costs Money

### ✅ FREE (Do Anytime)

- Starting backend/frontend
- Viewing API docs (/docs)
- Login/register
- Viewing dashboards
- GET requests to any endpoint
- Calculating scores from existing data
- Viewing cached insights

### 💰 COSTS MONEY (Manual Only)

- POST /api/analytics/developers/{id}/analyze
- Clicking "Run AI Analysis" button in UI
- **~$0.001 per 10 items**
- **~$0.01 per 100 items**

### ❌ DISABLED (Won't Run)

- Automatic AI analysis
- Celery Beat scheduler
- Background AI processing
- Any automatic OpenAI calls

---

## Quick Reference Commands

```bash
# Start backend
cd backend && uvicorn app.main:app --reload

# Start worker (no Beat!)
cd backend && celery -A app.tasks.celery_app worker --loglevel=info

# Start frontend
cd frontend && npm run dev

# Check OpenAI usage
open https://platform.openai.com/usage

# Check database
psql -U postgres -d devmetrics -c "SELECT COUNT(*) FROM work_activities;"

# View API docs
open http://localhost:8000/docs

# View frontend
open http://localhost:3000
```

---

## Next Steps

Once you've verified zero automatic costs:

1. ✅ Configure real GitHub/Jira integrations
2. ✅ Manually sync data (no AI cost)
3. ✅ Create developer profiles
4. ✅ Test manual AI analysis with small batches
5. ✅ Monitor costs closely
6. ✅ Scale up when comfortable

---

**Ready to start!** Run the backend and watch for any "Analyzing" messages (there should be none).

**Support:** Check `COST_CONTROL_GUIDE.md` and `TESTING_INSTRUCTIONS.md` for detailed guides.

---

*Last Updated: 2025-11-09*
*Zero automatic AI costs guaranteed!*
