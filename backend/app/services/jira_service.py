"""Jira integration service for fetching developer activity"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from atlassian import Jira
from sqlalchemy.orm import Session
import logging

from app.models import (
    DeveloperProfile,
    JiraTicket,
    JiraComment,
    IntegrationConfig,
)

logger = logging.getLogger(__name__)


class JiraService:
    """Service for interacting with Jira API"""

    def __init__(self, url: str, username: str, api_token: str):
        """
        Initialize Jira service

        Args:
            url: Jira instance URL (e.g., https://yourcompany.atlassian.net)
            username: Jira username/email
            api_token: Jira API token
        """
        self.client = Jira(url=url, username=username, password=api_token, cloud=True)
        self.url = url
        self.username = username

    @classmethod
    def from_integration_config(cls, config: IntegrationConfig) -> "JiraService":
        """
        Create service instance from integration config

        Args:
            config: IntegrationConfig with Jira credentials

        Returns:
            JiraService instance
        """
        url = config.config.get("url")
        username = config.config.get("username")
        api_token = config.config.get("api_token")

        if not all([url, username, api_token]):
            raise ValueError("Jira configuration incomplete")

        return cls(url=url, username=username, api_token=api_token)

    def test_connection(self) -> bool:
        """
        Test Jira API connection

        Returns:
            True if connection successful, False otherwise
        """
        try:
            myself = self.client.myself()
            logger.info(f"Jira connection successful for user: {myself['displayName']}")
            return True
        except Exception as e:
            logger.error(f"Jira connection failed: {e}")
            return False

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get Jira user information

        Args:
            username: Jira username/email

        Returns:
            Dict with user info or None
        """
        try:
            # Search for user
            users = self.client.user_find_by_user_string(query=username)
            if users:
                user = users[0]
                return {
                    "accountId": user.get("accountId"),
                    "displayName": user.get("displayName"),
                    "emailAddress": user.get("emailAddress"),
                    "avatarUrl": user.get("avatarUrls", {}).get("48x48"),
                }
            return None
        except Exception as e:
            logger.error(f"Failed to fetch user {username}: {e}")
            return None

    def sync_tickets_for_developer(
        self,
        db: Session,
        developer: DeveloperProfile,
        project_keys: Optional[List[str]] = None,
        days_back: int = 90,
    ) -> int:
        """
        Sync Jira tickets assigned to a developer

        Args:
            db: Database session
            developer: DeveloperProfile instance
            project_keys: List of project keys to sync (e.g., ['PROJ', 'TEAM'])
            days_back: Number of days to look back

        Returns:
            Number of tickets synced
        """
        if not developer.jira_username:
            logger.warning(f"Developer {developer.id} has no Jira username")
            return 0

        try:
            # Build JQL query
            since_date = datetime.utcnow() - timedelta(days=days_back)
            date_str = since_date.strftime("%Y-%m-%d")

            jql_parts = [f'assignee = "{developer.jira_username}"']

            if project_keys:
                projects = ", ".join([f'"{pk}"' for pk in project_keys])
                jql_parts.append(f"project in ({projects})")

            jql_parts.append(f'created >= "{date_str}"')

            jql = " AND ".join(jql_parts)
            logger.info(f"JQL Query: {jql}")

            # Execute search
            tickets_synced = 0
            start_at = 0
            max_results = 50

            while True:
                # Use the v3 API endpoint as the old one is deprecated
                response = self.client.jql(
                    jql, start=start_at, limit=max_results, fields="*all"
                )

                issues = response.get("issues", [])
                if not issues:
                    break

                for issue in issues:
                    ticket_key = issue["key"]
                    fields = issue["fields"]

                    # Check if ticket already exists
                    existing = (
                        db.query(JiraTicket).filter_by(ticket_key=ticket_key).first()
                    )

                    # Extract field values safely
                    status = fields.get("status", {}).get("name", "Unknown")
                    issue_type = fields.get("issuetype", {}).get("name", "Task")
                    priority = (
                        fields.get("priority", {}).get("name")
                        if fields.get("priority")
                        else None
                    )
                    story_points = fields.get("customfield_10016")  # Common field for story points
                    sprint = None

                    # Try to get sprint info
                    sprint_field = fields.get("customfield_10020")  # Common sprint field
                    if sprint_field and isinstance(sprint_field, list) and sprint_field:
                        # Sprint is usually in format: "com.atlassian.greenhopper.service.sprint.Sprint@..."
                        # We'll just get the sprint name if available
                        sprint = str(sprint_field[0]) if sprint_field else None

                    # Get labels
                    labels = fields.get("labels", [])

                    # Parse dates
                    created_at = self._parse_jira_date(fields.get("created"))
                    updated_at = self._parse_jira_date(fields.get("updated"))
                    resolved_at = self._parse_jira_date(fields.get("resolutiondate"))

                    if existing:
                        # Update existing ticket
                        existing.title = fields.get("summary", "")
                        existing.description = fields.get("description", "")
                        existing.status = status
                        existing.ticket_type = issue_type
                        existing.priority = priority
                        existing.story_points = story_points
                        existing.sprint = sprint
                        existing.labels = labels
                        existing.updated_at = updated_at
                        existing.resolved_at = resolved_at
                    else:
                        # Create new ticket
                        jira_ticket = JiraTicket(
                            developer_id=developer.id,
                            ticket_key=ticket_key,
                            title=fields.get("summary", ""),
                            description=fields.get("description", ""),
                            status=status,
                            ticket_type=issue_type,
                            priority=priority,
                            story_points=story_points,
                            sprint=sprint,
                            labels=labels,
                            ticket_url=f"{self.url}/browse/{ticket_key}",
                            created_at=created_at,
                            updated_at=updated_at,
                            resolved_at=resolved_at,
                            analyzed=False,
                        )
                        db.add(jira_ticket)
                        tickets_synced += 1

                # Check if there are more results
                total = response.get("total", 0)
                start_at += max_results
                if start_at >= total:
                    break

            db.commit()
            logger.info(
                f"Synced {tickets_synced} tickets for developer {developer.jira_username}"
            )
            return tickets_synced

        except Exception as e:
            logger.error(f"Error syncing Jira tickets: {e}")
            db.rollback()
            return 0

    def sync_comments_for_ticket(
        self, db: Session, ticket: JiraTicket, developer: DeveloperProfile
    ) -> int:
        """
        Sync comments for a specific Jira ticket

        Args:
            db: Database session
            ticket: JiraTicket instance
            developer: DeveloperProfile instance

        Returns:
            Number of comments synced
        """
        try:
            issue = self.client.issue(ticket.ticket_key)
            comments = issue.get("fields", {}).get("comment", {}).get("comments", [])

            comments_synced = 0

            for comment in comments:
                comment_id = comment["id"]
                author = comment.get("author", {})
                author_username = author.get("emailAddress", author.get("name"))

                # Only sync comments by this developer
                if author_username != developer.jira_username:
                    continue

                # Check if comment already exists
                existing = (
                    db.query(JiraComment).filter_by(comment_id=comment_id).first()
                )

                if existing:
                    continue

                # Create new comment record
                jira_comment = JiraComment(
                    ticket_id=ticket.id,
                    developer_id=developer.id,
                    comment_id=comment_id,
                    comment_text=comment.get("body", ""),
                    created_at=self._parse_jira_date(comment.get("created")),
                    updated_at=self._parse_jira_date(comment.get("updated")),
                    analyzed=False,
                )

                db.add(jira_comment)
                comments_synced += 1

            db.commit()
            return comments_synced

        except Exception as e:
            logger.error(
                f"Error syncing comments for ticket {ticket.ticket_key}: {e}"
            )
            db.rollback()
            return 0

    def sync_all_comments_for_developer(
        self, db: Session, developer: DeveloperProfile, days_back: int = 30
    ) -> int:
        """
        Sync all comments for a developer's tickets

        Args:
            db: Database session
            developer: DeveloperProfile instance
            days_back: Number of days to look back

        Returns:
            Total number of comments synced
        """
        # Get all tickets for this developer from the last N days
        since_date = datetime.utcnow() - timedelta(days=days_back)

        tickets = (
            db.query(JiraTicket)
            .filter(
                JiraTicket.developer_id == developer.id,
                JiraTicket.created_at >= since_date,
            )
            .all()
        )

        total_comments = 0
        for ticket in tickets:
            comments_count = self.sync_comments_for_ticket(db, ticket, developer)
            total_comments += comments_count

        logger.info(
            f"Synced {total_comments} comments for developer {developer.jira_username}"
        )
        return total_comments

    def sync_all_for_developer(
        self,
        db: Session,
        developer: DeveloperProfile,
        project_keys: Optional[List[str]] = None,
        days_back: int = 90,
    ) -> Dict[str, int]:
        """
        Sync all Jira activity for a developer

        Args:
            db: Database session
            developer: DeveloperProfile instance
            project_keys: List of project keys to sync
            days_back: Number of days to look back

        Returns:
            Dict with counts of synced items
        """
        logger.info(
            f"Starting full Jira sync for developer {developer.jira_username}"
        )

        tickets_count = self.sync_tickets_for_developer(
            db, developer, project_keys, days_back
        )
        comments_count = self.sync_all_comments_for_developer(
            db, developer, min(days_back, 30)  # Limit comments to 30 days
        )

        return {
            "tickets": tickets_count,
            "comments": comments_count,
        }

    def get_ticket_details(self, ticket_key: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific ticket (for AI analysis)

        Args:
            ticket_key: Jira ticket key (e.g., PROJ-123)

        Returns:
            Dict with ticket details or None
        """
        try:
            issue = self.client.issue(ticket_key)
            fields = issue.get("fields", {})

            return {
                "key": issue["key"],
                "summary": fields.get("summary"),
                "description": fields.get("description"),
                "status": fields.get("status", {}).get("name"),
                "type": fields.get("issuetype", {}).get("name"),
                "priority": fields.get("priority", {}).get("name"),
                "labels": fields.get("labels", []),
                "comments": fields.get("comment", {}).get("comments", []),
                "attachments": [
                    {"filename": att.get("filename"), "url": att.get("content")}
                    for att in fields.get("attachment", [])
                ],
            }

        except Exception as e:
            logger.error(f"Error fetching ticket details for {ticket_key}: {e}")
            return None

    @staticmethod
    def _parse_jira_date(date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse Jira date string to datetime

        Args:
            date_str: Date string from Jira API

        Returns:
            datetime object or None
        """
        if not date_str:
            return None

        try:
            # Jira format: 2024-01-15T10:30:45.000+0000
            return datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
        except Exception:
            return None
