"""
Fixtures for API tests.

Provides common test fixtures for FastAPI testing, including:
- Test database setup
- Test client
- Authentication fixtures
- Sample data
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fillscheduler.api.database.session import get_db
from fillscheduler.api.main import app
from fillscheduler.api.models.database import Base  # Import Base from models, not session
from fillscheduler.api.models.database import Schedule, User
from fillscheduler.api.utils.security import get_password_hash

# Test database (in-memory SQLite with shared pool)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """
    Create a test database for each test function.

    Yields:
        Session: SQLAlchemy session connected to test database
    """
    # Create test engine with StaticPool to share in-memory database across connections
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Critical: Share the in-memory database
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """
    Create a test client with test database dependency override.

    Args:
        test_db: Test database session

    Yields:
        TestClient: FastAPI test client
    """

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db

    # Disable startup/shutdown events for testing
    app.router.on_startup = []
    app.router.on_shutdown = []

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(test_db):
    """
    Create a test user in the database.

    Args:
        test_db: Test database session

    Returns:
        User: Test user object
    """
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_superuser=False,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_superuser(test_db):
    """
    Create a test superuser in the database.

    Args:
        test_db: Test database session

    Returns:
        User: Test superuser object
    """
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("AdminPassword123!"),
        is_active=True,
        is_superuser=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(client, test_user):
    """
    Get authentication token for test user.

    Args:
        client: Test client
        test_user: Test user

    Returns:
        str: JWT access token
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "TestPassword123!"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """
    Get authentication headers for test requests.

    Args:
        auth_token: JWT access token

    Returns:
        dict: Headers with Authorization
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def sample_lots():
    """
    Sample lots data for testing.

    Returns:
        list: List of lot dictionaries
    """
    return [
        {"lot_id": "LOT001", "lot_type": "TypeA", "vials": 1000, "fill_hours": 2.0},
        {"lot_id": "LOT002", "lot_type": "TypeB", "vials": 1500, "fill_hours": 3.0},
        {"lot_id": "LOT003", "lot_type": "TypeA", "vials": 800, "fill_hours": 1.6},
        {"lot_id": "LOT004", "lot_type": "TypeC", "vials": 1200, "fill_hours": 2.4},
    ]


@pytest.fixture(scope="function")
def sample_schedule(test_db, test_user):
    """
    Create a sample schedule in the database.

    Args:
        test_db: Test database session
        test_user: Test user

    Returns:
        Schedule: Sample schedule object
    """
    from datetime import datetime

    schedule = Schedule(
        user_id=test_user.id,
        name="Test Schedule",
        strategy="smart-pack",
        status="pending",
        config_json="{}",
        created_at=datetime.utcnow(),
    )
    test_db.add(schedule)
    test_db.commit()
    test_db.refresh(schedule)
    return schedule
