# Session 3 Complete: Analytics & Productivity Scoring

## Overview

Session 3 successfully implements the core analytics and productivity scoring system for DevMetrics AI. This session builds upon Sessions 1 & 2 and adds:

- Multi-dimensional productivity scoring with role-based evaluation
- Comprehensive analytics API endpoints
- AI-powered insights generation
- Historical trend analysis
- Team analytics and comparisons
- Intelligent recommendations

## What Was Built

### 1. Productivity Scoring Service

**File:** `backend/app/services/scoring_service.py`

Implements sophisticated productivity scoring with 6 dimensions:

**Score Components (0-10 each):**
1. **Complexity Score** - Difficulty of work tackled
2. **Velocity Score** - Consistent output and momentum
3. **Quality Score** - Code quality and standards adherence
4. **Impact Score** - Business and technical impact
5. **Collaboration Score** - Teamwork and code reviews
6. **Mentoring Score** - Knowledge sharing and helping others

**Role-Based Evaluation Weights:**

Different roles have different expectations:

```python
INTERN:
- complexity: 10%, velocity: 15%, quality: 25%
- impact: 10%, collaboration: 25%, mentoring: 15%
# Focus on learning and quality

JUNIOR:
- complexity: 15%, velocity: 20%, quality: 25%
- impact: 15%, collaboration: 20%, mentoring: 5%
# Balanced growth

MID:
- complexity: 20%, velocity: 20%, quality: 20%
- impact: 20%, collaboration: 15%, mentoring: 5%
# Well-rounded expectations

SENIOR:
- complexity: 25%, velocity: 15%, quality: 20%
- impact: 25%, collaboration: 10%, mentoring: 5%
# Complex problems, high impact

STAFF:
- complexity: 25%, velocity: 10%, quality: 20%
- impact: 30%, collaboration: 5%, mentoring: 10%
# Organizational impact, mentoring

PRINCIPAL:
- complexity: 20%, velocity: 5%, quality: 20%
- impact: 35%, collaboration: 10%, mentoring: 10%
# Strategic impact, technical leadership
```

**Key Methods:**
- `calculate_developer_score()` - Calculate comprehensive productivity score
- `calculate_team_scores()` - Aggregate team productivity
- `get_score_trends()` - Historical productivity trends
- `save_score()` - Persist scores to database

### 2. Analytics API Layer

**File:** `backend/app/schemas/analytics.py`

Created comprehensive schemas for analytics:
- `ProductivityScoreResponse` - Detailed score breakdown
- `DeveloperAnalyticsOverview` - Summary analytics
- `DeveloperProductivityResponse` - Detailed productivity
- `DeveloperTrendsResponse` - Historical trends
- `WorkBreakdownResponse` - Work type distribution
- `TeamAnalyticsOverview` - Team aggregate scores
- `DeveloperComparisonResponse` - Comparison to benchmarks
- `DeveloperInsightsResponse` - AI-generated insights
- `ScoreCalculationRequest/Response` - Score calculation

**File:** `backend/app/api/analytics.py`

Created 8 REST API endpoints:

1. **GET /api/analytics/developers/{id}/overview**
   - Summary analytics for developer
   - Activity counts, productivity score, work breakdown
   - Accessible by developer (own data) or manager/admin

2. **GET /api/analytics/developers/{id}/productivity**
   - Detailed productivity breakdown
   - All 6 score components
   - Role-based evaluation weights
   - Optional comparison to team/role averages
   - Accessible by developer (own data) or manager/admin

3. **GET /api/analytics/developers/{id}/trends**
   - Historical productivity trends
   - Up to 52 periods of data
   - Trend analysis (improving/declining/stable)
   - Average scores over time
   - Accessible by developer (own data) or manager/admin

4. **GET /api/analytics/developers/{id}/work-breakdown**
   - Detailed work type distribution
   - Complexity distribution (low/medium/high)
   - Source distribution (git/jira)
   - Recent activities list
   - Accessible by developer (own data) or manager/admin

5. **GET /api/analytics/teams/{team}/overview**
   - Team aggregate productivity scores
   - Top performers (top 3)
   - Individual scores for all team members
   - Team size and averages
   - Manager/Admin only

6. **POST /api/analytics/calculate-score**
   - Calculate/recalculate productivity score
   - On-demand score generation
   - Force recalculation option
   - Accessible for own profile or by manager/admin

7. **GET /api/analytics/developers/{id}/insights**
   - AI-generated productivity insights
   - Pattern detection
   - Anomaly detection
   - Personalized recommendations
   - Cached with regenerate option
   - Accessible by developer (own data) or manager/admin

### 3. AI Insights Service

**File:** `backend/app/services/insights_service.py`

Generates intelligent insights about developer productivity:

**Insight Types:**

1. **Productivity Trends**
   - Detects improving/declining productivity
   - Analyzes score consistency
   - Identifies variance patterns
   - Provides context-aware recommendations

2. **Work Style Patterns**
   - Identifies work type preferences
   - Analyzes complexity preferences
   - Detects specialization patterns
   - Recommends skill diversification

3. **Anomaly Detection**
   - Low activity warnings (potential blockers)
   - High activity alerts (burnout risk)
   - Collaboration gaps
   - Unusual patterns

4. **Personalized Recommendations**
   - Based on role level
   - Identifies improvement areas
   - Growth path suggestions
   - Actionable next steps

**Key Methods:**
- `generate_developer_insights()` - Generate all insights
- `_detect_productivity_patterns()` - Trend analysis
- `_detect_work_style_patterns()` - Work preferences
- `_detect_anomalies()` - Issue detection
- `_generate_recommendations()` - Personalized advice
- `save_insights()` - Persist to database
- `get_recent_insights()` - Retrieve cached insights

### 4. Application Updates

**File:** `backend/app/main.py`

Updated main application:
- Imported analytics router
- Added analytics routes at `/api/analytics`
- All 8 analytics endpoints now accessible

## API Endpoints Summary

### Individual Developer Analytics (7 endpoints)

```
GET  /api/analytics/developers/{id}/overview
     → Summary analytics, activity counts, score overview

GET  /api/analytics/developers/{id}/productivity
     → Detailed productivity with 6-component breakdown
     → Query: ?include_comparison=true

GET  /api/analytics/developers/{id}/trends
     → Historical trends up to 52 periods
     → Query: ?periods=12

GET  /api/analytics/developers/{id}/work-breakdown
     → Work type distribution, complexity bins
     → Query: ?limit=20 (recent activities)

GET  /api/analytics/developers/{id}/insights
     → AI-generated insights and recommendations
     → Query: ?regenerate=true

POST /api/analytics/calculate-score
     → Calculate productivity score on-demand
     → Body: {developer_id?, start_date?, end_date?, force_recalculate?}
```

### Team Analytics (1 endpoint)

```
GET  /api/analytics/teams/{team}/overview
     → Team aggregate scores
     → Top performers
     → All team member scores
```

## Authorization Model

**Access Control Rules:**

1. **Developers:**
   - ✅ Can view own analytics
   - ✅ Can calculate own scores
   - ✅ Can view own insights
   - ❌ Cannot view other developers' data
   - ❌ Cannot view team analytics

2. **Managers:**
   - ✅ Can view all developer analytics
   - ✅ Can calculate any developer's scores
   - ✅ Can view team analytics
   - ✅ Can trigger score calculations
   - ✅ Can view AI insights for anyone

3. **Admins:**
   - ✅ Full access to all analytics
   - ✅ Can perform all operations

## Productivity Scoring Algorithm

### Overall Score Calculation

```python
overall_score = (
    complexity_score * weight_complexity +
    velocity_score * weight_velocity +
    quality_score * weight_quality +
    impact_score * weight_impact +
    collaboration_score * weight_collaboration +
    mentoring_score * weight_mentoring
) * 10  # Scale to 0-100
```

### Component Calculations

**Complexity Score (0-10):**
- Average complexity of all work activities
- From AI analysis of code and tickets

**Velocity Score (0-10):**
- Activities per week
- Consistency (active days per week)
- Formula: `base_score * consistency_multiplier`
- 5-10 activities/week = 8-10 points
- 2-5 activities/week = 5-8 points

**Quality Score (0-10):**
- Average quality from AI analysis
- Code review feedback
- Test coverage (future enhancement)

**Impact Score (0-10):**
- Average impact from AI analysis
- Business value
- System criticality

**Collaboration Score (0-10):**
- Ratio of collaboration activities
- Code reviews, pair programming, documentation
- 20%+ collaboration = 10 points
- 10%+ collaboration = 7+ points

**Mentoring Score (0-10):**
- Documentation written
- Code reviews with teaching
- Pair programming
- Knowledge sharing indicators

## Testing Guide

### Prerequisites

1. Complete Session 1 & 2 setup
2. Have synced data from GitHub/Jira
3. Run AI analysis tasks to create WorkActivity records
4. Ensure at least one developer profile exists

### Running Analytics Tests

```bash
cd backend
./test_analytics.sh
```

The script tests:
- Developer analytics overview
- Detailed productivity scores
- Historical trends
- Work breakdown
- Team analytics
- AI insights generation
- Authorization controls
- Date filtering

### Manual Testing Examples

**1. Get Developer Analytics Overview:**
```bash
curl -X GET "http://localhost:8000/api/analytics/developers/1/overview" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**2. Get Detailed Productivity with Comparisons:**
```bash
curl -X GET "http://localhost:8000/api/analytics/developers/1/productivity?include_comparison=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**3. Calculate Productivity Score:**
```bash
curl -X POST "http://localhost:8000/api/analytics/calculate-score" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "developer_id": 1,
    "start_date": "2024-10-01",
    "end_date": "2024-10-31",
    "force_recalculate": true
  }'
```

**4. Get Historical Trends (Last 12 Periods):**
```bash
curl -X GET "http://localhost:8000/api/analytics/developers/1/trends?periods=12" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**5. Get Work Breakdown:**
```bash
curl -X GET "http://localhost:8000/api/analytics/developers/1/work-breakdown?limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**6. Get Team Analytics:**
```bash
curl -X GET "http://localhost:8000/api/analytics/teams/Engineering/overview" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**7. Get AI Insights (Force Regenerate):**
```bash
curl -X GET "http://localhost:8000/api/analytics/developers/1/insights?regenerate=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Database Verification

Check productivity scores:
```sql
-- View recent productivity scores
SELECT
  ps.id,
  ps.developer_id,
  ps.period_start,
  ps.period_end,
  ps.overall_score,
  ps.complexity_score,
  ps.velocity_score,
  ps.quality_score,
  ps.impact_score
FROM productivity_scores ps
ORDER BY ps.created_at DESC
LIMIT 10;

-- View AI insights
SELECT
  ai.id,
  ai.developer_id,
  ai.insight_type,
  ai.title,
  ai.confidence_score
FROM ai_insights ai
ORDER BY ai.created_at DESC
LIMIT 10;

-- Check work activities (source data)
SELECT COUNT(*) as activity_count,
       source_type,
       work_type
FROM work_activities
GROUP BY source_type, work_type;
```

## Example API Responses

### Productivity Score Response

```json
{
  "developer_id": 1,
  "developer_name": "John Doe",
  "role_level": "senior",
  "team": "Engineering",
  "period_start": "2024-10-01",
  "period_end": "2024-10-31",
  "overall_score": 78.5,
  "score_breakdown": {
    "complexity": 8.2,
    "velocity": 7.5,
    "quality": 8.0,
    "impact": 8.5,
    "collaboration": 6.8,
    "mentoring": 5.5
  },
  "evaluation_weights": {
    "complexity": 0.25,
    "velocity": 0.15,
    "quality": 0.20,
    "impact": 0.25,
    "collaboration": 0.10,
    "mentoring": 0.05
  },
  "work_breakdown": {
    "feature_development": 45.5,
    "bug_fix": 25.3,
    "code_review": 15.2,
    "documentation": 8.5,
    "refactoring": 5.5
  },
  "comparison_to_team": {
    "overall": {
      "developer": 78.5,
      "team_average": 72.3,
      "difference": 6.2
    }
  }
}
```

### AI Insights Response

```json
{
  "developer_id": 1,
  "developer_name": "John Doe",
  "period_start": "2024-10-01",
  "period_end": "2024-10-31",
  "insights": [
    {
      "insight_type": "productivity_trend",
      "title": "Strong Upward Productivity Trend",
      "description": "Productivity has improved by 7.2 points over recent periods. This shows consistent growth and improvement.",
      "confidence": 0.9,
      "recommendations": [
        "Continue current practices that are driving improvement",
        "Document what's working well to share with team",
        "Consider mentoring others with similar growth patterns"
      ],
      "supporting_data": {
        "recent_average": 78.5,
        "previous_average": 71.3,
        "improvement": 7.2
      }
    },
    {
      "insight_type": "work_preference",
      "title": "Strong Focus on Feature Development",
      "description": "65% of work is feature development. This shows clear specialization.",
      "confidence": 0.85,
      "recommendations": [
        "Leverage expertise in feature development for high-impact projects",
        "Consider diversifying work types for skill development",
        "Mentor others in this area of expertise"
      ]
    },
    {
      "insight_type": "recommendation",
      "title": "Improve Mentoring Score",
      "description": "Mentoring score of 5.5/10 is below target. Focus on this area for professional growth.",
      "confidence": 0.9,
      "recommendations": [
        "Write more technical documentation",
        "Help onboard new team members",
        "Share expertise in team meetings",
        "Review and provide feedback on others' code"
      ]
    }
  ],
  "patterns_detected": [
    "Strong Upward Productivity Trend",
    "Strong Focus on Feature Development"
  ],
  "anomalies": []
}
```

## Architecture Flow

### Score Calculation Flow

```
1. API request to calculate score
   ↓
2. ProductivityScoringService.calculate_developer_score()
   ↓
3. Fetch WorkActivity records for period
   ↓
4. Calculate 6 component scores
   ↓
5. Apply role-based weights
   ↓
6. Compute overall score (0-100)
   ↓
7. Save ProductivityScore to database
   ↓
8. Return detailed score breakdown
```

### Insights Generation Flow

```
1. API request for insights
   ↓
2. Check for cached insights
   ↓
3. If regenerate or no cache:
   ├─ InsightsService.generate_developer_insights()
   ├─ Detect productivity patterns
   ├─ Detect work style patterns
   ├─ Detect anomalies
   ├─ Generate recommendations
   └─ Save insights to database
   ↓
4. Return insights with patterns and anomalies
```

## Performance Considerations

1. **Score Calculation:**
   - Cached in `productivity_scores` table
   - Recalculate weekly (or on-demand)
   - Indexed by developer_id and period

2. **Insights Generation:**
   - Cached in `ai_insights` table
   - Regenerate on request or monthly
   - No external AI API calls (rule-based)

3. **Analytics Queries:**
   - Use database indexes on foreign keys
   - Aggregate queries optimized
   - Date range filtering efficient

## Troubleshooting

### No Productivity Score Calculated

**Problem:** `calculate-score` returns "No activity data found"

**Solution:**
1. Check if data has been synced from GitHub/Jira (Session 2)
2. Verify AI analysis has run: `SELECT COUNT(*) FROM work_activities;`
3. If zero, trigger sync: `POST /api/integrations/{id}/sync`
4. Wait for analysis tasks to complete
5. Retry score calculation

### Empty Team Analytics

**Problem:** Team analytics returns "No developers found in team"

**Solution:**
1. Check developer team assignments: `SELECT team FROM developer_profiles;`
2. Ensure team name matches exactly (case-sensitive)
3. Create developers with correct team name

### Insights Not Generated

**Problem:** Insights endpoint returns empty insights array

**Solution:**
1. Ensure productivity scores exist
2. Check if work activities exist
3. Use `?regenerate=true` to force generation
4. Verify developer has at least 2 score periods for trends

## What's Next: Frontend & Deployment

Future sessions will implement:

1. **Frontend Dashboard**
   - Next.js 14 app with TypeScript
   - Interactive productivity charts (Recharts)
   - Real-time analytics display
   - Developer and manager views
   - Team comparison views

2. **Advanced Features**
   - Real-time notifications
   - Custom report generation
   - Goal setting and tracking
   - Skill development tracking
   - Team health indicators

3. **Deployment**
   - Docker containerization
   - CI/CD pipeline setup
   - Production environment config
   - Monitoring and logging
   - Performance optimization

## Session 3 Summary

**Files Created/Modified:**
- `backend/app/services/scoring_service.py` - NEW (Productivity scoring)
- `backend/app/services/insights_service.py` - NEW (AI insights)
- `backend/app/schemas/analytics.py` - NEW (Analytics schemas)
- `backend/app/api/analytics.py` - NEW (Analytics endpoints)
- `backend/app/main.py` - MODIFIED (Added analytics routes)
- `backend/test_analytics.sh` - NEW (Testing script)
- `TESTING_CHECKLIST.md` - NEW (Comprehensive testing guide)

**API Endpoints Added:** 8
- GET /api/analytics/developers/{id}/overview
- GET /api/analytics/developers/{id}/productivity
- GET /api/analytics/developers/{id}/trends
- GET /api/analytics/developers/{id}/work-breakdown
- GET /api/analytics/developers/{id}/insights
- GET /api/analytics/teams/{team}/overview
- POST /api/analytics/calculate-score

**Key Features:**
- Multi-dimensional productivity scoring (6 components)
- Role-based evaluation (6 role levels with different weights)
- Historical trend analysis (up to 52 periods)
- Team analytics with top performers
- AI-powered insights (4 types)
- Personalized recommendations
- Anomaly detection
- Role-based access control

**Status:** ✅ Complete and ready for testing

---

*Generated: 2025-11-09 | Session 3 of DevMetrics AI Development*
