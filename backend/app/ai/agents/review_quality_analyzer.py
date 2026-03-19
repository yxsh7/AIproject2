"""AI agent for analyzing code review quality"""
import logging
from typing import Optional

from app.ai.base import get_ai_chat_model, extract_json

logger = logging.getLogger(__name__)


class ReviewQualityAnalyzer:
    """Analyzes the quality of code reviews using AI with rule-based fallback."""

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
        """
        if not comments:
            return {
                "quality_score": 0,
                "mentoring_detected": False,
                "comment_depth": "shallow",
                "explanation": "No review comments found.",
            }

        if self.model:
            try:
                return self._ai_analyze(reviewer_username, pr_title, review_state, comments)
            except Exception as e:
                logger.warning(f"AI review analysis failed, using fallback: {e}")

        return self._fallback_analyze(comments)

    def _fallback_analyze(self, comments: list[str]) -> dict:
        """Rule-based quality analysis when AI is unavailable."""
        if not comments:
            return {
                "quality_score": 0,
                "mentoring_detected": False,
                "comment_depth": "shallow",
                "explanation": "No comments to analyze.",
            }

        all_text = " ".join(comments)
        avg_len = sum(len(c) for c in comments) / len(comments)

        # Base score from comment length (avg 100 chars → 5 points, max 5)
        base_score = min(avg_len / 20.0, 5.0)

        # Bonus: questions (engagement) — up to +2
        question_count = all_text.count("?")
        question_bonus = min(question_count / 3.0, 2.0)

        # Bonus: code suggestions — +2 if any ``` found
        code_bonus = 2.0 if "```" in all_text else 0.0

        # Bonus: constructive language keywords — +1
        constructive_keywords = ["suggest", "consider", "why", "have you", "alternative", "what about", "instead"]
        keyword_bonus = 1.0 if any(kw in all_text.lower() for kw in constructive_keywords) else 0.0

        quality_score = min(base_score + question_bonus + code_bonus + keyword_bonus, 10.0)

        # Mentoring: any comment > 100 chars AND contains teaching language
        teaching_words = ["suggest", "consider", "explain", "note that", "keep in mind", "best practice", "have you", "alternative"]
        mentoring_detected = any(
            len(c) > 100 and any(tw in c.lower() for tw in teaching_words)
            for c in comments
        )

        # Comment depth
        if avg_len < 50:
            comment_depth = "shallow"
        elif avg_len < 150:
            comment_depth = "moderate"
        else:
            comment_depth = "deep"

        return {
            "quality_score": round(quality_score, 1),
            "mentoring_detected": mentoring_detected,
            "comment_depth": comment_depth,
            "explanation": f"Rule-based: avg_len={avg_len:.0f}, questions={question_count}, code_blocks={'yes' if code_bonus else 'no'}",
        }

    def _ai_analyze(
        self,
        reviewer_username: str,
        pr_title: str,
        review_state: str,
        comments: list[str],
    ) -> dict:
        """AI-powered quality analysis."""
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

        response = self.model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        result = extract_json(content)

        return {
            "quality_score": float(result.get("quality_score", 5)),
            "mentoring_detected": bool(result.get("mentoring_detected", False)),
            "comment_depth": result.get("comment_depth", "moderate"),
            "explanation": result.get("explanation", "AI analysis"),
        }
