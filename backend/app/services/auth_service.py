"""Authentication service for user registration and login"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import timedelta

from app.models import User, DeveloperProfile
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.config import settings


class AuthService:
    """Service for handling authentication operations"""

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        full_name: str,
        role: str = "developer",
    ) -> User:
        """
        Create a new user

        Args:
            db: Database session
            email: User email
            password: Plain text password
            full_name: User's full name
            role: User role (admin, manager, developer)

        Returns:
            Created User object
        """
        # Hash the password
        hashed_password = get_password_hash(password)

        # Create user
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=1,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        """
        Create an access token for a user

        Args:
            user: User object

        Returns:
            JWT access token string
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role},
            expires_delta=access_token_expires,
        )

        return access_token

    @staticmethod
    def get_current_user(db: Session, token_payload: Dict[str, Any]) -> Optional[User]:
        """
        Get current user from token payload

        Args:
            db: Database session
            token_payload: Decoded JWT token payload

        Returns:
            User object or None
        """
        user_id = token_payload.get("sub")
        if user_id is None:
            return None

        user = db.query(User).filter(User.id == int(user_id)).first()
        return user
