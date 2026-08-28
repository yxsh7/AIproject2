"""User model"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""

    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"


class User(Base):
    """User account model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.DEVELOPER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superadmin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Relationships
    developer_profile = relationship("DeveloperProfile", back_populates="user", uselist=False)
    organization = relationship("Organization", foreign_keys=[organization_id])

    def __repr__(self):
        return f"<User {self.email}>"
