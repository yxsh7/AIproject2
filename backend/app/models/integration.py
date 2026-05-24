"""Integration configuration model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class IntegrationType(str, enum.Enum):
    """Integration type enumeration"""

    GITHUB = "github"
    BITBUCKET = "bitbucket"
    GITLAB = "gitlab"
    JIRA = "jira"
    SLACK = "slack"


class IntegrationStatus(str, enum.Enum):
    """Integration status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    SYNCING = "syncing"


class IntegrationConfig(Base):
    """Integration configuration for external services"""

    __tablename__ = "integration_configs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Integration details
    type = Column(SQLEnum(IntegrationType, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    status = Column(SQLEnum(IntegrationStatus, values_callable=lambda x: [e.value for e in x]), default=IntegrationStatus.INACTIVE, nullable=False)

    # Configuration (encrypted JSON containing API tokens, etc.)
    config = Column(JSON, nullable=False)

    # Metadata
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    sync_frequency_minutes = Column(Integer, default=60)  # How often to sync

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="integrations")

    def __repr__(self):
        return f"<IntegrationConfig {self.type} - {self.status}>"
