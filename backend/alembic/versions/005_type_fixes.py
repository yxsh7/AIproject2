"""Fix column types: is_active/acknowledged INTEGER→BOOLEAN, rename code_quality_score→quality_score

Revision ID: 005
Revises: 004
Create Date: 2026-05-17
"""
from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users.is_active: INTEGER → BOOLEAN
    op.alter_column(
        'users', 'is_active',
        type_=sa.Boolean(),
        existing_type=sa.Integer(),
        postgresql_using='is_active::boolean',
    )

    # productivity_scores.code_quality_score → quality_score
    op.alter_column('productivity_scores', 'code_quality_score', new_column_name='quality_score')

    # ai_insights.acknowledged: INTEGER → BOOLEAN
    op.alter_column(
        'ai_insights', 'acknowledged',
        type_=sa.Boolean(),
        existing_type=sa.Integer(),
        postgresql_using='acknowledged::boolean',
    )


def downgrade() -> None:
    op.alter_column(
        'ai_insights', 'acknowledged',
        type_=sa.Integer(),
        existing_type=sa.Boolean(),
        postgresql_using='acknowledged::int',
    )

    op.alter_column('productivity_scores', 'quality_score', new_column_name='code_quality_score')

    op.alter_column(
        'users', 'is_active',
        type_=sa.Integer(),
        existing_type=sa.Boolean(),
        postgresql_using='is_active::int',
    )
