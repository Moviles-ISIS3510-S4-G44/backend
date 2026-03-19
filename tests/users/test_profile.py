import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from uuid import uuid7

from src.marketplace_andes_backend.auth.service import AuthService
from src.marketplace_andes_backend.users.models import User


@pytest.fixture
def auth_headers(session: Session) -> dict[str, str]:
    auth_user = AuthService(session).signup(
        name="Auth User",
        email="auth@example.com",
        password="secret123",
    )
    token = AuthService(session).create_access_token(auth_user)
    return {"Authorization": f"Bearer {token}"}


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

    def test_get_existing_user_profile(
        self, client: TestClient, auth_headers: dict[str, str], test_user: User
    ):
        """Test successful retrieval of an existing user profile."""
        response = client.get(f"/users/profile/{test_user.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert data["rating"] == 4

    def test_get_user_profile_with_high_rating(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        test_user_high_rating: User,
    ):
        """Test that profile correctly returns high rating (5)."""
        response = client.get(
            f"/users/profile/{test_user_high_rating.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 5

    def test_get_user_profile_with_low_rating(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        test_user_low_rating: User,
    ):
        """Test that profile correctly returns low rating (0)."""
        response = client.get(
            f"/users/profile/{test_user_low_rating.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 0

    def test_get_nonexistent_user_profile(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test that requesting a non-existent user returns 404."""
        response = client.get(f"/users/profile/{uuid7()}", headers=auth_headers)

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_get_user_profile_response_schema(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        test_user: User,
    ):
        """Test that the response matches the expected schema with all required fields."""
        response = client.get(f"/users/profile/{test_user.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify all required fields are present
        assert "id" in data
        assert "name" in data
        assert "email" in data
        assert "rating" in data

        # Verify field types
        assert isinstance(data["id"], str)
        assert isinstance(data["name"], str)
        assert isinstance(data["email"], str)
        assert isinstance(data["rating"], int)

    def test_get_user_profile_invalid_id_negative(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test that negative user IDs return 404."""
        response = client.get("/users/profile/not-a-uuid", headers=auth_headers)
        assert response.status_code == 422

    def test_get_user_profile_invalid_id_zero(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test that user ID of 0 returns 404."""
        response = client.get("/users/profile/0", headers=auth_headers)
        assert response.status_code == 422

    def test_get_user_profile_requires_authentication(
        self, client: TestClient, test_user: User
    ):
        response = client.get(f"/users/profile/{test_user.id}")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    @pytest.mark.parametrize("user_id", [str(uuid7()), str(uuid7()), str(uuid7())])
    def test_get_user_profile_various_nonexistent_ids(
        self, client: TestClient, auth_headers: dict[str, str], user_id: str
    ):
        """Test that various non-existent user IDs return 404."""
        response = client.get(f"/users/profile/{user_id}", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"
