"""Add organization_id to work_activities and productivity_scores

Revision ID: 006
Revises: 005
Create Date: 2026-08-24
"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('work_activities', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('productivity_scores', sa.Column('organization_id', sa.Integer(), nullable=True))

    op.execute("""
        UPDATE work_activities
        SET organization_id = dp.organization_id
        FROM developer_profiles dp
        WHERE work_activities.developer_id = dp.id
    """)
    op.execute("""
        UPDATE productivity_scores
        SET organization_id = dp.organization_id
        FROM developer_profiles dp
        WHERE productivity_scores.developer_id = dp.id
    """)

    op.alter_column('work_activities', 'organization_id', nullable=False)
    op.alter_column('productivity_scores', 'organization_id', nullable=False)

    op.create_foreign_key(
        'fk_work_activities_organization_id',
        'work_activities', 'organizations',
        ['organization_id'], ['id'],
    )
    op.create_foreign_key(
        'fk_productivity_scores_organization_id',
        'productivity_scores', 'organizations',
        ['organization_id'], ['id'],
    )
    op.create_index('ix_work_activities_organization_id', 'work_activities', ['organization_id'])
    op.create_index('ix_productivity_scores_organization_id', 'productivity_scores', ['organization_id'])


def downgrade() -> None:
    op.drop_index('ix_productivity_scores_organization_id', 'productivity_scores')
    op.drop_index('ix_work_activities_organization_id', 'work_activities')
    op.drop_constraint('fk_productivity_scores_organization_id', 'productivity_scores', type_='foreignkey')
    op.drop_constraint('fk_work_activities_organization_id', 'work_activities', type_='foreignkey')
    op.drop_column('productivity_scores', 'organization_id')
    op.drop_column('work_activities', 'organization_id')
