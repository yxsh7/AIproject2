"""Work Type Classifier Agent using Claude AI"""
import json
import logging
from typing import Dict, Any, Optional, List
from langchain_anthropic import ChatAnthropic

from app.config import settings
from app.ai.prompts.analysis_prompts import WORK_TYPE_CLASSIFIER_PROMPT

logger = logging.getLogger(__name__)


class WorkTypeClassifier:
    """Classifies Jira tickets into work types using Claude AI"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Work Type Classifier

        Args:
            api_key: Anthropic API key (defaults to settings)
        """
        self.api_key = api_key or settings.ANTHROPIC_API_KEY

        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        # Initialize Claude model
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=self.api_key,
            temperature=0.1,
            max_tokens=1024,
        )

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
        Classify a Jira ticket into work type with complexity and impact

        Args:
            ticket_key: Jira ticket key (e.g., PROJ-123)
            title: Ticket title
            ticket_type: Jira issue type (story, bug, task, etc.)
            description: Ticket description
            comments: List of comment texts
            status: Ticket status

        Returns:
            Dict with classification results
        """
        try:
            # Format comments
            comments_text = "\n\n".join(comments) if comments else "No comments yet"

            # Truncate if too long
            if description and len(description) > 2000:
                description = description[:2000] + "\n\n... (truncated)"

            if len(comments_text) > 3000:
                comments_text = comments_text[:3000] + "\n\n... (truncated)"

            # Format prompt
            formatted_prompt = WORK_TYPE_CLASSIFIER_PROMPT.format(
                ticket_key=ticket_key,
                title=title,
                ticket_type=ticket_type,
                description=description or "No description provided",
                comments=comments_text,
                status=status,
            )

            # Call Claude
            response = self.llm.invoke(formatted_prompt)
            content = response.content

            # Parse JSON response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)

            logger.info(
                f"Classified ticket {ticket_key}: type={result['work_type']}, "
                f"complexity={result['complexity_score']}, impact={result['impact_score']}"
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            logger.error(f"Response content: {content}")
            return self._fallback_classification(title, ticket_type, description)

        except Exception as e:
            logger.error(f"Error classifying ticket: {e}")
            return self._fallback_classification(title, ticket_type, description)

    def _fallback_classification(
        self, title: str, ticket_type: str, description: Optional[str]
    ) -> Dict[str, Any]:
        """
        Provide rule-based classification when AI fails

        Args:
            title: Ticket title
            ticket_type: Jira issue type
            description: Ticket description

        Returns:
            Basic classification dict
        """
        title_lower = title.lower()
        desc_lower = description.lower() if description else ""

        # Map Jira types to our work types
        type_mapping = {
            "bug": "bug_fix",
            "story": "code",
            "task": "code",
            "research": "research",
            "spike": "research",
        }

        work_type = type_mapping.get(ticket_type.lower(), "code")

        # Detect research
        if any(
            word in title_lower or word in desc_lower
            for word in ["research", "investigate", "explore", "evaluate", "analyze"]
        ):
            work_type = "research"

        # Detect documentation
        if any(
            word in title_lower or word in desc_lower
            for word in ["document", "readme", "guide", "wiki"]
        ):
            work_type = "documentation"

        # Detect dashboard/analytics
        if any(
            word in title_lower or word in desc_lower
            for word in ["dashboard", "report", "metrics", "analytics"]
        ):
            work_type = "dashboard"

        return {
            "work_type": work_type,
            "sub_type": ticket_type.lower(),
            "complexity_score": 5,
            "impact_score": 5,
            "time_estimate_hours": 8,
            "artifacts": [],
            "explanation": "Fallback classification (AI analysis failed)",
        }


# Example usage
if __name__ == "__main__":
    classifier = WorkTypeClassifier()

    result = classifier.classify_ticket(
        ticket_key="PROJ-234",
        title="Investigate caching solutions for API layer",
        ticket_type="Spike",
        description="""We're experiencing high latency on user profile endpoints.
        Need to research and recommend caching solution. Consider Redis, Memcached, and Varnish.""",
        comments=[
            "Day 1: Researched Redis vs Memcached. Redis has better data structure support.",
            "Day 2: Set up Redis benchmark. Achieved 85% latency reduction.",
            "Day 3: Created implementation plan. Estimated 3 days for integration.",
        ],
        status="Done",
    )

    print(json.dumps(result, indent=2))
