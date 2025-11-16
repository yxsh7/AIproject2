# Local Setup Guide - DevMetrics AI

Complete guide to clone and run DevMetrics AI on your local machine.

---

## 📋 Prerequisites

Before you start, make sure you have these installed:

### Required Software:
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** and npm - [Download](https://nodejs.org/)
- **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/)
- **Redis 6+** - [Download](https://redis.io/download)
- **Git** - [Download](https://git-scm.com/downloads)

### Verify Installation:
```bash
python --version      # Should be 3.11+
node --version        # Should be 18+
npm --version         # Should be 9+
psql --version        # Should be 14+
redis-cli --version   # Should be 6+
```

---

## 🚀 Step 1: Clone the Repository

```bash
# Clone your repository
git clone https://github.com/yxsh7/AIproject2.git

# Navigate to project directory
cd AIproject2

# Checkout the release branch
git checkout claude/ai-portfolio-ideation-011CUwstdoUF89cD23GYrcJi
```

---

## 🐘 Step 2: Set Up PostgreSQL Database

### Option A: macOS (using Homebrew)
```bash
# Start PostgreSQL
brew services start postgresql@14

# Create database and user
psql postgres
```

### Option B: Linux
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql
```

### Option C: Windows
```bash
# Start PostgreSQL service from Services app
# Then open pgAdmin or use psql
psql -U postgres
```

### Create Database (run in psql):
```sql
-- Create database
CREATE DATABASE devmetrics_ai;

-- Create user
CREATE USER devmetrics_user WITH PASSWORD 'devmetrics_password_2024';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE devmetrics_ai TO devmetrics_user;

-- Exit psql
\q
```

### Verify Database:
```bash
psql -U devmetrics_user -d devmetrics_ai -h localhost
# If you can connect, it's working!
# Type \q to exit
```

---

## 🔴 Step 3: Set Up Redis

### macOS:
```bash
brew services start redis
# Verify
redis-cli ping
# Should respond: PONG
```

### Linux:
```bash
sudo systemctl start redis
# Verify
redis-cli ping
# Should respond: PONG
```

### Windows:
```bash
# Download Redis from https://github.com/microsoftarchive/redis/releases
# Or use WSL for Redis
# Start Redis server
redis-server

# In another terminal, verify:
redis-cli ping
# Should respond: PONG
```

---

## 🐍 Step 4: Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Go back to project root
cd ..
```

---

## ⚙️ Step 5: Configure Environment Variables

### Backend Configuration:

```bash
# Create backend .env file
cat > backend/.env << 'EOF'
# Database
DATABASE_URL=postgresql://devmetrics_user:devmetrics_password_2024@localhost:5432/devmetrics_ai

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI API Keys (You'll need to add your own)
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Integration API Keys (Optional - add when you want to test integrations)
GITHUB_TOKEN=ghp_your_github_token_here
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_api_token_here

# Environment
ENVIRONMENT=development
EOF
```

**⚠️ IMPORTANT: Get Your API Keys**

1. **OpenAI API Key** (Required for AI analysis):
   - Go to https://platform.openai.com/api-keys
   - Create new secret key
   - Replace `sk-your-openai-api-key-here` with your key
   - **Cost:** ~$0.01 per 100 items analyzed (using GPT-4o-mini)

2. **Anthropic API Key** (Optional - alternative to OpenAI):
   - Go to https://console.anthropic.com/
   - Get API key from Account Settings
   - More expensive than OpenAI, only use if needed

3. **GitHub Token** (Optional - needed for GitHub integration):
   - Go to https://github.com/settings/tokens
   - Generate new token (classic)
   - Select scopes: `repo`, `read:user`
   - Replace `ghp_your_github_token_here` with your token

4. **Jira API Token** (Optional - needed for Jira integration):
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Create API token
   - Replace credentials in .env

### Frontend Configuration:

```bash
# Create frontend .env.local file
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

---

## 🗄️ Step 6: Run Database Migrations

```bash
# Make sure you're in project root and backend venv is activated
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run migrations
alembic upgrade head

# You should see output like:
# INFO  [alembic.runtime.migration] Running upgrade ... -> ..., create users table
# INFO  [alembic.runtime.migration] Running upgrade ... -> ..., create developer_profiles table
# etc.
```

---

## 📦 Step 7: Set Up Frontend

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Go back to project root
cd ..
```

---

## 🎬 Step 8: Start All Services

You'll need **4 terminal windows/tabs**:

### Terminal 1: Backend API
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Terminal 2: Celery Worker
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
celery -A app.tasks.celery_app worker --loglevel=info
```
**Expected output:**
```
-------------- celery@hostname v5.x.x
---- **** -----
--- * ***  * -- [Configuration]
-- * - **** ---
- ** ---------- .> app:         devmetrics_ai
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 8
-- ******* ----
--- ***** ----- [Queues]
 -------------- .> celery
```

### Terminal 3: Celery Beat (Optional - currently disabled)
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
celery -A app.tasks.celery_app beat --loglevel=info
```
**Note:** All automatic tasks are disabled, so this won't schedule anything. You can skip this if you want.

### Terminal 4: Frontend
```bash
cd frontend
npm run dev
```
**Expected output:**
```
   ▲ Next.js 14.x.x
   - Local:        http://localhost:3000
   - Ready in 2.5s
```

---

## ✅ Step 9: Verify Everything is Working

### 1. Check Backend Health:
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status":"healthy"}`

### 2. Check Backend API Docs:
Open browser: http://localhost:8000/docs
**Expected:** Interactive API documentation (Swagger UI)

### 3. Check Frontend:
Open browser: http://localhost:3000
**Expected:** Login page

### 4. Run Cost Verification:
```bash
# In project root
chmod +x verify_no_ai_costs.sh
./verify_no_ai_costs.sh
```
**Expected:** All checks should PASS

---

## 👤 Step 10: Create Your First User

### Option A: Using API Docs (Recommended)

1. Go to http://localhost:8000/docs
2. Find `POST /api/auth/register`
3. Click "Try it out"
4. Enter:
```json
{
  "email": "admin@devmetrics.ai",
  "password": "Admin@123456",
  "full_name": "Admin User",
  "role": "admin"
}
```
5. Click "Execute"
6. You should get a response with user details and access token

### Option B: Using curl

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@devmetrics.ai",
    "password": "Admin@123456",
    "full_name": "Admin User",
    "role": "admin"
  }'
```

---

## 🎯 Step 11: Login and Test

1. **Go to Frontend:** http://localhost:3000
2. **Login with:**
   - Email: `admin@devmetrics.ai`
   - Password: `Admin@123456`
3. **You should see:** Developer Dashboard
4. **Initial state:** "No data available yet" (this is expected)

---

## 🧪 Step 12: Test the System (Zero Cost Testing)

Follow the comprehensive testing guide:

```bash
cat TESTING_INSTRUCTIONS.md
```

**Quick Test Checklist:**

- [ ] ✅ Backend API running (http://localhost:8000/docs)
- [ ] ✅ Frontend running (http://localhost:3000)
- [ ] ✅ Celery worker running (check Terminal 2)
- [ ] ✅ Can register new user
- [ ] ✅ Can login successfully
- [ ] ✅ Dashboard loads without errors
- [ ] ✅ Cost verification script passes
- [ ] ✅ No automatic AI costs (check OpenAI dashboard)

---

## 🤖 Step 13: Optional - Test AI Analysis (Small Cost)

**⚠️ This will cost ~$0.01 per 100 items analyzed**

1. **Create Developer Profile:**
   - Go to http://localhost:8000/docs
   - Use `POST /api/developers/` endpoint
   - Create a profile for your admin user

2. **Add GitHub/Jira Integration:**
   - Use `POST /api/integrations/` endpoint
   - Add your GitHub or Jira credentials

3. **Sync Data:**
   - Use `POST /api/integrations/{id}/sync-github` endpoint
   - This fetches commits/PRs (no AI cost)

4. **Trigger AI Analysis:**
   - Login to frontend as manager/admin
   - Click "🤖 Run AI Analysis" button
   - Confirm the cost warning
   - Wait 2-5 minutes
   - Refresh page to see analytics

---

## 🛑 Troubleshooting

### Backend won't start:
```bash
# Check PostgreSQL is running
psql -U devmetrics_user -d devmetrics_ai -h localhost

# Check Redis is running
redis-cli ping

# Check .env file exists
ls -la backend/.env

# Check migrations ran
cd backend
alembic current
```

### Frontend won't start:
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check .env.local exists
ls -la .env.local
```

### Celery worker issues:
```bash
# Check Redis connection
redis-cli ping

# Check Celery can import app
cd backend
source venv/bin/activate
python -c "from app.tasks.celery_app import celery_app; print('OK')"
```

### Database connection errors:
```bash
# Verify PostgreSQL is running
brew services list | grep postgresql   # macOS
sudo systemctl status postgresql       # Linux

# Check if database exists
psql -U devmetrics_user -d devmetrics_ai -h localhost -c "\l"
```

### API Key Issues:
```bash
# Verify OpenAI key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-your-key-here"

# Should return list of models if key is valid
```

---

## 📊 Monitoring Costs

### OpenAI Dashboard:
1. Go to https://platform.openai.com/usage
2. Check daily usage
3. Set up billing alerts

### Expected Costs (with manual triggers only):
- **Automatic/Background:** $0.00 (disabled)
- **Per Manual Analysis:** ~$0.01 per 100 items
- **Monthly (1 dev, daily analysis):** ~$0.30/month
- **Monthly (10 devs, daily analysis):** ~$3.00/month

---

## 🎉 Success!

You should now have:
- ✅ Backend API running on http://localhost:8000
- ✅ Frontend running on http://localhost:3000
- ✅ PostgreSQL database configured
- ✅ Redis running
- ✅ Celery worker processing tasks
- ✅ Zero automatic AI costs verified
- ✅ Ready to test the system!

---

## 📚 Next Steps

1. **Read the documentation:**
   - `QUICK_START.md` - Quick reference
   - `TESTING_INSTRUCTIONS.md` - Detailed testing guide
   - `COST_CONTROL_GUIDE.md` - Monitor and control costs
   - `RELEASE_NOTES.md` - Feature overview

2. **Add your own data:**
   - Configure GitHub token for your repos
   - Configure Jira credentials
   - Sync your actual development data
   - Test AI analysis on real commits

3. **Customize:**
   - Adjust role-based scoring weights
   - Modify complexity scoring thresholds
   - Customize frontend theme
   - Add new analytics metrics

---

## 🆘 Need Help?

- **API Documentation:** http://localhost:8000/docs
- **Check Logs:** Look at terminal outputs for errors
- **Verify Setup:** Run `./verify_no_ai_costs.sh`
- **Database Issues:** Check `backend/alembic/versions/` for migrations

---

## 🔐 Security Notes

**Before deploying to production:**
- [ ] Change `SECRET_KEY` in backend/.env
- [ ] Use strong passwords for database
- [ ] Enable HTTPS
- [ ] Set up proper CORS policies
- [ ] Add rate limiting
- [ ] Review API key permissions
- [ ] Set up monitoring and alerts

---

**Happy Testing! 🚀**

Your DevMetrics AI system is now running locally and ready for development!
