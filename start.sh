#!/bin/bash
# DevMetrics AI — one-command launcher

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}${BLUE}  DevMetrics AI${NC}  — Engineering Intelligence Platform"
echo -e "  ${CYAN}───────────────────────────────────────────────${NC}"
echo ""

# ── 1. Infrastructure ────────────────────────────────────────────────────────

echo -e "${BLUE}[1/5]${NC} Starting infrastructure..."

if docker info > /dev/null 2>&1; then
  docker compose -f backend/docker-compose.yml up -d --quiet-pull 2>/dev/null \
    && echo -e "  ${GREEN}✓${NC} Docker services up (postgres + redis)" \
    || echo -e "  ${YELLOW}⚠${NC}  Docker compose failed — falling back to local services"
else
  echo -e "  ${YELLOW}⚠${NC}  Docker not running — checking local services"
fi

# Verify postgres
if pg_isready -q 2>/dev/null; then
  echo -e "  ${GREEN}✓${NC} PostgreSQL reachable"
else
  echo -e "  ${RED}✗${NC} PostgreSQL not reachable — start it or use Docker"
  exit 1
fi

# Verify redis
if redis-cli ping > /dev/null 2>&1; then
  echo -e "  ${GREEN}✓${NC} Redis reachable"
else
  echo -e "  ${RED}✗${NC} Redis not reachable — start it or use Docker"
  exit 1
fi

# ── 2. Environment check ──────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}[2/5]${NC} Checking environment..."

if [ -z "$VIRTUAL_ENV" ]; then
  echo -e "  ${YELLOW}⚠${NC}  No Python venv active (VIRTUAL_ENV not set)"
  echo -e "      Run: ${CYAN}source backend/venv/bin/activate${NC}"
fi

if [ ! -f "backend/.env" ]; then
  echo -e "  ${RED}✗${NC} backend/.env not found"
  echo -e "      Copy: ${CYAN}cp backend/.env.example backend/.env${NC} and fill in your credentials"
  exit 1
fi

echo -e "  ${GREEN}✓${NC} backend/.env present"

# ── 3. Database migration ────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}[3/5]${NC} Running migrations..."

(cd backend && alembic upgrade head) || {
  echo -e "  ${RED}✗${NC} Migration failed"
  exit 1
}
echo -e "  ${GREEN}✓${NC} Database up to date"

# ── 4. Seed if empty ─────────────────────────────────────────────────────────

USER_COUNT=$(cd backend && python -c "
import os, sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, text
engine = create_engine(os.getenv('DATABASE_URL', ''))
with engine.connect() as c:
    print(c.execute(text('SELECT COUNT(*) FROM users')).scalar())
" 2>/dev/null || echo "0")

if [ "$USER_COUNT" = "0" ]; then
  echo -e "  ${YELLOW}→${NC}  No users found — seeding demo data..."
  (cd backend && python seed_data.py) && echo -e "  ${GREEN}✓${NC} Demo data seeded"
else
  echo -e "  ${GREEN}✓${NC} Database has data ($USER_COUNT users)"
fi

# ── 5. Start services ────────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}[4/5]${NC} Starting backend..."
(cd backend && uvicorn app.main:app --reload --port 8000) &
BACKEND_PID=$!
trap "kill $BACKEND_PID 2>/dev/null" EXIT SIGINT SIGTERM

# Wait for backend to be ready
for i in {1..15}; do
  sleep 1
  if curl -s http://localhost:8000/health > /dev/null 2>&1 || \
     curl -s http://localhost:8000/docs  > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Backend ready"
    break
  fi
  if [ $i -eq 15 ]; then
    echo -e "  ${YELLOW}⚠${NC}  Backend taking longer than usual (continuing anyway)"
  fi
done

echo ""
echo -e "${BLUE}[5/5]${NC} Starting frontend..."
echo ""
echo -e "  ${BOLD}────────────────────────────────────────${NC}"
echo -e "  ${GREEN}✓${NC} App:        ${CYAN}http://localhost:3000${NC}"
echo -e "  ${GREEN}✓${NC} API docs:   ${CYAN}http://localhost:8000/docs${NC}"
echo -e ""
echo -e "  ${BOLD}Demo credentials${NC}"
echo -e "  Manager:   ${CYAN}manager@devmetrics.ai${NC} / ${CYAN}Manager123!${NC}"
echo -e "  Developer: ${CYAN}dev1@devmetrics.ai${NC}     / ${CYAN}Dev123!${NC}"
echo -e "  ${BOLD}────────────────────────────────────────${NC}"
echo ""

(cd frontend && npm run dev)
