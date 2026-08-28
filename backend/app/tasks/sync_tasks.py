"""Background tasks for syncing data from GitHub, Jira, and Slack"""
import logging
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from sqlalchemy.orm import Session
from app.models import (
    IntegrationConfig,
    IntegrationType,
    IntegrationStatus,
    DeveloperProfile,
)
from app.services.github_service import GitHubService
from app.services.jira_service import JiraService
from app.services.slack_service import SlackService

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.sync_tasks.sync_integration_task")
def sync_integration_task(integration_id: int, days_back: int = 30):
    """
    Sync a specific integration (GitHub, Jira, or Slack)

    Args:
        integration_id: Integration configuration ID
        days_back: Number of days to sync back

    Returns:
        Dict with sync results
    """
    db = SessionLocal()

    try:
        integration = (
            db.query(IntegrationConfig)
            .filter(IntegrationConfig.id == integration_id)
            .first()
        )

        if not integration:
            logger.error(f"Integration {integration_id} not found")
            return {"error": "Integration not found"}

        logger.info(f"Starting sync for integration {integration_id} ({integration.type})")

        # Update status to syncing
        integration.status = IntegrationStatus.SYNCING
        db.commit()

        if integration.type == IntegrationType.GITHUB:
            result = sync_github_integration(db, integration, days_back)
        elif integration.type == IntegrationType.JIRA:
            result = sync_jira_integration(db, integration, days_back)
        elif integration.type == IntegrationType.SLACK:
            result = sync_slack_integration(db, integration, days_back)
        else:
            result = {"error": f"Unsupported integration type: {integration.type}"}

        # Update integration status
        if "error" in result:
            integration.status = IntegrationStatus.ERROR
            integration.last_error = result["error"]
        else:
            integration.status = IntegrationStatus.ACTIVE
            integration.last_sync_at = datetime.now(timezone.utc)
            integration.last_error = None

        db.commit()

        logger.info(f"Sync completed for integration {integration_id}: {result}")
        return result

    except Exception as e:
        logger.error(f"Error syncing integration {integration_id}: {e}")

        # Update integration status to error
        integration = (
            db.query(IntegrationConfig)
            .filter(IntegrationConfig.id == integration_id)
            .first()
        )
        if integration:
            integration.status = IntegrationStatus.ERROR
            integration.last_error = str(e)
            db.commit()

        return {"error": str(e)}

    finally:
        db.close()


def sync_github_integration(
    db: Session, integration: IntegrationConfig, days_back: int
) -> dict:
    """
    Sync GitHub data for all developers

    Args:
        db: Database session
        integration: GitHub integration configuration
        days_back: Number of days to sync back

    Returns:
        Dict with sync statistics
    """
    try:
        github_service = GitHubService.from_integration_config(integration)
        org_name = integration.config.get("organization_name")
        repos = integration.config.get("repos")

        # Get all developers with GitHub username
        developers = (
            db.query(DeveloperProfile)
            .filter(
                DeveloperProfile.organization_id == integration.organization_id,
                DeveloperProfile.github_username.isnot(None),
            )
            .all()
        )

        logger.info(f"Syncing GitHub for {len(developers)} developers")

        total_commits = 0
        total_prs = 0
        total_reviews = 0

        for developer in developers:
            try:
                result = github_service.sync_all_for_developer(
                    db, developer, org_name, days_back, repos
                )

                total_commits += result.get("commits", 0)
                total_prs += result.get("pull_requests", 0)
                total_reviews += result.get("code_reviews", 0)

                logger.info(
                    f"Synced GitHub for {developer.github_username}: "
                    f"{result['commits']} commits, {result['pull_requests']} PRs, "
                    f"{result['code_reviews']} reviews"
                )

            except Exception as e:
                logger.error(
                    f"Error syncing GitHub for developer {developer.id}: {e}"
                )
                continue

        return {
            "developers_synced": len(developers),
            "total_commits": total_commits,
            "total_pull_requests": total_prs,
            "total_code_reviews": total_reviews,
        }

    except Exception as e:
        logger.error(f"Error in GitHub sync: {e}")
        return {"error": str(e)}


def sync_jira_integration(
    db: Session, integration: IntegrationConfig, days_back: int
) -> dict:
    """
    Sync Jira data for all developers

    Args:
        db: Database session
        integration: Jira integration configuration
        days_back: Number of days to sync back

    Returns:
        Dict with sync statistics
    """
    try:
        jira_service = JiraService.from_integration_config(integration)
        project_keys = integration.config.get("project_keys")

        # Get all developers with Jira username
        developers = (
            db.query(DeveloperProfile)
            .filter(
                DeveloperProfile.organization_id == integration.organization_id,
                DeveloperProfile.jira_username.isnot(None),
            )
            .all()
        )

        logger.info(f"Syncing Jira for {len(developers)} developers")

        total_tickets = 0
        total_comments = 0

        for developer in developers:
            try:
                result = jira_service.sync_all_for_developer(
                    db, developer, project_keys, days_back
                )

                total_tickets += result.get("tickets", 0)
                total_comments += result.get("comments", 0)

                logger.info(
                    f"Synced Jira for {developer.jira_username}: "
                    f"{result['tickets']} tickets, {result['comments']} comments"
                )

            except Exception as e:
                logger.error(f"Error syncing Jira for developer {developer.id}: {e}")
                continue

        return {
            "developers_synced": len(developers),
            "total_tickets": total_tickets,
            "total_comments": total_comments,
        }

    except Exception as e:
        logger.error(f"Error in Jira sync: {e}")
        return {"error": str(e)}


def sync_slack_integration(
    db: Session, integration: IntegrationConfig, days_back: int
) -> dict:
    """Sync Slack data for all developers with slack_user_id set."""
    try:
        slack_service = SlackService.from_integration_config(integration)
        channel_ids = integration.config.get("channel_ids", [])

        developers = (
            db.query(DeveloperProfile)
            .filter(
                DeveloperProfile.organization_id == integration.organization_id,
                DeveloperProfile.slack_user_id.isnot(None),
            )
            .all()
        )

        logger.info(f"Syncing Slack for {len(developers)} developers")

        total_messages = 0
        total_reactions = 0

        for developer in developers:
            try:
                result = slack_service.sync_all_for_developer(
                    db, developer.id, developer.slack_user_id, channel_ids, days_back
                )
                total_messages += result.get("messages", 0)
                total_reactions += result.get("reactions", 0)
            except Exception as e:
                logger.error(f"Error syncing Slack for developer {developer.id}: {e}")
                continue

        return {
            "developers_synced": len(developers),
            "total_messages": total_messages,
            "total_reactions": total_reactions,
        }

    except Exception as e:
        logger.error(f"Error in Slack sync: {e}")
        return {"error": str(e)}


@celery_app.task(name="app.tasks.sync_tasks.sync_all_github")
def sync_all_github():
    """
    Periodic task to sync all GitHub integrations
    """
    db = SessionLocal()

    try:
        # Get all active GitHub integrations
        integrations = (
            db.query(IntegrationConfig)
            .filter(
                IntegrationConfig.type == IntegrationType.GITHUB,
                IntegrationConfig.status == IntegrationStatus.ACTIVE,
            )
            .all()
        )

        logger.info(f"Found {len(integrations)} active GitHub integrations to sync")

        results = []
        for integration in integrations:
            try:
                result = sync_github_integration(db, integration, days_back=7)  # Last week
                results.append({"integration_id": integration.id, "result": result})

                # Update last_sync_at
                integration.last_sync_at = datetime.now(timezone.utc)
                db.commit()

            except Exception as e:
                logger.error(f"Error syncing GitHub integration {integration.id}: {e}")
                results.append({"integration_id": integration.id, "error": str(e)})

        return {"integrations_synced": len(integrations), "results": results}

    finally:
        db.close()


@celery_app.task(name="app.tasks.sync_tasks.sync_all_jira")
def sync_all_jira():
    """
    Periodic task to sync all Jira integrations
    """
    db = SessionLocal()

    try:
        # Get all active Jira integrations
        integrations = (
            db.query(IntegrationConfig)
            .filter(
                IntegrationConfig.type == IntegrationType.JIRA,
                IntegrationConfig.status == IntegrationStatus.ACTIVE,
            )
            .all()
        )

        logger.info(f"Found {len(integrations)} active Jira integrations to sync")

        results = []
        for integration in integrations:
            try:
                result = sync_jira_integration(db, integration, days_back=30)  # Last month
                results.append({"integration_id": integration.id, "result": result})

                # Update last_sync_at
                integration.last_sync_at = datetime.now(timezone.utc)
                db.commit()

            except Exception as e:
                logger.error(f"Error syncing Jira integration {integration.id}: {e}")
                results.append({"integration_id": integration.id, "error": str(e)})

        return {"integrations_synced": len(integrations), "results": results}

    finally:
        db.close()


@celery_app.task(name="app.tasks.sync_tasks.sync_all_slack")
def sync_all_slack():
    """Periodic task to sync all Slack integrations."""
    db = SessionLocal()

    try:
        integrations = (
            db.query(IntegrationConfig)
            .filter(
                IntegrationConfig.type == IntegrationType.SLACK,
                IntegrationConfig.status == IntegrationStatus.ACTIVE,
            )
            .all()
        )

        logger.info(f"Found {len(integrations)} active Slack integrations to sync")

        results = []
        for integration in integrations:
            try:
                result = sync_slack_integration(db, integration, days_back=7)
                integration.last_sync_at = datetime.now(timezone.utc)
                db.commit()
                results.append({"integration_id": integration.id, "result": result})
            except Exception as e:
                logger.error(f"Error syncing Slack integration {integration.id}: {e}")
                results.append({"integration_id": integration.id, "error": str(e)})

        return {"integrations_synced": len(integrations), "results": results}

    finally:
        db.close()
