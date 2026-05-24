"""Prompt templates for AI analysis agents - concise for small/free models"""

CODE_COMPLEXITY_PROMPT = """Analyze this git commit and return ONLY a JSON object.

Commit: {commit_message}
Files changed: {files_changed}, additions: {additions}, deletions: {deletions}
Diff: {diff}

Return ONLY this JSON (no explanation, no markdown):
{{"complexity_score": 7, "quality_score": 8, "impact": "medium", "work_type": "feature", "technical_debt_delta": -1, "affected_systems": ["auth", "api"], "novelty_level": "moderate", "summary": "one sentence describing what this commit does"}}

Field rules:
- complexity_score: 1-10 integer (1=trivial change, 10=major system overhaul)
- quality_score: 1-10 integer (1=poor, 10=excellent practices)
- impact: exactly one of "low", "medium", "high", "critical"
- work_type: exactly one of "feature", "bug_fix", "refactoring", "documentation", "testing", "config", "other"
- technical_debt_delta: integer (negative removes debt, positive adds it)
- affected_systems: list of short module/system names
- novelty_level: exactly one of "routine", "moderate", "high"
- summary: one sentence (under 100 chars)"""


WORK_TYPE_CLASSIFIER_PROMPT = """Classify this Jira ticket and return ONLY a JSON object.

Ticket: {ticket_key} — {title}
Type: {ticket_type} | Status: {status}
Description: {description}
Comments: {comments}

Return ONLY this JSON (no explanation, no markdown):
{{"work_type": "code", "sub_type": "feature", "complexity_score": 6, "impact_score": 7, "time_estimate_hours": 8, "summary": "one sentence describing this ticket"}}

Field rules:
- work_type: exactly one of "code", "bug_fix", "research", "documentation", "dashboard", "testing", "operations", "design", "mentoring", "other"
- sub_type: short sub-classification string
- complexity_score: 1-10 integer
- impact_score: 1-10 integer
- time_estimate_hours: positive integer (hours to complete)
- summary: one sentence (under 100 chars)"""
