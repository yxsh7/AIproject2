"""Slack integration service for fetching developer activity"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    logger.warning("slack_sdk not installed. Slack integration unavailable.")

from app.models import DeveloperProfile, IntegrationConfig, IntegrationType
from app.models.slack_activity import SlackMessage, SlackReaction


class SlackService:
    """Service for interacting with Slack API using a bot token."""

    def __init__(self, bot_token: str):
        if not SLACK_AVAILABLE:
            raise RuntimeError("slack_sdk is not installed. Run: pip install slack_sdk")
        self.client = WebClient(token=bot_token)
        self.bot_token = bot_token

    @classmethod
    def from_integration_config(cls, config: IntegrationConfig) -> "SlackService":
        token = config.config.get("bot_token")
        if not token:
            raise ValueError("Slack bot token not found in config")
        return cls(bot_token=token)

    def test_connection(self) -> bool:
        try:
            response = self.client.auth_test()
            logger.info(f"Slack connection successful: team={response['team']}")
            return True
        except Exception as e:
            logger.error(f"Slack connection failed: {e}")
            return False

    def sync_messages_for_developer(
        self,
        db: Session,
        developer_id: int,
        slack_user_id: str,
        channel_ids: list[str],
        days_back: int = 7,
    ) -> int:
        """Sync messages sent by developer in specified channels. Returns count synced."""
        if not SLACK_AVAILABLE:
            return 0

        since_ts = (datetime.now(timezone.utc) - timedelta(days=days_back)).timestamp()
        synced = 0

        for channel_id in channel_ids:
            try:
                channel_name = self._get_channel_name(channel_id)  # ONE call per channel
                cursor = None
                while True:
                    kwargs = {
                        "channel": channel_id,
                        "oldest": str(since_ts),
                        "limit": 200,
                    }
                    if cursor:
                        kwargs["cursor"] = cursor

                    response = self.client.conversations_history(**kwargs)
                    messages = response.get("messages", [])

                    for msg in messages:
                        # Only messages from this user
                        if msg.get("user") != slack_user_id:
                            continue
                        if msg.get("subtype"):
                            continue  # Skip join/leave/bot messages

                        message_ts = msg.get("ts", "")
                        if not message_ts:
                            continue

                        # Dedup check
                        existing = db.query(SlackMessage).filter_by(message_ts=message_ts).first()
                        if existing:
                            continue

                        text = msg.get("text", "")
                        has_code_block = 1 if "```" in text else 0
                        reply_count = int(msg.get("reply_count", 0))
                        reactions = msg.get("reactions", [])
                        reaction_count = sum(r.get("count", 0) for r in reactions)

                        msg_dt = datetime.fromtimestamp(float(message_ts))

                        slack_msg = SlackMessage(
                            developer_id=developer_id,
                            channel_id=channel_id,
                            channel_name=channel_name,
                            message_ts=message_ts,
                            message_date=msg_dt.date(),
                            has_code_block=has_code_block,
                            reply_count=reply_count,
                            reaction_count=reaction_count,
                        )
                        db.add(slack_msg)
                        synced += 1

                    if not response.get("has_more") or not messages:
                        break
                    cursor = response.get("response_metadata", {}).get("next_cursor")
                    if not cursor:
                        break

            except Exception as e:
                logger.error(f"Error syncing messages for channel {channel_id}: {e}")
                continue

        if synced > 0:
            db.commit()

        return synced

    def sync_reactions_for_developer(
        self,
        db: Session,
        developer_id: int,
        slack_user_id: str,
        days_back: int = 7,
    ) -> int:
        """Sync reactions given by developer. Returns count synced."""
        if not SLACK_AVAILABLE:
            return 0

        synced = 0
        try:
            cursor = None
            while True:
                kwargs = {"user": slack_user_id, "limit": 200}
                if cursor:
                    kwargs["cursor"] = cursor

                response = self.client.reactions_list(**kwargs)
                items = response.get("items", [])

                since_dt = datetime.now(timezone.utc) - timedelta(days=days_back)

                for item in items:
                    message = item.get("message", {})
                    reactions = message.get("reactions", [])

                    for reaction in reactions:
                        if slack_user_id not in reaction.get("users", []):
                            continue

                        msg_ts = message.get("ts", "")
                        if not msg_ts:
                            continue

                        reaction_dt = datetime.fromtimestamp(float(msg_ts))
                        # NOTE: Slack API returns message timestamp, not reaction timestamp.
                        # Reactions on old messages may be filtered out even if recently given.
                        if reaction_dt < since_dt:
                            continue

                        reaction_name = reaction.get("name", "")
                        target_user = message.get("user", "")

                        # Dedup check
                        existing = db.query(SlackReaction).filter_by(
                            developer_id=developer_id,
                            reaction_name=reaction_name,
                            target_message_ts=msg_ts,
                        ).first()
                        if existing:
                            continue

                        slack_reaction = SlackReaction(
                            developer_id=developer_id,
                            reaction_name=reaction_name,
                            target_message_ts=msg_ts,
                            target_user_id=target_user,
                            reaction_date=reaction_dt.date(),
                        )
                        db.add(slack_reaction)
                        synced += 1

                if not response.get("has_more") or not items:
                    break
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break

        except Exception as e:
            logger.error(f"Error syncing reactions for user {slack_user_id}: {e}")

        if synced > 0:
            db.commit()

        return synced

    def sync_all_for_developer(
        self,
        db: Session,
        developer_id: int,
        slack_user_id: str,
        channel_ids: list[str],
        days_back: int = 7,
    ) -> dict:
        messages = self.sync_messages_for_developer(db, developer_id, slack_user_id, channel_ids, days_back)
        reactions = self.sync_reactions_for_developer(db, developer_id, slack_user_id, days_back)
        return {"messages": messages, "reactions": reactions}

    def _get_channel_name(self, channel_id: str) -> Optional[str]:
        try:
            info = self.client.conversations_info(channel=channel_id)
            return info["channel"]["name"]
        except Exception:
            return None
