"""Analytics and productivity API endpoints"""
from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analytics import (
    DeveloperAnalyticsOverview,
    DeveloperProductivityResponse,
    DeveloperTrendsResponse,
    WorkBreakdownResponse,
    TeamAnalyticsOverview,
    DeveloperComparisonResponse,
    DeveloperInsightsResponse,
    ScoreCalculationRequest,
    ScoreCalculationResponse,
    ProductivityScoreResponse,
    WorkActivityResponse,
    TrendDataPoint,
    TeamMemberScore,
    ComparisonData,
)
from app.models import User, DeveloperProfile, WorkActivity, ProductivityScore
from app.api.dependencies import get_current_active_user
from app.services.scoring_service import ProductivityScoringService, ROLE_WEIGHTS

router = APIRouter()


def check_analytics_access(
    current_user: User, developer_id: int, db: Session
) -> bool:
    """
    Check if user has access to developer's analytics

    Rules:
    - Developers can see their own analytics
    - Managers can see all analytics
    - Admins can see all analytics
    """
    if current_user.role in ["manager", "admin"]:
        return True

    # Check if developer is viewing their own profile
    developer = (
        db.query(DeveloperProfile)
        .filter(DeveloperProfile.id == developer_id)
        .first()
    )

    if developer and developer.user_id == current_user.id:
        return True

    return False


@router.get("/developers/{developer_id}/overview", response_model=DeveloperAnalyticsOverview)
def get_developer_overview(
    developer_id: int,
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get analytics overview for a developer

    Args:
        developer_id: Developer profile ID
        start_date: Start of analytics period (default: 30 days ago)
        end_date: End of analytics period (default: today)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Developer analytics overview

    Raises:
        HTTPException: If user doesn't have access or developer not found
    """
    # Check access
    if not check_analytics_access(current_user, developer_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this developer's analytics",
        )

    # Get developer
    developer = (
        db.query(DeveloperProfile)
        .filter(DeveloperProfile.id == developer_id)
        .first()
    )

    if not developer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found",
        )

    # Default dates
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Get productivity score
    scoring_service = ProductivityScoringService(db)
    productivity_score = scoring_service.calculate_developer_score(
        developer_id, start_date, end_date
    )

    # Get activity summary
    activities = (
        db.query(WorkActivity)
        .filter(
            WorkActivity.developer_id == developer_id,
            WorkActivity.activity_date >= start_date,
            WorkActivity.activity_date <= end_date,
        )
        .all()
    )

    activity_summary = {
        "total_activities": len(activities),
        "total_commits": sum(1 for a in activities if a.source_type == "git"),
        "total_tickets": sum(1 for a in activities if a.source_type == "jira"),
        "days_active": len(set(a.activity_date for a in activities)),
        "avg_complexity": round(
            sum(a.complexity_score for a in activities) / len(activities), 2
        )
        if activities
        else 0,
        "avg_impact": round(
            sum(a.impact_score for a in activities) / len(activities), 2
        )
        if activities
        else 0,
    }

    work_breakdown = productivity_score.work_breakdown if productivity_score else {}

    return DeveloperAnalyticsOverview(
        developer_id=developer.id,
        developer_name=developer.user.full_name if developer.user else "Unknown",
        role_level=developer.role_level.value,
        team=developer.team,
        period_start=start_date,
        period_end=end_date,
        productivity_score=productivity_score,
        activity_summary=activity_summary,
        work_breakdown=work_breakdown,
    )


@router.get("/developers/{developer_id}/productivity", response_model=DeveloperProductivityResponse)
def get_developer_productivity(
    developer_id: int,
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    include_comparison: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get detailed productivity analytics for a developer

    Args:
        developer_id: Developer profile ID
        start_date: Start of analytics period
        end_date: End of analytics period
        include_comparison: Include comparison to team/role
        db: Database session
        current_user: Current authenticated user

    Returns:
        Detailed productivity analytics
    """
    # Check access
    if not check_analytics_access(current_user, developer_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this developer's analytics",
        )

    # Get developer
    developer = (
        db.query(DeveloperProfile)
        .filter(DeveloperProfile.id == developer_id)
        .first()
    )

    if not developer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found",
        )

    # Default dates
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Calculate productivity score
    scoring_service = ProductivityScoringService(db)
    productivity_score = scoring_service.calculate_developer_score(
        developer_id, start_date, end_date
    )

    if not productivity_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No activity data found for this period",
        )

    # Score breakdown
    score_breakdown = {
        "complexity": productivity_score.complexity_score,
        "velocity": productivity_score.velocity_score,
        "quality": productivity_score.quality_score,
        "impact": productivity_score.impact_score,
        "collaboration": productivity_score.collaboration_score,
        "mentoring": productivity_score.mentoring_score,
    }

    # Evaluation weights
    weights = ROLE_WEIGHTS.get(developer.role_level, ROLE_WEIGHTS["mid"])

    # Activity stats
    activity_stats = productivity_score.metadata or {}

    # Comparison data
    comparison_to_team = None
    comparison_to_role = None

    if include_comparison and developer.team:
        # Team comparison
        team_scores = scoring_service.calculate_team_scores(
            developer.team, start_date, end_date
        )

        if "error" not in team_scores:
            comparison_to_team = {
                "overall": {
                    "developer": productivity_score.overall_score,
                    "team_average": team_scores["average_overall_score"],
                    "difference": round(
                        productivity_score.overall_score
                        - team_scores["average_overall_score"],
                        2,
                    ),
                },
                "complexity": {
                    "developer": productivity_score.complexity_score,
                    "team_average": team_scores["average_complexity_score"],
                },
                "velocity": {
                    "developer": productivity_score.velocity_score,
                    "team_average": team_scores["average_velocity_score"],
                },
                "quality": {
                    "developer": productivity_score.quality_score,
                    "team_average": team_scores["average_quality_score"],
                },
                "impact": {
                    "developer": productivity_score.impact_score,
                    "team_average": team_scores["average_impact_score"],
                },
            }

    return DeveloperProductivityResponse(
        developer_id=developer.id,
        developer_name=developer.user.full_name if developer.user else "Unknown",
        role_level=developer.role_level.value,
        team=developer.team,
        period_start=start_date,
        period_end=end_date,
        overall_score=productivity_score.overall_score,
        score_breakdown=score_breakdown,
        evaluation_weights=weights,
        work_breakdown=productivity_score.work_breakdown,
        activity_stats=activity_stats,
        comparison_to_team=comparison_to_team,
        comparison_to_role=comparison_to_role,
    )


@router.get("/developers/{developer_id}/trends", response_model=DeveloperTrendsResponse)
def get_developer_trends(
    developer_id: int,
    periods: int = Query(default=12, ge=1, le=52),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get historical productivity trends for a developer

    Args:
        developer_id: Developer profile ID
        periods: Number of periods to retrieve (default: 12)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Historical trends data
    """
    # Check access
    if not check_analytics_access(current_user, developer_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this developer's analytics",
        )

    # Get developer
    developer = (
        db.query(DeveloperProfile)
        .filter(DeveloperProfile.id == developer_id)
        .first()
    )

    if not developer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found",
        )

    # Get trends
    scoring_service = ProductivityScoringService(db)
    trends_data = scoring_service.get_score_trends(developer_id, periods)

    # Analyze trends
    trend_analysis = {}
    if len(trends_data) >= 2:
        latest_score = trends_data[-1]["overall_score"]
        previous_score = trends_data[-2]["overall_score"]
        change = latest_score - previous_score

        trend_analysis = {
            "latest_score": latest_score,
            "previous_score": previous_score,
            "change": round(change, 2),
            "trend_direction": "improving" if change > 0 else "declining" if change < 0 else "stable",
            "average_score": round(
                sum(t["overall_score"] for t in trends_data) / len(trends_data), 2
            ),
        }

    trends = [TrendDataPoint(**t) for t in trends_data]

    return DeveloperTrendsResponse(
        developer_id=developer.id,
        developer_name=developer.user.full_name if developer.user else "Unknown",
        trends=trends,
        trend_analysis=trend_analysis,
    )


@router.get("/developers/{developer_id}/work-breakdown", response_model=WorkBreakdownResponse)
def get_work_breakdown(
    developer_id: int,
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get detailed work breakdown for a developer

    Args:
        developer_id: Developer profile ID
        start_date: Start of period
        end_date: End of period
        limit: Number of recent activities to include
        db: Database session
        current_user: Current authenticated user

    Returns:
        Work breakdown by type, complexity, and source
    """
    # Check access
    if not check_analytics_access(current_user, developer_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this developer's analytics",
        )

    # Get developer
    developer = (
        db.query(DeveloperProfile)
        .filter(DeveloperProfile.id == developer_id)
        .first()
    )

    if not developer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found",
        )

    # Default dates
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Get activities
    activities = (
        db.query(WorkActivity)
        .filter(
            WorkActivity.developer_id == developer_id,
            WorkActivity.activity_date >= start_date,
            WorkActivity.activity_date <= end_date,
        )
        .order_by(WorkActivity.activity_date.desc())
        .all()
    )

    if not activities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No activity data found for this period",
        )

    # Work type distribution
    work_types = {}
    for activity in activities:
        work_type = activity.work_type.value if activity.work_type else "unknown"
        work_types[work_type] = work_types.get(work_type, 0) + 1

    work_type_distribution = {
        wt: round((count / len(activities)) * 100, 2)
        for wt, count in work_types.items()
    }

    # Complexity distribution (bins)
    complexity_bins = {"low": 0, "medium": 0, "high": 0}
    for activity in activities:
        if activity.complexity_score <= 3:
            complexity_bins["low"] += 1
        elif activity.complexity_score <= 7:
            complexity_bins["medium"] += 1
        else:
            complexity_bins["high"] += 1

    # Source distribution
    source_distribution = {}
    for activity in activities:
        source = activity.source_type
        source_distribution[source] = source_distribution.get(source, 0) + 1

    # Recent activities
    recent = activities[:limit]

    return WorkBreakdownResponse(
        developer_id=developer.id,
        developer_name=developer.user.full_name if developer.user else "Unknown",
        period_start=start_date,
        period_end=end_date,
        work_type_distribution=work_type_distribution,
        complexity_distribution=complexity_bins,
        source_distribution=source_distribution,
        recent_activities=[WorkActivityResponse.model_validate(a) for a in recent],
        total_activities=len(activities),
    )


@router.get("/teams/{team}/overview", response_model=TeamAnalyticsOverview)
def get_team_overview(
    team: str,
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get analytics overview for a team

    Args:
        team: Team name
        start_date: Start of analytics period
        end_date: End of analytics period
        db: Database session
        current_user: Current authenticated user (manager/admin only)

    Returns:
        Team analytics overview
    """
    # Only managers and admins can view team analytics
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers and admins can view team analytics",
        )

    # Default dates
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Calculate team scores
    scoring_service = ProductivityScoringService(db)
    team_data = scoring_service.calculate_team_scores(team, start_date, end_date)

    if "error" in team_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=team_data["error"],
        )

    # Convert to response models
    top_performers = [TeamMemberScore(**p) for p in team_data["top_performers"]]
    individual_scores = [TeamMemberScore(**s) for s in team_data["individual_scores"]]

    return TeamAnalyticsOverview(
        team=team,
        team_size=team_data["team_size"],
        period_start=team_data["period_start"],
        period_end=team_data["period_end"],
        average_overall_score=team_data["average_overall_score"],
        average_complexity_score=team_data["average_complexity_score"],
        average_velocity_score=team_data["average_velocity_score"],
        average_quality_score=team_data["average_quality_score"],
        average_impact_score=team_data["average_impact_score"],
        average_collaboration_score=team_data["average_collaboration_score"],
        average_mentoring_score=team_data["average_mentoring_score"],
        top_performers=top_performers,
        individual_scores=individual_scores,
    )


@router.post("/calculate-score", response_model=ScoreCalculationResponse)
def calculate_productivity_score(
    request: ScoreCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Calculate/recalculate productivity score

    Args:
        request: Score calculation request
        db: Database session
        current_user: Current authenticated user

    Returns:
        Calculation result
    """
    # Determine developer ID
    developer_id = request.developer_id

    if not developer_id:
        # Calculate for current user's developer profile
        developer = (
            db.query(DeveloperProfile)
            .filter(DeveloperProfile.user_id == current_user.id)
            .first()
        )

        if not developer:
            return ScoreCalculationResponse(
                success=False,
                message="No developer profile found for current user",
                errors=["Create a developer profile first"],
            )

        developer_id = developer.id
    else:
        # Check if user can calculate for other developers
        if not check_analytics_access(current_user, developer_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to calculate scores for this developer",
            )

    # Calculate score
    scoring_service = ProductivityScoringService(db)
    score = scoring_service.calculate_developer_score(
        developer_id, request.start_date, request.end_date
    )

    if not score:
        return ScoreCalculationResponse(
            success=False,
            message="No activity data found for the specified period",
            errors=["Ensure data has been synced from GitHub/Jira"],
        )

    # Save score
    saved_score = scoring_service.save_score(score)

    return ScoreCalculationResponse(
        success=True,
        message="Productivity score calculated successfully",
        score=ProductivityScoreResponse.model_validate(saved_score),
    )


@router.get("/developers/{developer_id}/insights", response_model=DeveloperInsightsResponse)
def get_developer_insights(
    developer_id: int,
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    regenerate: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get AI-generated insights for a developer

    Args:
        developer_id: Developer profile ID
        start_date: Start of analysis period
        end_date: End of analysis period
        regenerate: Force regenerate insights (default: use cached)
        db: Database session
        current_user: Current authenticated user

    Returns:
        AI-generated insights and recommendations
    """
    # Check access
    if not check_analytics_access(current_user, developer_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this developer's insights",
        )

    # Get developer
    developer = (
        db.query(DeveloperProfile)
        .filter(DeveloperProfile.id == developer_id)
        .first()
    )

    if not developer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found",
        )

    # Default dates
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Import here to avoid circular imports
    from app.services.insights_service import InsightsService

    insights_service = InsightsService(db)

    # Generate or retrieve insights
    if regenerate:
        # Generate fresh insights
        insights_data = insights_service.generate_developer_insights(
            developer_id, start_date, end_date
        )

        # Save to database
        insights_service.save_insights(
            developer_id, insights_data, start_date, end_date
        )
    else:
        # Try to get recent cached insights
        recent_insights = insights_service.get_recent_insights(developer_id, limit=20)

        # Filter by date range
        insights_data = []
        for insight in recent_insights:
            if (
                insight.period_start >= start_date
                and insight.period_end <= end_date
            ):
                insights_data.append({
                    "insight_type": insight.insight_type.value,
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence_score,
                    "recommendations": insight.recommendations,
                    "supporting_data": insight.supporting_data or {},
                })

        # If no cached insights, generate new ones
        if not insights_data:
            insights_data = insights_service.generate_developer_insights(
                developer_id, start_date, end_date
            )
            insights_service.save_insights(
                developer_id, insights_data, start_date, end_date
            )

    # Extract patterns and anomalies
    patterns_detected = [
        insight["title"]
        for insight in insights_data
        if insight["insight_type"] in ["productivity_trend", "work_preference", "consistency"]
    ]

    anomalies = [
        {
            "type": insight["insight_type"],
            "description": insight["description"],
            "severity": "high" if insight["confidence"] > 0.8 else "medium",
        }
        for insight in insights_data
        if insight["insight_type"] in ["anomaly", "collaboration_gap"]
    ]

    # Convert to response format
    from app.schemas.analytics import InsightResponse

    insights = [InsightResponse(**insight) for insight in insights_data]

    return DeveloperInsightsResponse(
        developer_id=developer.id,
        developer_name=developer.user.full_name if developer.user else "Unknown",
        period_start=start_date,
        period_end=end_date,
        insights=insights,
        patterns_detected=patterns_detected,
        anomalies=anomalies,
    )


@router.post("/developers/{developer_id}/analyze")
def trigger_ai_analysis(
    developer_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Manually trigger AI analysis for a developer (COSTS MONEY - use sparingly)

    This endpoint triggers AI analysis of unanalyzed commits and tickets.
    Only use this when you want to analyze new data.

    Args:
        developer_id: Developer profile ID
        limit: Maximum number of items to analyze (default: 50)
        db: Database session
        current_user: Current authenticated user (manager/admin only)

    Returns:
        Job IDs for the triggered analysis tasks

    Raises:
        HTTPException: If user doesn't have permission
    """
    # Only managers and admins can trigger AI analysis
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers and admins can trigger AI analysis",
        )

    # Verify developer exists
    developer = (
        db.query(DeveloperProfile)
        .filter(DeveloperProfile.id == developer_id)
        .first()
    )

    if not developer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found",
        )

    # Import analysis tasks
    from app.tasks.analysis_tasks import analyze_git_commits, analyze_jira_tickets

    # Trigger AI analysis tasks
    commit_job = analyze_git_commits.delay(developer_id, limit=limit)
    ticket_job = analyze_jira_tickets.delay(developer_id, limit=limit)

    return {
        "message": f"AI analysis triggered for {developer.user.full_name if developer.user else f'developer {developer_id}'}",
        "warning": "This will incur AI API costs (approximately $0.01 per 100 items)",
        "commit_analysis_job_id": str(commit_job.id),
        "ticket_analysis_job_id": str(ticket_job.id),
        "max_items_to_analyze": limit,
        "estimated_cost_usd": round((limit / 100) * 0.01, 4),
    }
