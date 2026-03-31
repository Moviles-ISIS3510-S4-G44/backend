from uuid import UUID
import secrets
import hashlib
from datetime import datetime, timedelta, UTC

import jwt

from .schemas import TokenConfig, RefreshToken


class JWTService:
    def __init__(self, config: TokenConfig):
        self.__config = config

    @property
    def jwt_access_token_expire_minutes(self) -> int:
        return self.__config.jwt_access_token_expire_minutes

    @property
    def jwt_refresh_token_expire_minutes(self) -> int:
        return self.__config.jwt_refresh_token_expire_minutes

    def create_access_token(self, user_id: UUID) -> str:
        expires_at = datetime.now(UTC) + timedelta(
            minutes=self.__config.jwt_access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "exp": expires_at,
        }
        return jwt.encode(
            payload,
            self.__config.jwt_secret_key,
            algorithm=self.__config.jwt_algorithm,
        )

    def verify_access_token(self, token: str) -> UUID:
        payload = jwt.decode(
            token,
            self.__config.jwt_secret_key,
            algorithms=[self.__config.jwt_algorithm],
        )
        return UUID(payload["sub"])

    def hash_token(self, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()

    def create_refresh_token(self) -> RefreshToken:
        raw_token = secrets.token_urlsafe(64)
        expires = datetime.now(UTC) + timedelta(
            minutes=self.__config.jwt_refresh_token_expire_minutes
        )
        return RefreshToken(
            token=raw_token,
            expires_at=expires,
        )
