"""Analytics and productivity schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import date


class ProductivityScoreResponse(BaseModel):
    """Schema for productivity score response"""

    id: int
    developer_id: int
    period_start: date
    period_end: date
    overall_score: float
    complexity_score: float
    velocity_score: float
    quality_score: float
    impact_score: float
    collaboration_score: float
    mentoring_score: float
    total_commits: int
    total_prs: int
    total_tickets: int
    lines_added: int
    lines_deleted: int
    work_breakdown: Dict[str, float]
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class DeveloperAnalyticsOverview(BaseModel):
    """Overview analytics for a developer"""

    developer_id: int
    developer_name: str
    role_level: str
    team: Optional[str]
    period_start: date
    period_end: date
    productivity_score: Optional[ProductivityScoreResponse]
    activity_summary: Dict[str, Any]
    work_breakdown: Dict[str, float]


class DeveloperProductivityResponse(BaseModel):
    """Detailed productivity analytics for a developer"""

    developer_id: int
    developer_name: str
    role_level: str
    team: Optional[str]
    period_start: date
    period_end: date
    overall_score: float
    score_breakdown: Dict[str, float]
    evaluation_weights: Dict[str, float]
    work_breakdown: Dict[str, float]
    activity_stats: Dict[str, Any]
    comparison_to_team: Optional[Dict[str, Any]] = None
    comparison_to_role: Optional[Dict[str, Any]] = None


class TrendDataPoint(BaseModel):
    """Single data point in a trend"""

    period_start: str
    period_end: str
    overall_score: float
    complexity_score: float
    velocity_score: float
    quality_score: float
    impact_score: float
    collaboration_score: float
    mentoring_score: float


class DeveloperTrendsResponse(BaseModel):
    """Historical trends for a developer"""

    developer_id: int
    developer_name: str
    trends: List[TrendDataPoint]
    trend_analysis: Dict[str, Any]


class WorkActivityResponse(BaseModel):
    """Individual work activity"""

    id: int
    activity_date: date
    work_type: str
    complexity_score: float
    impact_score: float
    quality_score: float
    time_estimate_hours: int
    source_type: str
    ai_analysis: Optional[Dict[str, Any]]
    artifacts: Optional[List[Dict[str, Any]]]

    class Config:
        from_attributes = True


class WorkBreakdownResponse(BaseModel):
    """Breakdown of work by type and complexity"""

    developer_id: int
    developer_name: str
    period_start: date
    period_end: date
    work_type_distribution: Dict[str, float]
    complexity_distribution: Dict[str, int]
    source_distribution: Dict[str, int]
    recent_activities: List[WorkActivityResponse]
    total_activities: int


class TeamMemberScore(BaseModel):
    """Individual team member score"""

    developer_id: int
    developer_name: str
    role_level: str
    overall_score: float
    complexity_score: float
    velocity_score: float
    quality_score: float
    impact_score: float
    collaboration_score: float
    mentoring_score: float


class TeamAnalyticsOverview(BaseModel):
    """Overview analytics for a team"""

    team: str
    team_size: int
    period_start: date
    period_end: date
    average_overall_score: float
    average_complexity_score: float
    average_velocity_score: float
    average_quality_score: float
    average_impact_score: float
    average_collaboration_score: float
    average_mentoring_score: float
    top_performers: List[TeamMemberScore]
    individual_scores: List[TeamMemberScore]


class ComparisonData(BaseModel):
    """Comparison data between developer and benchmark"""

    developer_score: float
    benchmark_score: float
    difference: float
    percentile: Optional[float] = None


class DeveloperComparisonResponse(BaseModel):
    """Compare developer to team/role averages"""

    developer_id: int
    developer_name: str
    role_level: str
    team: Optional[str]
    period_start: date
    period_end: date
    developer_scores: Dict[str, float]
    team_comparison: Optional[Dict[str, ComparisonData]] = None
    role_comparison: Optional[Dict[str, ComparisonData]] = None
    strengths: List[str]
    improvement_areas: List[str]


class InsightResponse(BaseModel):
    """AI-generated insight"""

    insight_type: str
    title: str
    description: str
    confidence: float
    recommendations: List[str]
    supporting_data: Dict[str, Any]


class DeveloperInsightsResponse(BaseModel):
    """AI insights for a developer"""

    developer_id: int
    developer_name: str
    period_start: date
    period_end: date
    insights: List[InsightResponse]
    patterns_detected: List[str]
    anomalies: List[Dict[str, Any]]


class AnalyticsQueryParams(BaseModel):
    """Query parameters for analytics endpoints"""

    start_date: Optional[date] = Field(
        default=None, description="Start date for analytics period"
    )
    end_date: Optional[date] = Field(
        default=None, description="End date for analytics period"
    )
    include_comparison: bool = Field(
        default=True, description="Include comparison to team/role averages"
    )


class ScoreCalculationRequest(BaseModel):
    """Request to calculate/recalculate scores"""

    developer_id: Optional[int] = Field(
        default=None, description="Specific developer ID (admin only for others)"
    )
    start_date: Optional[date] = Field(
        default=None, description="Start of evaluation period"
    )
    end_date: Optional[date] = Field(default=None, description="End of evaluation period")
    force_recalculate: bool = Field(
        default=False, description="Force recalculation even if recent score exists"
    )


class ScoreCalculationResponse(BaseModel):
    """Response after score calculation"""

    success: bool
    message: str
    score: Optional[ProductivityScoreResponse] = None
    errors: Optional[List[str]] = None
