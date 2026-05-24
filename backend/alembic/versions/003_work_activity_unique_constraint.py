"""Add unique constraint to work_activities

Revision ID: 003
Revises: 002
Create Date: 2026-03-19
"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove duplicate rows — keep the one with the highest id per (developer_id, source_type, source_id)
    op.execute("""
        DELETE FROM work_activities
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM work_activities
            GROUP BY developer_id, source_type, source_id
        )
    """)

    # Now add the unique constraint
    op.create_unique_constraint(
        'uq_work_activity_source',
        'work_activities',
        ['developer_id', 'source_type', 'source_id']
    )


def downgrade() -> None:
    op.drop_constraint('uq_work_activity_source', 'work_activities', type_='unique')
