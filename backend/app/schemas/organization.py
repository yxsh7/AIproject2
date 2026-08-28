"""Organization and invite schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrganizationResponse(BaseModel):
    """Schema for organization response"""

    id: int
    name: str
    slug: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InviteCreate(BaseModel):
    """Schema for creating an invite code"""

    role: str = Field(..., description="Role granted to whoever redeems this code: developer or manager")
    max_uses: Optional[int] = Field(default=None, description="Max redemptions; omit for unlimited")
    expires_in_days: Optional[int] = Field(default=None, description="Days until expiry; omit for never")


class InviteResponse(BaseModel):
    """Schema for invite response"""

    id: int
    organization_id: int
    code: str
    role: str
    max_uses: Optional[int]
    used_count: int
    expires_at: Optional[datetime]
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
