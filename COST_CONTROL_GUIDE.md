# DevMetrics AI - Cost Control & Monitoring Guide

## Overview

This guide explains how to monitor and control costs for the DevMetrics AI platform, specifically OpenAI API usage.

## ⚠️ IMPORTANT: Cost Control Measures

### All Automatic AI Analysis is DISABLED by Default

To prevent unexpected costs, **ALL automatic background AI analysis tasks are disabled** in the default configuration.

### What's Disabled

1. **Automatic AI Analysis** ❌
   - `analyze_all_unanalyzed` task (was every 4 hours)
   - No automatic OpenAI API calls
   - No automatic commit/ticket analysis

2. **Automatic Syncing** ❌ (Optional - Currently Disabled)
   - `sync_all_github` task (was every 2 hours)
   - `sync_all_jira` task (was every 3 hours)
   - Note: Syncing does NOT use AI and has no API costs

### What Still Works

1. **Manual Triggers** ✅
   - POST /api/integrations/{id}/sync - Sync GitHub/Jira manually
   - POST /api/analytics/developers/{id}/analyze - Run AI analysis manually
   - All manual operations available via API or UI

2. **Data Fetching** ✅
   - All GET endpoints work normally
   - No AI costs for viewing analytics
   - Viewing cached insights is free

---

## Cost Breakdown

### AI Analysis Costs (OpenAI GPT-4o-mini)

**Input Pricing:** $0.150 per 1M tokens
**Output Pricing:** $0.600 per 1M tokens

**Estimated Cost Per Item:**
- Code commit analysis: ~500 tokens = $0.0001
- Jira ticket analysis: ~300 tokens = $0.00006

**Cost Per Developer:**
- 100 commits analyzed = $0.01
- 50 tickets analyzed = $0.003
- **Total: ~$0.01-0.02 per month** (if analyzed once)

**For 100 Developers:**
- One-time analysis: ~$1-2
- Monthly (if re-analyzed): ~$1-2/month

### No-Cost Operations

These operations have **ZERO AI API costs:**
- Syncing data from GitHub/Jira
- Viewing analytics dashboards
- Viewing cached scores
- Viewing previously generated insights
- Calculating scores from existing data
- All GET endpoints

---

## How to Enable/Disable Features

### 1. Celery Beat Schedule (Automatic Tasks)

**File:** `backend/app/tasks/celery_app.py`

**Current State:** All automatic tasks disabled

```python
celery_app.conf.beat_schedule = {
    # All tasks commented out (disabled)
}
```

**To Enable GitHub Sync (No cost):**
```python
celery_app.conf.beat_schedule = {
    "sync-github-every-2-hours": {
        "task": "app.tasks.sync_tasks.sync_all_github",
        "schedule": crontab(minute=0, hour="*/2"),
    },
}
```

**To Enable AI Analysis (COSTS MONEY - NOT RECOMMENDED):**
```python
# Only uncomment if you want automatic analysis
# "analyze-activities-every-4-hours": {
#     "task": "app.tasks.analysis_tasks.analyze_all_unanalyzed",
#     "schedule": crontab(minute=0, hour="*/4"),
# },
```

---

## Manual Trigger Workflow

### For Managers/Admins

**Step 1: Sync Data (No Cost)**
```bash
POST /api/integrations/{integration_id}/sync
{
  "days_back": 30
}
```

**Step 2: Run AI Analysis (Costs Money)**
```bash
POST /api/analytics/developers/{developer_id}/analyze?limit=50
```

**Step 3: View Results (No Cost)**
```bash
GET /api/analytics/developers/{developer_id}/productivity
GET /api/analytics/developers/{developer_id}/insights
```

### Using the UI

1. Login as manager/admin
2. Click "🤖 Run AI Analysis" button in header
3. Confirm the cost warning dialog
4. Wait 2-5 minutes for analysis to complete
5. Refresh dashboard to see results

---

## Monitoring Costs

### 1. OpenAI Dashboard

**URL:** https://platform.openai.com/usage

**What to Monitor:**
- Daily API usage
- Token consumption
- Cost per day
- Rate limits

**Set Up Alerts:**
1. Go to https://platform.openai.com/account/billing/limits
2. Set monthly budget limit (e.g., $10)
3. Enable email notifications
4. Set usage alerts at 50%, 75%, 90%

### 2. Application Logs

**Backend Logs:**
```bash
# Check Celery worker logs for AI analysis
tail -f celery_worker.log | grep "AI analysis"

# Check FastAPI logs
tail -f backend.log | grep "analyze"
```

**Key Log Messages:**
- `"Analyzing {N} commits for developer"` - AI analysis started
- `"Successfully analyzed {N} commits"` - AI analysis completed
- `"AI analysis triggered"` - Manual trigger invoked

### 3. Database Queries

**Check How Many Items Are Unanalyzed:**
```sql
-- Unanalyzed commits
SELECT COUNT(*) FROM git_commits WHERE analyzed = FALSE;

-- Unanalyzed tickets
SELECT COUNT(*) FROM jira_tickets WHERE analyzed = FALSE;

-- Recent AI-generated work activities
SELECT COUNT(*), source_type
FROM work_activities
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY source_type;
```

**Check Analysis History:**
```sql
-- When was last analysis run?
SELECT
  developer_id,
  MAX(created_at) as last_analysis
FROM work_activities
GROUP BY developer_id;

-- How many items analyzed per developer?
SELECT
  developer_id,
  COUNT(*) as items_analyzed,
  source_type
FROM work_activities
GROUP BY developer_id, source_type;
```

---

## Cost Optimization Tips

### 1. Batch Analysis

Instead of analyzing frequently:
- Run analysis once per week
- Analyze in batches (50-100 items)
- Only analyze new items (unanalyzed)

### 2. Limit Scope

```python
# Analyze only recent commits
analyze_git_commits.delay(developer_id, limit=20)  # Instead of 100

# Analyze only critical developers
# Run analysis for specific team members only
```

### 3. Use Cached Data

- Insights are cached in database
- Use `regenerate=false` parameter
- Scores are calculated from existing data (no AI cost)

```bash
# Free: Uses cached insights
GET /api/analytics/developers/1/insights?regenerate=false

# Costs money: Regenerates insights
GET /api/analytics/developers/1/insights?regenerate=true
```

### 4. Calculate Scores Without AI

Productivity scores can be calculated from existing work activities:

```bash
# No AI cost - calculates from existing data
POST /api/analytics/calculate-score
{
  "developer_id": 1,
  "force_recalculate": true
}
```

---

## Testing Without Costs

### 1. Start Backend Without AI

```bash
# Terminal 1: API server only
cd backend
uvicorn app.main:app --reload

# Terminal 2: Celery worker (no Beat scheduler)
celery -A app.tasks.celery_app worker --loglevel=info

# DO NOT START: Celery Beat (periodic tasks)
# This prevents automatic tasks from running
```

### 2. Verify No API Calls

**Check OpenAI Dashboard:**
- Go to https://platform.openai.com/usage
- Verify no new API calls in last hour
- Daily usage should be $0.00

**Check Application Logs:**
```bash
# Should see NO "Analyzing" messages
grep -i "analyzing" celery_worker.log
```

### 3. Test Endpoints

**Safe Endpoints (No Cost):**
- ✅ GET /api/auth/me
- ✅ GET /api/developers
- ✅ GET /api/analytics/developers/{id}/overview
- ✅ GET /api/analytics/developers/{id}/productivity
- ✅ POST /api/integrations/{id}/sync (no AI)

**Cost-Incurring Endpoints:**
- ❌ POST /api/analytics/developers/{id}/analyze (manual trigger)
- ❌ Automatic celery beat tasks (if enabled)

---

## Budget Planning

### Monthly Cost Estimates

**Small Team (10 developers):**
- One-time setup analysis: $0.10-0.20
- Monthly re-analysis: $0.10-0.20
- **Total: ~$0.30/month**

**Medium Team (50 developers):**
- One-time setup: $0.50-1.00
- Monthly re-analysis: $0.50-1.00
- **Total: ~$1.50/month**

**Large Team (100 developers):**
- One-time setup: $1.00-2.00
- Monthly re-analysis: $1.00-2.00
- **Total: ~$3.00/month**

**Enterprise (500 developers):**
- One-time setup: $5.00-10.00
- Monthly re-analysis: $5.00-10.00
- **Total: ~$15/month**

### OpenAI Tier Limits

**Free Tier:**
- $5 free credits (new accounts)
- 3 RPM (requests per minute)
- Good for testing

**Tier 1 ($5+ spent):**
- 500 RPM
- $100/month limit
- Good for small-medium teams

**Tier 2 ($50+ spent):**
- 5,000 RPM
- $500/month limit
- Good for large teams

---

## Emergency: Stop All Costs

If costs are too high:

### 1. Disable API Key
```bash
# Remove API key from environment
cd backend
nano .env

# Comment out:
# OPENAI_API_KEY=sk-...
```

### 2. Stop Celery Beat
```bash
# Kill the Beat scheduler
pkill -f "celery.*beat"

# Verify it's stopped
ps aux | grep celery
```

### 3. Check Active Tasks
```bash
# Cancel running tasks
celery -A app.tasks.celery_app purge

# Inspect active tasks
celery -A app.tasks.celery_app inspect active
```

### 4. Database Cleanup
```sql
-- Mark all as analyzed to prevent re-analysis
UPDATE git_commits SET analyzed = TRUE;
UPDATE jira_tickets SET analyzed = TRUE;
```

---

## Best Practices

### ✅ DO

1. **Monitor OpenAI usage dashboard daily**
2. **Set budget limits on OpenAI account**
3. **Use manual triggers only**
4. **Test with small batches first** (limit=10)
5. **Keep Celery Beat disabled in development**
6. **Review logs before running analysis**
7. **Calculate costs before triggering**

### ❌ DON'T

1. **Enable automatic analysis without monitoring**
2. **Run analysis on all developers simultaneously**
3. **Set large limits** (>100) without checking costs
4. **Forget to check OpenAI usage**
5. **Leave Celery Beat running unattended**
6. **Regenerate insights frequently**
7. **Analyze same data multiple times**

---

## FAQ

**Q: Why is automatic analysis disabled?**
A: To prevent unexpected costs. You control exactly when AI is used.

**Q: Can I view analytics without costs?**
A: Yes! All GET endpoints and cached data are free.

**Q: How do I run analysis for one person?**
A: Use `POST /api/analytics/developers/{id}/analyze?limit=50`

**Q: What if I accidentally enable automatic analysis?**
A: Stop Celery Beat immediately and check OpenAI usage dashboard.

**Q: Can I use a different AI model?**
A: Yes, change `AI_MODEL_NAME` in .env to `gpt-3.5-turbo` for lower costs.

**Q: Is there a free alternative?**
A: You could use local models (Ollama, LLaMA) but accuracy may vary.

---

## Support

If you have questions about costs:
1. Check OpenAI usage dashboard
2. Review application logs
3. Check this guide
4. Monitor database queries
5. Contact support if needed

**OpenAI Support:** https://help.openai.com/

---

**Last Updated:** 2025-11-09
**Status:** All automatic AI analysis DISABLED - Manual triggers only
