# DevMetrics AI - Engineering Intelligence Platform

## Project Overview

An AI-powered engineering productivity analytics platform that analyzes developer contributions across GitHub/Bitbucket and Jira to provide intelligent insights on productivity, code complexity, and team performance.

---

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (with SQLAlchemy ORM)
- **AI/ML**:
  - LangChain for agent orchestration
  - Claude API (Anthropic) for code analysis
  - OpenAI API (fallback/comparison)
- **Task Queue**: Celery + Redis (for async data sync)
- **Caching**: Redis
- **API Integrations**:
  - PyGithub (GitHub API)
  - Atlassian Python API (Jira)
  - GitPython (Git operations)

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **UI Library**:
  - TailwindCSS
  - shadcn/ui (component library)
  - Framer Motion (animations)
- **Charts**: Recharts
- **State Management**: Zustand
- **API Client**: Axios + SWR (data fetching)

### DevOps & Tools
- **Containerization**: Docker + Docker Compose
- **Environment**: Python venv, Node 20+
- **Code Quality**: Ruff (Python), ESLint (JS)
- **Database Migrations**: Alembic

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Manager    │  │  Developer   │  │    Admin     │     │
│  │  Dashboard   │  │  Dashboard   │  │    Panel     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                    REST API (HTTP/JSON)
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Layer (Routes)                      │  │
│  │  /auth  /teams  /developers  /analytics  /insights  │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Business Logic Layer                       │  │
│  │  - Productivity Scoring                              │  │
│  │  - Work Classification                               │  │
│  │  - Team Analytics                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        AI Agent Layer (LangChain)                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │   Code   │  │   Work   │  │  Impact  │          │  │
│  │  │ Analyzer │  │Classifier│  │  Scorer  │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Integration Layer (Celery Tasks)               │  │
│  │  - GitHub Data Sync                                  │  │
│  │  - Jira Data Sync                                    │  │
│  │  - Periodic Analysis Jobs                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    PostgreSQL           Redis              External APIs
  (Primary Data)       (Cache/Queue)      (GitHub/Jira)
```

---

## Database Schema

### Core Tables

```sql
-- Users & Authentication
users
  - id (PK)
  - email
  - name
  - role (manager, developer, admin)
  - created_at

-- Organizations
organizations
  - id (PK)
  - name
  - github_org
  - jira_workspace
  - created_at

-- Developer Profiles
developer_profiles
  - id (PK)
  - user_id (FK)
  - organization_id (FK)
  - role_level (intern, junior, mid, senior, staff, principal)
  - team
  - github_username
  - jira_username
  - start_date
  - focus_areas (JSON)
  - created_at

-- Role Profiles (Templates)
role_profiles
  - id (PK)
  - role_level
  - expected_work_types (JSON)
  - complexity_expectation
  - evaluation_criteria (JSON)

-- Integration Configs
integration_configs
  - id (PK)
  - organization_id (FK)
  - type (github, jira, slack)
  - credentials (encrypted JSON)
  - status (active, inactive)
  - last_sync_at

-- Git Commits
git_commits
  - id (PK)
  - developer_id (FK)
  - repo_name
  - commit_sha
  - message
  - files_changed
  - additions
  - deletions
  - committed_at
  - analyzed (boolean)
  - analysis_result (JSON)

-- Pull Requests
pull_requests
  - id (PK)
  - developer_id (FK)
  - repo_name
  - pr_number
  - title
  - description
  - state (open, merged, closed)
  - files_changed
  - additions
  - deletions
  - created_at
  - merged_at
  - analysis_result (JSON)

-- Code Reviews
code_reviews
  - id (PK)
  - reviewer_id (FK)
  - pr_id (FK)
  - comment_count
  - quality_score (AI-generated)
  - reviewed_at
  - analysis_result (JSON)

-- Jira Tickets
jira_tickets
  - id (PK)
  - developer_id (FK)
  - ticket_key
  - title
  - description
  - status
  - type (story, bug, task, research)
  - story_points
  - created_at
  - updated_at
  - resolved_at
  - analysis_result (JSON)

-- Jira Comments
jira_comments
  - id (PK)
  - ticket_id (FK)
  - developer_id (FK)
  - comment_text
  - created_at
  - analysis_result (JSON)

-- Work Activities (AI-analyzed work)
work_activities
  - id (PK)
  - developer_id (FK)
  - activity_date
  - work_type (code, research, documentation, dashboard, meeting, etc.)
  - complexity_score (1-10)
  - impact_score (1-10)
  - quality_score (1-10)
  - time_estimate_hours
  - source_type (git, jira)
  - source_id
  - ai_analysis (JSON)
  - artifacts (JSON array)

-- Productivity Scores
productivity_scores
  - id (PK)
  - developer_id (FK)
  - period_start
  - period_end
  - overall_score
  - code_quality_score
  - complexity_score
  - impact_score
  - collaboration_score
  - mentoring_score
  - breakdown (JSON)
  - insights (JSON)
  - calculated_at

-- AI Insights
ai_insights
  - id (PK)
  - organization_id (FK)
  - developer_id (FK, nullable for team insights)
  - insight_type (individual, team, trend, alert)
  - title
  - description
  - priority (low, medium, high)
  - created_at
  - acknowledged (boolean)
```

---

## API Endpoints

### Authentication
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me
```

### Organizations
```
POST   /api/organizations
GET    /api/organizations/:id
PATCH  /api/organizations/:id
```

### Developer Management
```
POST   /api/developers
GET    /api/developers
GET    /api/developers/:id
PATCH  /api/developers/:id
DELETE /api/developers/:id
```

### Integrations
```
POST   /api/integrations/github
POST   /api/integrations/jira
GET    /api/integrations
PATCH  /api/integrations/:id
DELETE /api/integrations/:id
POST   /api/integrations/:id/sync  (trigger manual sync)
```

### Analytics
```
GET    /api/analytics/team
GET    /api/analytics/developer/:id
GET    /api/analytics/developer/:id/timeline
GET    /api/analytics/developer/:id/work-breakdown
GET    /api/analytics/team/comparison
```

### Insights
```
GET    /api/insights/team
GET    /api/insights/developer/:id
POST   /api/insights/:id/acknowledge
```

### Admin
```
GET    /api/admin/sync-status
POST   /api/admin/trigger-analysis
GET    /api/admin/system-health
```

---

## AI Agent System

### 1. Code Complexity Analyzer Agent

**Purpose**: Analyze git commits and PRs for technical complexity

**Inputs**:
- Commit diffs
- File changes
- Commit messages
- PR descriptions

**Analysis**:
- Cyclomatic complexity (using AST parsing)
- Cognitive complexity
- Architectural impact (core vs peripheral)
- Code quality patterns
- Technical debt addition/removal

**Output**:
```json
{
  "complexity_score": 8,
  "quality_score": 7,
  "impact_level": "high",
  "work_type": "refactoring",
  "explanation": "Major architectural change to authentication system...",
  "technical_debt_delta": -15,
  "affected_systems": ["auth", "user-service"],
  "novelty": "high"
}
```

### 2. Work Type Classifier Agent

**Purpose**: Classify Jira tickets into work types

**Inputs**:
- Ticket title
- Ticket description
- Comments
- Linked PRs
- Attachments

**Analysis**:
- Primary work type detection
- Complexity estimation
- Time estimation
- Artifact identification

**Output**:
```json
{
  "work_type": "research",
  "sub_type": "technology_evaluation",
  "complexity_score": 8,
  "impact_score": 9,
  "time_estimate_hours": 16,
  "artifacts": [
    {"type": "document", "url": "..."},
    {"type": "benchmark", "description": "..."}
  ],
  "explanation": "Deep technical research with benchmarking..."
}
```

### 3. Impact Scorer Agent

**Purpose**: Determine business and technical impact

**Inputs**:
- Work activity data
- Codebase context
- Team context

**Analysis**:
- Customer-facing impact
- Critical path determination
- System reliability impact
- Team enablement impact

**Output**:
```json
{
  "impact_score": 9,
  "impact_areas": ["reliability", "performance", "customer_experience"],
  "affected_users": "10K+",
  "business_value": "high",
  "explanation": "Fixed critical payment bug affecting..."
}
```

### 4. Collaboration Analyzer Agent

**Purpose**: Analyze team collaboration and mentoring

**Inputs**:
- Code review comments
- PR review activity
- Jira comments
- Mentions in tickets

**Analysis**:
- Review quality
- Mentoring indicators
- Knowledge sharing
- Cross-team collaboration

**Output**:
```json
{
  "collaboration_score": 9,
  "reviews_given": 12,
  "review_quality": "excellent",
  "mentoring_count": 3,
  "knowledge_sharing_instances": 5,
  "explanation": "Provided detailed reviews with code examples..."
}
```

---

## Productivity Scoring Algorithm

### Role-Based Weighted Scoring

```python
def calculate_productivity_score(developer, period):
    """
    Multi-dimensional scoring based on developer role
    """
    role = developer.role_level
    weights = get_role_weights(role)

    # Gather all activities in period
    activities = get_activities(developer, period)

    # Calculate dimension scores
    scores = {
        'code_quality': calculate_code_quality(activities),
        'complexity': calculate_complexity(activities),
        'velocity': calculate_velocity(activities),
        'impact': calculate_impact(activities),
        'collaboration': calculate_collaboration(activities),
        'mentoring': calculate_mentoring(activities),
        'learning': calculate_learning(activities)
    }

    # Apply role-specific weights
    weighted_score = sum(
        scores[dim] * weights.get(dim, 0)
        for dim in scores
    )

    # Normalize to 0-100
    final_score = min(100, max(0, weighted_score))

    return {
        'overall': final_score,
        'breakdown': scores,
        'weights': weights
    }
```

### Dimension Calculations

**Code Quality (0-100)**:
- Best practices adherence
- Test coverage changes
- Code review feedback
- Bug introduction rate

**Complexity (0-100)**:
- Average complexity of work
- Novel vs routine work ratio
- Architectural contributions
- Problem-solving depth

**Velocity (0-100)**:
- Work completion rate
- Story points vs estimates
- Cycle time efficiency
- Consistency over time

**Impact (0-100)**:
- Business value delivered
- Critical bug fixes
- Performance improvements
- User-facing changes

**Collaboration (0-100)**:
- Code review quality & quantity
- Helping team members
- Documentation contributions
- Knowledge sharing

**Mentoring (0-100)** (Senior+ only):
- Junior developer support
- Pair programming
- Technical guidance
- Onboarding contributions

**Learning (0-100)** (Junior/Intern focus):
- Skill acquisition
- Complexity progression
- Independence growth
- Feedback incorporation

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal**: Basic infrastructure and data ingestion

- [x] Project setup (backend + frontend)
- [ ] Database schema implementation
- [ ] Authentication system
- [ ] GitHub integration (basic)
- [ ] Jira integration (basic)
- [ ] Data sync jobs (Celery)
- [ ] Basic API endpoints

**Deliverable**: Can pull data from GitHub and Jira into database

### Phase 2: AI Analysis (Week 3-4)
**Goal**: Intelligent work analysis

- [ ] LangChain agent setup
- [ ] Code complexity analyzer
- [ ] Work type classifier
- [ ] Basic productivity scoring
- [ ] Analysis pipeline
- [ ] Scheduled analysis jobs

**Deliverable**: AI can analyze commits and tickets

### Phase 3: Frontend Dashboard (Week 4-5)
**Goal**: User interfaces

- [ ] Developer dashboard
  - Personal score
  - Work breakdown
  - Timeline view
  - Contribution details
- [ ] Manager dashboard
  - Team overview
  - Individual deep dives
  - Comparison views
- [ ] Admin panel
  - Team setup
  - Role assignment
  - Integration management

**Deliverable**: Functional dashboards showing data

### Phase 4: Intelligence & Insights (Week 5-6)
**Goal**: AI-generated insights

- [ ] Insight generation system
- [ ] Trend detection
- [ ] Alert system
- [ ] Recommendations engine
- [ ] Weekly summaries

**Deliverable**: Platform generates actionable insights

### Phase 5: Polish & Scale (Week 6+)
**Goal**: Production-ready

- [ ] Performance optimization
- [ ] Error handling
- [ ] Loading states
- [ ] Animations (Framer Motion)
- [ ] Responsive design
- [ ] Documentation
- [ ] Demo data seeding

**Deliverable**: Production-ready platform

---

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@localhost:5432/devmetrics
REDIS_URL=redis://localhost:6379/0

# AI APIs
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...

# Integrations
GITHUB_APP_ID=
GITHUB_APP_SECRET=
JIRA_API_TOKEN=

# Security
JWT_SECRET_KEY=
ENCRYPTION_KEY=

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## Project Structure

```
devmetrics-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Configuration
│   │   ├── database.py             # DB connection
│   │   │
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   ├── developer.py
│   │   │   ├── git_commit.py
│   │   │   ├── jira_ticket.py
│   │   │   └── productivity_score.py
│   │   │
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── developer.py
│   │   │   ├── analytics.py
│   │   │   └── integration.py
│   │   │
│   │   ├── api/                    # API routes
│   │   │   ├── auth.py
│   │   │   ├── developers.py
│   │   │   ├── analytics.py
│   │   │   ├── integrations.py
│   │   │   └── insights.py
│   │   │
│   │   ├── services/               # Business logic
│   │   │   ├── github_service.py
│   │   │   ├── jira_service.py
│   │   │   ├── productivity_service.py
│   │   │   └── insight_service.py
│   │   │
│   │   ├── ai/                     # AI agents
│   │   │   ├── agents/
│   │   │   │   ├── code_analyzer.py
│   │   │   │   ├── work_classifier.py
│   │   │   │   ├── impact_scorer.py
│   │   │   │   └── collaboration_analyzer.py
│   │   │   ├── orchestrator.py     # LangGraph orchestration
│   │   │   └── prompts/            # Prompt templates
│   │   │
│   │   ├── tasks/                  # Celery tasks
│   │   │   ├── sync_github.py
│   │   │   ├── sync_jira.py
│   │   │   └── analyze_activities.py
│   │   │
│   │   └── utils/
│   │       ├── security.py
│   │       ├── code_parser.py
│   │       └── scoring.py
│   │
│   ├── alembic/                    # DB migrations
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js app router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx        # Developer dashboard
│   │   │   ├── manager/
│   │   │   │   └── page.tsx        # Manager dashboard
│   │   │   └── admin/
│   │   │       └── page.tsx        # Admin panel
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn components
│   │   │   ├── charts/             # Chart components
│   │   │   ├── developer/
│   │   │   │   ├── ScoreCard.tsx
│   │   │   │   ├── WorkBreakdown.tsx
│   │   │   │   └── Timeline.tsx
│   │   │   └── manager/
│   │   │       ├── TeamOverview.tsx
│   │   │       ├── DeveloperCard.tsx
│   │   │       └── InsightsList.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts              # API client
│   │   │   └── utils.ts
│   │   │
│   │   └── store/                  # Zustand stores
│   │       └── useAuthStore.ts
│   │
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
│
└── README.md
```

---

## Development Workflow

### 1. Initial Setup
```bash
# Clone repo
git clone <repo-url>
cd devmetrics-ai

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database setup
docker-compose up -d postgres redis
alembic upgrade head

# Frontend setup
cd ../frontend
npm install

# Run dev servers
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: Celery worker
cd backend && celery -A app.tasks worker --loglevel=info

# Terminal 3: Frontend
cd frontend && npm run dev
```

### 2. Daily Development
- Pull latest from git
- Run migrations if any
- Start all services (backend, celery, frontend)
- Make changes
- Test locally
- Commit with clear messages

### 3. Testing
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test
```

---

## Next Steps (Immediate)

1. **Create project structure**
2. **Setup database with models**
3. **Build GitHub integration**
4. **Build Jira integration**
5. **Create basic API endpoints**
6. **Setup frontend with basic UI**
7. **Implement AI agents**
8. **Build dashboards**

---

## Notes & Decisions

### Why These Technologies?
- **FastAPI**: Fast, async, great for AI integration
- **Next.js**: Best DX, SSR, great performance
- **PostgreSQL**: Relational data, complex queries
- **LangChain**: Agent orchestration, tool calling
- **Claude API**: Best for code understanding
- **Celery**: Robust task queue for background jobs

### Design Decisions
- **Multi-dimensional scoring**: Avoids oversimplification
- **Role-based weights**: Fair comparison across levels
- **Transparent metrics**: Developers see what managers see
- **AI explanations**: Every score has reasoning
- **Flexible work types**: Captures non-code work

### Future Enhancements
- Slack integration
- Bitbucket/GitLab support
- Mobile app
- Custom report builder
- API webhooks
- SSO/SAML
- White-label option
- Advanced ML models (trend prediction)

---

## Success Metrics

### MVP Success:
- [ ] Can sync GitHub data for 10 developers
- [ ] Can sync Jira data for 10 developers
- [ ] AI correctly classifies work types (>80% accuracy)
- [ ] Productivity scores make sense to managers
- [ ] Dashboard loads in <2 seconds
- [ ] Can demo full workflow in 10 minutes

### Production Success:
- [ ] 100+ developers tracked
- [ ] <5 min data lag
- [ ] 95% uptime
- [ ] Positive feedback from managers
- [ ] Developers find personal dashboards useful

---

**Last Updated**: 2025-11-09
**Status**: Phase 1 - Foundation (Starting)
