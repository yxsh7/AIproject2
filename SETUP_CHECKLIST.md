# Setup Checklist - Quick Reference

Use this checklist to quickly set up DevMetrics AI locally.

---

## ⚡ Quick Setup (Copy-Paste Commands)

### 1️⃣ Prerequisites Check
```bash
# Verify all required software is installed
python --version      # Need 3.11+
node --version        # Need 18+
psql --version        # Need 14+
redis-cli --version   # Need 6+
git --version         # Any recent version
```
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL 14+ installed
- [ ] Redis 6+ installed
- [ ] Git installed

---

### 2️⃣ Clone Repository
```bash
git clone https://github.com/yxsh7/AIproject2.git
cd AIproject2
git checkout claude/ai-portfolio-ideation-011CUwstdoUF89cD23GYrcJi
```
- [ ] Repository cloned
- [ ] Branch checked out

---

### 3️⃣ Start Services
```bash
# Start PostgreSQL
# macOS: brew services start postgresql@14
# Linux: sudo systemctl start postgresql
# Windows: Start from Services app

# Start Redis
# macOS: brew services start redis
# Linux: sudo systemctl start redis
# Windows: redis-server
```
- [ ] PostgreSQL running
- [ ] Redis running

---

### 4️⃣ Create Database
```bash
# Connect to PostgreSQL
psql postgres  # or: sudo -u postgres psql

# Run these SQL commands:
```
```sql
CREATE DATABASE devmetrics_ai;
CREATE USER devmetrics_user WITH PASSWORD 'devmetrics_password_2024';
GRANT ALL PRIVILEGES ON DATABASE devmetrics_ai TO devmetrics_user;
\q
```
- [ ] Database created
- [ ] User created
- [ ] Privileges granted

---

### 5️⃣ Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..
```
- [ ] Virtual environment created
- [ ] Dependencies installed

---

### 6️⃣ Configure Backend Environment
```bash
# Create backend/.env with these variables:
```
```bash
DATABASE_URL=postgresql://devmetrics_user:devmetrics_password_2024@localhost:5432/devmetrics_ai
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-change-this-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GITHUB_TOKEN=ghp_your-github-token-here
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-token-here
ENVIRONMENT=development
```
- [ ] backend/.env file created
- [ ] OpenAI API key added (get from https://platform.openai.com/api-keys)
- [ ] Other optional keys added

---

### 7️⃣ Run Database Migrations
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
alembic upgrade head
cd ..
```
- [ ] Migrations completed successfully

---

### 8️⃣ Frontend Setup
```bash
cd frontend
npm install
cd ..
```
- [ ] Frontend dependencies installed

---

### 9️⃣ Configure Frontend Environment
```bash
# Create frontend/.env.local with:
```
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```
- [ ] frontend/.env.local file created

---

### 🔟 Start All Services (4 Terminals)

**Terminal 1 - Backend API:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- [ ] Backend running on http://localhost:8000

**Terminal 2 - Celery Worker:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
celery -A app.tasks.celery_app worker --loglevel=info
```
- [ ] Celery worker running

**Terminal 3 - Celery Beat (Optional):**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
celery -A app.tasks.celery_app beat --loglevel=info
```
- [ ] Celery beat running (optional - all tasks disabled)

**Terminal 4 - Frontend:**
```bash
cd frontend
npm run dev
```
- [ ] Frontend running on http://localhost:3000

---

### 1️⃣1️⃣ Verify Setup

```bash
# Check backend health
curl http://localhost:8000/health

# Run cost verification
chmod +x verify_no_ai_costs.sh
./verify_no_ai_costs.sh

# Open browser tests
# - http://localhost:8000/docs (API docs)
# - http://localhost:3000 (Frontend)
```
- [ ] Backend health check passes
- [ ] Cost verification passes (all 5 checks)
- [ ] API docs accessible
- [ ] Frontend accessible

---

### 1️⃣2️⃣ Create First User

Go to http://localhost:8000/docs, find `POST /api/auth/register`, and register:
```json
{
  "email": "admin@devmetrics.ai",
  "password": "Admin@123456",
  "full_name": "Admin User",
  "role": "admin"
}
```
- [ ] First user created
- [ ] Can login at http://localhost:3000

---

## ✅ Success Criteria

You should have:
- [x] All services running (PostgreSQL, Redis, Backend, Celery, Frontend)
- [x] Can access API docs: http://localhost:8000/docs
- [x] Can access frontend: http://localhost:3000
- [x] Can register and login
- [x] Cost verification passes
- [x] Dashboard loads (shows "No data" initially - this is expected)

---

## 🚨 Quick Troubleshooting

**Backend won't start?**
```bash
# Check database connection
psql -U devmetrics_user -d devmetrics_ai -h localhost

# Check Redis
redis-cli ping  # Should return PONG

# Check .env exists
ls -la backend/.env
```

**Frontend won't start?**
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check .env.local
ls -la .env.local
```

**Migrations fail?**
```bash
# Check database is running and accessible
psql -U devmetrics_user -d devmetrics_ai -h localhost

# Try resetting migrations (CAUTION: deletes all data)
cd backend
alembic downgrade base
alembic upgrade head
```

**Celery worker issues?**
```bash
# Check Redis is running
redis-cli ping

# Check worker can import tasks
cd backend
source venv/bin/activate
python -c "from app.tasks.celery_app import celery_app; print('OK')"
```

---

## 📚 Full Documentation

For detailed setup instructions, see:
- `LOCAL_SETUP_GUIDE.md` - Complete setup guide with explanations
- `QUICK_START.md` - 5-minute quick start
- `TESTING_INSTRUCTIONS.md` - How to test the system
- `COST_CONTROL_GUIDE.md` - Monitor and control AI costs

---

## 🎉 Ready!

Once all checkboxes are complete, you're ready to test DevMetrics AI!

**Next Steps:**
1. Login to http://localhost:3000
2. Create a developer profile
3. Add GitHub/Jira integration
4. Sync some data
5. Run manual AI analysis (costs ~$0.01)

**Zero Cost Testing:**
Everything except "Run AI Analysis" button is free. You can test for hours with $0.00 cost!
