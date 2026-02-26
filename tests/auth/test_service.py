from datetime import timedelta

import pytest
from fastapi import HTTPException

from backend.auth.schemas import UserCreate
from backend.auth.service import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    hash_password,
    register_user,
    verify_password,
)


def test_hash_password_uses_argon2() -> None:
    raw_password = "StrongPassword123!"

    hashed = hash_password(raw_password)

    assert hashed.startswith("$argon2")
    assert verify_password(raw_password, hashed)


def test_create_and_decode_access_token_round_trip() -> None:
    token = create_access_token("42", expires_delta=timedelta(minutes=5))

    payload = decode_access_token(token)

    assert payload.sub == "42"


def test_decode_invalid_token_raises_http_401() -> None:
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("not-a-valid-token")

    assert exc_info.value.status_code == 401


def test_register_user_hashes_password(db_session) -> None:
    payload = UserCreate(
        email="seller@example.com",
        username="seller_01",
        full_name="Seller Student",
        password="StrongPassword123!",
    )

    user = register_user(db_session, payload)

    assert user.id is not None
    assert user.hashed_password != payload.password
    assert user.hashed_password.startswith("$argon2")
    assert verify_password(payload.password, user.hashed_password)


def test_authenticate_user_by_email_or_username(db_session) -> None:
    payload = UserCreate(
        email="buyer@example.com",
        username="buyer_01",
        full_name="Buyer Student",
        password="StrongPassword123!",
    )
    user = register_user(db_session, payload)

    by_email = authenticate_user(db_session, payload.email, payload.password)
    by_username = authenticate_user(db_session, payload.username, payload.password)

    assert by_email.id == user.id
    assert by_username.id == user.id


def test_authenticate_user_wrong_password_returns_401(db_session) -> None:
    payload = UserCreate(
        email="wrongpass@example.com",
        username="wrongpass_01",
        full_name="Wrong Pass",
        password="StrongPassword123!",
    )
    register_user(db_session, payload)

    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(db_session, payload.username, "BadPassword999!")

    assert exc_info.value.status_code == 401
