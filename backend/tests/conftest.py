"""Shared fixtures for the test suite.

Uses an in-memory SQLite database so tests run without a live Postgres instance.
Each test gets a fresh database via function-scoped fixtures.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.models.developer import DeveloperProfile, RoleLevel
from app.models.work_activity import WorkActivity, WorkType
from app.utils.security import get_password_hash, create_access_token


# ─── Database ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def engine():
    # StaticPool forces all connections to share the same underlying SQLite
    # connection, so in-memory data is visible across threads (required for
    # FastAPI TestClient which runs the ASGI app in a worker thread).
    e = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(e)
    yield e
    Base.metadata.drop_all(e)


@pytest.fixture(scope="function")
def db(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db):
    def _override():
        yield db

    app.dependency_overrides[get_db] = _override
    # Deliberately NOT entered as a context manager: `with TestClient(app) as c:`
    # would run the app's lifespan startup, which calls init_db() against the
    # real DATABASE_URL engine (Postgres) rather than this test's in-memory
    # SQLite session — and fails outright if Postgres isn't running locally.
    # Every request handler gets its DB session via the get_db override above,
    # so the real engine is never touched by anything the tests actually exercise.
    c = TestClient(app, raise_server_exceptions=True)
    yield c
    app.dependency_overrides.clear()


# ─── Seed helpers ─────────────────────────────────────────────────────────────

@pytest.fixture
def org(db):
    o = Organization(name="Test Org", slug="test-org")
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


@pytest.fixture
def org2(db):
    """A second organization, for cross-tenant isolation tests. Deliberately uses
    the same team name ("backend") as `org`'s developers, to prove team-scoped
    queries don't blend across organizations."""
    o = Organization(name="Other Org", slug="other-org")
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


@pytest.fixture
def org2_manager_user(db, org2):
    u = User(
        email="manager@other-org.com",
        hashed_password=get_password_hash("password"),
        full_name="Other Org Manager",
        role=UserRole.MANAGER,
        is_active=True,
        organization_id=org2.id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def org2_developer_user(db, org2):
    u = User(
        email="dev@other-org.com",
        hashed_password=get_password_hash("password"),
        full_name="Other Org Developer",
        role=UserRole.DEVELOPER,
        is_active=True,
        organization_id=org2.id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def org2_developer_profile(db, org2_developer_user, org2):
    p = DeveloperProfile(
        user_id=org2_developer_user.id,
        organization_id=org2.id,
        role_level=RoleLevel.MID,
        team="backend",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def manager_user(db, org):
    u = User(
        email="manager@test.com",
        hashed_password=get_password_hash("password"),
        full_name="Test Manager",
        role=UserRole.MANAGER,
        is_active=True,
        organization_id=org.id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def developer_user(db, org):
    u = User(
        email="dev@test.com",
        hashed_password=get_password_hash("password"),
        full_name="Test Developer",
        role=UserRole.DEVELOPER,
        is_active=True,
        organization_id=org.id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def other_developer_user(db, org):
    u = User(
        email="other@test.com",
        hashed_password=get_password_hash("password"),
        full_name="Other Developer",
        role=UserRole.DEVELOPER,
        is_active=True,
        organization_id=org.id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def developer_profile(db, developer_user, org):
    p = DeveloperProfile(
        user_id=developer_user.id,
        organization_id=org.id,
        role_level=RoleLevel.MID,
        team="backend",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def other_developer_profile(db, other_developer_user, org):
    p = DeveloperProfile(
        user_id=other_developer_user.id,
        organization_id=org.id,
        role_level=RoleLevel.JUNIOR,
        team="backend",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def work_activities(db, developer_profile):
    """10 code activities spread over the last 10 days."""
    today = date.today()
    activities = []
    for i in range(10):
        a = WorkActivity(
            developer_id=developer_profile.id,
            organization_id=developer_profile.organization_id,
            source_type="git",
            source_id=f"commit-{i}",
            work_type=WorkType.CODE,
            activity_date=today - timedelta(days=i),
            complexity_score=6,
            impact_score=5,
            quality_score=7,
            ai_analysis={"summary": f"commit {i}"},
        )
        activities.append(a)
        db.add(a)
    db.commit()
    return activities


# ─── Auth helper ──────────────────────────────────────────────────────────────

def auth_header(user: User) -> dict:
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
    )
    return {"Authorization": f"Bearer {token}"}
