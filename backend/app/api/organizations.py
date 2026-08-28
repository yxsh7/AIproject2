"""Organization and invite-code API endpoints"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.organization import (
    OrganizationResponse,
    InviteCreate,
    InviteResponse,
    ScoringWeights,
)
from app.models import Organization, OrganizationInvite, User
from app.api.dependencies import require_role, get_current_org_id
from app.services.scoring_service import ROLE_WEIGHTS
from app.models.developer import RoleLevel

router = APIRouter()

INVITABLE_ROLES = {"developer", "manager"}


def _generate_invite_code() -> str:
    return secrets.token_urlsafe(6)


@router.get("/me", response_model=OrganizationResponse)
def get_my_organization(
    db: Session = Depends(get_db),
    org_id: int = Depends(get_current_org_id),
):
    """Get the current user's organization."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    return org


@router.post(
    "/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED
)
def create_invite(
    data: InviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
    org_id: int = Depends(get_current_org_id),
):
    """Generate an invite code for the current organization (admin only).

    Codes carry a fixed role chosen here, not picked by whoever redeems them —
    this keeps a shared join link from letting someone self-select 'manager'.
    """
    if data.role not in INVITABLE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"role must be one of: {', '.join(sorted(INVITABLE_ROLES))}",
        )

    expires_at = None
    if data.expires_in_days is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=data.expires_in_days)

    invite = OrganizationInvite(
        organization_id=org_id,
        code=_generate_invite_code(),
        role=data.role,
        created_by=current_user.id,
        max_uses=data.max_uses,
        expires_at=expires_at,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


@router.get("/invites", response_model=List[InviteResponse])
def list_invites(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
    org_id: int = Depends(get_current_org_id),
):
    """List invite codes for the current organization (admin only)."""
    return (
        db.query(OrganizationInvite)
        .filter(OrganizationInvite.organization_id == org_id)
        .order_by(OrganizationInvite.created_at.desc())
        .all()
    )


@router.delete("/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_invite(
    invite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
    org_id: int = Depends(get_current_org_id),
):
    """Revoke an invite code (admin only)."""
    invite = (
        db.query(OrganizationInvite)
        .filter(
            OrganizationInvite.id == invite_id,
            OrganizationInvite.organization_id == org_id,
        )
        .first()
    )
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found"
        )

    invite.is_active = False
    db.commit()
    return None


@router.get("/scoring-weights", response_model=ScoringWeights)
def get_scoring_weights(
    db: Session = Depends(get_db),
    org_id: int = Depends(get_current_org_id),
):
    """
    Get the current organization's custom scoring weight profile.

    Returns the org's override if one is set, otherwise the built-in
    MID-level defaults — a sane, valid starting point for the editor
    rather than an empty form.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    weights = org.custom_scoring_weights or ROLE_WEIGHTS[RoleLevel.MID]
    return ScoringWeights(**weights)


@router.put("/scoring-weights", response_model=ScoringWeights)
def update_scoring_weights(
    data: ScoringWeights,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
    org_id: int = Depends(get_current_org_id),
):
    """
    Set a custom scoring weight profile for the current organization
    (admin only). Applies uniformly across all role levels going
    forward — existing saved scores are not retroactively recomputed.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    org.custom_scoring_weights = data.model_dump()
    db.commit()
    return data
