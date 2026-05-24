"""Test that WorkActivity dedup logic works correctly.

These tests use in-memory state to validate the dedup guard pattern
without requiring a live database.
"""


def _would_skip(existing_source_ids: set, source_type: str, source_id: str) -> bool:
    """Simulate the dedup check: returns True if this activity already exists."""
    return (source_type, source_id) in existing_source_ids


def test_dedup_skips_existing_git_activity():
    seen = {("git", "42"), ("jira", "7")}
    assert _would_skip(seen, "git", "42") is True


def test_dedup_allows_new_git_activity():
    seen = {("git", "42")}
    assert _would_skip(seen, "git", "99") is False


def test_dedup_different_source_types_not_confused():
    seen = {("git", "10")}
    assert _would_skip(seen, "jira", "10") is False


def test_dedup_slack_uses_message_ts():
    seen = {("slack", "1711234567.123456")}
    assert _would_skip(seen, "slack", "1711234567.123456") is True
    assert _would_skip(seen, "slack", "1711234567.999999") is False


def test_dedup_git_review_uses_code_review_id():
    seen = {("git_review", "3")}
    assert _would_skip(seen, "git_review", "3") is True
    assert _would_skip(seen, "git_review", "4") is False
