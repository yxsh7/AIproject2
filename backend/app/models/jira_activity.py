"""Jira activity models (tickets and comments)"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class JiraTicket(Base):
    """Jira ticket/issue model"""

    __tablename__ = "jira_tickets"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False, index=True)

    # Ticket details
    ticket_key = Column(String, unique=True, nullable=False, index=True)  # e.g., PROJ-123
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, index=True)  # open, in_progress, done, etc.
    ticket_type = Column(String, nullable=False)  # story, bug, task, research, etc.
    priority = Column(String, nullable=True)

    # Metadata
    story_points = Column(Float, nullable=True)
    sprint = Column(String, nullable=True, index=True)
    labels = Column(JSON, nullable=True)  # List of labels

    # URLs
    ticket_url = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # AI Analysis
    analyzed = Column(Integer, default=0)  # 0=False, 1=True
    analysis_result = Column(JSON, nullable=True)
    # Example: {
    #   "work_type": "research",
    #   "complexity_score": 8,
    #   "impact_score": 9,
    #   "time_estimate_hours": 16,
    #   "artifacts": [...],
    #   "explanation": "..."
    # }

    # Relationships
    developer = relationship("DeveloperProfile", back_populates="jira_tickets")
    comments = relationship("JiraComment", back_populates="ticket")

    def __repr__(self):
        return f"<JiraTicket {self.ticket_key}>"


class JiraComment(Base):
    """Jira comment model"""

    __tablename__ = "jira_comments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("jira_tickets.id"), nullable=False, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False, index=True)

    # Comment details
    comment_id = Column(String, nullable=False, index=True)  # Jira comment ID
    comment_text = Column(Text, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    # AI Analysis
    analyzed = Column(Integer, default=0)  # 0=False, 1=True
    analysis_result = Column(JSON, nullable=True)
    # Example: {
    #   "contribution_type": "solution",
    #   "helpfulness": "high",
    #   "collaboration_detected": true
    # }

    # Relationships
    ticket = relationship("JiraTicket", back_populates="comments")
    developer = relationship("DeveloperProfile", back_populates="jira_comments")

    def __repr__(self):
        return f"<JiraComment {self.comment_id} on {self.ticket_id}>"
