"""GitHub integration service for fetching developer activity"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta, timezone
from github import Github, Auth, GithubException
from sqlalchemy.orm import Session
import logging

from app.models import (
    DeveloperProfile,
    GitCommit,
    PullRequest,
    CodeReview,
    IntegrationConfig,
)
from app.utils.security import decrypt_secret

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
        return cls(access_token=decrypt_secret(token))

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

    def _get_repos(
        self, org_name: Optional[str], repos: Optional[List[str]] = None
    ) -> List:
        """
        Resolve the list of repos to scan.

        If `repos` (a list of full 'owner/repo' names) is given, fetch exactly
        those — this is the fast, scoped path and the one that should be used
        whenever the caller knows which repos it cares about. Otherwise fall
        back to listing every repo the token can access under the org (or the
        user's own account if org access fails / no org is configured) — slow,
        and for a personal-account token pulls in unrelated repos too, but kept
        as the default so existing integrations without explicit repo scoping
        keep working.
        """
        if repos:
            resolved = []
            for full_name in repos:
                try:
                    resolved.append(self.client.get_repo(full_name))
                except GithubException as e:
                    logger.error(f"Could not access configured repo {full_name}: {e}")
            return resolved

        if org_name:
            try:
                org = self.client.get_organization(org_name)
                return list(org.get_repos())
            except GithubException:
                logger.info(
                    f"Could not access org {org_name}, falling back to user repos"
                )

        user = self.client.get_user()
        return list(
            user.get_repos(affiliation="owner,collaborator,organization_member")
        )

    def sync_commits_for_developer(
        self,
        db: Session,
        developer: DeveloperProfile,
        org_name: str,
        days_back: int = 30,
        repos: Optional[List[str]] = None,
    ) -> int:
        """
        Sync commits for a developer from org (or explicitly scoped) repositories

        Args:
            db: Database session
            developer: DeveloperProfile instance
            org_name: GitHub organization name
            days_back: Number of days to look back
            repos: Optional list of full 'owner/repo' names to scope the scan to

        Returns:
            Number of commits synced
        """
        if not developer.github_username:
            logger.warning(f"Developer {developer.id} has no GitHub username")
            return 0

        try:
            repos = self._get_repos(org_name, repos)
            logger.info(f"Found {len(repos)} repositories to scan for commits")

            since_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            commits_synced = 0

            for repo in repos:
                try:
                    # Try multiple author formats (username and email)
                    commits = repo.get_commits(
                        author=developer.github_username, since=since_date
                    )

                    for commit in commits:
                        # Check if commit already exists
                        existing = (
                            db.query(GitCommit).filter_by(commit_sha=commit.sha).first()
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
                            analyzed=0,
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
        repos: Optional[List[str]] = None,
    ) -> int:
        """
        Sync pull requests created by a developer

        Args:
            db: Database session
            developer: DeveloperProfile instance
            org_name: GitHub organization name
            days_back: Number of days to look back
            repos: Optional list of full 'owner/repo' names to scope the scan to

        Returns:
            Number of PRs synced
        """
        if not developer.github_username:
            logger.warning(f"Developer {developer.id} has no GitHub username")
            return 0

        try:
            repos = self._get_repos(org_name, repos)
            logger.info(f"Found {len(repos)} repositories to scan for PRs")

            since_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            prs_synced = 0

            for repo in repos:
                try:
                    # Get all PRs (open and closed)
                    pulls = repo.get_pulls(
                        state="all", sort="created", direction="desc"
                    )

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
                            analyzed=0,
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
        repos: Optional[List[str]] = None,
    ) -> int:
        """
        Sync code reviews given by a developer

        Args:
            db: Database session
            developer: DeveloperProfile instance
            org_name: GitHub organization name
            days_back: Number of days to look back
            repos: Optional list of full 'owner/repo' names to scope the scan to

        Returns:
            Number of reviews synced
        """
        if not developer.github_username:
            logger.warning(f"Developer {developer.id} has no GitHub username")
            return 0

        try:
            repos = self._get_repos(org_name, repos)
            logger.info(f"Found {len(repos)} repositories to scan for code reviews")

            since_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            reviews_synced = 0

            for repo in repos:
                try:
                    # Get all PRs to check for reviews
                    pulls = repo.get_pulls(
                        state="all", sort="created", direction="desc"
                    )

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
                                .filter_by(
                                    repo_name=repo.full_name, pr_number=pr.number
                                )
                                .first()
                            )

                            if not db_pr:
                                continue  # PR not in our DB yet

                            # Check if review already exists
                            existing = (
                                db.query(CodeReview)
                                .filter_by(reviewer_id=developer.id, pr_id=db_pr.id)
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
        repos: Optional[List[str]] = None,
    ) -> Dict[str, int]:
        """
        Sync all GitHub activity for a developer

        Args:
            db: Database session
            developer: DeveloperProfile instance
            org_name: GitHub organization name
            days_back: Number of days to look back
            repos: Optional list of full 'owner/repo' names to scope the scan to

        Returns:
            Dict with counts of synced items
        """
        logger.info(
            f"Starting full GitHub sync for developer {developer.github_username}"
        )

        commits_count = self.sync_commits_for_developer(
            db, developer, org_name, days_back, repos
        )
        prs_count = self.sync_pull_requests_for_developer(
            db, developer, org_name, days_back, repos
        )
        reviews_count = self.sync_code_reviews_for_developer(
            db, developer, org_name, days_back, repos
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

    def list_repos(self, org_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all accessible repositories

        Args:
            org_name: Optional organization name

        Returns:
            List of repository info dicts
        """
        try:
            repos = self._get_repos(org_name)
            return [
                {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "private": repo.private,
                    "description": repo.description,
                    "language": repo.language,
                    "updated_at": (
                        repo.updated_at.isoformat() if repo.updated_at else None
                    ),
                    "url": repo.html_url,
                }
                for repo in repos
            ]
        except GithubException as e:
            logger.error(f"Error listing repos: {e}")
            return []

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection info and authenticated user details

        Returns:
            Dict with connection status and user info
        """
        try:
            user = self.client.get_user()
            rate_limit = self.client.get_rate_limit()

            return {
                "connected": True,
                "username": user.login,
                "name": user.name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "rate_limit": {
                    "remaining": rate_limit.core.remaining,
                    "limit": rate_limit.core.limit,
                    "reset_at": rate_limit.core.reset.isoformat(),
                },
            }
        except GithubException as e:
            return {
                "connected": False,
                "error": str(e),
            }
