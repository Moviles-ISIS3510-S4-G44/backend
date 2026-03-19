import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.marketplace_andes_backend.app import app
from src.marketplace_andes_backend.db import get_engine, get_session
from src.marketplace_andes_backend.users.models import User


@pytest.fixture
def session():
    """Create a database session with transaction support for test data setup.

    Uses a savepoint approach to rollback changes after each test while
    keeping the main migration-created schema intact.
    """
    engine = get_engine()
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)
    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(session: Session):
    """Create a test client that uses the test session for dependency injection."""

    def get_test_session():
        yield session

    # Override the get_session dependency to use our test session
    app.dependency_overrides[get_session] = get_test_session

    client = TestClient(app)
    yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(session: Session) -> User:
    """Create a test user in the database."""
    user = User(
        name="John Doe",
        email="john@example.com",
        rating=4,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def test_user_high_rating(session: Session) -> User:
    """Create a test user with high rating."""
    user = User(
        name="Jane Smith",
        email="jane@example.com",
        rating=5,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def test_user_low_rating(session: Session) -> User:
    """Create a test user with low rating."""
    user = User(
        name="Bob Wilson",
        email="bob@example.com",
        rating=0,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


class TestGetUserProfile:
    """Tests for GET /users/profile/{user_id} endpoint."""

    def test_get_existing_user_profile(self, client: TestClient, test_user: User):
        """Test successful retrieval of an existing user profile."""
        response = client.get(f"/users/profile/{test_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert data["rating"] == 4

    def test_get_user_profile_with_high_rating(
        self, client: TestClient, test_user_high_rating: User
    ):
        """Test that profile correctly returns high rating (5)."""
        response = client.get(f"/users/profile/{test_user_high_rating.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 5

    def test_get_user_profile_with_low_rating(
        self, client: TestClient, test_user_low_rating: User
    ):
        """Test that profile correctly returns low rating (0)."""
        response = client.get(f"/users/profile/{test_user_low_rating.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 0

    def test_get_nonexistent_user_profile(self, client: TestClient):
        """Test that requesting a non-existent user returns 404."""
        response = client.get("/users/profile/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_get_user_profile_response_schema(
        self, client: TestClient, test_user: User
    ):
        """Test that the response matches the expected schema with all required fields."""
        response = client.get(f"/users/profile/{test_user.id}")

        assert response.status_code == 200
        data = response.json()

        # Verify all required fields are present
        assert "id" in data
        assert "name" in data
        assert "email" in data
        assert "rating" in data

        # Verify field types
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["email"], str)
        assert isinstance(data["rating"], int)

    def test_get_user_profile_invalid_id_negative(self, client: TestClient):
        """Test that negative user IDs return 404."""
        response = client.get("/users/profile/-1")
        assert response.status_code == 404

    def test_get_user_profile_invalid_id_zero(self, client: TestClient):
        """Test that user ID of 0 returns 404."""
        response = client.get("/users/profile/0")
        assert response.status_code == 404

    @pytest.mark.parametrize("user_id", [99999, 100000, 999999])
    def test_get_user_profile_various_nonexistent_ids(
        self, client: TestClient, user_id: int
    ):
        """Test that various non-existent user IDs return 404."""
        response = client.get(f"/users/profile/{user_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"
