"""AI agent for analyzing code review quality"""
import logging

from app.ai.base import get_ai_chat_model, invoke_and_parse_json, AIAnalysisError

logger = logging.getLogger(__name__)


class ReviewQualityAnalyzer:
    """Analyzes the quality of code reviews using AI. No rule-based fallback:
    if AI analysis can't be completed, callers get an AIAnalysisError so the
    review is left unanalyzed rather than scored with fabricated data."""

    def __init__(self):
        self.model = get_ai_chat_model()

    def analyze_review(
        self,
        reviewer_username: str,
        pr_title: str,
        review_state: str,
        comments: list[str],
    ) -> dict:
        """
        Analyze code review quality.

        Args:
            reviewer_username: GitHub username of the reviewer
            pr_title: Title of the PR being reviewed
            review_state: 'approved', 'changes_requested', or 'commented'
            comments: List of review comment bodies

        Returns:
            Dict with quality_score (0-10), mentoring_detected (bool),
            comment_depth ('shallow'/'moderate'/'deep'), explanation (str)

        Raises:
            AIAnalysisError: if no AI provider is configured, or the AI call/
                response parsing fails after retries. Not raised when there
                are simply no comments to analyze — that's a legitimate empty
                result, not an AI failure.
        """
        if not comments:
            return {
                "quality_score": 0,
                "mentoring_detected": False,
                "comment_depth": "shallow",
                "explanation": "No review comments found.",
            }

        if not self.model:
            raise AIAnalysisError("No AI provider configured")

        comments_text = "\n---\n".join(comments[:10])  # Limit to 10 comments

        prompt = f"""Analyze the quality of this code review and respond with JSON only.

Reviewer: {reviewer_username}
PR Title: {pr_title}
Review State: {review_state}
Review Comments:
{comments_text[:2000]}

Respond with this exact JSON structure:
{{
  "quality_score": <number 0-10>,
  "mentoring_detected": <true/false>,
  "comment_depth": "<shallow|moderate|deep>",
  "explanation": "<one sentence summary>"
}}

Scoring guide:
- 0-2: LGTM only, no substance
- 3-5: Some comments, basic feedback
- 6-8: Constructive feedback, questions, suggestions
- 9-10: Deep technical insights, code examples, mentoring"""

        result = invoke_and_parse_json(self.model, prompt)

        return {
            "quality_score": round(float(result.get("quality_score", 5)), 1),
            "mentoring_detected": bool(result.get("mentoring_detected", False)),
            "comment_depth": result.get("comment_depth", "moderate"),
            "explanation": result.get("explanation", "AI analysis"),
        }
