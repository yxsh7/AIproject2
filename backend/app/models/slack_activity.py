"""Slack activity models"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, JSON, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class SlackMessage(Base):
    """A message sent by a developer in a monitored Slack channel."""

    __tablename__ = "slack_messages"

    __table_args__ = (
        UniqueConstraint('message_ts', name='uq_slack_message_ts'),
    )

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False, index=True)
    channel_id = Column(String, nullable=False)
    channel_name = Column(String, nullable=True)
    message_ts = Column(String, nullable=False)  # Slack timestamp — globally unique; uniqueness enforced by uq_slack_message_ts constraint
    message_date = Column(Date, nullable=False)
    has_code_block = Column(Integer, nullable=False, default=0)
    reply_count = Column(Integer, nullable=False, default=0)
    reaction_count = Column(Integer, nullable=False, default=0)
    analyzed = Column(Integer, nullable=False, default=0)
    analysis_result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    developer = relationship("DeveloperProfile", foreign_keys=[developer_id], back_populates="slack_messages")

    def __repr__(self):
        return f"<SlackMessage {self.message_ts} in {self.channel_name}>"


class SlackReaction(Base):
    """An emoji reaction given by a developer to another user's message."""

    __tablename__ = "slack_reactions"

    __table_args__ = (
        UniqueConstraint('developer_id', 'reaction_name', 'target_message_ts', name='uq_slack_reaction'),
    )

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False, index=True)
    reaction_name = Column(String, nullable=False)
    target_message_ts = Column(String, nullable=False)  # No FK — reactions may reference messages in unmonitored channels
    target_user_id = Column(String, nullable=True)
    reaction_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    developer = relationship("DeveloperProfile", foreign_keys=[developer_id], back_populates="slack_reactions")

    def __repr__(self):
        return f"<SlackReaction :{self.reaction_name}: by {self.developer_id}>"
