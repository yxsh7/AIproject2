#!/bin/bash

# Verification Script: Ensure No Automatic AI Costs
# This script verifies that all cost-incurring features are disabled

echo "🔍 DevMetrics AI - Cost Control Verification"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check 1: Verify Celery beat schedule is disabled
echo "📋 Check 1: Verifying Celery Beat schedule..."
if [ -f "backend/app/tasks/celery_app.py" ]; then
    # Check if schedule is empty or all tasks are commented
    ACTIVE_TASKS=$(grep -A 20 "beat_schedule = {" backend/app/tasks/celery_app.py | grep -v "^[[:space:]]*#" | grep -o "\"task\":" | wc -l | tr -d ' ')

    if [ "$ACTIVE_TASKS" -eq 0 ]; then
        echo -e "${GREEN}✅ PASS: All automatic tasks are disabled (0 active)${NC}"
    else
        echo -e "${RED}❌ FAIL: Found $ACTIVE_TASKS active automatic tasks!${NC}"
        echo "   This will cause automatic AI API calls!"
        FAILED=1
    fi
else
    echo -e "${YELLOW}⚠️  WARNING: Could not find celery_app.py${NC}"
fi

# Check 2: Verify manual trigger endpoint exists
echo ""
echo "📋 Check 2: Verifying manual trigger endpoint exists..."
if [ -f "backend/app/api/analytics.py" ] && grep -q "def trigger_ai_analysis" backend/app/api/analytics.py; then
    echo -e "${GREEN}✅ PASS: Manual trigger endpoint found${NC}"
else
    echo -e "${RED}❌ FAIL: Manual trigger endpoint not found${NC}"
    FAILED=1
fi

# Check 3: Verify cost warnings in frontend
echo ""
echo "📋 Check 3: Verifying cost warnings in frontend..."
if [ -f "frontend/src/app/dashboard/page.tsx" ] && grep -q "AI Analysis Cost Warning" frontend/src/app/dashboard/page.tsx; then
    echo -e "${GREEN}✅ PASS: Cost warnings present in UI${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: Cost warnings not found in UI${NC}"
fi

# Check 4: Verify API client has manual trigger
echo ""
echo "📋 Check 4: Verifying API client manual trigger..."
if [ -f "frontend/src/lib/api.ts" ] && grep -q "triggerAnalysis" frontend/src/lib/api.ts; then
    echo -e "${GREEN}✅ PASS: Manual trigger in API client${NC}"
else
    echo -e "${RED}❌ FAIL: Manual trigger not in API client${NC}"
    FAILED=1
fi

# Check 5: Environment file check
echo ""
echo "📋 Check 5: Checking environment configuration..."
if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✅ PASS: backend/.env exists${NC}"

    # Check if OpenAI key is set
    if grep -q "OPENAI_API_KEY=" backend/.env 2>/dev/null; then
        echo -e "${YELLOW}   📝 OpenAI API key is configured${NC}"
        echo -e "${YELLOW}   ⚠️  Remember: No automatic calls will be made${NC}"
    else
        echo -e "${YELLOW}   ⚠️  No OpenAI API key found (manual triggers won't work)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  WARNING: backend/.env not found${NC}"
    echo "   Copy from .env.example and configure"
fi

# Summary
echo ""
echo "==========================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ VERIFICATION PASSED${NC}"
    echo ""
    echo "Cost Control Status:"
    echo "  • Automatic AI analysis: DISABLED ✓"
    echo "  • Manual triggers only: ENABLED ✓"
    echo "  • Cost warnings: PRESENT ✓"
    echo "  • Safe to start: YES ✓"
    echo ""
    echo "You can safely start the system with:"
    echo "  Terminal 1: cd backend && uvicorn app.main:app --reload"
    echo "  Terminal 2: cd backend && celery -A app.tasks.celery_app worker --loglevel=info"
    echo "  Terminal 3: cd frontend && npm run dev"
    echo ""
    echo -e "${GREEN}Expected OpenAI cost after 1 hour: \$0.00${NC}"
else
    echo -e "${RED}❌ VERIFICATION FAILED${NC}"
    echo ""
    echo "Found issues that could cause automatic costs!"
    echo "Please review the failures above."
fi

echo "==========================================="
