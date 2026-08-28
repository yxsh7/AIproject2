"""Add organization_invites table and organizations.is_active

Revision ID: 008
Revises: 007
Create Date: 2026-08-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'organizations',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    )

    # Reuse the existing `userrole` enum type (created in migration 001) rather than
    # letting op.create_table try to CREATE TYPE again — postgresql.ENUM with
    # create_type=False is the documented way to reference an already-existing
    # Postgres enum type from a new table/column.
    userrole_enum = postgresql.ENUM('admin', 'manager', 'developer', name='userrole', create_type=False)

    op.create_table(
        'organization_invites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('role', userrole_enum, nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('used_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code', name='uq_organization_invite_code'),
    )
    op.create_index('ix_organization_invites_organization_id', 'organization_invites', ['organization_id'])
    op.create_index('ix_organization_invites_code', 'organization_invites', ['code'])


def downgrade() -> None:
    op.drop_index('ix_organization_invites_code', 'organization_invites')
    op.drop_index('ix_organization_invites_organization_id', 'organization_invites')
    op.drop_table('organization_invites')
    op.drop_column('organizations', 'is_active')
