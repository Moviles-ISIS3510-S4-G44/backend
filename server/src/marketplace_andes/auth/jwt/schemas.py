from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TokenConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    jwt_public_key: str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_minutes: int


class RefreshToken(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    token: str
    expires_at: datetime
