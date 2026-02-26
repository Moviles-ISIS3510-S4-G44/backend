from fastapi.testclient import TestClient


def _register(client: TestClient, email: str = "student@example.com", username: str = "student01"):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "username": username,
            "full_name": "Student User",
            "password": "StrongPassword123!",
        },
    )


def _login(client: TestClient, identifier: str):
    return client.post(
        "/auth/login",
        json={"identifier": identifier, "password": "StrongPassword123!"},
    )


def test_register_creates_user(client: TestClient) -> None:
    response = _register(client)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "student@example.com"
    assert data["username"] == "student01"
    assert "hashed_password" not in data


def test_register_duplicate_user_returns_409(client: TestClient) -> None:
    first = _register(client)
    second = _register(client)

    assert first.status_code == 201
    assert second.status_code == 409


def test_login_with_email_returns_jwt(client: TestClient) -> None:
    _register(client)
    response = _login(client, "student@example.com")

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["expires_in"] > 0


def test_login_with_invalid_credentials_returns_401(client: TestClient) -> None:
    _register(client)
    response = client.post(
        "/auth/login",
        json={"identifier": "student01", "password": "WrongPassword123!"},
    )

    assert response.status_code == 401


def test_me_requires_bearer_token(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_returns_current_user(client: TestClient) -> None:
    _register(client)
    login_response = _login(client, "student01")
    token = login_response.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["username"] == "student01"


def test_refresh_returns_new_access_token(client: TestClient) -> None:
    _register(client)
    login_response = _login(client, "student01")
    token = login_response.json()["access_token"]

    response = client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
