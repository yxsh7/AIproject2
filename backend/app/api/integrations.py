"""Integration management API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.integration import (
    GitHubIntegrationCreate,
    JiraIntegrationCreate,
    IntegrationResponse,
    IntegrationSyncRequest,
    IntegrationSyncResponse,
    SyncStatusResponse,
    IntegrationTestResponse,
)
from app.models import IntegrationConfig, IntegrationType, IntegrationStatus, User
from app.api.dependencies import get_current_active_user
from app.services.github_service import GitHubService
from app.services.jira_service import JiraService

router = APIRouter()


@router.post("/github", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
def create_github_integration(
    integration_data: GitHubIntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Configure GitHub integration (Admin only)

    Args:
        integration_data: GitHub integration configuration
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created integration configuration

    Raises:
        HTTPException: If user is not admin or integration fails
    """
    # Only admins can configure integrations
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can configure integrations",
        )

    organization_id = current_user.organization_id or 1

    # Test the connection first
    try:
        github_service = GitHubService(access_token=integration_data.access_token)
        if not github_service.test_connection():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to connect to GitHub. Please check your access token.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub connection error: {str(e)}",
        )

    # Check if GitHub integration already exists for this org
    existing = (
        db.query(IntegrationConfig)
        .filter(
            IntegrationConfig.organization_id == organization_id,
            IntegrationConfig.type == IntegrationType.GITHUB,
        )
        .first()
    )

    if existing:
        # Update existing integration
        existing.config = {
            "organization_name": integration_data.organization_name,
            "access_token": integration_data.access_token,
        }
        existing.status = IntegrationStatus.ACTIVE
        db.commit()
        db.refresh(existing)
        return existing

    # Create new integration
    integration = IntegrationConfig(
        organization_id=organization_id,
        type=IntegrationType.GITHUB,
        status=IntegrationStatus.ACTIVE,
        config={
            "organization_name": integration_data.organization_name,
            "access_token": integration_data.access_token,
        },
    )

    db.add(integration)
    db.commit()
    db.refresh(integration)

    return integration


@router.post("/jira", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
def create_jira_integration(
    integration_data: JiraIntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Configure Jira integration (Admin only)

    Args:
        integration_data: Jira integration configuration
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created integration configuration

    Raises:
        HTTPException: If user is not admin or integration fails
    """
    # Only admins can configure integrations
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can configure integrations",
        )

    organization_id = current_user.organization_id or 1

    # Test the connection first
    try:
        jira_service = JiraService(
            url=str(integration_data.workspace_url),
            username=integration_data.username,
            api_token=integration_data.api_token,
        )
        if not jira_service.test_connection():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to connect to Jira. Please check your credentials.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Jira connection error: {str(e)}",
        )

    # Check if Jira integration already exists
    existing = (
        db.query(IntegrationConfig)
        .filter(
            IntegrationConfig.organization_id == organization_id,
            IntegrationConfig.type == IntegrationType.JIRA,
        )
        .first()
    )

    if existing:
        # Update existing integration
        existing.config = {
            "url": str(integration_data.workspace_url),
            "username": integration_data.username,
            "api_token": integration_data.api_token,
            "project_keys": integration_data.project_keys or [],
        }
        existing.status = IntegrationStatus.ACTIVE
        db.commit()
        db.refresh(existing)
        return existing

    # Create new integration
    integration = IntegrationConfig(
        organization_id=organization_id,
        type=IntegrationType.JIRA,
        status=IntegrationStatus.ACTIVE,
        config={
            "url": str(integration_data.workspace_url),
            "username": integration_data.username,
            "api_token": integration_data.api_token,
            "project_keys": integration_data.project_keys or [],
        },
    )

    db.add(integration)
    db.commit()
    db.refresh(integration)

    return integration


@router.get("/", response_model=List[IntegrationResponse])
def list_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all integrations for the organization

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of integrations
    """
    organization_id = current_user.organization_id or 1

    integrations = (
        db.query(IntegrationConfig)
        .filter(IntegrationConfig.organization_id == organization_id)
        .all()
    )

    return integrations


@router.post("/{integration_id}/sync", response_model=IntegrationSyncResponse)
async def trigger_sync(
    integration_id: int,
    sync_request: IntegrationSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Trigger manual sync for an integration

    Args:
        integration_id: Integration ID
        sync_request: Sync configuration (days back)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Sync job information

    Raises:
        HTTPException: If integration not found or user not authorized
    """
    # Only managers and admins can trigger syncs
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers and admins can trigger syncs",
        )

    integration = (
        db.query(IntegrationConfig)
        .filter(IntegrationConfig.id == integration_id)
        .first()
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found"
        )

    # Update integration status
    integration.status = IntegrationStatus.SYNCING
    db.commit()

    # Import here to avoid circular imports
    from app.tasks.sync_tasks import sync_integration_task

    # Trigger background task
    job = sync_integration_task.delay(integration_id, sync_request.days_back)

    return IntegrationSyncResponse(
        job_id=str(job.id),
        message=f"Sync started for {integration.type} integration",
        estimated_time_minutes=5,  # Rough estimate
    )


@router.get("/{integration_id}/status", response_model=SyncStatusResponse)
def get_sync_status(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get sync status for an integration

    Args:
        integration_id: Integration ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Sync status information

    Raises:
        HTTPException: If integration not found
    """
    integration = (
        db.query(IntegrationConfig)
        .filter(IntegrationConfig.id == integration_id)
        .first()
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found"
        )

    return SyncStatusResponse(
        integration_id=integration.id,
        status=integration.status,
        last_sync_at=integration.last_sync_at,
        last_error=integration.last_error,
        next_sync_estimate=None,  # We'll implement this later
        progress=None,
    )


@router.post("/{integration_id}/test", response_model=IntegrationTestResponse)
def test_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Test an integration connection

    Args:
        integration_id: Integration ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Test result

    Raises:
        HTTPException: If integration not found or user not authorized
    """
    # Only admins can test integrations
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can test integrations",
        )

    integration = (
        db.query(IntegrationConfig)
        .filter(IntegrationConfig.id == integration_id)
        .first()
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found"
        )

    try:
        if integration.type == IntegrationType.GITHUB:
            service = GitHubService.from_integration_config(integration)
            success = service.test_connection()
            message = "GitHub connection successful" if success else "GitHub connection failed"

        elif integration.type == IntegrationType.JIRA:
            service = JiraService.from_integration_config(integration)
            success = service.test_connection()
            message = "Jira connection successful" if success else "Jira connection failed"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Integration type {integration.type} not supported",
            )

        return IntegrationTestResponse(success=success, message=message)

    except Exception as e:
        return IntegrationTestResponse(
            success=False, message=f"Connection error: {str(e)}"
        )


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete an integration (Admin only)

    Args:
        integration_id: Integration ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If integration not found or user not authorized
    """
    # Only admins can delete integrations
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete integrations",
        )

    integration = (
        db.query(IntegrationConfig)
        .filter(IntegrationConfig.id == integration_id)
        .first()
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found"
        )

    db.delete(integration)
    db.commit()

    return None
