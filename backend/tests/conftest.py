"""Pytest configuration, test database fixtures, and authenticated client helpers."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.dependencies import create_access_token, get_password_hash
from app.models.users import User
from app.models.creators import CreatorProfile

# In-memory SQLite database for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Provides a transactional database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Provides a TestClient with database dependency overridden."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def brand_user(db_session):
    """Creates and returns a fixture brand user."""
    user = User(
        email="test_brand@maccall.demo",
        password_hash=get_password_hash("password123"),
        full_name="Elena Test Brand",
        role="brand",
        location="Paris",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def creator_user(db_session):
    """Creates and returns a fixture creator user and profile."""
    user = User(
        email="test_creator@maccall.demo",
        password_hash=get_password_hash("password123"),
        full_name="Aarav Test Creator",
        role="creator",
        location="Milan",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = CreatorProfile(
        user_id=user.id,
        display_name="Aarav Test Creator",
        tagline="AI Cinema Director",
        specialization="Cinematic Video & Luxury",
        skills=["Visual Direction", "Prompt Engineering"],
        ai_tools=["Runway Gen-3", "Midjourney v6", "ComfyUI"],
        starting_rate=800.0,
        delivery_days=5,
        commercial_rights=True,
        availability_status="available",
        rating=4.95,
        sla_score=99.0,
        is_verified=True,
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return user


@pytest.fixture
def brand_token(brand_user):
    """Returns a valid JWT token for the fixture brand user."""
    return create_access_token({"sub": str(brand_user.id), "role": brand_user.role})


@pytest.fixture
def creator_token(creator_user):
    """Returns a valid JWT token for the fixture creator user."""
    return create_access_token({"sub": str(creator_user.id), "role": creator_user.role})
