"""Organization model"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text
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

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    developer_profiles = relationship("DeveloperProfile", back_populates="organization")
    integrations = relationship("IntegrationConfig", back_populates="organization")
    insights = relationship("AIInsight", back_populates="organization")
    invites = relationship("OrganizationInvite", back_populates="organization")

    def __repr__(self):
        return f"<Organization {self.name}>"
