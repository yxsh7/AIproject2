"""GitHub integration service for fetching developer activity"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from github import Github, Auth, GithubException
from sqlalchemy.orm import Session
import logging

from app.models import (
    DeveloperProfile,
    GitCommit,
    PullRequest,
    CodeReview,
    IntegrationConfig,
    IntegrationType,
)

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub API"""

    def __init__(self, access_token: str):
        """
        Initialize GitHub service

        Args:
            access_token: GitHub personal access token or OAuth token
        """
        auth = Auth.Token(access_token)
        self.client = Github(auth=auth)
        self.access_token = access_token

    @classmethod
    def from_integration_config(cls, config: IntegrationConfig) -> "GitHubService":
        """
        Create service instance from integration config

        Args:
            config: IntegrationConfig with GitHub credentials

        Returns:
            GitHubService instance
        """
        token = config.config.get("access_token")
        if not token:
            raise ValueError("GitHub access token not found in config")
        return cls(access_token=token)

    def test_connection(self) -> bool:
        """
        Test GitHub API connection

        Returns:
            True if connection successful, False otherwise
        """
        try:
            user = self.client.get_user()
            logger.info(f"GitHub connection successful for user: {user.login}")
            return True
        except GithubException as e:
            logger.error(f"GitHub connection failed: {e}")
            return False

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get GitHub user information

        Args:
            username: GitHub username

        Returns:
            Dict with user info or None
        """
        try:
            user = self.client.get_user(username)
            return {
                "login": user.login,
                "name": user.name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "bio": user.bio,
                "company": user.company,
                "location": user.location,
            }
        except GithubException as e:
            logger.error(f"Failed to fetch user {username}: {e}")
            return None

    def sync_commits_for_developer(
        self,
        db: Session,
        developer: DeveloperProfile,
        org_name: str,
        days_back: int = 30,
    ) -> int:
        """
        Sync commits for a developer from all org repositories

        Args:
            db: Database session
            developer: DeveloperProfile instance
            org_name: GitHub organization name
            days_back: Number of days to look back

        Returns:
            Number of commits synced
        """
        if not developer.github_username:
            logger.warning(f"Developer {developer.id} has no GitHub username")
            return 0

        try:
            # Handle both organization and personal accounts
            if org_name:
                org = self.client.get_organization(org_name)
                repos = org.get_repos()
            else:
                # Personal account - get authenticated user's repos
                user = self.client.get_user()
                repos = user.get_repos()

            since_date = datetime.utcnow() - timedelta(days=days_back)
            commits_synced = 0

            for repo in repos:
                try:
                    commits = repo.get_commits(
                        author=developer.github_username, since=since_date
                    )

                    for commit in commits:
                        # Check if commit already exists
                        existing = (
                            db.query(GitCommit)
                            .filter_by(commit_sha=commit.sha)
                            .first()
                        )

                        if existing:
                            continue

                        # Create new commit record
                        git_commit = GitCommit(
                            developer_id=developer.id,
                            repo_name=repo.full_name,
                            commit_sha=commit.sha,
                            message=commit.commit.message,
                            branch=None,  # GitHub API doesn't easily provide this
                            files_changed=len(commit.files) if commit.files else 0,
                            additions=commit.stats.additions if commit.stats else 0,
                            deletions=commit.stats.deletions if commit.stats else 0,
                            committed_at=commit.commit.author.date,
                            analyzed=False,
                        )

                        db.add(git_commit)
                        commits_synced += 1

                except GithubException as e:
                    logger.error(f"Error fetching commits from {repo.name}: {e}")
                    continue

            db.commit()
            logger.info(
                f"Synced {commits_synced} commits for developer {developer.github_username}"
            )
            return commits_synced

        except GithubException as e:
            logger.error(f"Error syncing commits: {e}")
            db.rollback()
            return 0

    def sync_pull_requests_for_developer(
        self,
        db: Session,
        developer: DeveloperProfile,
        org_name: str,
        days_back: int = 30,
    ) -> int:
        """
        Sync pull requests created by a developer

        Args:
            db: Database session
            developer: DeveloperProfile instance
            org_name: GitHub organization name
            days_back: Number of days to look back

        Returns:
            Number of PRs synced
        """
        if not developer.github_username:
            logger.warning(f"Developer {developer.id} has no GitHub username")
            return 0

        try:
            # Handle both organization and personal accounts
            if org_name:
                org = self.client.get_organization(org_name)
                repos = org.get_repos()
            else:
                # Personal account - get authenticated user's repos
                user = self.client.get_user()
                repos = user.get_repos()

            since_date = datetime.utcnow() - timedelta(days=days_back)
            prs_synced = 0

            for repo in repos:
                try:
                    # Get all PRs (open and closed)
                    pulls = repo.get_pulls(state="all", sort="created", direction="desc")

                    for pr in pulls:
                        # Filter by author and date
                        if pr.user.login != developer.github_username:
                            continue

                        if pr.created_at < since_date:
                            break  # Stop if we've gone too far back

                        # Check if PR already exists
                        existing = (
                            db.query(PullRequest)
                            .filter_by(repo_name=repo.full_name, pr_number=pr.number)
                            .first()
                        )

                        if existing:
                            # Update if status changed
                            if existing.state != pr.state:
                                existing.state = pr.state
                                existing.merged_at = pr.merged_at
                                existing.closed_at = pr.closed_at
                                existing.updated_at = pr.updated_at
                            continue

                        # Create new PR record
                        pull_request = PullRequest(
                            developer_id=developer.id,
                            repo_name=repo.full_name,
                            pr_number=pr.number,
                            title=pr.title,
                            description=pr.body,
                            state=pr.state,
                            files_changed=pr.changed_files,
                            additions=pr.additions,
                            deletions=pr.deletions,
                            commits_count=pr.commits,
                            html_url=pr.html_url,
                            created_at=pr.created_at,
                            updated_at=pr.updated_at,
                            merged_at=pr.merged_at,
                            closed_at=pr.closed_at,
                            analyzed=False,
                        )

                        db.add(pull_request)
                        prs_synced += 1

                except GithubException as e:
                    logger.error(f"Error fetching PRs from {repo.name}: {e}")
                    continue

            db.commit()
            logger.info(
                f"Synced {prs_synced} PRs for developer {developer.github_username}"
            )
            return prs_synced

        except GithubException as e:
            logger.error(f"Error syncing PRs: {e}")
            db.rollback()
            return 0

    def sync_code_reviews_for_developer(
        self,
        db: Session,
        developer: DeveloperProfile,
        org_name: str,
        days_back: int = 30,
    ) -> int:
        """
        Sync code reviews given by a developer

        Args:
            db: Database session
            developer: DeveloperProfile instance
            org_name: GitHub organization name
            days_back: Number of days to look back

        Returns:
            Number of reviews synced
        """
        if not developer.github_username:
            logger.warning(f"Developer {developer.id} has no GitHub username")
            return 0

        try:
            # Handle both organization and personal accounts
            if org_name:
                org = self.client.get_organization(org_name)
                repos = org.get_repos()
            else:
                # Personal account - get authenticated user's repos
                user = self.client.get_user()
                repos = user.get_repos()

            since_date = datetime.utcnow() - timedelta(days=days_back)
            reviews_synced = 0

            for repo in repos:
                try:
                    # Get all PRs to check for reviews
                    pulls = repo.get_pulls(state="all", sort="created", direction="desc")

                    for pr in pulls:
                        if pr.created_at < since_date:
                            break

                        # Get reviews for this PR
                        reviews = pr.get_reviews()

                        for review in reviews:
                            if review.user.login != developer.github_username:
                                continue

                            # Get corresponding PR in our database
                            db_pr = (
                                db.query(PullRequest)
                                .filter_by(repo_name=repo.full_name, pr_number=pr.number)
                                .first()
                            )

                            if not db_pr:
                                continue  # PR not in our DB yet

                            # Check if review already exists
                            existing = (
                                db.query(CodeReview)
                                .filter_by(
                                    reviewer_id=developer.id, pr_id=db_pr.id
                                )
                                .first()
                            )

                            if existing:
                                continue

                            # Count review comments
                            comment_count = len(list(pr.get_review_comments()))

                            # Create new review record
                            code_review = CodeReview(
                                reviewer_id=developer.id,
                                pr_id=db_pr.id,
                                comment_count=comment_count,
                                review_state=review.state,
                                reviewed_at=review.submitted_at or pr.created_at,
                            )

                            db.add(code_review)
                            reviews_synced += 1

                except GithubException as e:
                    logger.error(f"Error fetching reviews from {repo.name}: {e}")
                    continue

            db.commit()
            logger.info(
                f"Synced {reviews_synced} code reviews for developer {developer.github_username}"
            )
            return reviews_synced

        except GithubException as e:
            logger.error(f"Error syncing code reviews: {e}")
            db.rollback()
            return 0

    def sync_all_for_developer(
        self,
        db: Session,
        developer: DeveloperProfile,
        org_name: str,
        days_back: int = 30,
    ) -> Dict[str, int]:
        """
        Sync all GitHub activity for a developer

        Args:
            db: Database session
            developer: DeveloperProfile instance
            org_name: GitHub organization name
            days_back: Number of days to look back

        Returns:
            Dict with counts of synced items
        """
        logger.info(
            f"Starting full GitHub sync for developer {developer.github_username}"
        )

        commits_count = self.sync_commits_for_developer(
            db, developer, org_name, days_back
        )
        prs_count = self.sync_pull_requests_for_developer(
            db, developer, org_name, days_back
        )
        reviews_count = self.sync_code_reviews_for_developer(
            db, developer, org_name, days_back
        )

        return {
            "commits": commits_count,
            "pull_requests": prs_count,
            "code_reviews": reviews_count,
        }

    def get_commit_diff(self, repo_full_name: str, commit_sha: str) -> Optional[str]:
        """
        Get the diff for a specific commit (for AI analysis)

        Args:
            repo_full_name: Full repository name (org/repo)
            commit_sha: Commit SHA

        Returns:
            Diff as string or None
        """
        try:
            repo = self.client.get_repo(repo_full_name)
            commit = repo.get_commit(commit_sha)

            # Get file diffs
            files_diff = []
            for file in commit.files:
                if file.patch:  # Some files (like binaries) don't have patches
                    files_diff.append(f"File: {file.filename}\n{file.patch}")

            return "\n\n".join(files_diff)

        except GithubException as e:
            logger.error(f"Error fetching diff for {commit_sha}: {e}")
            return None

    def get_pr_diff(self, repo_full_name: str, pr_number: int) -> Optional[str]:
        """
        Get the diff for a pull request (for AI analysis)

        Args:
            repo_full_name: Full repository name (org/repo)
            pr_number: PR number

        Returns:
            Diff as string or None
        """
        try:
            repo = self.client.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)

            # Get file diffs
            files_diff = []
            for file in pr.get_files():
                if file.patch:
                    files_diff.append(f"File: {file.filename}\n{file.patch}")

            return "\n\n".join(files_diff)

        except GithubException as e:
            logger.error(f"Error fetching PR diff for #{pr_number}: {e}")
            return None
