"""Organization model"""

from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Organization(Base):
    """Organization/Company model"""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Integration identifiers
    github_org = Column(String, nullable=True, index=True)
    jira_workspace = Column(String, nullable=True)

    # Optional override of ROLE_WEIGHTS (scoring_service.py) — when set, applies
    # uniformly across all role levels for this org instead of the per-role
    # defaults. {"complexity": float, "velocity": float, "quality": float,
    # "impact": float, "collaboration": float, "mentoring": float}, summing to 1.0.
    custom_scoring_weights = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    developer_profiles = relationship("DeveloperProfile", back_populates="organization")
    integrations = relationship("IntegrationConfig", back_populates="organization")
    insights = relationship("AIInsight", back_populates="organization")
    invites = relationship("OrganizationInvite", back_populates="organization")

    def __repr__(self):
        return f"<Organization {self.name}>"
