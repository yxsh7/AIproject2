# DevMetrics AI

**AI-Powered Engineering Intelligence Platform**

An intelligent productivity analytics platform that understands the complexity of engineering work. Not just lines of code, but real impact.

## 🎯 What is DevMetrics AI?

DevMetrics AI analyzes developer contributions across GitHub/Bitbucket and Jira using AI to provide intelligent insights on:
- **Code complexity** - Not just LOC, but actual cognitive complexity
- **Work type classification** - Automatically understands research, documentation, coding, etc.
- **Multi-dimensional scoring** - Role-based evaluation across quality, impact, and collaboration
- **AI-generated insights** - Actionable recommendations for managers and developers

## 🚀 Key Features

### For Developers
- 📊 Personal productivity dashboard
- 📈 Multi-dimensional score breakdown
- 📅 Work timeline and contribution history
- 🎯 Transparent metrics (see what your manager sees)
- 🏆 Credit for complex work (refactoring, architecture, research)

### For Managers
- 👥 Team overview and individual deep dives
- 🔍 AI-powered insights and alerts
- 📊 Workload distribution analysis
- 🎯 Role-based performance evaluation
- 🚨 Burnout risk detection

### For Organizations
- 📈 Engineering efficiency metrics
- 🎓 Skill gap analysis
- 🔄 Continuous improvement insights
- 📋 Data-driven performance reviews

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL + SQLAlchemy
- Redis + Celery
- LangChain + Claude API + OpenAI API
- PyGithub, Atlassian API

**Frontend:**
- Next.js 14 (App Router)
- TailwindCSS + shadcn/ui
- Framer Motion
- Recharts
- Zustand + SWR

**AI/ML:**
- Claude API (Anthropic) - Code analysis
- OpenAI API - Complementary analysis
- LangChain - Agent orchestration
- Custom complexity analysis

## 📁 Project Structure

```
devmetrics-ai/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic
│   │   ├── ai/             # AI agents
│   │   └── tasks/          # Celery tasks
│   └── requirements.txt
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities
│   │   └── store/         # State management
│   └── package.json
│
├── IMPLEMENTATION_PLAN.md  # Detailed technical plan
├── PROGRESS.md            # Current progress tracker
└── README.md              # This file
```

## 🚦 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- GitHub account (for integration)
- Jira account (for integration)
- Anthropic API key
- OpenAI API key (optional)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AIproject2
```

### 2. Backend Setup

```bash
cd backend

# Start PostgreSQL and Redis
docker-compose up -d

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

### 4. Start Celery Worker (Background Tasks)

```bash
cd backend
celery -A app.tasks worker --loglevel=info
```

## 📖 Documentation

- **[Implementation Plan](IMPLEMENTATION_PLAN.md)** - Detailed technical architecture and plan
- **[Progress Tracker](PROGRESS.md)** - Current implementation status
- **[Backend README](backend/README.md)** - Backend-specific setup and docs
- **API Docs** - Available at http://localhost:8000/docs when backend is running

## 🎯 Current Status

**Phase 1: Foundation** ✅
- [x] Project structure
- [x] Database models
- [x] Basic backend setup
- [x] Basic frontend setup

**Phase 2: Core Features** 🚧 In Progress
- [ ] GitHub integration
- [ ] Jira integration
- [ ] AI analysis agents
- [ ] API endpoints
- [ ] Authentication

**Phase 3: Dashboards** 📋 Planned
- [ ] Developer dashboard
- [ ] Manager dashboard
- [ ] Admin panel

**Phase 4: Intelligence** 📋 Planned
- [ ] Insight generation
- [ ] Trend analysis
- [ ] Recommendations

See [PROGRESS.md](PROGRESS.md) for detailed status.

## 🔐 Security & Privacy

- **Transparent**: Developers see exactly what managers see
- **Secure**: Encrypted API tokens, JWT authentication
- **Privacy-focused**: No real-time surveillance, aggregate weekly/monthly reports
- **Developer-first**: Tool for growth, not punishment

## 🎨 Design Principles

1. **Multi-dimensional scoring** - No single metric defines productivity
2. **Role-based evaluation** - Fair comparison across experience levels
3. **AI explanations** - Every score has reasoning
4. **Capture all work** - Code, research, documentation, mentoring
5. **Context-aware** - Understands sprint goals, team dynamics

## 🤝 Contributing

This is currently a personal project/portfolio piece. See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for the development roadmap.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Anthropic Claude** - For excellent code understanding
- **LangChain** - For agent orchestration
- **FastAPI** - For amazing Python web framework
- **Next.js** - For great React framework
- **shadcn/ui** - For beautiful UI components

---

**Built by [Yash Kamthe](https://github.com/yxsh7)** | [LinkedIn](https://linkedin.com/in/yashkamthe)

*An AI Engineering Portfolio Project showcasing LLM orchestration, multi-agent systems, and full-stack development*
