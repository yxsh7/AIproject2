"""Productivity scoring and AI insights models"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Date, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ProductivityScore(Base):
    """
    Productivity score calculated for a developer over a time period
    """

    __tablename__ = "productivity_scores"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False, index=True)

    # Time period
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    period_type = Column(String, nullable=False)  # daily, weekly, sprint, monthly

    # Overall score (0-100)
    overall_score = Column(Integer, nullable=False)

    # Dimension scores (0-100)
    code_quality_score = Column(Integer, nullable=True)
    complexity_score = Column(Integer, nullable=True)
    velocity_score = Column(Integer, nullable=True)
    impact_score = Column(Integer, nullable=True)
    collaboration_score = Column(Integer, nullable=True)
    mentoring_score = Column(Integer, nullable=True)
    learning_score = Column(Integer, nullable=True)

    # Detailed breakdown
    breakdown = Column(JSON, nullable=False)
    # Example: {
    #   "total_activities": 15,
    #   "work_type_distribution": {"code": 60, "review": 25, "research": 15},
    #   "complexity_distribution": {...},
    #   "highlights": [...]
    # }

    # AI-generated insights
    insights = Column(JSON, nullable=True)
    # Example: {
    #   "strengths": ["Complex problem-solving", "Mentoring"],
    #   "observations": ["Working late nights"],
    #   "suggestions": ["Consider delegating more"]
    # }

    # Calculation metadata
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(String, default="1.0")  # Algorithm version

    # Relationships
    developer = relationship("DeveloperProfile", back_populates="productivity_scores")

    def __repr__(self):
        return f"<ProductivityScore {self.developer_id} - {self.period_start} to {self.period_end}: {self.overall_score}>"


class InsightType(str, enum.Enum):
    """Type of AI insight"""

    INDIVIDUAL = "individual"  # About a specific developer
    TEAM = "team"  # About the team
    TREND = "trend"  # Trend analysis
    ALERT = "alert"  # Actionable alert
    RECOMMENDATION = "recommendation"  # Suggestion


class InsightPriority(str, enum.Enum):
    """Insight priority level"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AIInsight(Base):
    """
    AI-generated insights about developers and teams
    """

    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=True, index=True)
    # If developer_id is NULL, it's a team/organization-level insight

    # Insight details
    insight_type = Column(SQLEnum(InsightType), nullable=False, index=True)
    priority = Column(SQLEnum(InsightPriority), default=InsightPriority.MEDIUM, nullable=False, index=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    # Metadata
    metadata = Column(JSON, nullable=True)
    # Example: {
    #   "metric_change": -30,
    #   "time_period": "this_week",
    #   "affected_developers": [1, 2, 3],
    #   "data": {...}
    # }

    # Actions
    action_items = Column(JSON, nullable=True)
    # Example: [
    #   {"action": "Schedule 1:1", "assignee": "manager"},
    #   {"action": "Reduce concurrent tickets", "assignee": "manager"}
    # ]

    # Status
    acknowledged = Column(Integer, default=0)  # 0=False, 1=True
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    organization = relationship("Organization", back_populates="insights")
    developer = relationship("DeveloperProfile", back_populates="insights")

    def __repr__(self):
        return f"<AIInsight {self.insight_type} - {self.priority}: {self.title}>"
