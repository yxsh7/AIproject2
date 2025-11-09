"""API dependencies for authentication and authorization"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.utils.security import decode_access_token
from app.services.auth_service import AuthService

# Security scheme for JWT
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer credentials (JWT token)
        db: Database session

    Returns:
        Current authenticated User

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    token_payload = decode_access_token(credentials.credentials)
    if token_payload is None:
        raise credentials_exception

    # Get user from database
    user = AuthService.get_current_user(db, token_payload)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current active user

    Args:
        current_user: Current authenticated user

    Returns:
        Current active User

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(required_role: str):
    """
    Dependency factory to require a specific user role

    Args:
        required_role: Required role (admin, manager, developer)

    Returns:
        Dependency function
    """

    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This endpoint requires {required_role} role",
            )
        return current_user

    return role_checker


def require_manager_or_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require manager or admin role

    Args:
        current_user: Current authenticated user

    Returns:
        Current user if manager or admin

    Raises:
        HTTPException: If user is not manager or admin
    """
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires manager or admin role",
        )
    return current_user
