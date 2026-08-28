"""Code Complexity Analyzer Agent"""
import logging
from typing import Dict, Any, Optional

from app.ai.base import get_ai_chat_model, invoke_and_parse_json, AIAnalysisError
from app.ai.prompts.analysis_prompts import CODE_COMPLEXITY_PROMPT

logger = logging.getLogger(__name__)


class CodeComplexityAnalyzer:
    """Analyzes git commits for complexity and quality using AI. No rule-based
    fallback: if AI analysis can't be completed, callers get an AIAnalysisError
    so the commit is left unanalyzed rather than scored with fabricated data."""

    def __init__(self):
        self.llm = get_ai_chat_model()
        if self.llm:
            logger.info("Code Analyzer initialized with AI model")
        else:
            logger.warning("Code Analyzer has no AI provider configured — analysis will fail")

    def analyze_commit(
        self,
        commit_message: str,
        files_changed: int,
        additions: int,
        deletions: int,
        diff: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a git commit for complexity and quality using AI.

        Raises:
            AIAnalysisError: if no AI provider is configured, or the AI call/
                response parsing fails after retries.
        """
        if not self.llm:
            raise AIAnalysisError("No AI provider configured")

        # Truncate diff to keep prompt within token limits for free models
        if diff and len(diff) > 3000:
            diff = diff[:3000] + "\n... (diff truncated)"

        formatted_prompt = CODE_COMPLEXITY_PROMPT.format(
            commit_message=commit_message,
            files_changed=files_changed,
            additions=additions,
            deletions=deletions,
            diff=diff or "No diff available",
        )

        result = invoke_and_parse_json(self.llm, formatted_prompt)

        # Ensure all required keys with sensible defaults
        result.setdefault("complexity_score", 5)
        result.setdefault("quality_score", 5)
        result.setdefault("impact", "medium")
        result.setdefault("work_type", "feature")
        result.setdefault("technical_debt_delta", 0)
        result.setdefault("affected_systems", [])
        result.setdefault("novelty_level", "moderate")
        result.setdefault("summary", commit_message[:100])

        # Clamp numeric scores
        result["complexity_score"] = max(1, min(10, int(result["complexity_score"])))
        result["quality_score"] = max(1, min(10, int(result["quality_score"])))

        logger.info(
            f"AI analyzed commit: complexity={result['complexity_score']}, "
            f"quality={result['quality_score']}, type={result['work_type']}"
        )
        return result
