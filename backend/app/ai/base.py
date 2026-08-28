"""Base AI model factory for DevMetrics AI"""

import json
import logging
import time
import requests
from typing import Optional, Any, Dict

from app.config import settings

logger = logging.getLogger(__name__)


class AIAnalysisError(Exception):
    """Raised when AI analysis could not be completed — either no provider is
    configured or every retry attempt failed. Callers must not substitute
    rule-based/heuristic data for this; the item should be left unanalyzed
    so it can be retried on a future run."""

    pass


_OPENROUTER_HEADERS = {
    "HTTP-Referer": "http://localhost:3000",
    "X-Title": "DevMetrics AI",
}


def extract_json(text: str) -> Dict:
    """
    Robustly extract JSON from LLM response text.
    Handles markdown fences, preamble text, and slightly malformed JSON.

    Raises ValueError if no valid JSON can be found.
    """
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    if "```json" in text:
        try:
            content = text.split("```json")[1].split("```")[0].strip()
            return json.loads(content)
        except (IndexError, json.JSONDecodeError):
            pass

    if "```" in text:
        try:
            content = text.split("```")[1].split("```")[0].strip()
            return json.loads(content)
        except (IndexError, json.JSONDecodeError):
            pass

    # Walk braces to find the first complete {...} block
    start = text.find("{")
    if start != -1:
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break

    raise ValueError(f"Could not extract JSON from LLM response: {text[:300]}")


def invoke_and_parse_json(
    llm: Any, prompt: str, retries: int = 3, backoff_seconds: float = 1.5
) -> Dict:
    """
    Call the LLM and parse its response as JSON, retrying transient failures
    (timeouts, truncated/malformed JSON, rate limits) before giving up.

    Raises AIAnalysisError if every attempt fails — callers must treat this as
    a hard failure for the item being analyzed, not fall back to heuristics.
    """
    last_error: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            response = llm.invoke(prompt)
            return extract_json(response.content)
        except Exception as e:
            last_error = e
            logger.warning(f"AI call attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(backoff_seconds * attempt)

    raise AIAnalysisError(
        f"AI analysis failed after {retries} attempts: {last_error}"
    ) from last_error


class _OpenRouterResponse:
    """Minimal wrapper so callers can do response.content"""

    def __init__(self, content: str):
        self.content = content


class _OpenRouterClient:
    """Direct HTTP client for OpenRouter — no langchain needed."""

    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def invoke(self, prompt: str) -> _OpenRouterResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **_OPENROUTER_HEADERS,
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()

        # OpenRouter can return HTTP 200 with an error body (e.g. the free
        # model is overloaded/rate-limited) — raise_for_status() won't catch
        # that, so check explicitly instead of letting a bare KeyError surface.
        if "error" in data:
            raise RuntimeError(f"OpenRouter returned an error: {data['error']}")
        if "choices" not in data or not data["choices"]:
            raise RuntimeError(f"OpenRouter response had no choices: {data}")

        content = data["choices"][0]["message"]["content"]
        return _OpenRouterResponse(content)


def get_ai_chat_model() -> Optional[Any]:
    """
    Get a configured AI chat model based on settings.

    Returns an object with an .invoke(prompt: str) method.
    Priority: OpenRouter → Anthropic → None (rule-based)
    """
    if settings.OPENROUTER_API_KEY:
        try:
            model = (
                settings.OPENROUTER_MODEL or "nvidia/nemotron-3-super-120b-a12b:free"
            )
            temperature = getattr(settings, "AI_MODEL_TEMPERATURE", 0.1)
            max_tokens = getattr(settings, "AI_MODEL_MAX_TOKENS", 1000)
            logger.info(f"Using OpenRouter model: {model}")
            return _OpenRouterClient(
                api_key=settings.OPENROUTER_API_KEY,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenRouter client: {e}")

    if (
        getattr(settings, "ANTHROPIC_API_KEY", None)
        and settings.AI_MODEL_PROVIDER.lower() == "anthropic"
    ):
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            model_name = settings.AI_MODEL_NAME or "claude-3-haiku-20240307"
            max_tokens = getattr(settings, "AI_MODEL_MAX_TOKENS", 1000)

            class _AnthropicClient:
                def invoke(self, prompt: str) -> _OpenRouterResponse:
                    msg = client.messages.create(
                        model=model_name,
                        max_tokens=max_tokens,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    return _OpenRouterResponse(msg.content[0].text)

            logger.info(f"Using Anthropic model: {model_name}")
            return _AnthropicClient()
        except ImportError:
            logger.warning("anthropic SDK not installed; skipping Anthropic")
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic model: {e}")

    logger.info("No AI API key configured. Running in rule-based mode (no AI costs).")
    return None


def check_ai_available() -> bool:
    """Returns True if at least one AI provider is configured."""
    return bool(
        settings.OPENROUTER_API_KEY
        or getattr(settings, "ANTHROPIC_API_KEY", None)
        or getattr(settings, "OPENAI_API_KEY", None)
    )


def get_ai_status() -> dict:
    """Returns current AI configuration status."""
    return {
        "provider": (
            "openrouter" if settings.OPENROUTER_API_KEY else settings.AI_MODEL_PROVIDER
        ),
        "model": settings.OPENROUTER_MODEL or settings.AI_MODEL_NAME,
        "available": check_ai_available(),
        "openrouter_configured": bool(settings.OPENROUTER_API_KEY),
        "anthropic_configured": bool(getattr(settings, "ANTHROPIC_API_KEY", None)),
        "openai_configured": bool(getattr(settings, "OPENAI_API_KEY", None)),
    }
