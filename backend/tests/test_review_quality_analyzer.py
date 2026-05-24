"""Unit tests for ReviewQualityAnalyzer rule-based fallback."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ai.agents.review_quality_analyzer import ReviewQualityAnalyzer


def test_empty_comments_returns_low_score():
    analyzer = ReviewQualityAnalyzer()
    result = analyzer.analyze_review(
        reviewer_username="alice",
        pr_title="Fix login bug",
        review_state="commented",
        comments=[],
    )
    assert result["quality_score"] == 0
    assert result["mentoring_detected"] is False
    assert result["comment_depth"] == "shallow"


def test_lgtm_only_gives_low_score():
    analyzer = ReviewQualityAnalyzer()
    result = analyzer.analyze_review(
        reviewer_username="alice",
        pr_title="Add feature",
        review_state="approved",
        comments=["LGTM", "looks good"],
    )
    assert result["quality_score"] <= 3


def test_deep_constructive_comment_gives_high_score():
    analyzer = ReviewQualityAnalyzer()
    long_comment = (
        "Have you considered using a more efficient algorithm here? "
        "The current O(n²) approach will struggle with large datasets. "
        "I suggest using a hash map to reduce it to O(n). "
        "```python\nresult = {k: v for k, v in items}\n``` "
        "This would also improve readability."
    )
    result = analyzer.analyze_review(
        reviewer_username="alice",
        pr_title="Optimize search",
        review_state="changes_requested",
        comments=[long_comment],
    )
    assert result["quality_score"] >= 6
    assert result["mentoring_detected"] is True
    assert result["comment_depth"] in ("moderate", "deep")


def test_questions_boost_score():
    analyzer = ReviewQualityAnalyzer()
    result_with_questions = analyzer.analyze_review(
        reviewer_username="alice",
        pr_title="Refactor",
        review_state="commented",
        comments=["Why is this needed? Have you considered alternatives? What about edge cases?"],
    )
    result_no_questions = analyzer.analyze_review(
        reviewer_username="alice",
        pr_title="Refactor",
        review_state="commented",
        comments=["This is a comment about the code quality."],
    )
    assert result_with_questions["quality_score"] >= result_no_questions["quality_score"]


def test_code_block_boosts_score():
    analyzer = ReviewQualityAnalyzer()
    result = analyzer.analyze_review(
        reviewer_username="alice",
        pr_title="PR",
        review_state="commented",
        comments=["Consider this approach:\n```python\nreturn sorted(items, key=lambda x: x.value)\n```"],
    )
    assert result["quality_score"] >= 4


def test_result_has_required_keys():
    analyzer = ReviewQualityAnalyzer()
    result = analyzer.analyze_review("u", "t", "approved", ["ok"])
    assert "quality_score" in result
    assert "mentoring_detected" in result
    assert "comment_depth" in result
    assert "explanation" in result
    assert 0 <= result["quality_score"] <= 10
