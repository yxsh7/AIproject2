"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import UserRegister, UserLogin, UserWithToken, UserResponse
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_active_user
from app.models import User

router = APIRouter()


@router.post("/register", response_model=UserWithToken, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user with access token

    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Validate role
    valid_roles = ["admin", "manager", "developer"]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )

    # Create user
    user = AuthService.create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role,
    )

    # Generate access token
    access_token = AuthService.create_access_token_for_user(user)

    return UserWithToken(
        user=UserResponse.from_orm(user), access_token=access_token, token_type="bearer"
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
        user=UserResponse.from_orm(user), access_token=access_token, token_type="bearer"
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
    return UserResponse.from_orm(current_user)
