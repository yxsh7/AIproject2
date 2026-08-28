"""Organization and invite schemas"""

from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime


class ScoringWeights(BaseModel):
    """
    Custom weight profile overriding the built-in per-role-level defaults
    (ROLE_WEIGHTS in scoring_service.py). Applies uniformly across all role
    levels for the organization when set.
    """

    complexity: float = Field(..., ge=0, le=1)
    velocity: float = Field(..., ge=0, le=1)
    quality: float = Field(..., ge=0, le=1)
    impact: float = Field(..., ge=0, le=1)
    collaboration: float = Field(..., ge=0, le=1)
    mentoring: float = Field(..., ge=0, le=1)

    @model_validator(mode="after")
    def _weights_sum_to_one(self):
        total = (
            self.complexity
            + self.velocity
            + self.quality
            + self.impact
            + self.collaboration
            + self.mentoring
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0 (got {total:.3f})")
        return self


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

    role: str = Field(
        ...,
        description="Role granted to whoever redeems this code: developer or manager",
    )
    max_uses: Optional[int] = Field(
        default=None, description="Max redemptions; omit for unlimited"
    )
    expires_in_days: Optional[int] = Field(
        default=None, description="Days until expiry; omit for never"
    )


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
