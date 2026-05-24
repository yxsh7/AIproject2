"""Add organization_id to users

Revision ID: 002
Revises: 001_initial
Create Date: 2026-03-19
"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('organization_id', sa.Integer(), nullable=True)
    )
    # Set existing users to org 1
    op.execute("UPDATE users SET organization_id = 1 WHERE organization_id IS NULL")
    op.create_foreign_key(
        'fk_users_organization_id',
        'users', 'organizations',
        ['organization_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_users_organization_id', 'users', type_='foreignkey')
    op.drop_column('users', 'organization_id')
