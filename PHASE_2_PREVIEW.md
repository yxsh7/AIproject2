# DevMetrics AI - Phase 2 Implementation Preview

**What You're About to Build**

This document previews exactly what will be implemented in Phase 2, so you can review before we start building.

---

## 📋 Phase 2 Overview

**Goal**: Build the core API endpoints and productivity scoring system

**Timeline**: ~8-12 hours of development

**What You'll Have**: A functional backend that can:
- Accept API requests for developers, analytics, and integrations
- Calculate productivity scores
- Run background sync jobs
- Provide data to frontends

---

## 🔧 What We'll Build (In Detail)

### 1. API Endpoints (FastAPI Routes)

#### **Authentication Routes** (`/api/auth`)

**File**: `backend/app/api/auth.py`

```python
POST /api/auth/register
- Register new user account
- Input: email, password, full_name, role
- Output: user_id, access_token
- Creates User + DeveloperProfile if role=developer

POST /api/auth/login
- Login with email/password
- Input: email, password
- Output: access_token, user info
- Returns JWT token for subsequent requests

GET /api/auth/me
- Get current user info
- Requires: JWT token in header
- Output: user profile, organization, role
```

**Why**: Every application needs auth. This lets users log in and protects endpoints.

---

#### **Developer Management Routes** (`/api/developers`)

**File**: `backend/app/api/developers.py`

```python
POST /api/developers
- Create new developer profile
- Input: user_id, github_username, jira_username, role_level, team
- Output: developer_profile object
- Manager/Admin only

GET /api/developers
- List all developers in organization
- Query params: team, role_level, page, limit
- Output: paginated list of developers
- Manager/Admin only

GET /api/developers/:id
- Get specific developer details
- Output: full profile + recent activity summary
- Developers can see their own, managers see all

PATCH /api/developers/:id
- Update developer profile
- Input: fields to update (team, role_level, focus_areas, etc.)
- Output: updated profile
- Manager/Admin only
```

**Why**: Managers need to add developers to the system and assign roles.

---

#### **Integration Routes** (`/api/integrations`)

**File**: `backend/app/api/integrations.py`

```python
POST /api/integrations/github
- Configure GitHub integration
- Input: organization_name, access_token
- Tests connection, saves config
- Output: integration_id, status
- Admin only

POST /api/integrations/jira
- Configure Jira integration
- Input: workspace_url, api_token, username
- Tests connection, saves config
- Output: integration_id, status
- Admin only

GET /api/integrations
- List all integrations for org
- Output: list of integrations with status
- Admin only

POST /api/integrations/:id/sync
- Trigger manual sync for integration
- Starts background Celery job
- Output: job_id, estimated_time
- Admin only

GET /api/integrations/:id/status
- Check sync status
- Output: last_sync, next_sync, errors, progress
```

**Why**: Admins need to connect the system to GitHub and Jira.

---

#### **Analytics Routes** (`/api/analytics`)

**File**: `backend/app/api/analytics.py`

```python
GET /api/analytics/team
- Get team-wide analytics
- Query params: start_date, end_date, team
- Output:
  {
    "team_score": 78,
    "total_developers": 10,
    "work_breakdown": {"code": 60, "research": 15, ...},
    "top_performers": [...],
    "bottlenecks": [...]
  }
- Manager only

GET /api/analytics/developer/:id
- Get developer analytics for period
- Query params: start_date, end_date
- Output:
  {
    "overall_score": 85,
    "breakdown": {
      "code_quality": 90,
      "complexity": 82,
      "impact": 88,
      ...
    },
    "work_summary": {...},
    "recent_highlights": [...]
  }
- Developers see own, managers see all

GET /api/analytics/developer/:id/timeline
- Get day-by-day activity timeline
- Query params: start_date, end_date
- Output: array of daily activities with scores
- For visualizing trends over time

GET /api/analytics/developer/:id/work-breakdown
- Get work type distribution
- Output: pie chart data of work types
```

**Why**: This is the core value - showing productivity insights.

---

#### **Insights Routes** (`/api/insights`)

**File**: `backend/app/api/insights.py`

```python
GET /api/insights/team
- Get AI-generated team insights
- Output: list of insights (alerts, trends, recommendations)
- Example: "Sarah's productivity dropped 30% - high context switching"
- Manager only

GET /api/insights/developer/:id
- Get AI insights for specific developer
- Output: personal insights and suggestions
- Developers see own, managers see all

POST /api/insights/:id/acknowledge
- Mark insight as acknowledged
- Updates acknowledged_by and acknowledged_at
- For tracking which insights have been acted on
```

**Why**: AI insights are the "intelligence" part - actionable recommendations.

---

### 2. Productivity Scoring Service

**File**: `backend/app/services/productivity_service.py`

**What It Does**:
```python
class ProductivityService:
    def calculate_score_for_developer(
        developer_id,
        start_date,
        end_date
    ) -> ProductivityScore:
        """
        Calculate multi-dimensional productivity score

        Process:
        1. Get all work activities in date range
        2. Get developer's role profile (weights)
        3. Calculate dimension scores:
           - Code Quality: Based on PR reviews, patterns
           - Complexity: Average complexity of work
           - Velocity: Work completed vs estimates
           - Impact: Business value delivered
           - Collaboration: Code reviews, mentoring
           - (Role-specific dimensions)
        4. Apply role-based weights
        5. Generate AI insights
        6. Save ProductivityScore to database
        """
```

**Scoring Algorithm Example**:
```python
# For a Senior Engineer:
weights = {
    "code_quality": 0.30,
    "complexity": 0.25,
    "impact": 0.25,
    "collaboration": 0.20
}

# Calculate each dimension (0-100)
code_quality = analyze_code_quality(activities)  # e.g., 90
complexity = analyze_complexity(activities)      # e.g., 85
impact = analyze_impact(activities)              # e.g., 88
collaboration = analyze_collaboration(activities)# e.g., 92

# Weighted score
overall = (90 * 0.30) + (85 * 0.25) + (88 * 0.25) + (92 * 0.20)
        = 27 + 21.25 + 22 + 18.4
        = 88.65 → 89/100
```

**Why**: This is the core intelligence - converting raw activities into meaningful scores.

---

### 3. Celery Background Tasks

**File**: `backend/app/tasks/sync_tasks.py`

**What We'll Build**:

```python
@celery.task
def sync_github_for_developer(developer_id, days_back=30):
    """
    Background task to sync GitHub activity

    Steps:
    1. Get developer profile
    2. Get organization's GitHub integration
    3. Initialize GitHubService
    4. Sync commits, PRs, code reviews
    5. Update last_sync timestamp
    6. Return sync stats
    """

@celery.task
def sync_jira_for_developer(developer_id, days_back=90):
    """
    Background task to sync Jira activity

    Steps:
    1. Get developer profile
    2. Get organization's Jira integration
    3. Initialize JiraService
    4. Sync tickets and comments
    5. Update last_sync timestamp
    6. Return sync stats
    """

@celery.task
def analyze_git_commits(developer_id, limit=100):
    """
    Background task to run AI analysis on commits

    Steps:
    1. Get unanalyzed commits for developer
    2. For each commit:
       - Get commit diff from GitHub
       - Run CodeComplexityAnalyzer
       - Save analysis_result to commit
       - Create WorkActivity record
    3. Return analysis stats
    """

@celery.task
def analyze_jira_tickets(developer_id, limit=100):
    """
    Background task to run AI analysis on tickets

    Steps:
    1. Get unanalyzed tickets for developer
    2. For each ticket:
       - Get ticket details from Jira
       - Run WorkTypeClassifier
       - Save analysis_result to ticket
       - Create WorkActivity record
    3. Return analysis stats
    """

@celery.task
def calculate_productivity_scores(organization_id, period="weekly"):
    """
    Scheduled task to calculate scores for all developers

    Steps:
    1. Get all developers in organization
    2. For each developer:
       - Calculate score for period
       - Generate AI insights
       - Save to database
    3. Send notifications if configured
    """
```

**Celery Beat Schedule** (runs automatically):
```python
# backend/app/tasks/beat_schedule.py

CELERYBEAT_SCHEDULE = {
    # Sync GitHub every hour
    'sync-github-hourly': {
        'task': 'sync_all_github',
        'schedule': crontab(minute=0, hour='*/1'),
    },

    # Sync Jira every 2 hours
    'sync-jira-every-2-hours': {
        'task': 'sync_all_jira',
        'schedule': crontab(minute=0, hour='*/2'),
    },

    # Run AI analysis every 4 hours
    'analyze-activities': {
        'task': 'analyze_all_activities',
        'schedule': crontab(minute=0, hour='*/4'),
    },

    # Calculate weekly scores (every Monday at 9am)
    'calculate-weekly-scores': {
        'task': 'calculate_productivity_scores',
        'schedule': crontab(minute=0, hour=9, day_of_week=1),
        'kwargs': {'period': 'weekly'}
    },
}
```

**Why**: Background tasks keep data fresh without blocking API requests.

---

### 4. Database Migrations (Alembic)

**File**: `backend/alembic/versions/001_initial_schema.py`

**What It Does**:
- Generates SQL migration scripts from SQLAlchemy models
- Creates all 13 database tables
- Sets up indexes for performance
- Adds foreign key constraints

**Commands**:
```bash
# Initialize Alembic
alembic init alembic

# Auto-generate migration from models
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

**Why**: Professional way to manage database changes over time.

---

## 📊 Data Flow Example

Let's trace a complete workflow:

### **Scenario**: Manager adds a new developer

1. **Manager creates developer** (`POST /api/developers`)
   ```json
   {
     "email": "alice@company.com",
     "github_username": "alice-dev",
     "jira_username": "alice@company.com",
     "role_level": "senior",
     "team": "backend"
   }
   ```

2. **System creates** User + DeveloperProfile in database

3. **Manager triggers GitHub sync** (`POST /api/integrations/1/sync`)

4. **Celery task starts**:
   - `sync_github_for_developer(alice_id, days_back=30)`
   - Fetches last 30 days of commits, PRs, reviews
   - Saves to database (unanalyzed)

5. **Another Celery task analyzes commits**:
   - `analyze_git_commits(alice_id)`
   - For each commit:
     - Get diff from GitHub
     - Call GPT-4o-mini for analysis
     - Save complexity, quality, impact scores
     - Create WorkActivity record

6. **Jira sync runs similarly**:
   - Fetches tickets
   - AI classifies work type
   - Creates more WorkActivity records

7. **Weekly score calculation**:
   - `calculate_productivity_scores(org_id)`
   - Aggregates all WorkActivities
   - Applies role-based weights
   - Calculates overall score: **88/100**
   - Generates insights: "Alice is a strong technical leader. High code quality and mentoring activity."
   - Saves ProductivityScore

8. **Manager views dashboard**:
   - `GET /api/analytics/team`
   - Sees Alice: 88/100 (Senior Engineer)
   - Work breakdown: 50% code, 25% reviews, 15% architecture, 10% meetings
   - Insights: "Strong performer, ready for Staff promotion"

---

## 🎨 What Won't Be Built Yet (Phase 3+)

To keep scope manageable, we're **NOT** building in Phase 2:

- ❌ Frontend dashboards (React components)
- ❌ Charts and visualizations
- ❌ Real-time WebSocket updates
- ❌ Email notifications
- ❌ Advanced AI insights (trend prediction, burnout detection)
- ❌ Export to PDF/CSV
- ❌ Slack integration
- ❌ Custom report builder

These come in later phases after the API works.

---

## 💰 Cost Estimation (AI Usage)

With **GPT-4o-mini** (configured by default):

**Pricing**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens

**Typical Analysis**:
- Commit analysis: ~500 input tokens, ~150 output tokens
- Ticket analysis: ~400 input tokens, ~120 output tokens

**Cost per developer per month**:
- 100 commits analyzed: ~$0.007
- 50 tickets analyzed: ~$0.003
- **Total: ~$0.01 per developer/month**

**For 100 developers**: ~$1/month in AI costs 🎉

**If using Claude Sonnet**: ~$3/million tokens = **~$30/month for 100 devs**

**Recommendation**: Start with GPT-4o-mini, upgrade to Claude Sonnet if you need better code understanding.

---

## 📝 Files That Will Be Created

```
backend/app/api/
├── __init__.py
├── auth.py                  # Authentication endpoints
├── developers.py            # Developer management
├── integrations.py          # GitHub/Jira setup
├── analytics.py             # Productivity analytics
└── insights.py              # AI insights

backend/app/services/
├── productivity_service.py  # Scoring logic
├── insight_service.py       # Insight generation
└── auth_service.py          # JWT tokens, password hashing

backend/app/tasks/
├── __init__.py
├── celery_app.py           # Celery configuration
├── sync_tasks.py           # GitHub/Jira sync tasks
├── analysis_tasks.py       # AI analysis tasks
└── beat_schedule.py        # Scheduled tasks

backend/app/utils/
├── security.py             # Password hashing, JWT
├── scoring.py              # Scoring algorithms
└── pagination.py           # API pagination helpers

backend/app/schemas/
├── __init__.py
├── auth.py                 # Pydantic schemas for auth
├── developer.py            # Schemas for developers
├── analytics.py            # Schemas for analytics
└── integration.py          # Schemas for integrations

backend/alembic/
└── versions/
    └── 001_initial_schema.py

backend/tests/
├── test_api/
├── test_services/
└── test_tasks/
```

**Total**: ~20-25 new files, ~3,000-4,000 lines of code

---

## ⏱️ Time Breakdown

| Task | Estimated Time |
|------|----------------|
| API Routes (5 files) | 3-4 hours |
| Productivity Service | 2-3 hours |
| Celery Tasks | 2-3 hours |
| Auth & Security | 1-2 hours |
| Database Migrations | 1 hour |
| Testing & Debugging | 2-3 hours |
| **Total** | **11-16 hours** |

Realistically: **2-3 development sessions**

---

## ✅ Success Criteria

Phase 2 will be **COMPLETE** when:

1. ✅ You can register and login via API
2. ✅ You can create developers via API
3. ✅ You can configure GitHub/Jira integrations
4. ✅ Background sync pulls real data from GitHub/Jira
5. ✅ AI analysis runs on commits and tickets
6. ✅ Productivity scores are calculated correctly
7. ✅ Analytics API returns meaningful data
8. ✅ All endpoints work via Postman/curl
9. ✅ Database migrations work
10. ✅ Basic tests pass

**Not required**: Frontend, visualizations, email, Slack

---

## 🚀 After Phase 2

You'll have:
- ✅ Fully functional backend API
- ✅ AI-powered analysis engine
- ✅ Background job processing
- ✅ Real productivity scoring
- ✅ Ready for frontend development

You can:
- ✅ Demo via Postman/curl
- ✅ Show real productivity scores
- ✅ Prove the AI works
- ✅ Build frontend dashboards (Phase 3)

---

## 🤔 Questions to Consider Before Starting

1. **Do you want to build all of this?** (Or focus on specific parts?)
2. **Should we add authentication first?** (Or skip for now and use dummy data?)
3. **Do you want to test with your real GitHub/Jira?** (Or use mock data?)
4. **GPT-4o-mini is good enough?** (Or want to keep Claude option?)
5. **Should we add tests as we go?** (Or build tests after?)

---

## 📊 Recommendation

**My suggestion**: Build in this order:

**Session 1** (4-5 hours):
1. Auth endpoints (register, login)
2. Developer endpoints (CRUD)
3. Database migrations
4. Test with Postman

**Session 2** (4-5 hours):
5. Integration endpoints
6. Celery tasks (sync GitHub/Jira)
7. Test syncing real data

**Session 3** (4-5 hours):
8. AI analysis tasks
9. Productivity scoring service
10. Analytics endpoints
11. Full end-to-end test

**Result**: Working backend in 3 sessions!

---

**Ready to start building Phase 2?** Or want to adjust the plan first?
