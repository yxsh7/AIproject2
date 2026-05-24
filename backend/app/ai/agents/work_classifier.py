"""Work Type Classifier Agent"""
import logging
from typing import Dict, Any, Optional, List

from app.ai.base import get_ai_chat_model, extract_json
from app.ai.prompts.analysis_prompts import WORK_TYPE_CLASSIFIER_PROMPT

logger = logging.getLogger(__name__)


class WorkTypeClassifier:
    """Classifies Jira tickets into work types using AI with rule-based fallback"""

    def __init__(self):
        self.llm = get_ai_chat_model()
        if self.llm:
            logger.info("Work Classifier initialized with AI model")
        else:
            logger.info("Work Classifier initialized in rule-based fallback mode")

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
        Falls back to rule-based classification if AI is unavailable or fails.
        """
        if not self.llm:
            return self._fallback_classification(title, ticket_type, description)

        try:
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

            response = self.llm.invoke(formatted_prompt)
            result = extract_json(response.content)

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

        except Exception as e:
            logger.error(f"AI classification failed for {ticket_key}, using fallback: {e}")
            return self._fallback_classification(title, ticket_type, description)

    def _fallback_classification(
        self, title: str, ticket_type: str, description: Optional[str]
    ) -> Dict[str, Any]:
        """Rule-based classification when AI is unavailable or fails"""
        title_lower = title.lower()
        desc_lower = (description or "").lower()

        type_mapping = {
            "bug": "bug_fix",
            "story": "code",
            "task": "code",
            "research": "research",
            "spike": "research",
        }
        work_type = type_mapping.get(ticket_type.lower(), "code")

        if any(w in title_lower or w in desc_lower for w in ["research", "investigate", "explore", "evaluate"]):
            work_type = "research"
        elif any(w in title_lower or w in desc_lower for w in ["document", "readme", "guide", "wiki"]):
            work_type = "documentation"
        elif any(w in title_lower or w in desc_lower for w in ["dashboard", "report", "metrics", "analytics"]):
            work_type = "dashboard"

        return {
            "work_type": work_type,
            "sub_type": ticket_type.lower(),
            "complexity_score": 5,
            "impact_score": 5,
            "time_estimate_hours": 8,
            "artifacts": [],
            "summary": f"Rule-based: {title[:80]}",
        }
