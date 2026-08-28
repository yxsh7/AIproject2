"""Make users.organization_id NOT NULL

Revision ID: 007
Revises: 006
Create Date: 2026-08-24
"""
from alembic import op
import sqlalchemy as sa

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE users SET organization_id = 1 WHERE organization_id IS NULL")
    op.alter_column('users', 'organization_id', nullable=False)


def downgrade() -> None:
    op.alter_column('users', 'organization_id', nullable=True)
