"""Integration schemas"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime


class GitHubIntegrationCreate(BaseModel):
    """Schema for creating GitHub integration"""

    organization_name: str = Field(..., description="GitHub organization name")
    access_token: str = Field(..., description="GitHub personal access token or OAuth token")
    repos: Optional[list[str]] = Field(
        default=None,
        description=(
            "Limit sync to these repos (full 'owner/repo' names). Omit to scan every "
            "repo the token can access — fine for a real GitHub org, but slow and "
            "over-broad for a personal-account token, since it pulls in unrelated "
            "personal/other-employer repos too."
        ),
    )


class JiraIntegrationCreate(BaseModel):
    """Schema for creating Jira integration"""

    workspace_url: HttpUrl = Field(..., description="Jira workspace URL (e.g., https://yourcompany.atlassian.net)")
    username: str = Field(..., description="Jira username/email")
    api_token: str = Field(..., description="Jira API token")
    project_keys: Optional[list[str]] = Field(default=None, description="List of Jira project keys to sync")


class SlackIntegrationCreate(BaseModel):
    """Schema for creating Slack integration"""

    bot_token: str = Field(..., description="Slack bot token (xoxb-...)")
    channel_ids: list[str] = Field(..., description="List of Slack channel IDs to monitor")


class IntegrationResponse(BaseModel):
    """Schema for integration response"""

    id: int
    organization_id: int
    type: str
    status: str
    last_sync_at: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class IntegrationSyncRequest(BaseModel):
    """Schema for triggering integration sync"""

    days_back: int = Field(default=30, ge=1, le=365, description="Number of days to sync back")


class IntegrationSyncResponse(BaseModel):
    """Schema for sync response"""

    job_id: str
    message: str
    estimated_time_minutes: int


class SyncStatusResponse(BaseModel):
    """Schema for sync status response"""

    integration_id: int
    status: str
    last_sync_at: Optional[datetime]
    last_error: Optional[str]
    next_sync_estimate: Optional[datetime]
    progress: Optional[Dict[str, Any]]


class IntegrationTestResponse(BaseModel):
    """Schema for integration test response"""

    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
