"""Initial database schema

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('admin', 'manager', 'developer', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=True, default=1),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('github_org', sa.String(), nullable=True),
        sa.Column('jira_workspace', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)
    op.create_index(op.f('ix_organizations_github_org'), 'organizations', ['github_org'], unique=False)

    # Create role_profiles table
    op.create_table(
        'role_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_level', sa.Enum('intern', 'junior', 'mid', 'senior', 'staff', 'principal', name='rolelevel'), nullable=False),
        sa.Column('expected_work_types', sa.JSON(), nullable=False),
        sa.Column('complexity_expectation', sa.String(), nullable=False),
        sa.Column('evaluation_criteria', sa.JSON(), nullable=False),
        sa.Column('mentoring_expected', sa.Integer(), nullable=True, default=0),
        sa.Column('autonomy_level', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_profiles_id'), 'role_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_role_profiles_role_level'), 'role_profiles', ['role_level'], unique=True)

    # Create developer_profiles table
    op.create_table(
        'developer_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('role_level', sa.Enum('intern', 'junior', 'mid', 'senior', 'staff', 'principal', name='rolelevel', create_type=False), nullable=False),
        sa.Column('team', sa.String(), nullable=True),
        sa.Column('job_title', sa.String(), nullable=True),
        sa.Column('github_username', sa.String(), nullable=True),
        sa.Column('jira_username', sa.String(), nullable=True),
        sa.Column('slack_user_id', sa.String(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('focus_areas', sa.JSON(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_developer_profiles_id'), 'developer_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_developer_profiles_role_level'), 'developer_profiles', ['role_level'], unique=False)
    op.create_index(op.f('ix_developer_profiles_team'), 'developer_profiles', ['team'], unique=False)
    op.create_index(op.f('ix_developer_profiles_github_username'), 'developer_profiles', ['github_username'], unique=False)
    op.create_index(op.f('ix_developer_profiles_jira_username'), 'developer_profiles', ['jira_username'], unique=False)

    # Create integration_configs table
    op.create_table(
        'integration_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('github', 'bitbucket', 'gitlab', 'jira', 'slack', name='integrationtype'), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', 'error', 'syncing', name='integrationstatus'), nullable=False),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('sync_frequency_minutes', sa.Integer(), nullable=True, default=60),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_integration_configs_id'), 'integration_configs', ['id'], unique=False)
    op.create_index(op.f('ix_integration_configs_type'), 'integration_configs', ['type'], unique=False)

    # Create git_commits table
    op.create_table(
        'git_commits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('repo_name', sa.String(), nullable=False),
        sa.Column('commit_sha', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('branch', sa.String(), nullable=True),
        sa.Column('files_changed', sa.Integer(), nullable=True, default=0),
        sa.Column('additions', sa.Integer(), nullable=True, default=0),
        sa.Column('deletions', sa.Integer(), nullable=True, default=0),
        sa.Column('committed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('analyzed', sa.Integer(), nullable=True, default=0),
        sa.Column('analysis_result', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('commit_sha')
    )
    op.create_index(op.f('ix_git_commits_id'), 'git_commits', ['id'], unique=False)
    op.create_index(op.f('ix_git_commits_developer_id'), 'git_commits', ['developer_id'], unique=False)
    op.create_index(op.f('ix_git_commits_repo_name'), 'git_commits', ['repo_name'], unique=False)
    op.create_index(op.f('ix_git_commits_commit_sha'), 'git_commits', ['commit_sha'], unique=False)
    op.create_index(op.f('ix_git_commits_committed_at'), 'git_commits', ['committed_at'], unique=False)

    # Create pull_requests table
    op.create_table(
        'pull_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('repo_name', sa.String(), nullable=False),
        sa.Column('pr_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('files_changed', sa.Integer(), nullable=True, default=0),
        sa.Column('additions', sa.Integer(), nullable=True, default=0),
        sa.Column('deletions', sa.Integer(), nullable=True, default=0),
        sa.Column('commits_count', sa.Integer(), nullable=True, default=0),
        sa.Column('html_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('merged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('analyzed', sa.Integer(), nullable=True, default=0),
        sa.Column('analysis_result', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pull_requests_id'), 'pull_requests', ['id'], unique=False)
    op.create_index(op.f('ix_pull_requests_developer_id'), 'pull_requests', ['developer_id'], unique=False)
    op.create_index(op.f('ix_pull_requests_repo_name'), 'pull_requests', ['repo_name'], unique=False)
    op.create_index(op.f('ix_pull_requests_state'), 'pull_requests', ['state'], unique=False)
    op.create_index(op.f('ix_pull_requests_created_at'), 'pull_requests', ['created_at'], unique=False)

    # Create code_reviews table
    op.create_table(
        'code_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('pr_id', sa.Integer(), nullable=False),
        sa.Column('comment_count', sa.Integer(), nullable=True, default=0),
        sa.Column('review_state', sa.String(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('quality_score', sa.Integer(), nullable=True),
        sa.Column('analysis_result', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['reviewer_id'], ['developer_profiles.id'], ),
        sa.ForeignKeyConstraint(['pr_id'], ['pull_requests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_code_reviews_id'), 'code_reviews', ['id'], unique=False)
    op.create_index(op.f('ix_code_reviews_reviewer_id'), 'code_reviews', ['reviewer_id'], unique=False)
    op.create_index(op.f('ix_code_reviews_reviewed_at'), 'code_reviews', ['reviewed_at'], unique=False)

    # Create jira_tickets table
    op.create_table(
        'jira_tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('ticket_key', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('ticket_type', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('story_points', sa.Float(), nullable=True),
        sa.Column('sprint', sa.String(), nullable=True),
        sa.Column('labels', sa.JSON(), nullable=True),
        sa.Column('ticket_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('analyzed', sa.Integer(), nullable=True, default=0),
        sa.Column('analysis_result', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticket_key')
    )
    op.create_index(op.f('ix_jira_tickets_id'), 'jira_tickets', ['id'], unique=False)
    op.create_index(op.f('ix_jira_tickets_developer_id'), 'jira_tickets', ['developer_id'], unique=False)
    op.create_index(op.f('ix_jira_tickets_ticket_key'), 'jira_tickets', ['ticket_key'], unique=False)
    op.create_index(op.f('ix_jira_tickets_status'), 'jira_tickets', ['status'], unique=False)
    op.create_index(op.f('ix_jira_tickets_sprint'), 'jira_tickets', ['sprint'], unique=False)
    op.create_index(op.f('ix_jira_tickets_created_at'), 'jira_tickets', ['created_at'], unique=False)

    # Create jira_comments table
    op.create_table(
        'jira_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.String(), nullable=False),
        sa.Column('comment_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('analyzed', sa.Integer(), nullable=True, default=0),
        sa.Column('analysis_result', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['ticket_id'], ['jira_tickets.id'], ),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jira_comments_id'), 'jira_comments', ['id'], unique=False)
    op.create_index(op.f('ix_jira_comments_ticket_id'), 'jira_comments', ['ticket_id'], unique=False)
    op.create_index(op.f('ix_jira_comments_developer_id'), 'jira_comments', ['developer_id'], unique=False)
    op.create_index(op.f('ix_jira_comments_comment_id'), 'jira_comments', ['comment_id'], unique=False)
    op.create_index(op.f('ix_jira_comments_created_at'), 'jira_comments', ['created_at'], unique=False)

    # Create work_activities table
    op.create_table(
        'work_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('activity_date', sa.Date(), nullable=False),
        sa.Column('work_type', sa.Enum('code', 'research', 'documentation', 'dashboard', 'meeting', 'mentoring', 'code_review', 'operations', 'design', 'testing', 'bug_fix', 'refactoring', 'other', name='worktype'), nullable=False),
        sa.Column('complexity_score', sa.Integer(), nullable=False),
        sa.Column('impact_score', sa.Integer(), nullable=False),
        sa.Column('quality_score', sa.Integer(), nullable=False),
        sa.Column('time_estimate_hours', sa.Integer(), nullable=True),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('source_id', sa.String(), nullable=False),
        sa.Column('ai_analysis', sa.JSON(), nullable=False),
        sa.Column('artifacts', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_work_activities_id'), 'work_activities', ['id'], unique=False)
    op.create_index(op.f('ix_work_activities_developer_id'), 'work_activities', ['developer_id'], unique=False)
    op.create_index(op.f('ix_work_activities_activity_date'), 'work_activities', ['activity_date'], unique=False)
    op.create_index(op.f('ix_work_activities_work_type'), 'work_activities', ['work_type'], unique=False)
    op.create_index(op.f('ix_work_activities_source_type'), 'work_activities', ['source_type'], unique=False)

    # Create productivity_scores table
    op.create_table(
        'productivity_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('period_type', sa.String(), nullable=False),
        sa.Column('overall_score', sa.Integer(), nullable=False),
        sa.Column('code_quality_score', sa.Integer(), nullable=True),
        sa.Column('complexity_score', sa.Integer(), nullable=True),
        sa.Column('velocity_score', sa.Integer(), nullable=True),
        sa.Column('impact_score', sa.Integer(), nullable=True),
        sa.Column('collaboration_score', sa.Integer(), nullable=True),
        sa.Column('mentoring_score', sa.Integer(), nullable=True),
        sa.Column('learning_score', sa.Integer(), nullable=True),
        sa.Column('breakdown', sa.JSON(), nullable=False),
        sa.Column('insights', sa.JSON(), nullable=True),
        sa.Column('total_commits', sa.Integer(), nullable=True, default=0),
        sa.Column('total_prs', sa.Integer(), nullable=True, default=0),
        sa.Column('total_tickets', sa.Integer(), nullable=True, default=0),
        sa.Column('lines_added', sa.Integer(), nullable=True, default=0),
        sa.Column('lines_deleted', sa.Integer(), nullable=True, default=0),
        sa.Column('work_breakdown', sa.JSON(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('version', sa.String(), nullable=True, default='1.0'),
        sa.Column('score_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_productivity_scores_id'), 'productivity_scores', ['id'], unique=False)
    op.create_index(op.f('ix_productivity_scores_developer_id'), 'productivity_scores', ['developer_id'], unique=False)
    op.create_index(op.f('ix_productivity_scores_period_start'), 'productivity_scores', ['period_start'], unique=False)
    op.create_index(op.f('ix_productivity_scores_period_end'), 'productivity_scores', ['period_end'], unique=False)

    # Create ai_insights table
    op.create_table(
        'ai_insights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=True),
        sa.Column('insight_type', sa.Enum('individual', 'team', 'trend', 'alert', 'recommendation', name='insighttype'), nullable=False),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'critical', name='insightpriority'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('supporting_data', sa.JSON(), nullable=True),
        sa.Column('action_items', sa.JSON(), nullable=True),
        sa.Column('acknowledged', sa.Integer(), nullable=True, default=0),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acknowledged_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.ForeignKeyConstraint(['acknowledged_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_insights_id'), 'ai_insights', ['id'], unique=False)
    op.create_index(op.f('ix_ai_insights_organization_id'), 'ai_insights', ['organization_id'], unique=False)
    op.create_index(op.f('ix_ai_insights_developer_id'), 'ai_insights', ['developer_id'], unique=False)
    op.create_index(op.f('ix_ai_insights_insight_type'), 'ai_insights', ['insight_type'], unique=False)
    op.create_index(op.f('ix_ai_insights_priority'), 'ai_insights', ['priority'], unique=False)
    op.create_index(op.f('ix_ai_insights_created_at'), 'ai_insights', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order of creation (respecting foreign keys)
    op.drop_table('ai_insights')
    op.drop_table('productivity_scores')
    op.drop_table('work_activities')
    op.drop_table('jira_comments')
    op.drop_table('jira_tickets')
    op.drop_table('code_reviews')
    op.drop_table('pull_requests')
    op.drop_table('git_commits')
    op.drop_table('integration_configs')
    op.drop_table('developer_profiles')
    op.drop_table('role_profiles')
    op.drop_table('organizations')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS insightpriority')
    op.execute('DROP TYPE IF EXISTS insighttype')
    op.execute('DROP TYPE IF EXISTS worktype')
    op.execute('DROP TYPE IF EXISTS integrationstatus')
    op.execute('DROP TYPE IF EXISTS integrationtype')
    op.execute('DROP TYPE IF EXISTS rolelevel')
    op.execute('DROP TYPE IF EXISTS userrole')
