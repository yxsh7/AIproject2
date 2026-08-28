"""Developer management API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.developer import (
    DeveloperProfileCreate,
    DeveloperProfileUpdate,
    DeveloperProfileResponse,
    DeveloperWithUser,
)
from app.models import DeveloperProfile, User
from app.api.dependencies import get_current_active_user, require_manager_or_admin, get_current_org_id

router = APIRouter()


@router.post(
    "/", response_model=DeveloperProfileResponse, status_code=status.HTTP_201_CREATED
)
def create_developer_profile(
    profile_data: DeveloperProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
    org_id: int = Depends(get_current_org_id),
):
    """
    Create a new developer profile (Manager/Admin only)

    Args:
        profile_data: Developer profile data
        db: Database session
        current_user: Current authenticated user (manager or admin)

    Returns:
        Created developer profile

    Raises:
        HTTPException: If user doesn't exist, belongs to another org, or already has a profile
    """
    # Check if user exists and belongs to the caller's organization
    user = db.query(User).filter(User.id == profile_data.user_id).first()
    if not user or user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if developer profile already exists
    existing_profile = (
        db.query(DeveloperProfile)
        .filter(DeveloperProfile.user_id == profile_data.user_id)
        .first()
    )
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Developer profile already exists for this user",
        )

    # Validate role_level
    valid_roles = ["intern", "junior", "mid", "senior", "staff", "principal"]
    if profile_data.role_level not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role_level. Must be one of: {', '.join(valid_roles)}",
        )

    # Create developer profile — organization_id always comes from the caller's own
    # org, never trusted from the request body
    developer_profile = DeveloperProfile(**profile_data.dict(), organization_id=org_id)
    db.add(developer_profile)
    db.commit()
    db.refresh(developer_profile)

    return developer_profile


@router.get("/", response_model=List[DeveloperWithUser])
def list_developers(
    team: Optional[str] = Query(None, description="Filter by team"),
    role_level: Optional[str] = Query(None, description="Filter by role level"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    org_id: int = Depends(get_current_org_id),
):
    """
    List all developer profiles in the caller's organization

    Args:
        team: Optional filter by team
        role_level: Optional filter by role level
        skip: Number of records to skip (pagination)
        limit: Max number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of developer profiles with user info
    """
    # Build query, scoped to the caller's organization
    query = db.query(DeveloperProfile).join(User).filter(DeveloperProfile.organization_id == org_id)

    # Apply filters
    if team:
        query = query.filter(DeveloperProfile.team == team)

    if role_level:
        query = query.filter(DeveloperProfile.role_level == role_level)

    # Get results
    developers = query.offset(skip).limit(limit).all()

    # Format response with user info
    result = []
    for dev in developers:
        result.append(
            DeveloperWithUser(
                id=dev.id,
                user_id=dev.user_id,
                email=dev.user.email,
                full_name=dev.user.full_name,
                role_level=dev.role_level,
                team=dev.team,
                github_username=dev.github_username,
                jira_username=dev.jira_username,
                created_at=dev.created_at,
            )
        )

    return result


@router.get("/{developer_id}", response_model=DeveloperProfileResponse)
def get_developer(
    developer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    org_id: int = Depends(get_current_org_id),
):
    """
    Get a specific developer profile

    Args:
        developer_id: Developer profile ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Developer profile

    Raises:
        HTTPException: If developer not found, belongs to another org, or unauthorized
    """
    developer = (
        db.query(DeveloperProfile).filter(DeveloperProfile.id == developer_id).first()
    )

    if not developer or developer.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Developer not found"
        )

    # Developers can only see their own profile, managers/admins can see all
    if current_user.role == "developer":
        if developer.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own profile",
            )

    return developer


@router.patch("/{developer_id}", response_model=DeveloperProfileResponse)
def update_developer(
    developer_id: int,
    profile_update: DeveloperProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    org_id: int = Depends(get_current_org_id),
):
    """
    Update a developer profile.
    Developers can update their own profile; managers/admins can update any profile
    within their own organization.
    """
    developer = (
        db.query(DeveloperProfile).filter(DeveloperProfile.id == developer_id).first()
    )

    if not developer or developer.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Developer not found"
        )

    # Developers can only update their own profile
    if current_user.role not in ("manager", "admin"):
        if developer.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own profile",
            )
        # Developers cannot change their own role_level
        profile_update_data = profile_update.dict(exclude_unset=True)
        profile_update_data.pop("role_level", None)
        profile_update = DeveloperProfileUpdate(**profile_update_data)

    # Update only provided fields
    update_data = profile_update.dict(exclude_unset=True)

    # Validate role_level if provided
    if "role_level" in update_data:
        valid_roles = ["intern", "junior", "mid", "senior", "staff", "principal"]
        if update_data["role_level"] not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role_level. Must be one of: {', '.join(valid_roles)}",
            )

    for key, value in update_data.items():
        setattr(developer, key, value)

    db.commit()
    db.refresh(developer)

    return developer


@router.delete("/{developer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_developer(
    developer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
    org_id: int = Depends(get_current_org_id),
):
    """
    Delete a developer profile (Manager/Admin only)

    Args:
        developer_id: Developer profile ID
        db: Database session
        current_user: Current authenticated user (manager or admin)

    Raises:
        HTTPException: If developer not found or belongs to another org
    """
    developer = (
        db.query(DeveloperProfile).filter(DeveloperProfile.id == developer_id).first()
    )

    if not developer or developer.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Developer not found"
        )

    db.delete(developer)
    db.commit()

    return None
