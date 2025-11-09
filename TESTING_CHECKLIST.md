# DevMetrics AI - Comprehensive Testing Checklist

## Pre-Testing Setup

### Environment Setup
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed (for frontend when ready)
- [ ] PostgreSQL installed and running
- [ ] Redis installed and running
- [ ] All Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables configured in `backend/.env`

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/devmetrics

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Models
AI_MODEL_PROVIDER=openai
AI_MODEL_NAME=gpt-4o-mini
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# GitHub (for testing)
GITHUB_ACCESS_TOKEN=your-github-token
GITHUB_ORG=your-org-name

# Jira (for testing)
JIRA_WORKSPACE_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-jira-token
JIRA_PROJECT_KEY=PROJ
```

### Services to Start
- [ ] PostgreSQL database running
- [ ] Redis server running
- [ ] FastAPI server running (`uvicorn app.main:app --reload`)
- [ ] Celery worker running (`celery -A app.tasks.celery_app worker --loglevel=info`)
- [ ] Celery beat running (`celery -A app.tasks.celery_app beat --loglevel=info`)
- [ ] (Optional) Flower monitoring (`celery -A app.tasks.celery_app flower --port=5555`)

---

## Session 1: Authentication & Developer Management

### Database Migrations
- [ ] Run `alembic upgrade head` successfully
- [ ] Verify all 13 tables created in PostgreSQL
- [ ] Check table schemas match model definitions

### Authentication API Tests

#### User Registration
- [ ] Register admin user (role: admin)
- [ ] Register manager user (role: manager)
- [ ] Register developer user (role: developer)
- [ ] Verify password is hashed in database
- [ ] Test duplicate email rejection
- [ ] Test invalid email format rejection
- [ ] Test weak password rejection

#### User Login
- [ ] Login with valid admin credentials
- [ ] Login with valid manager credentials
- [ ] Login with valid developer credentials
- [ ] Verify JWT token is returned
- [ ] Test login with wrong password
- [ ] Test login with non-existent email
- [ ] Verify token expiration works

#### User Profile
- [ ] GET /api/auth/me with valid token
- [ ] Verify correct user data returned
- [ ] Test with invalid token
- [ ] Test with expired token
- [ ] Test without Authorization header

### Developer Management API Tests

#### Create Developer Profile (Manager/Admin Only)
- [ ] Admin can create developer profile
- [ ] Manager can create developer profile
- [ ] Developer cannot create profile (403)
- [ ] Create intern-level developer
- [ ] Create junior-level developer
- [ ] Create mid-level developer
- [ ] Create senior-level developer
- [ ] Create staff-level developer
- [ ] Create principal-level developer
- [ ] Verify GitHub username stored
- [ ] Verify Jira username stored
- [ ] Test with missing required fields

#### List Developers
- [ ] Get all developers (no filters)
- [ ] Filter by team
- [ ] Filter by role_level
- [ ] Filter by both team and role_level
- [ ] Verify pagination works (if implemented)
- [ ] All user roles can list developers

#### Get Single Developer
- [ ] Get developer by valid ID
- [ ] Get non-existent developer (404)
- [ ] Verify all fields returned correctly
- [ ] Developer can see their own profile
- [ ] Manager can see any developer profile

#### Update Developer Profile (Manager/Admin Only)
- [ ] Update developer's role_level
- [ ] Update developer's team
- [ ] Update GitHub username
- [ ] Update Jira username
- [ ] Update skills
- [ ] Developer cannot update (403)
- [ ] Test partial updates
- [ ] Verify updated_at timestamp changes

#### Delete Developer Profile (Admin Only)
- [ ] Admin can delete developer
- [ ] Manager cannot delete (403)
- [ ] Developer cannot delete (403)
- [ ] Delete non-existent developer (404)
- [ ] Verify cascading deletes work

### Automated Test Script
- [ ] Run `./backend/test_api.sh`
- [ ] All 12 tests pass
- [ ] No authorization bypass issues
- [ ] Role-based access control working

---

## Session 2: Integrations & Background Tasks

### Integration Configuration

#### GitHub Integration
- [ ] POST /api/integrations/github with valid token
- [ ] Connection test passes before saving
- [ ] Configuration saved in database
- [ ] Test with invalid GitHub token (400)
- [ ] Test without admin role (403)
- [ ] Update existing GitHub integration
- [ ] Verify access token encrypted/secure

#### Jira Integration
- [ ] POST /api/integrations/jira with valid credentials
- [ ] Connection test passes before saving
- [ ] Configuration saved in database
- [ ] Test with invalid Jira credentials (400)
- [ ] Test without admin role (403)
- [ ] Update existing Jira integration
- [ ] Verify API token encrypted/secure

#### List Integrations
- [ ] GET /api/integrations/ returns all integrations
- [ ] Shows GitHub integration with status
- [ ] Shows Jira integration with status
- [ ] Shows last_sync_at timestamp
- [ ] Shows any error messages

#### Test Integration Connection
- [ ] POST /api/integrations/{id}/test for GitHub
- [ ] POST /api/integrations/{id}/test for Jira
- [ ] Returns success=true for valid config
- [ ] Returns success=false for invalid config
- [ ] Only admin can test (403 for others)

#### Delete Integration
- [ ] DELETE /api/integrations/{id} as admin
- [ ] Manager cannot delete (403)
- [ ] Developer cannot delete (403)
- [ ] Delete non-existent integration (404)

### Background Sync Tasks

#### GitHub Sync
- [ ] Trigger manual GitHub sync
- [ ] Verify job_id returned
- [ ] Check Celery worker logs for task execution
- [ ] Verify commits synced to database
- [ ] Verify pull requests synced to database
- [ ] Verify code reviews synced to database
- [ ] Check sync statistics returned
- [ ] Verify last_sync_at updated
- [ ] Test with multiple developers
- [ ] Test with 0 commits (no errors)

#### Jira Sync
- [ ] Trigger manual Jira sync
- [ ] Verify job_id returned
- [ ] Check Celery worker logs for task execution
- [ ] Verify tickets synced to database
- [ ] Verify comments synced to database
- [ ] Check sync statistics returned
- [ ] Verify last_sync_at updated
- [ ] Test with multiple developers
- [ ] Test with 0 tickets (no errors)

#### Sync Status Monitoring
- [ ] GET /api/integrations/{id}/status shows ACTIVE
- [ ] Status shows SYNCING during sync
- [ ] Status shows ERROR on failure
- [ ] last_error populated on failure
- [ ] last_sync_at updates after success

#### Periodic Sync (Celery Beat)
- [ ] GitHub sync runs every 2 hours
- [ ] Jira sync runs every 3 hours
- [ ] Check Beat scheduler logs
- [ ] Verify tasks triggered automatically
- [ ] No duplicate tasks created

### AI Analysis Tasks

#### Commit Analysis
- [ ] Trigger analyze_git_commits task
- [ ] Verify CodeComplexityAnalyzer called
- [ ] Check AI response parsed correctly
- [ ] Verify WorkActivity records created
- [ ] Verify complexity_score calculated
- [ ] Verify impact_score calculated
- [ ] Verify quality_score calculated
- [ ] Verify work_type assigned
- [ ] Check commits marked as analyzed
- [ ] Verify batch processing (10 commits)
- [ ] Test with GPT-4o-mini (cost check)
- [ ] Test with Claude Sonnet (if configured)

#### Ticket Analysis
- [ ] Trigger analyze_jira_tickets task
- [ ] Verify WorkTypeClassifier called
- [ ] Check AI response parsed correctly
- [ ] Verify WorkActivity records created
- [ ] Verify ticket work_type detected
- [ ] Verify complexity estimated
- [ ] Verify time estimate calculated
- [ ] Check tickets marked as analyzed
- [ ] Test with ticket comments
- [ ] Verify artifact detection

#### Periodic Analysis (Celery Beat)
- [ ] Analysis runs every 4 hours
- [ ] Processes all unanalyzed items
- [ ] Check Beat scheduler logs
- [ ] Verify analyze_all_unanalyzed triggers
- [ ] No duplicate analysis

### Celery Infrastructure
- [ ] Redis connection working
- [ ] Celery worker starts without errors
- [ ] Celery beat starts without errors
- [ ] Tasks appear in worker logs
- [ ] Task results stored in Redis
- [ ] Task retry logic works on failure
- [ ] No memory leaks in long-running workers

### Automated Test Script
- [ ] Run `./backend/test_integrations.sh`
- [ ] Set environment variables first
- [ ] All integration tests pass
- [ ] Sync jobs triggered successfully
- [ ] Status checks work

---

## Session 3: Analytics & Productivity Scoring

### Productivity Scoring Service

#### Score Calculation
- [ ] Calculate complexity score (0-10)
- [ ] Calculate velocity score (0-10)
- [ ] Calculate quality score (0-10)
- [ ] Calculate impact score (0-10)
- [ ] Calculate collaboration score (0-10)
- [ ] Calculate mentoring score (0-10)
- [ ] Calculate overall productivity score (0-100)
- [ ] Verify weighted averaging works

#### Role-Based Evaluation
- [ ] Intern evaluation uses correct weights
- [ ] Junior evaluation uses correct weights
- [ ] Mid-level evaluation uses correct weights
- [ ] Senior evaluation uses correct weights
- [ ] Staff evaluation uses correct weights
- [ ] Principal evaluation uses correct weights
- [ ] Custom role weights can be configured

#### Historical Trends
- [ ] Calculate weekly trends
- [ ] Calculate monthly trends
- [ ] Calculate quarterly trends
- [ ] Identify improving trends
- [ ] Identify declining trends
- [ ] Detect anomalies

### Analytics API Endpoints

#### Individual Developer Analytics
- [ ] GET /api/analytics/developers/{id}/overview
- [ ] GET /api/analytics/developers/{id}/productivity
- [ ] GET /api/analytics/developers/{id}/trends
- [ ] GET /api/analytics/developers/{id}/work-breakdown
- [ ] Filter by date range
- [ ] Developer can see own analytics
- [ ] Manager can see all analytics
- [ ] Developer cannot see others (403)

#### Team Analytics
- [ ] GET /api/analytics/teams/{team}/overview
- [ ] GET /api/analytics/teams/{team}/productivity
- [ ] GET /api/analytics/teams/{team}/comparison
- [ ] Aggregate team metrics correctly
- [ ] Show top performers
- [ ] Show areas for improvement

#### Comparison & Benchmarking
- [ ] Compare developer to team average
- [ ] Compare developer to role average
- [ ] Compare teams
- [ ] Anonymized comparison (no names)
- [ ] Role-normalized scores

### AI Insights Generation

#### Pattern Detection
- [ ] Detect productivity patterns
- [ ] Identify work style patterns
- [ ] Detect optimal work times
- [ ] Identify collaboration patterns

#### Recommendations
- [ ] Generate productivity recommendations
- [ ] Suggest skill development areas
- [ ] Recommend optimal task types
- [ ] Suggest mentoring opportunities

#### Anomaly Detection
- [ ] Detect unusual activity spikes
- [ ] Detect unusual activity drops
- [ ] Flag potential burnout indicators
- [ ] Identify blocked developers

---

## Integration Tests (End-to-End)

### Complete Workflow Tests

#### New Developer Onboarding Flow
1. [ ] Admin registers in system
2. [ ] Admin configures GitHub integration
3. [ ] Admin configures Jira integration
4. [ ] Manager creates developer profile
5. [ ] Sync triggers automatically
6. [ ] Developer data appears in database
7. [ ] AI analysis runs automatically
8. [ ] Productivity scores calculated
9. [ ] Developer can view own dashboard
10. [ ] Manager can view team dashboard

#### Daily Operations Flow
1. [ ] Developer commits code to GitHub
2. [ ] Developer updates Jira ticket
3. [ ] Periodic sync runs (2-4 hours later)
4. [ ] New commits synced to database
5. [ ] New tickets synced to database
6. [ ] AI analysis runs automatically
7. [ ] Productivity scores updated
8. [ ] Analytics refresh with new data
9. [ ] Insights generated
10. [ ] Dashboard shows latest data

#### Manager Review Flow
1. [ ] Manager logs in
2. [ ] Views team overview
3. [ ] Filters by date range
4. [ ] Views individual developer
5. [ ] Sees productivity breakdown
6. [ ] Sees work type distribution
7. [ ] Sees AI-generated insights
8. [ ] Compares to team average
9. [ ] Exports report (if implemented)

---

## Performance Tests

### API Performance
- [ ] /api/auth/login responds < 200ms
- [ ] /api/developers/ responds < 500ms
- [ ] /api/analytics/* responds < 1s
- [ ] Handle 100 concurrent requests
- [ ] No memory leaks with sustained load

### Database Performance
- [ ] Query developer analytics < 500ms
- [ ] Query team analytics < 1s
- [ ] Indexes created on foreign keys
- [ ] Indexes created on frequently queried fields
- [ ] No N+1 query issues

### Background Task Performance
- [ ] Process 100 commits < 2 minutes
- [ ] Process 100 tickets < 2 minutes
- [ ] AI analysis batch size optimal
- [ ] No task queue buildup
- [ ] Redis memory usage acceptable

---

## Security Tests

### Authentication & Authorization
- [ ] JWT tokens expire correctly
- [ ] Expired tokens rejected
- [ ] Invalid tokens rejected
- [ ] Missing tokens rejected (401)
- [ ] Role-based access enforced
- [ ] Cannot bypass role checks
- [ ] Password hashing secure (bcrypt)
- [ ] No passwords in logs/responses

### Data Security
- [ ] API tokens encrypted in database
- [ ] Access tokens not in responses
- [ ] Sensitive data not in logs
- [ ] SQL injection prevented (SQLAlchemy ORM)
- [ ] No data leakage between orgs
- [ ] Developer cannot see others' data

### API Security
- [ ] CORS configured correctly
- [ ] Rate limiting (if implemented)
- [ ] Input validation on all endpoints
- [ ] No XSS vulnerabilities
- [ ] No CSRF vulnerabilities
- [ ] Error messages don't leak info

---

## Data Validation Tests

### GitHub Data
- [ ] Commits have valid SHAs
- [ ] Commit timestamps parsed correctly
- [ ] File counts accurate
- [ ] Additions/deletions accurate
- [ ] PR references valid
- [ ] Author attribution correct

### Jira Data
- [ ] Ticket keys valid format
- [ ] Status values correct
- [ ] Priority values correct
- [ ] Timestamps parsed correctly
- [ ] Comments attributed correctly
- [ ] Assignee mapping correct

### AI Analysis Data
- [ ] Complexity scores in range 0-10
- [ ] Impact scores in range 0-10
- [ ] Quality scores in range 0-10
- [ ] Work types valid enum values
- [ ] Time estimates reasonable
- [ ] JSON analysis parseable

### Productivity Scores
- [ ] All scores in valid ranges
- [ ] Overall score 0-100
- [ ] Component scores 0-10
- [ ] Weights sum to 1.0
- [ ] No negative scores
- [ ] No NaN/Infinity values

---

## Error Handling Tests

### API Error Handling
- [ ] 400 Bad Request for invalid input
- [ ] 401 Unauthorized for missing auth
- [ ] 403 Forbidden for insufficient permissions
- [ ] 404 Not Found for missing resources
- [ ] 500 Internal Server Error logged properly
- [ ] Error messages user-friendly
- [ ] Stack traces not exposed

### Background Task Error Handling
- [ ] GitHub API rate limit handled
- [ ] Jira API errors caught
- [ ] AI API errors handled gracefully
- [ ] Tasks retry on transient failures
- [ ] Failed tasks don't crash worker
- [ ] Errors logged with context
- [ ] Integration status updated on error

### Database Error Handling
- [ ] Connection failures handled
- [ ] Constraint violations caught
- [ ] Transactions rolled back on error
- [ ] Deadlocks retried
- [ ] No data corruption on errors

---

## Monitoring & Observability

### Logging
- [ ] Application logs structured
- [ ] Log levels appropriate
- [ ] Sensitive data not logged
- [ ] Errors logged with context
- [ ] Background tasks logged
- [ ] Performance metrics logged

### Metrics (if implemented)
- [ ] API request counts
- [ ] API response times
- [ ] Task execution times
- [ ] Task success/failure rates
- [ ] Database query times
- [ ] AI API usage/costs

### Celery Monitoring
- [ ] Flower dashboard accessible
- [ ] Task states visible
- [ ] Worker health visible
- [ ] Queue lengths monitored
- [ ] Failed tasks tracked

---

## Regression Tests

### After Each New Feature
- [ ] All previous API endpoints still work
- [ ] No breaking changes to schemas
- [ ] Background tasks still execute
- [ ] Database migrations compatible
- [ ] Performance not degraded

### Before Each Release
- [ ] Run all automated test scripts
- [ ] Manual smoke testing complete
- [ ] No critical bugs open
- [ ] Documentation updated
- [ ] Migration path tested

---

## Documentation Tests

### API Documentation
- [ ] OpenAPI/Swagger docs accessible at /docs
- [ ] All endpoints documented
- [ ] Request schemas documented
- [ ] Response schemas documented
- [ ] Authentication requirements clear
- [ ] Examples provided

### Code Documentation
- [ ] All modules have docstrings
- [ ] All classes have docstrings
- [ ] All public functions documented
- [ ] Complex logic has comments
- [ ] TODOs tracked

### User Documentation
- [ ] README.md up to date
- [ ] Setup instructions complete
- [ ] Environment variables documented
- [ ] Testing guide available
- [ ] Troubleshooting guide available

---

## Test Automation Scripts Location

- `backend/test_api.sh` - Session 1 tests
- `backend/test_integrations.sh` - Session 2 tests
- `backend/test_analytics.sh` - Session 3 tests (to be created)
- `backend/test_e2e.sh` - End-to-end tests (to be created)

---

## Notes

- Run tests in order: Session 1 → Session 2 → Session 3 → Integration
- Ensure all services running before testing
- Check logs for errors even if tests pass
- Test with real GitHub/Jira data for accuracy
- Monitor AI API costs during testing
- Use staging database for destructive tests
- Document any test failures with reproduction steps

---

**Last Updated:** 2025-11-09
**Status:** Sessions 1 & 2 complete, Session 3 in progress
