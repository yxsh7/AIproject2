"""Code Complexity Analyzer Agent"""
import logging
from typing import Dict, Any, Optional

from app.ai.base import get_ai_chat_model, extract_json
from app.ai.prompts.analysis_prompts import CODE_COMPLEXITY_PROMPT

logger = logging.getLogger(__name__)


class CodeComplexityAnalyzer:
    """Analyzes git commits for complexity and quality using AI with rule-based fallback"""

    def __init__(self):
        self.llm = get_ai_chat_model()
        if self.llm:
            logger.info("Code Analyzer initialized with AI model")
        else:
            logger.info("Code Analyzer initialized in rule-based fallback mode")

    def analyze_commit(
        self,
        commit_message: str,
        files_changed: int,
        additions: int,
        deletions: int,
        diff: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a git commit for complexity and quality.
        Falls back to rule-based analysis if AI is unavailable or fails.
        """
        if not self.llm:
            return self._fallback_analysis(commit_message, files_changed, additions, deletions)

        try:
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

            response = self.llm.invoke(formatted_prompt)
            result = extract_json(response.content)

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

        except Exception as e:
            logger.error(f"AI analysis failed, using fallback: {e}")
            return self._fallback_analysis(commit_message, files_changed, additions, deletions)

    def _fallback_analysis(
        self, commit_message: str, files_changed: int, additions: int, deletions: int
    ) -> Dict[str, Any]:
        """Rule-based analysis when AI is unavailable or fails"""
        total_changes = additions + deletions

        if total_changes < 10:
            complexity = 2
        elif total_changes < 50:
            complexity = 4
        elif total_changes < 200:
            complexity = 6
        elif total_changes < 500:
            complexity = 8
        else:
            complexity = 9

        message_lower = commit_message.lower()
        if any(w in message_lower for w in ["fix", "bug", "issue", "patch"]):
            work_type = "bug_fix"
        elif any(w in message_lower for w in ["refactor", "cleanup", "simplify", "reorganize"]):
            work_type = "refactoring"
        elif any(w in message_lower for w in ["test", "spec", "coverage"]):
            work_type = "testing"
        elif any(w in message_lower for w in ["doc", "readme", "comment", "changelog"]):
            work_type = "documentation"
        else:
            work_type = "feature"

        return {
            "complexity_score": complexity,
            "quality_score": 5,
            "impact": "medium",
            "work_type": work_type,
            "technical_debt_delta": 0,
            "affected_systems": [],
            "novelty_level": "moderate",
            "summary": f"Rule-based: {commit_message[:80]}",
        }
