#!/bin/bash

# DevMetrics AI - System Startup Script
# This script starts all services in the correct order with cost monitoring

echo "🚀 DevMetrics AI - Safe Startup (Zero AI Costs)"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

# Check PostgreSQL
if ! pg_isready -q 2>/dev/null; then
    echo -e "${RED}❌ PostgreSQL is not running${NC}"
    echo "Start it with: brew services start postgresql (macOS)"
    echo "Or: sudo systemctl start postgresql (Linux)"
    exit 1
else
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
fi

# Check Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}❌ Redis is not running${NC}"
    echo "Start it with: brew services start redis (macOS)"
    echo "Or: sudo systemctl start redis (Linux)"
    exit 1
else
    echo -e "${GREEN}✅ Redis is running${NC}"
fi

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  backend/.env not found${NC}"
    echo "Creating from .env.example..."
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}⚠️  Please edit backend/.env with your database credentials${NC}"
    exit 1
else
    echo -e "${GREEN}✅ backend/.env exists${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Running database migrations...${NC}"
cd backend
alembic upgrade head
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database migrations complete${NC}"
else
    echo -e "${RED}❌ Database migration failed${NC}"
    exit 1
fi
cd ..

echo ""
echo -e "${BLUE}Step 3: System is ready to start!${NC}"
echo ""
echo "⚠️  IMPORTANT: Cost Control Verification"
echo "=========================================  "
echo ""
echo "1. Celery Beat is DISABLED (no automatic tasks)"
echo "2. All AI analysis is MANUAL only"
echo "3. You control when OpenAI API is called"
echo ""
echo -e "${GREEN}To start the system, run these commands in separate terminals:${NC}"
echo ""
echo -e "${YELLOW}Terminal 1 - Backend API:${NC}"
echo "  cd backend"
echo "  uvicorn app.main:app --reload --port 8000"
echo ""
echo -e "${YELLOW}Terminal 2 - Celery Worker (NO BEAT):${NC}"
echo "  cd backend"
echo "  celery -A app.tasks.celery_app worker --loglevel=info"
echo ""
echo -e "${YELLOW}Terminal 3 - Frontend:${NC}"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo -e "${RED}DO NOT RUN: celery -A app.tasks.celery_app beat${NC}"
echo -e "${RED}(Beat scheduler is disabled to prevent automatic costs)${NC}"
echo ""
echo -e "${BLUE}After starting, verify zero costs:${NC}"
echo "1. Check OpenAI usage: https://platform.openai.com/usage"
echo "2. Watch Celery logs for 'Analyzing' messages (should be NONE)"
echo "3. Wait 10 minutes, check OpenAI usage again (should still be \$0.00)"
echo ""
echo -e "${GREEN}✅ System ready for safe testing!${NC}"
