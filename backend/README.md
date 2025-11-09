# DevMetrics AI - Backend

FastAPI backend for the DevMetrics AI engineering intelligence platform.

## Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16+ (via Docker)
- Redis 7+ (via Docker)

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Verify services are running
docker-compose ps

# Create .env file
cp .env.example .env

# Edit .env and add your API keys:
# - ANTHROPIC_API_KEY
# - OPENAI_API_KEY
# - JWT_SECRET_KEY (generate with: openssl rand -hex 32)
# - ENCRYPTION_KEY (generate with: openssl rand -hex 32)
```

### 3. Run Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial schema"

# Run migrations
alembic upgrade head
```

### 4. Run Development Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 5. Run Celery Worker (for background tasks)

```bash
# In a separate terminal
celery -A app.tasks worker --loglevel=info
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   │
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── developer.py
│   │   ├── integration.py
│   │   ├── git_activity.py
│   │   ├── jira_activity.py
│   │   ├── work_activity.py
│   │   └── productivity.py
│   │
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   ├── services/            # Business logic
│   ├── ai/                  # AI agents
│   ├── tasks/               # Celery tasks
│   └── utils/               # Utilities
│
├── alembic/                 # Database migrations
├── tests/                   # Tests
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Developers
- `GET /api/developers` - List developers
- `POST /api/developers` - Create developer profile
- `GET /api/developers/:id` - Get developer details
- `PATCH /api/developers/:id` - Update developer

### Analytics
- `GET /api/analytics/team` - Team analytics
- `GET /api/analytics/developer/:id` - Developer analytics
- `GET /api/analytics/developer/:id/timeline` - Work timeline

### Integrations
- `POST /api/integrations/github` - Configure GitHub
- `POST /api/integrations/jira` - Configure Jira
- `POST /api/integrations/:id/sync` - Trigger sync

### Insights
- `GET /api/insights/team` - Team insights
- `GET /api/insights/developer/:id` - Developer insights

## Database Schema

See `IMPLEMENTATION_PLAN.md` for complete schema documentation.

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code
black app/

# Lint code
ruff check app/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Environment Variables

See `.env.example` for all available configuration options.

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# View PostgreSQL logs
docker-compose logs postgres

# Restart services
docker-compose restart
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

## Next Steps

1. ✅ Database models created
2. ⏳ Create API routes
3. ⏳ Implement GitHub integration
4. ⏳ Implement Jira integration
5. ⏳ Build AI analysis agents
6. ⏳ Add authentication
7. ⏳ Add tests
