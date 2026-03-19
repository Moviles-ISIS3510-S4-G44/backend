import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.marketplace_andes_backend.auth.models import UserAuth
from src.marketplace_andes_backend.auth.service import AuthService
from src.marketplace_andes_backend.users.models import User


@pytest.fixture
def registered_user(session: Session) -> User:
    return AuthService(session).signup(
        name="John Doe",
        email="john@example.com",
        password="secret123",
    )


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )

    assert response.status_code == 200
    return response.json()["access_token"]


class TestAuthRoutes:
    def test_signup_success(self, client: TestClient, session: Session):
        response = client.post(
            "/auth/signup",
            json={
                "name": "Alice",
                "email": "alice@example.com",
                "password": "secret123",
            },
        )

        assert response.status_code == 201
        assert response.json() == {
            "id": response.json()["id"],
            "name": "Alice",
            "email": "alice@example.com",
            "rating": 0,
        }

        user = session.exec(select(User).where(User.email == "alice@example.com")).first()
        assert user is not None
        assert response.json()["id"] == str(user.id)

        user_auth = session.exec(select(UserAuth).where(UserAuth.user_id == user.id)).first()
        assert user_auth is not None
        assert user_auth.id == user.id
        assert user_auth.user_id == user.id
        assert user_auth.hashed_password != "secret123"

    def test_signup_duplicate_rejected(self, client: TestClient, registered_user: User):
        response = client.post(
            "/auth/signup",
            json={
                "name": "John Doe",
                "email": registered_user.email,
                "password": "secret123",
            },
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Email already registered"

    def test_login_success(self, client: TestClient, registered_user: User):
        response = client.post(
            "/auth/login",
            data={"username": registered_user.email, "password": "secret123"},
        )

        assert response.status_code == 200
        assert response.json()["token_type"] == "bearer"
        assert response.json()["access_token"]

    def test_login_invalid_password_rejected(
        self, client: TestClient, registered_user: User
    ):
        response = client.post(
            "/auth/login",
            data={"username": registered_user.email, "password": "wrong-password"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_me_with_valid_token(self, client: TestClient, registered_user: User):
        token = _login(client, registered_user.email, "secret123")

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(registered_user.id),
            "name": registered_user.name,
            "email": registered_user.email,
            "rating": registered_user.rating,
        }

    def test_me_missing_token_rejected(self, client: TestClient):
        response = client.get("/auth/me")

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_me_invalid_token_rejected(self, client: TestClient):
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"
