"""Developer profile schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DeveloperProfileCreate(BaseModel):
    """Schema for creating a developer profile"""

    user_id: int
    organization_id: int
    role_level: str = Field(..., description="Role level: intern, junior, mid, senior, staff, principal")
    team: Optional[str] = None
    job_title: Optional[str] = None
    github_username: Optional[str] = None
    jira_username: Optional[str] = None
    slack_user_id: Optional[str] = None
    focus_areas: Optional[List[str]] = Field(default=None, description="List of focus areas")
    bio: Optional[str] = None


class DeveloperProfileUpdate(BaseModel):
    """Schema for updating a developer profile"""

    role_level: Optional[str] = None
    team: Optional[str] = None
    job_title: Optional[str] = None
    github_username: Optional[str] = None
    jira_username: Optional[str] = None
    slack_user_id: Optional[str] = None
    focus_areas: Optional[List[str]] = None
    bio: Optional[str] = None


class DeveloperProfileResponse(BaseModel):
    """Schema for developer profile response"""

    id: int
    user_id: int
    organization_id: int
    role_level: str
    team: Optional[str]
    job_title: Optional[str]
    github_username: Optional[str]
    jira_username: Optional[str]
    slack_user_id: Optional[str]
    focus_areas: Optional[List[str]]
    bio: Optional[str]
    start_date: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class DeveloperWithUser(BaseModel):
    """Schema for developer with user info"""

    id: int
    user_id: int
    email: str
    full_name: str
    role_level: str
    team: Optional[str]
    github_username: Optional[str]
    jira_username: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
