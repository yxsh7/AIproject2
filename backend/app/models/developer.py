"""Developer profile models"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class RoleLevel(str, enum.Enum):
    """Developer role level"""

    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"


class RoleProfile(Base):
    """Role profile template defining expectations per role level"""

    __tablename__ = "role_profiles"

    id = Column(Integer, primary_key=True, index=True)
    role_level = Column(SQLEnum(RoleLevel, values_callable=lambda x: [e.value for e in x]), unique=True, nullable=False, index=True)

    # Expected work distribution (JSON: {work_type: percentage})
    # e.g., {"code": 70, "meetings": 15, "documentation": 15}
    expected_work_types = Column(JSON, nullable=False)

    # Complexity expectation level
    complexity_expectation = Column(String, nullable=False)  # low, medium, high, very-high

    # Evaluation criteria weights (JSON: {criterion: weight})
    # e.g., {"code_quality": 0.3, "velocity": 0.25, "impact": 0.25, "collaboration": 0.2}
    evaluation_criteria = Column(JSON, nullable=False)

    # Whether mentoring is expected
    mentoring_expected = Column(Integer, default=0)  # 0=False, 1=True

    # Autonomy level
    autonomy_level = Column(String, nullable=False)  # needs-guidance, some-guidance, mostly-independent, fully-independent

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<RoleProfile {self.role_level}>"


class DeveloperProfile(Base):
    """Developer profile with role and integration info"""

    __tablename__ = "developer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Role information
    role_level = Column(SQLEnum(RoleLevel, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    team = Column(String, nullable=True, index=True)
    job_title = Column(String, nullable=True)

    # Integration identifiers
    github_username = Column(String, nullable=True, index=True)
    jira_username = Column(String, nullable=True, index=True)
    slack_user_id = Column(String, nullable=True)

    # Additional info
    start_date = Column(DateTime(timezone=True), nullable=True)
    focus_areas = Column(JSON, nullable=True)  # List of focus areas: ["backend", "architecture", "mentoring"]
    bio = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="developer_profile")
    organization = relationship("Organization", back_populates="developer_profiles")
    git_commits = relationship("GitCommit", back_populates="developer")
    pull_requests = relationship("PullRequest", back_populates="developer")
    code_reviews = relationship("CodeReview", back_populates="reviewer", foreign_keys="CodeReview.reviewer_id")
    jira_tickets = relationship("JiraTicket", back_populates="developer")
    jira_comments = relationship("JiraComment", back_populates="developer")
    work_activities = relationship("WorkActivity", back_populates="developer")
    productivity_scores = relationship("ProductivityScore", back_populates="developer")
    insights = relationship("AIInsight", back_populates="developer")
    slack_messages = relationship("SlackMessage", foreign_keys="SlackMessage.developer_id", back_populates="developer")
    slack_reactions = relationship("SlackReaction", foreign_keys="SlackReaction.developer_id", back_populates="developer")

    def __repr__(self):
        return f"<DeveloperProfile {self.github_username or self.user_id}>"
