"""Add Slack message and reaction tables

Revision ID: 004
Revises: 003
Create Date: 2026-03-19
"""
from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'slack_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('channel_name', sa.String(), nullable=True),
        sa.Column('message_ts', sa.String(), nullable=False),
        sa.Column('message_date', sa.Date(), nullable=False),
        sa.Column('has_code_block', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reply_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reaction_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('analyzed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('analysis_result', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_ts', name='uq_slack_message_ts'),
    )
    op.create_index('ix_slack_messages_developer_id', 'slack_messages', ['developer_id'])

    op.create_table(
        'slack_reactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('reaction_name', sa.String(), nullable=False),
        sa.Column('target_message_ts', sa.String(), nullable=False),
        sa.Column('target_user_id', sa.String(), nullable=True),
        sa.Column('reaction_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('developer_id', 'reaction_name', 'target_message_ts', name='uq_slack_reaction'),
    )
    op.create_index('ix_slack_reactions_developer_id', 'slack_reactions', ['developer_id'])


def downgrade() -> None:
    op.drop_index('ix_slack_reactions_developer_id', 'slack_reactions')
    op.drop_table('slack_reactions')
    op.drop_index('ix_slack_messages_developer_id', 'slack_messages')
    op.drop_table('slack_messages')
