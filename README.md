# DevMetrics AI

**AI-Powered Engineering Intelligence Platform**

Understand developer productivity beyond lines of code. AI-powered insights that measure real impact, complexity, and collaboration.

## Features

### For Developers
- Personal productivity dashboard with multi-dimensional scoring
- Transparent metrics - see exactly what your manager sees
- Credit for complex work (refactoring, architecture, research)
- AI-generated growth recommendations

### For Managers
- Team overview and individual deep dives
- AI-powered insights and burnout risk detection
- Role-based performance evaluation (intern to principal)
- Workload distribution analysis

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis (for background tasks)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

### Start Background Worker (Optional)

```bash
cd backend
# Linux/Mac:
celery -A app.tasks worker --loglevel=info

# Windows:
celery -A app.tasks worker --loglevel=info --pool=solo
```

## Configuration

### Required Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/devmetrics

# Security
JWT_SECRET=your-secret-key

# AI Provider (choose one)
OPENAI_API_KEY=sk-...
# Or use OpenRouter:
OPENAI_API_BASE=https://openrouter.ai/api/v1

# Optional
REDIS_URL=redis://localhost:6379
ANTHROPIC_API_KEY=...
```

### Integrations

After starting the app:
1. Login as admin
2. Go to Dashboard > Integrations
3. Connect GitHub with a Personal Access Token
4. Connect Jira with API token (optional)

## Tech Stack

**Backend:** FastAPI, PostgreSQL, SQLAlchemy, Celery, LangChain

**Frontend:** Next.js 14, TailwindCSS, TypeScript

**AI:** OpenAI GPT-4o-mini (or Claude via Anthropic)

## API Documentation

When the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT License

---

Built by [Yash Kamthe](https://github.com/yxsh7)
