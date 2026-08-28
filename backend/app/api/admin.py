"""Superadmin (platform-level) API endpoints — cross-organization visibility and controls"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.schemas.admin import (
    AdminOrganizationResponse,
    AdminOrganizationUpdate,
    AdminUserResponse,
    AdminUserUpdate,
)
from app.models import Organization, User, DeveloperProfile
from app.api.dependencies import require_superadmin

router = APIRouter()


@router.get("/organizations", response_model=List[AdminOrganizationResponse])
def list_organizations(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_superadmin),
):
    """List every organization on the platform with basic stats."""
    user_counts = dict(
        db.query(User.organization_id, func.count(User.id))
        .group_by(User.organization_id)
        .all()
    )
    developer_counts = dict(
        db.query(DeveloperProfile.organization_id, func.count(DeveloperProfile.id))
        .group_by(DeveloperProfile.organization_id)
        .all()
    )

    orgs = db.query(Organization).order_by(Organization.created_at.desc()).all()
    return [
        AdminOrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            is_active=org.is_active,
            user_count=user_counts.get(org.id, 0),
            developer_count=developer_counts.get(org.id, 0),
            created_at=org.created_at,
        )
        for org in orgs
    ]


@router.get("/organizations/{org_id}", response_model=AdminOrganizationResponse)
def get_organization(
    org_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_superadmin),
):
    """Get a single organization's detail and stats."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    user_count = db.query(func.count(User.id)).filter(User.organization_id == org_id).scalar()
    developer_count = (
        db.query(func.count(DeveloperProfile.id))
        .filter(DeveloperProfile.organization_id == org_id)
        .scalar()
    )

    return AdminOrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        is_active=org.is_active,
        user_count=user_count,
        developer_count=developer_count,
        created_at=org.created_at,
    )


@router.patch("/organizations/{org_id}", response_model=AdminOrganizationResponse)
def update_organization(
    org_id: int,
    data: AdminOrganizationUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_superadmin),
):
    """Suspend or reactivate an organization. Suspension is enforced on every
    subsequent request from that org's users via get_current_active_user."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    org.is_active = data.is_active
    db.commit()
    db.refresh(org)

    user_count = db.query(func.count(User.id)).filter(User.organization_id == org_id).scalar()
    developer_count = (
        db.query(func.count(DeveloperProfile.id))
        .filter(DeveloperProfile.organization_id == org_id)
        .scalar()
    )

    return AdminOrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        is_active=org.is_active,
        user_count=user_count,
        developer_count=developer_count,
        created_at=org.created_at,
    )


@router.get("/users", response_model=List[AdminUserResponse])
def list_all_users(
    organization_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_superadmin),
):
    """List users across every organization, optionally filtered to one org."""
    query = db.query(User, Organization.name).join(Organization, User.organization_id == Organization.id)
    if organization_id is not None:
        query = query.filter(User.organization_id == organization_id)

    rows = query.order_by(User.created_at.desc()).all()
    return [
        AdminUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_superadmin=user.is_superadmin,
            organization_id=user.organization_id,
            organization_name=org_name,
            created_at=user.created_at,
        )
        for user, org_name in rows
    ]


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
def update_user(
    user_id: int,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_superadmin),
):
    """Deactivate or reactivate a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = data.is_active
    db.commit()
    db.refresh(user)

    org = db.query(Organization).filter(Organization.id == user.organization_id).first()

    return AdminUserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        is_superadmin=user.is_superadmin,
        organization_id=user.organization_id,
        organization_name=org.name if org else "",
        created_at=user.created_at,
    )
