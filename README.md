# DevMetrics AI

**AI-Powered Engineering Intelligence Platform**

DevMetrics AI analyzes developer contributions across GitHub, Jira, and Slack using AI to produce multi-dimensional productivity scores — measuring complexity, velocity, quality, impact, collaboration, and mentoring, weighted by role level (junior to principal).

---

## What it does

**For developers:** A personal dashboard showing how their work is scored, what types of work they're spending time on, and AI-generated growth recommendations — all visible to them, not just their manager.

**For managers:** Team overview with individual deep dives, burnout risk detection, workload distribution analysis, and AI-generated insights surfaced from real activity patterns.

**For everyone:** Scores are role-aware (a junior is not evaluated like a senior), complexity-aware (refactoring and architecture count), and transparent (developers see exactly what managers see).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, PostgreSQL, Alembic |
| Background tasks | Celery, Redis |
| AI | OpenRouter (free inference), rule-based fallback |
| Integrations | PyGithub, Atlassian API, slack-sdk |
| Frontend | Next.js 14 (App Router), TypeScript, TailwindCSS |
| Auth | JWT, bcrypt |
| Testing | pytest, SQLite in-memory, FastAPI TestClient |

---

## Architecture highlights

- **Role-weighted scoring** — `ROLE_WEIGHTS` per level drive how complexity, velocity, quality, impact, collaboration, and mentoring are blended into an overall score
- **N+1-free team scoring** — bulk-fetches all developer activities in 2 queries instead of N+1
- **AI with rule-based fallback** — if no API key is configured the system scores everything using heuristics; AI enriches but isn't required
- **Demo mode** — set `DEMO_MODE=true` to serve pre-loaded sample data without requiring real integration credentials

---

## Running locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for PostgreSQL + Redis)

### 1. Start infrastructure

```bash
docker compose -f backend/docker-compose.yml up -d
```

### 2. Backend

```bash
cd backend

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

cp .env.example .env
# Edit .env — set JWT_SECRET_KEY, ENCRYPTION_KEY, and optionally OPENROUTER_API_KEY

alembic upgrade head
python seed_data.py          # loads demo data + accounts

uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### 3. Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
# → http://localhost:3000
```

### 4. Background worker (optional — needed for real sync jobs)

```bash
cd backend
celery -A app.tasks worker --loglevel=info --pool=solo   # Windows
# celery -A app.tasks worker --loglevel=info             # Mac/Linux
```

---

## Demo

The login page has a **Try Demo** button — one click, no setup needed beyond running the seed script. The demo account is a manager with access to the full team view, insights, and individual analytics.

To run in demo mode (disables real sync, uses seed data only):

```env
# backend/.env
DEMO_MODE=true
```

---

## Running tests

```bash
cd backend
pytest tests/ -v
# 64 tests — scoring service (unit + integration) and analytics API endpoints
```

---

## Project structure

```
backend/
  app/
    api/          # FastAPI routers (analytics, auth, integrations, developers)
    models/       # SQLAlchemy models
    schemas/      # Pydantic schemas
    services/     # Business logic (scoring, insights, GitHub, Jira, Slack)
    ai/           # AI agents + base model factory
    tasks/        # Celery background tasks
  alembic/        # Database migrations (001–005)
  tests/          # pytest suite

frontend/
  src/
    app/          # Next.js App Router pages
    components/   # Shared UI components
    lib/          # API client, utilities
    store/        # Zustand auth store
```

---

Built by [Yash Kamthe](https://github.com/yxsh7)
