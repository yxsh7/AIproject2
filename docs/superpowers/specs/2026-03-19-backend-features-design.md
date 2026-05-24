# Backend Features Design — 2026-03-19

## Scope
Four backend improvements to DevMetrics AI:
1. Multi-tenancy fix (remove hardcoded `organization_id = 1`)
2. WorkActivity duplicate prevention
3. Slack integration
4. PR review quality scoring

---

## 1. Multi-tenancy Fix

### Problem
`organization_id = 1` is hardcoded in three places in `app/api/integrations.py`. The `User` model has no `organization_id` field, making it impossible to derive the correct org from the current authenticated user.

### Solution
- Add `organization_id` column to `User` (Integer FK → organizations, nullable=True, default=1).
- `organization_id` is **internal-only** — NOT exposed in registration schema. All new users default to org 1. This makes the field ready for future multi-tenancy without requiring registration changes now.
- `app/schemas/auth.py` is NOT changed.
- Create Alembic migration: `add_organization_id_to_users`.
- Update `AuthService.create_user()` to accept optional `organization_id` kwarg (defaults to 1).
- Replace all three `organization_id = 1` occurrences in `integrations.py` with helper: `org_id = current_user.organization_id or 1`.

### Data model change
```python
# app/models/user.py
organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, default=1)
```

---

## 2. WorkActivity Duplicate Prevention

### Problem
`analysis_tasks.py` unconditionally creates a new `WorkActivity` for every analyzed commit/ticket. Re-running analysis duplicates records and inflates all scores.

### source_id semantics (canonical definition)
| source_type  | source_id value          |
|-------------|--------------------------|
| git         | str(GitCommit.id)        |
| jira        | str(JiraTicket.id)       |
| slack       | SlackMessage.message_ts  |
| git_review  | str(CodeReview.id)       |

### Solution
- Add `UniqueConstraint('developer_id', 'source_type', 'source_id', name='uq_work_activity_source')` to `WorkActivity`.
- Create Alembic migration: `add_work_activity_unique_constraint`. Migration deduplicates existing rows first (keep max id per group), then adds the constraint.
- After dedup migration, the `GitCommit.analyzed` and `JiraTicket.analyzed` flags remain the primary idempotency guard for *analysis* (tasks skip records where `analyzed == True`). The unique constraint is a safety net against the case where two task workers race. Do NOT reset `analyzed` flags in the migration.
- In `analyze_git_commits()` and `analyze_jira_tickets()`, add existence check before `db.add()`:

```python
# For git commits
existing = db.query(WorkActivity).filter_by(
    developer_id=developer_id, source_type="git", source_id=str(commit.id)
).first()
if existing:
    continue

# For jira tickets
existing = db.query(WorkActivity).filter_by(
    developer_id=developer_id, source_type="jira", source_id=str(ticket.id)
).first()
if existing:
    continue
```

---

## 3. Slack Integration

### Architecture
```
Slack API (Bot Token)
    ↓
SlackService (new)
    ↓
sync_slack_integration Celery task  ← dispatched by sync_integration_task
    ↓
SlackMessage / SlackReaction models (new)
    ↓
analyze_slack_messages Celery task
    ↓
WorkActivity (source_type="slack")
    ↓
ProductivityScoringService (collaboration score update)
```

### New Models (`app/models/slack_activity.py`)

All `Integer 0/1` boolean columns: `nullable=False, default=0` (matches project convention).

**SlackMessage**
- `id`, `developer_id` (FK developer_profiles, nullable=False, index=True)
- `channel_id` (String, nullable=False), `channel_name` (String, nullable=True)
- `message_ts` (String, unique=True, nullable=False) — Slack's message timestamp, unique globally
- `message_date` (Date, nullable=False)
- `has_code_block` (Integer, nullable=False, default=0) — message contains ``` code blocks
- `reply_count` (Integer, nullable=False, default=0)
- `reaction_count` (Integer, nullable=False, default=0)
- `analyzed` (Integer, nullable=False, default=0)
- `analysis_result` (JSON, nullable=True)
- `created_at`

**SlackReaction**
- `id`, `developer_id` (FK developer_profiles, nullable=False, index=True)
- `reaction_name` (String, nullable=False)
- `target_message_ts` (String, nullable=False)
- `target_user_id` (String, nullable=True)
- `reaction_date` (Date, nullable=False)
- `created_at`
- `UniqueConstraint('developer_id', 'reaction_name', 'target_message_ts', name='uq_slack_reaction')`

### New Service (`app/services/slack_service.py`)
Uses `slack_sdk` library.

Methods:
- `__init__(bot_token: str)`
- `from_integration_config(integration) -> SlackService` — classmethod
- `test_connection() -> bool` — calls `client.auth_test()`
- `sync_messages_for_developer(db, developer_id, slack_user_id, channel_ids, days_back) -> int` — creates SlackMessage records, returns count
- `sync_reactions_for_developer(db, developer_id, slack_user_id, days_back) -> int` — creates SlackReaction records
- `sync_all_for_developer(db, developer_id, slack_user_id, channel_ids, days_back) -> dict`

Dedup for SlackMessage: upsert-or-skip on `message_ts` (unique constraint).
Dedup for SlackReaction: check before insert on `(developer_id, reaction_name, target_message_ts)`.

### API Endpoint (`app/api/integrations.py`)
```
POST /api/integrations/slack
  body: SlackIntegrationCreate { bot_token: str, channel_ids: list[str] }
  - Admin only
  - Validates token via slack_service.test_connection()
  - Creates/updates IntegrationConfig(type=SLACK, config={bot_token, channel_ids})
```

Also update `test_integration` to handle `IntegrationType.SLACK`.

### Celery Tasks

**`app/tasks/sync_tasks.py`** — Two changes:
1. Add `SLACK` branch to `sync_integration_task` dispatcher:
```python
elif integration.type == IntegrationType.SLACK:
    result = sync_slack_integration(db, integration, days_back)
```
2. Add `sync_slack_integration(db, integration, days_back)` function (NOT Celery task — called from within `sync_integration_task` like the existing `sync_github_integration` / `sync_jira_integration` helpers).
3. Add `sync_all_slack()` periodic Celery task (mirrors `sync_all_github`/`sync_all_jira`).

**`app/tasks/analysis_tasks.py`** — New task:
`analyze_slack_messages(developer_id: int, limit: int = 200)`:
- Fetches `SlackMessage` records where `developer_id == developer_id AND analyzed == False`
- For each message:
  - `has_code_block == 1 → work_type = CODE_REVIEW`
  - `reply_count > 2 → work_type = MENTORING`
  - else → `work_type = OTHER`
  - Dedup check: `db.query(WorkActivity).filter_by(developer_id=developer_id, source_type="slack", source_id=msg.message_ts).first()`
  - Create WorkActivity if not exists, set `analyzed = 1`
- Add to `analyze_all_unanalyzed()`: `analyze_slack_messages.delay(developer.id)`

### Schema (`app/schemas/integration.py`)
```python
class SlackIntegrationCreate(BaseModel):
    bot_token: str
    channel_ids: list[str]
```

### `app/models/__init__.py` and `alembic/env.py`
Both must be updated to import `SlackMessage, SlackReaction`. Alembic autogenerate will not detect new tables unless `env.py` imports them.

---

## 4. PR Review Quality Scoring

### Problem
`CodeReview.quality_score` is always null. Code reviews are counted but not quality-assessed.

### New AI Agent (`app/ai/agents/review_quality_analyzer.py`)
`ReviewQualityAnalyzer` class mirroring `CodeComplexityAnalyzer` pattern:
- `analyze_review(reviewer_username: str, pr_title: str, review_state: str, comments: list[str]) -> dict`
- Rule-based fallback (default path, no AI required):
  - `quality_score`: average comment length ÷ 20 capped at 5, + bonus for `?` questions (+1 per 3 questions, max +2), ` ``` ` code blocks (+2 if any), "suggest"/"consider"/"why"/"have you"/"alternative" keywords (+1)
  - `mentoring_detected`: True if any comment > 100 chars AND contains teaching language
  - `comment_depth`: avg_len < 50 → "shallow", < 150 → "moderate", ≥ 150 → "deep"
  - Returns dict: `{quality_score, mentoring_detected, comment_depth, explanation}`
- AI path: structured prompt via `get_ai_chat_model()` → JSON output

### Enhanced GitHub Service (`app/services/github_service.py`)
In `sync_code_reviews_for_developer()`:
- After fetching each `PullRequestReview`, also fetch inline review comments:
  ```python
  comments = list(pr.get_review_comments())
  raw_comments = [c.body for c in comments if c.user.login == reviewer_username]
  ```
- Merge into `code_review.analysis_result`:
  ```python
  code_review.analysis_result = {"raw_comments": raw_comments, "comment_count": len(raw_comments)}
  ```

### New Analysis Task (`app/tasks/analysis_tasks.py`)
`analyze_code_reviews(developer_id: int, limit: int = 100)`:
- Fetches `CodeReview` records where `reviewer_id == developer_id AND quality_score IS NULL`
- **In Python** (not SQL): filter to records where `analysis_result` exists and contains `raw_comments` key
  ```python
  reviews = [r for r in reviews_query if r.analysis_result and "raw_comments" in r.analysis_result]
  ```
- For each review, call `ReviewQualityAnalyzer.analyze_review()`
- Update `code_review.quality_score` and `code_review.analysis_result`
- Create WorkActivity (source_type="git_review", source_id=str(code_review.id), work_type=CODE_REVIEW)
- Dedup check before WorkActivity insert
- Add to `analyze_all_unanalyzed()`: `analyze_code_reviews.delay(developer.id)`

### Scoring Service Update (`app/services/scoring_service.py`)
Update `_calculate_collaboration_score` signature:
```python
def _calculate_collaboration_score(
    self,
    activities: List[WorkActivity],
    developer_id: int,
    start_date: date,
    end_date: date,
) -> float:
```
Inside, after computing `collaboration_ratio`:
- Query `CodeReview` records for `reviewer_id == developer_id` in the period that have `quality_score IS NOT NULL`
- If reviews exist: compute `quality_multiplier = avg(quality_score) / 5.0` (quality 5 = 1.0x, quality 10 = 2.0x, quality 0 = 0.0x)
- Blend: `final_score = (work_type_based_score * 0.5) + (work_type_based_score * quality_multiplier * 0.5)`
- If no reviews with quality_score: fall back to 100% work_type_based_score (no regression)

Update the single call site in `calculate_developer_score()`:
```python
collaboration_score = self._calculate_collaboration_score(
    activities, developer_id, start_date, end_date
)
```

---

## Migration Order
1. `add_organization_id_to_users` — ALTER TABLE users ADD COLUMN organization_id
2. `add_work_activity_unique_constraint` — DELETE duplicates, then ADD CONSTRAINT
3. `add_slack_models` — CREATE TABLE slack_messages, CREATE TABLE slack_reactions

---

## Files Changed (complete)
| File | Change |
|------|--------|
| `app/models/user.py` | Add organization_id FK column |
| `app/models/slack_activity.py` | **New** — SlackMessage + SlackReaction |
| `app/models/__init__.py` | Export SlackMessage, SlackReaction |
| `app/models/work_activity.py` | Add UniqueConstraint uq_work_activity_source |
| `app/api/integrations.py` | Fix 3 hardcoded org_ids; add POST /slack; add SLACK branch to test_integration |
| `app/services/slack_service.py` | **New** |
| `app/services/github_service.py` | Fetch review comment bodies in sync_code_reviews_for_developer |
| `app/services/scoring_service.py` | Update _calculate_collaboration_score signature + quality weighting |
| `app/services/auth_service.py` | Accept optional organization_id in create_user |
| `app/ai/agents/review_quality_analyzer.py` | **New** |
| `app/tasks/sync_tasks.py` | Add SLACK branch to sync_integration_task; add sync_slack_integration helper; add sync_all_slack task |
| `app/tasks/analysis_tasks.py` | Add analyze_code_reviews task; add analyze_slack_messages task; add dedup checks to existing tasks; trigger new tasks from analyze_all_unanalyzed |
| `app/schemas/integration.py` | Add SlackIntegrationCreate |
| `alembic/env.py` | Import SlackMessage, SlackReaction for autogenerate |
| `alembic/versions/` | 3 new migration files |
| `requirements.txt` | Add slack_sdk if missing |
