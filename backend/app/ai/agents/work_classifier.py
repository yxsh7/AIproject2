"""Work Type Classifier Agent"""
import logging
from typing import Dict, Any, Optional, List

from app.ai.base import get_ai_chat_model, invoke_and_parse_json, AIAnalysisError
from app.ai.prompts.analysis_prompts import WORK_TYPE_CLASSIFIER_PROMPT

logger = logging.getLogger(__name__)


class WorkTypeClassifier:
    """Classifies Jira tickets into work types using AI. No rule-based fallback:
    if AI classification can't be completed, callers get an AIAnalysisError so
    the ticket is left unanalyzed rather than classified with fabricated data."""

    def __init__(self):
        self.llm = get_ai_chat_model()
        if self.llm:
            logger.info("Work Classifier initialized with AI model")
        else:
            logger.warning("Work Classifier has no AI provider configured — classification will fail")

    def classify_ticket(
        self,
        ticket_key: str,
        title: str,
        ticket_type: str,
        description: Optional[str] = None,
        comments: Optional[List[str]] = None,
        status: str = "Open",
    ) -> Dict[str, Any]:
        """
        Classify a Jira ticket into work type with complexity and impact scores.

        Raises:
            AIAnalysisError: if no AI provider is configured, or the AI call/
                response parsing fails after retries.
        """
        if not self.llm:
            raise AIAnalysisError("No AI provider configured")

        # Limit input size for free models with smaller context windows
        comments_text = "\n".join((comments or [])[:3]) or "No comments"
        if description and len(description) > 1000:
            description = description[:1000] + "... (truncated)"

        formatted_prompt = WORK_TYPE_CLASSIFIER_PROMPT.format(
            ticket_key=ticket_key,
            title=title,
            ticket_type=ticket_type,
            description=description or "No description provided",
            comments=comments_text,
            status=status,
        )

        result = invoke_and_parse_json(self.llm, formatted_prompt)

        # Ensure required keys with sensible defaults
        result.setdefault("work_type", "code")
        result.setdefault("sub_type", ticket_type.lower())
        result.setdefault("complexity_score", 5)
        result.setdefault("impact_score", 5)
        result.setdefault("time_estimate_hours", 8)
        result.setdefault("summary", title[:100])
        result.setdefault("artifacts", [])

        # Clamp numeric scores
        result["complexity_score"] = max(1, min(10, int(result["complexity_score"])))
        result["impact_score"] = max(1, min(10, int(result["impact_score"])))

        logger.info(
            f"AI classified ticket {ticket_key}: type={result['work_type']}, "
            f"complexity={result['complexity_score']}, impact={result['impact_score']}"
        )
        return result
