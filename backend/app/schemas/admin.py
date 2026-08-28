"""Superadmin (platform-level) schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AdminOrganizationResponse(BaseModel):
    """Schema for an organization row in the superadmin org list"""

    id: int
    name: str
    slug: str
    is_active: bool
    user_count: int
    developer_count: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminOrganizationUpdate(BaseModel):
    """Schema for suspending/reactivating an organization"""

    is_active: bool


class AdminUserResponse(BaseModel):
    """Schema for a user row in the superadmin cross-org user list"""

    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    is_superadmin: bool
    organization_id: int
    organization_name: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminUserUpdate(BaseModel):
    """Schema for deactivating/reactivating a user"""

    is_active: bool
