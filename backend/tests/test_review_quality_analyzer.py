"""Unit tests for ReviewQualityAnalyzer.

No rule-based fallback exists any more: if AI can't produce a result (no
provider configured, or every retry attempt fails), analyze_review() must
raise AIAnalysisError rather than substitute heuristic scores. These tests
inject a fake LLM directly (bypassing get_ai_chat_model()/real network calls)
so retry/failure behavior can be tested deterministically and offline.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from types import SimpleNamespace

from app.ai.agents.review_quality_analyzer import ReviewQualityAnalyzer
from app.ai.base import AIAnalysisError


class _FakeModel:
    """Fake LLM: pops one entry per .invoke() call. An entry that is an
    Exception instance is raised; otherwise it's returned as response.content."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return SimpleNamespace(content=item)


def _analyzer_with_model(model):
    analyzer = ReviewQualityAnalyzer()
    analyzer.model = model
    return analyzer


VALID_RESPONSE = (
    '{"quality_score": 7, "mentoring_detected": true, '
    '"comment_depth": "deep", "explanation": "Constructive, in-depth feedback."}'
)


def test_empty_comments_returns_zero_without_calling_ai():
    """No comments is a legitimate empty result, not an AI failure — doesn't
    even need a model configured."""
    analyzer = _analyzer_with_model(None)
    result = analyzer.analyze_review(
        reviewer_username="alice", pr_title="Fix login bug",
        review_state="commented", comments=[],
    )
    assert result["quality_score"] == 0
    assert result["mentoring_detected"] is False
    assert result["comment_depth"] == "shallow"


def test_no_ai_configured_raises():
    analyzer = _analyzer_with_model(None)
    with pytest.raises(AIAnalysisError):
        analyzer.analyze_review(
            reviewer_username="alice", pr_title="Add feature",
            review_state="approved", comments=["LGTM"],
        )


def test_successful_analysis_returns_expected_shape():
    model = _FakeModel([VALID_RESPONSE])
    analyzer = _analyzer_with_model(model)
    result = analyzer.analyze_review(
        reviewer_username="alice", pr_title="Optimize search",
        review_state="changes_requested", comments=["Have you considered a hash map?"],
    )
    assert result["quality_score"] == 7.0
    assert result["mentoring_detected"] is True
    assert result["comment_depth"] == "deep"
    assert "explanation" in result
    assert model.calls == 1


def test_retries_on_transient_failure_then_succeeds(monkeypatch):
    monkeypatch.setattr("app.ai.base.time.sleep", lambda _: None)
    model = _FakeModel([ValueError("truncated JSON"), VALID_RESPONSE])
    analyzer = _analyzer_with_model(model)
    result = analyzer.analyze_review(
        reviewer_username="alice", pr_title="Refactor",
        review_state="commented", comments=["Why is this needed?"],
    )
    assert result["quality_score"] == 7.0
    assert model.calls == 2


def test_gives_up_after_max_retries_raises(monkeypatch):
    monkeypatch.setattr("app.ai.base.time.sleep", lambda _: None)
    model = _FakeModel([ValueError("bad json")] * 5)
    analyzer = _analyzer_with_model(model)
    with pytest.raises(AIAnalysisError):
        analyzer.analyze_review(
            reviewer_username="alice", pr_title="PR",
            review_state="commented", comments=["Consider this approach"],
        )
    assert model.calls == 3  # default retries=3, never exceeds that
