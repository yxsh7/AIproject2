"""Authentication schemas"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Schema for user registration"""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=2)
    role: str = Field(default="developer", description="User role: admin, manager, developer")


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data"""

    email: Optional[str] = None
    user_id: Optional[int] = None


class UserResponse(BaseModel):
    """Schema for user response"""

    id: int
    email: str
    full_name: str
    role: str
    is_active: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class UserWithToken(BaseModel):
    """Schema for user with access token"""

    user: UserResponse
    access_token: str
    token_type: str = "bearer"
