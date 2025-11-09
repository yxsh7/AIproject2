"""Git activity models (commits, PRs, code reviews)"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class GitCommit(Base):
    """Git commit model"""

    __tablename__ = "git_commits"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False, index=True)

    # Commit details
    repo_name = Column(String, nullable=False, index=True)
    commit_sha = Column(String, unique=True, nullable=False, index=True)
    message = Column(Text, nullable=False)
    branch = Column(String, nullable=True)

    # Stats
    files_changed = Column(Integer, default=0)
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)

    # Timestamps
    committed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # AI Analysis
    analyzed = Column(Integer, default=0)  # 0=False, 1=True
    analysis_result = Column(JSON, nullable=True)
    # Example: {
    #   "complexity_score": 8,
    #   "quality_score": 7,
    #   "work_type": "refactoring",
    #   "impact_level": "high",
    #   "explanation": "..."
    # }

    # Relationships
    developer = relationship("DeveloperProfile", back_populates="git_commits")

    def __repr__(self):
        return f"<GitCommit {self.commit_sha[:8]} - {self.repo_name}>"


class PullRequest(Base):
    """Pull request model"""

    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False, index=True)

    # PR details
    repo_name = Column(String, nullable=False, index=True)
    pr_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    state = Column(String, nullable=False, index=True)  # open, merged, closed

    # Stats
    files_changed = Column(Integer, default=0)
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    commits_count = Column(Integer, default=0)

    # URLs
    html_url = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    merged_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # AI Analysis
    analyzed = Column(Integer, default=0)  # 0=False, 1=True
    analysis_result = Column(JSON, nullable=True)

    # Relationships
    developer = relationship("DeveloperProfile", back_populates="pull_requests")
    code_reviews = relationship("CodeReview", back_populates="pull_request")

    def __repr__(self):
        return f"<PullRequest #{self.pr_number} - {self.repo_name}>"


class CodeReview(Base):
    """Code review model (reviews given by developers)"""

    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False, index=True)
    pr_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=False)

    # Review details
    comment_count = Column(Integer, default=0)
    review_state = Column(String, nullable=True)  # approved, changes_requested, commented

    # Timestamps
    reviewed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # AI Analysis
    quality_score = Column(Integer, nullable=True)  # 0-10 scale
    analysis_result = Column(JSON, nullable=True)
    # Example: {
    #   "helpfulness": "high",
    #   "mentoring_detected": true,
    #   "security_issues_found": 1,
    #   "explanation": "..."
    # }

    # Relationships
    reviewer = relationship("DeveloperProfile", back_populates="code_reviews", foreign_keys=[reviewer_id])
    pull_request = relationship("PullRequest", back_populates="code_reviews")

    def __repr__(self):
        return f"<CodeReview by {self.reviewer_id} on PR {self.pr_id}>"
