"""Authentication schemas"""

from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional
from datetime import datetime
import enum


class RegisterMode(str, enum.Enum):
    """How a new user joins the platform"""

    CREATE_ORG = "create_org"
    JOIN_ORG = "join_org"


class UserRegister(BaseModel):
    """
    Schema for user registration.

    A user either creates a brand-new company (becoming its admin) or joins an
    existing one via an invite code (landing with the role the code grants).
    Role is never accepted directly from the client — accepting it there let
    anyone self-promote to admin (`POST /register {"role": "admin"}` worked
    unconditionally before this schema existed).
    """

    email: EmailStr
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )
    full_name: str = Field(..., min_length=2)
    mode: RegisterMode
    organization_name: Optional[str] = Field(
        default=None, min_length=2, description="Required when mode=create_org"
    )
    invite_code: Optional[str] = Field(
        default=None, description="Required when mode=join_org"
    )

    @model_validator(mode="after")
    def _validate_mode_fields(self):
        if self.mode == RegisterMode.CREATE_ORG and not self.organization_name:
            raise ValueError(
                "organization_name is required when creating a new company"
            )
        if self.mode == RegisterMode.JOIN_ORG and not self.invite_code:
            raise ValueError("invite_code is required when joining with an invite code")
        return self


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
    is_active: bool
    organization_id: int
    is_superadmin: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class UserWithToken(BaseModel):
    """Schema for user with access token"""

    user: UserResponse
    access_token: str
    token_type: str = "bearer"
