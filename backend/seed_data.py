"""
DevMetrics AI - Database Seed Script
=====================================
Creates demo data for local development and testing.
Safe to run multiple times (idempotent).

Usage:
    cd backend
    python seed_data.py
"""

import sys
import os
import random
import string
from datetime import date, datetime, timedelta

# Add the backend directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed; rely on environment variables being set
    pass

from app.database import SessionLocal, Base, engine
from app.models import (
    User,
    Organization,
    DeveloperProfile,
    GitCommit,
    JiraTicket,
    WorkActivity,
    ProductivityScore,
    AIInsight,
    WorkType,
    RoleLevel,
    InsightType,
    InsightPriority,
)
from app.utils.security import get_password_hash


def _random_sha():
    return ''.join(random.choices(string.hexdigits[:16], k=40))


def _random_date(days_back_max: int = 90, days_back_min: int = 0) -> date:
    offset = random.randint(days_back_min, days_back_max)
    return date.today() - timedelta(days=offset)


def _weighted_score(low: int, high: int) -> int:
    return random.randint(low, high)


def seed_organization(db) -> Organization:
    """Create or retrieve demo organization."""
    org = db.query(Organization).filter(Organization.slug == "demo-org").first()
    if org:
        print(f"  Organization already exists: {org.name}")
        return org

    org = Organization(
        name="Demo Engineering",
        slug="demo-org",
        description="Demo organization for DevMetrics AI",
        github_org="demo-engineering",
        jira_workspace="demo.atlassian.net",
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    print(f"  Created organization: {org.name}")
    return org


def seed_user(db, email: str, password: str, full_name: str, role: str) -> User:
    """Create or retrieve a user."""
    user = db.query(User).filter(User.email == email).first()
    if user:
        print(f"  User already exists: {email}")
        return user

    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        role=role,
        is_active=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"  Created user: {email} ({role})")
    return user


def seed_developer_profile(
    db,
    user: User,
    org: Organization,
    role_level: str,
    team: str,
    github_username: str,
    jira_username: str,
    job_title: str,
) -> DeveloperProfile:
    """Create or retrieve a developer profile."""
    profile = (
        db.query(DeveloperProfile)
        .filter(DeveloperProfile.user_id == user.id)
        .first()
    )
    if profile:
        print(f"    Developer profile already exists for: {user.full_name}")
        return profile

    profile = DeveloperProfile(
        user_id=user.id,
        organization_id=org.id,
        role_level=role_level,
        team=team,
        job_title=job_title,
        github_username=github_username,
        jira_username=jira_username,
        focus_areas=["backend", "api"],
        bio=f"Demo developer profile for {user.full_name}",
        start_date=datetime.now() - timedelta(days=random.randint(180, 1000)),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    print(f"    Created developer profile: {user.full_name} ({role_level})")
    return profile


def seed_git_commits(db, developer: DeveloperProfile, count: int = 8):
    """Seed sample git commits for a developer."""
    existing = (
        db.query(GitCommit)
        .filter(GitCommit.developer_id == developer.id)
        .count()
    )
    if existing >= count:
        print(f"    Git commits already exist for developer {developer.id} ({existing} records)")
        return

    repos = ["backend-api", "frontend-app", "data-pipeline", "infra-terraform"]
    messages = [
        "feat: add user authentication endpoint",
        "fix: resolve null pointer exception in payment service",
        "refactor: extract shared utility functions",
        "docs: update API documentation",
        "test: add unit tests for scoring service",
        "perf: optimize database queries with indexes",
        "chore: update dependencies to latest versions",
        "feat: implement dashboard analytics charts",
        "fix: correct calculation in productivity scorer",
        "refactor: improve error handling throughout",
    ]

    to_create = count - existing
    for i in range(to_create):
        sha = _random_sha()
        # Ensure unique sha
        while db.query(GitCommit).filter(GitCommit.commit_sha == sha).first():
            sha = _random_sha()

        commit = GitCommit(
            developer_id=developer.id,
            repo_name=random.choice(repos),
            commit_sha=sha,
            message=random.choice(messages),
            branch=random.choice(["main", "feature/auth", "fix/api", "develop"]),
            files_changed=random.randint(1, 15),
            additions=random.randint(10, 300),
            deletions=random.randint(0, 100),
            committed_at=datetime.combine(_random_date(90, 0), datetime.min.time()),
            analyzed=0,
            analysis_result=None,
        )
        db.add(commit)

    db.commit()
    print(f"    Created {to_create} git commits for developer {developer.id}")


def seed_jira_tickets(db, developer: DeveloperProfile, count: int = 8):
    """Seed sample Jira tickets for a developer."""
    existing = (
        db.query(JiraTicket)
        .filter(JiraTicket.developer_id == developer.id)
        .count()
    )
    if existing >= count:
        print(f"    Jira tickets already exist for developer {developer.id} ({existing} records)")
        return

    ticket_types = ["story", "bug", "task", "research"]
    statuses = ["done", "in_progress", "open"]
    priorities = ["high", "medium", "low"]
    titles = [
        "Implement user profile settings page",
        "Fix login timeout issue",
        "Research GraphQL migration options",
        "Add rate limiting to API endpoints",
        "Optimize slow database queries",
        "Write integration tests for auth module",
        "Design caching strategy for analytics",
        "Fix broken CI/CD pipeline",
        "Implement CSV export feature",
        "Update API documentation",
    ]

    to_create = count - existing
    for i in range(to_create):
        project_prefix = random.choice(["PROJ", "DEV", "INFRA"])
        ticket_num = random.randint(100, 999)
        ticket_key = f"{project_prefix}-{ticket_num}"

        # Avoid duplicate ticket keys
        attempts = 0
        while db.query(JiraTicket).filter(JiraTicket.ticket_key == ticket_key).first():
            ticket_num = random.randint(100, 9999)
            ticket_key = f"{project_prefix}-{ticket_num}"
            attempts += 1
            if attempts > 20:
                break

        created = _random_date(90, 10)
        resolved = created + timedelta(days=random.randint(1, 14)) if random.random() > 0.3 else None

        ticket = JiraTicket(
            developer_id=developer.id,
            ticket_key=ticket_key,
            title=random.choice(titles),
            description="Demo ticket created by seed script.",
            status=random.choice(statuses),
            ticket_type=random.choice(ticket_types),
            priority=random.choice(priorities),
            story_points=random.choice([1, 2, 3, 5, 8]),
            sprint=f"Sprint {random.randint(10, 25)}",
            labels=["backend", "api"],
            created_at=datetime.combine(created, datetime.min.time()),
            resolved_at=datetime.combine(resolved, datetime.min.time()) if resolved else None,
            analyzed=0,
        )
        db.add(ticket)

    db.commit()
    print(f"    Created {to_create} Jira tickets for developer {developer.id}")


def seed_work_activities(db, developer: DeveloperProfile, count: int = 10):
    """Seed work activity records for a developer."""
    existing = (
        db.query(WorkActivity)
        .filter(WorkActivity.developer_id == developer.id)
        .count()
    )
    if existing >= count:
        print(f"    Work activities already exist for developer {developer.id} ({existing} records)")
        return

    work_types = [
        WorkType.CODE, WorkType.CODE_REVIEW, WorkType.BUG_FIX,
        WorkType.REFACTORING, WorkType.DOCUMENTATION, WorkType.RESEARCH,
        WorkType.TESTING, WorkType.MENTORING,
    ]
    sources = ["git", "jira"]

    # Determine score ranges based on role level
    role = developer.role_level
    if role == RoleLevel.JUNIOR:
        complexity_range = (3, 6)
        impact_range = (3, 6)
        quality_range = (5, 8)
    elif role == RoleLevel.MID:
        complexity_range = (4, 7)
        impact_range = (4, 7)
        quality_range = (5, 9)
    elif role == RoleLevel.SENIOR:
        complexity_range = (6, 10)
        impact_range = (6, 10)
        quality_range = (6, 10)
    else:
        complexity_range = (4, 8)
        impact_range = (4, 8)
        quality_range = (5, 9)

    to_create = count - existing
    for i in range(to_create):
        activity_date = _random_date(90, 0)
        work_type = random.choice(work_types)
        source = random.choice(sources)

        activity = WorkActivity(
            developer_id=developer.id,
            activity_date=activity_date,
            work_type=work_type,
            complexity_score=_weighted_score(*complexity_range),
            impact_score=_weighted_score(*impact_range),
            quality_score=_weighted_score(*quality_range),
            time_estimate_hours=random.choice([1, 2, 4, 8, 16]),
            source_type=source,
            source_id=f"{source}-{random.randint(1000, 9999)}",
            ai_analysis={
                "summary": f"Worked on {work_type.value} tasks",
                "explanation": "Demo activity created by seed script",
                "tags": ["demo", work_type.value],
                "affected_systems": ["api", "database"],
            },
            artifacts=None,
        )
        db.add(activity)

    db.commit()
    print(f"    Created {to_create} work activities for developer {developer.id}")


def seed_productivity_scores(db, developer: DeveloperProfile, months: int = 3):
    """Seed historical productivity scores for a developer."""
    existing = (
        db.query(ProductivityScore)
        .filter(ProductivityScore.developer_id == developer.id)
        .count()
    )
    if existing >= months:
        print(f"    Productivity scores already exist for developer {developer.id} ({existing} records)")
        return

    role = developer.role_level
    if role == RoleLevel.JUNIOR:
        base_overall = random.randint(45, 65)
    elif role == RoleLevel.MID:
        base_overall = random.randint(55, 75)
    elif role == RoleLevel.SENIOR:
        base_overall = random.randint(65, 85)
    else:
        base_overall = random.randint(50, 70)

    to_create = months - existing
    for i in range(to_create, 0, -1):
        period_end = date.today() - timedelta(days=30 * (i - 1))
        period_start = period_end - timedelta(days=30)

        # Add slight trend upward
        trend_bonus = (months - i) * 2
        overall = min(100, base_overall + trend_bonus + random.randint(-5, 5))

        score = ProductivityScore(
            developer_id=developer.id,
            period_start=period_start,
            period_end=period_end,
            period_type="monthly",
            overall_score=overall,
            complexity_score=round(random.uniform(4.0, 9.0), 2),
            velocity_score=round(random.uniform(4.0, 9.0), 2),
            quality_score=round(random.uniform(5.0, 9.5), 2),
            impact_score=round(random.uniform(4.0, 9.0), 2),
            collaboration_score=round(random.uniform(3.0, 8.5), 2),
            mentoring_score=round(random.uniform(2.0, 8.0), 2),
            breakdown={
                "total_activities": random.randint(20, 60),
                "work_type_distribution": {
                    "code": 50,
                    "code_review": 20,
                    "documentation": 15,
                    "research": 15,
                },
            },
            work_breakdown={
                "code": round(random.uniform(40, 60), 1),
                "code_review": round(random.uniform(10, 25), 1),
                "documentation": round(random.uniform(5, 20), 1),
                "research": round(random.uniform(5, 15), 1),
            },
            total_commits=random.randint(10, 40),
            total_prs=random.randint(2, 10),
            total_tickets=random.randint(5, 20),
            lines_added=random.randint(200, 2000),
            lines_deleted=random.randint(50, 500),
            score_metadata={
                "role_level": role.value,
                "activity_count": random.randint(20, 60),
                "days_active": random.randint(15, 22),
            },
        )
        db.add(score)

    db.commit()
    print(f"    Created {to_create} productivity scores for developer {developer.id}")


def seed_ai_insights(db, developer: DeveloperProfile, org: Organization, count: int = 3):
    """Seed AI insight records for a developer."""
    existing = (
        db.query(AIInsight)
        .filter(AIInsight.developer_id == developer.id)
        .count()
    )
    if existing >= count:
        print(f"    AI insights already exist for developer {developer.id} ({existing} records)")
        return

    insight_templates = [
        {
            "insight_type": InsightType.RECOMMENDATION,
            "priority": InsightPriority.MEDIUM,
            "title": "Increase Code Review Participation",
            "description": "Participating in more code reviews will improve code quality and team collaboration.",
            "action_items": [
                {"action": "Review at least 2 PRs per week", "assignee": "developer"},
                {"action": "Provide constructive feedback on code style", "assignee": "developer"},
            ],
            "supporting_data": {
                "confidence": 0.85,
                "current_review_rate": "5%",
                "target_rate": "20%",
                "period_start": str(date.today() - timedelta(days=30)),
                "period_end": str(date.today()),
            },
        },
        {
            "insight_type": InsightType.INDIVIDUAL,
            "priority": InsightPriority.LOW,
            "title": "Strong Code Quality Trend",
            "description": "Quality scores have been consistently high over the past month, indicating excellent development practices.",
            "action_items": [
                {"action": "Document best practices to share with team", "assignee": "developer"},
            ],
            "supporting_data": {
                "confidence": 0.9,
                "avg_quality_score": 8.2,
                "trend": "stable",
                "period_start": str(date.today() - timedelta(days=30)),
                "period_end": str(date.today()),
            },
        },
        {
            "insight_type": InsightType.TREND,
            "priority": InsightPriority.HIGH,
            "title": "Productivity Improving",
            "description": "Productivity has increased by 12 points over the past 3 months, showing consistent growth.",
            "action_items": [
                {"action": "Continue current development practices", "assignee": "developer"},
                {"action": "Consider taking on more complex tasks", "assignee": "manager"},
            ],
            "supporting_data": {
                "confidence": 0.88,
                "improvement_points": 12,
                "average_score": 72.5,
                "period_start": str(date.today() - timedelta(days=90)),
                "period_end": str(date.today()),
            },
        },
    ]

    to_create = count - existing
    for template in insight_templates[:to_create]:
        insight = AIInsight(
            organization_id=org.id,
            developer_id=developer.id,
            insight_type=template["insight_type"],
            priority=template["priority"],
            title=template["title"],
            description=template["description"],
            action_items=template["action_items"],
            supporting_data=template["supporting_data"],
            acknowledged=0,
        )
        db.add(insight)

    db.commit()
    print(f"    Created {to_create} AI insights for developer {developer.id}")


def main():
    print("\n" + "=" * 60)
    print("DevMetrics AI - Database Seed Script")
    print("=" * 60)

    # Initialize database tables
    print("\n[1/7] Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("  Database tables ready.")

    db = SessionLocal()

    try:
        # Step 1: Organization
        print("\n[2/7] Seeding organization...")
        org = seed_organization(db)

        # Step 2: Users
        print("\n[3/7] Seeding users...")

        admin_user = seed_user(
            db,
            email="admin@devmetrics.ai",
            password="admin123",
            full_name="Admin User",
            role="admin",
        )

        manager_user = seed_user(
            db,
            email="manager@devmetrics.ai",
            password="Manager123!",
            full_name="Sarah Manager",
            role="manager",
        )

        seed_user(
            db,
            email="demo@devmetrics.ai",
            password="demo",
            full_name="Demo User",
            role="manager",
        )

        junior_user = seed_user(
            db,
            email="junior@devmetrics.ai",
            password="Dev123!",
            full_name="Alex Junior",
            role="developer",
        )

        mid_user = seed_user(
            db,
            email="dev@devmetrics.ai",
            password="Dev123!",
            full_name="Jordan Developer",
            role="developer",
        )

        senior_user = seed_user(
            db,
            email="senior@devmetrics.ai",
            password="Dev123!",
            full_name="Casey Senior",
            role="developer",
        )

        # Step 3: Developer profiles
        print("\n[4/7] Seeding developer profiles...")

        junior_dev = seed_developer_profile(
            db, junior_user, org,
            role_level=RoleLevel.JUNIOR.value,
            team="backend",
            github_username="alex-junior",
            jira_username="alex.junior",
            job_title="Junior Software Engineer",
        )

        mid_dev = seed_developer_profile(
            db, mid_user, org,
            role_level=RoleLevel.MID.value,
            team="backend",
            github_username="jordan-dev",
            jira_username="jordan.developer",
            job_title="Software Engineer",
        )

        senior_dev = seed_developer_profile(
            db, senior_user, org,
            role_level=RoleLevel.SENIOR.value,
            team="backend",
            github_username="casey-senior",
            jira_username="casey.senior",
            job_title="Senior Software Engineer",
        )

        # Also create a developer profile for manager (optional, so they can view their own dashboard)
        manager_dev = seed_developer_profile(
            db, manager_user, org,
            role_level=RoleLevel.SENIOR.value,
            team="backend",
            github_username="sarah-manager",
            jira_username="sarah.manager",
            job_title="Engineering Manager",
        )

        all_devs = [junior_dev, mid_dev, senior_dev, manager_dev]

        # Step 4: Git commits
        print("\n[5/7] Seeding git commits...")
        for dev in all_devs:
            seed_git_commits(db, dev, count=random.randint(7, 12))

        # Step 5: Jira tickets
        print("\n    Seeding Jira tickets...")
        for dev in all_devs:
            seed_jira_tickets(db, dev, count=random.randint(7, 12))

        # Step 6: Work activities
        print("\n[6/7] Seeding work activities...")
        for dev in all_devs:
            seed_work_activities(db, dev, count=random.randint(15, 25))

        # Step 7: Productivity scores
        print("\n    Seeding productivity scores...")
        for dev in all_devs:
            seed_productivity_scores(db, dev, months=3)

        # Step 8: AI Insights
        print("\n[7/7] Seeding AI insights...")
        for dev in all_devs:
            seed_ai_insights(db, dev, org, count=3)

        print("\n" + "=" * 60)
        print("Seeding complete!")
        print("=" * 60)
        print("\nDemo accounts:")
        print("  Demo:     demo@devmetrics.ai      / demo")
        print("  Admin:    admin@devmetrics.ai     / admin123")
        print("  Manager:  manager@devmetrics.ai   / Manager123!")
        print("  Senior:   senior@devmetrics.ai    / Dev123!")
        print("  Mid:      dev@devmetrics.ai        / Dev123!")
        print("  Junior:   junior@devmetrics.ai    / Dev123!")
        print("\nStart the backend: uvicorn app.main:app --reload")
        print("Start the frontend: cd ../frontend && npm run dev")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
