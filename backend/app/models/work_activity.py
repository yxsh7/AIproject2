"""Work activity model - unified view of all developer work"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Date, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class WorkType(str, enum.Enum):
    """Type of work activity"""

    CODE = "code"
    RESEARCH = "research"
    DOCUMENTATION = "documentation"
    DASHBOARD = "dashboard"
    MEETING = "meeting"
    MENTORING = "mentoring"
    CODE_REVIEW = "code_review"
    OPERATIONS = "operations"
    DESIGN = "design"
    TESTING = "testing"
    BUG_FIX = "bug_fix"
    REFACTORING = "refactoring"
    OTHER = "other"


class WorkActivity(Base):
    """
    Unified work activity model - AI-analyzed work from various sources

    This is the core analytical table that combines insights from
    git commits, PRs, Jira tickets, etc. into a single timeline of work.
    """

    __tablename__ = "work_activities"

    __table_args__ = (
        UniqueConstraint('developer_id', 'source_type', 'source_id', name='uq_work_activity_source'),
    )

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    # Activity metadata
    activity_date = Column(Date, nullable=False, index=True)
    work_type = Column(SQLEnum(WorkType, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)

    # Scores (0-10 scale)
    complexity_score = Column(Integer, nullable=False)  # How complex was the work?
    impact_score = Column(Integer, nullable=False)  # What was the business/technical impact?
    quality_score = Column(Integer, nullable=False)  # How good was the quality?

    # Estimates
    time_estimate_hours = Column(Integer, nullable=True)  # Estimated hours spent

    # Source tracking
    source_type = Column(String, nullable=False, index=True)  # git, jira, slack
    source_id = Column(String, nullable=False)  # ID in source system

    # AI Analysis
    ai_analysis = Column(JSON, nullable=False)
    # Example: {
    #   "summary": "Refactored payment processing system",
    #   "explanation": "Major architectural change...",
    #   "tags": ["critical", "architecture", "backend"],
    #   "affected_systems": ["payment", "billing"]
    # }

    # Artifacts (links to outputs)
    artifacts = Column(JSON, nullable=True)
    # Example: [
    #   {"type": "pr", "url": "..."},
    #   {"type": "document", "url": "..."},
    #   {"type": "dashboard", "url": "..."}
    # ]

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    developer = relationship("DeveloperProfile", back_populates="work_activities")

    def __repr__(self):
        return f"<WorkActivity {self.work_type} - {self.activity_date}>"
