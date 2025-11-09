"""Code Complexity Analyzer Agent using Claude AI"""
import json
import logging
from typing import Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from app.config import settings
from app.ai.prompts.analysis_prompts import CODE_COMPLEXITY_PROMPT

logger = logging.getLogger(__name__)


class CodeAnalysisResult(BaseModel):
    """Pydantic model for code analysis results"""

    complexity_score: int = Field(..., ge=0, le=10, description="Cognitive complexity score")
    quality_score: int = Field(..., ge=0, le=10, description="Code quality score")
    impact_level: str = Field(..., description="Impact level: low, medium, high, critical")
    work_type: str = Field(..., description="Type of work")
    technical_debt_delta: int = Field(..., description="Tech debt added (+) or removed (-)")
    affected_systems: list[str] = Field(default_factory=list, description="Systems affected")
    novelty: str = Field(..., description="Novelty level: routine, moderate, high")
    explanation: str = Field(..., description="Explanation of analysis")


class CodeComplexityAnalyzer:
    """Analyzes git commits for complexity and quality using Claude AI"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Code Complexity Analyzer

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
            temperature=0.1,  # Low temperature for consistent analysis
            max_tokens=1024,
        )

        # Create prompt template
        self.prompt = PromptTemplate(
            template=CODE_COMPLEXITY_PROMPT,
            input_variables=[
                "commit_message",
                "files_changed",
                "additions",
                "deletions",
                "diff",
            ],
        )

    def analyze_commit(
        self,
        commit_message: str,
        files_changed: int,
        additions: int,
        deletions: int,
        diff: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a git commit for complexity and quality

        Args:
            commit_message: Commit message
            files_changed: Number of files changed
            additions: Lines added
            deletions: Lines deleted
            diff: Code diff (optional but recommended)

        Returns:
            Dict with analysis results
        """
        try:
            # Truncate diff if too long (Claude has token limits)
            if diff and len(diff) > 10000:
                diff = diff[:10000] + "\n\n... (diff truncated)"

            # Format prompt
            formatted_prompt = self.prompt.format(
                commit_message=commit_message,
                files_changed=files_changed,
                additions=additions,
                deletions=deletions,
                diff=diff or "Diff not available",
            )

            # Call Claude
            response = self.llm.invoke(formatted_prompt)
            content = response.content

            # Parse JSON response
            # Claude might wrap JSON in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)

            logger.info(
                f"Analyzed commit: complexity={result['complexity_score']}, "
                f"quality={result['quality_score']}, type={result['work_type']}"
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            logger.error(f"Response content: {content}")
            # Return fallback analysis
            return self._fallback_analysis(
                commit_message, files_changed, additions, deletions
            )

        except Exception as e:
            logger.error(f"Error analyzing commit: {e}")
            return self._fallback_analysis(
                commit_message, files_changed, additions, deletions
            )

    def _fallback_analysis(
        self, commit_message: str, files_changed: int, additions: int, deletions: int
    ) -> Dict[str, Any]:
        """
        Provide basic rule-based analysis when AI fails

        Args:
            commit_message: Commit message
            files_changed: Number of files changed
            additions: Lines added
            deletions: Lines deleted

        Returns:
            Basic analysis dict
        """
        # Simple heuristics
        total_changes = additions + deletions

        # Complexity based on size
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

        # Detect work type from commit message
        message_lower = commit_message.lower()
        if any(word in message_lower for word in ["fix", "bug", "issue"]):
            work_type = "bug_fix"
        elif any(word in message_lower for word in ["refactor", "cleanup", "simplify"]):
            work_type = "refactoring"
        elif any(word in message_lower for word in ["test", "spec"]):
            work_type = "testing"
        elif any(word in message_lower for word in ["doc", "readme", "comment"]):
            work_type = "documentation"
        else:
            work_type = "feature"

        return {
            "complexity_score": complexity,
            "quality_score": 5,  # Neutral
            "impact_level": "medium",
            "work_type": work_type,
            "technical_debt_delta": 0,
            "affected_systems": [],
            "novelty": "moderate",
            "explanation": "Fallback analysis (AI analysis failed)",
        }


# Example usage
if __name__ == "__main__":
    # Test the analyzer
    analyzer = CodeComplexityAnalyzer()

    result = analyzer.analyze_commit(
        commit_message="Refactored authentication system to use JWT tokens",
        files_changed=5,
        additions=250,
        deletions=180,
        diff="""
        --- a/auth/authentication.py
        +++ b/auth/authentication.py
        - def authenticate(username, password):
        -     # Old session-based auth
        -     session = create_session(username)
        -     return session
        + def authenticate(username, password):
        +     # New JWT-based auth
        +     token = create_jwt_token(username)
        +     return token
        """,
    )

    print(json.dumps(result, indent=2))
