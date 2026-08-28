"""Authentication API endpoints"""
import re
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import UserRegister, UserLogin, UserWithToken, UserResponse, RegisterMode
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_active_user
from app.models import User, Organization, OrganizationInvite

router = APIRouter()


def _slugify_unique(db: Session, name: str) -> str:
    """Turn an organization name into a unique URL-safe slug."""
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "org"
    slug = base
    suffix = 2
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{base}-{suffix}"
        suffix += 1
    return slug


def _redeem_invite(db: Session, code: str) -> OrganizationInvite:
    """Validate and return a usable invite, raising 400 if it can't be redeemed."""
    invite = db.query(OrganizationInvite).filter(OrganizationInvite.code == code).first()
    if not invite or not invite.is_active:
        raise HTTPException(status_code=400, detail="Invalid or expired invite code")
    if invite.expires_at and invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired invite code")
    if invite.max_uses is not None and invite.used_count >= invite.max_uses:
        raise HTTPException(status_code=400, detail="Invalid or expired invite code")
    return invite


@router.post("/register", response_model=UserWithToken, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user, either creating a new company (becoming its admin) or
    joining an existing one via an invite code (landing with the invite's role).

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user with access token

    Raises:
        HTTPException: If email already exists, or the invite code is invalid/expired
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    if user_data.mode == RegisterMode.CREATE_ORG:
        slug = _slugify_unique(db, user_data.organization_name)
        org = Organization(name=user_data.organization_name, slug=slug)
        db.add(org)
        db.commit()
        db.refresh(org)

        user = AuthService.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            organization_id=org.id,
            role="admin",
        )
    else:
        invite = _redeem_invite(db, user_data.invite_code)

        user = AuthService.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            organization_id=invite.organization_id,
            role=invite.role.value,
        )

        invite.used_count += 1
        db.commit()

    # Generate access token
    access_token = AuthService.create_access_token_for_user(user)

    return UserWithToken(
        user=UserResponse.model_validate(user), access_token=access_token, token_type="bearer"
    )


@router.post("/login", response_model=UserWithToken)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password

    Args:
        user_credentials: Login credentials
        db: Database session

    Returns:
        User with access token

    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user
    user = AuthService.authenticate_user(
        db=db, email=user_credentials.email, password=user_credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token = AuthService.create_access_token_for_user(user)

    return UserWithToken(
        user=UserResponse.model_validate(user), access_token=access_token, token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user information

    Args:
        current_user: Current authenticated user (from JWT token)

    Returns:
        Current user information
    """
    return UserResponse.model_validate(current_user)
