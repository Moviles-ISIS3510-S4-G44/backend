from unittest.mock import Mock
from uuid import uuid7

import pytest

from marketplace_andes.auth.exceptions import InvalidCredentialsError
from marketplace_andes.auth.jwt.schemas import TokenConfig
from marketplace_andes.auth.jwt.service import JWTService
from marketplace_andes.auth.service import AuthService


def build_jwt_service() -> JWTService:
    return JWTService(
        TokenConfig(
            jwt_public_key="unused-public-key",
            jwt_secret_key="test-secret-key-with-at-least-32-bytes",
            jwt_algorithm="HS256",
            jwt_access_token_expire_minutes=15,
            jwt_refresh_token_expire_minutes=60,
        )
    )


def test_jwt_access_token_round_trip() -> None:
    jwt_service = build_jwt_service()
    user_id = uuid7()

    token = jwt_service.create_access_token(user_id)

    assert jwt_service.verify_access_token(token) == user_id


def test_jwt_hash_token_is_deterministic() -> None:
    jwt_service = build_jwt_service()
    raw_token = "refresh-token-value"

    first_hash = jwt_service.hash_token(raw_token)
    second_hash = jwt_service.hash_token(raw_token)

    assert first_hash == second_hash
    assert first_hash != raw_token


def test_authenticate_user_rejects_unknown_username() -> None:
    session = Mock()
    jwt_service = Mock()
    password_hasher = Mock()
    auth_repository = Mock()
    auth_session_repository = Mock()
    user_repository = Mock()
    user_repository.get_id_from_username.return_value = None

    service = AuthService(
        session=session,
        jwt_service=jwt_service,
        password_hasher=password_hasher,
        auth_repository=auth_repository,
        auth_session_repository=auth_session_repository,
        user_repository=user_repository,
    )

    with pytest.raises(InvalidCredentialsError):
        service.authenticate_user("missing-user", "secret", "127.0.0.1")

    session.commit.assert_not_called()
    auth_session_repository.create_session.assert_not_called()
    auth_repository.get_hashed_password.assert_not_called()
    password_hasher.verify.assert_not_called()
