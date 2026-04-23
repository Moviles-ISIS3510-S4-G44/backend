import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    db_host: str = Field(default="postgres")
    db_port: int = Field(default=5432)
    db_user: str = Field(default="backend_user")
    db_password: str = Field(default="password")
    db_name: str = Field(default="marketplace")

    db_echo: bool = Field(default=False)
    enable_otel: bool = Field(default=False)
    jwt_public_key: str = Field(default="change-me-in-production-32-bytes")
    jwt_secret_key: str = Field(default="change-me-in-production-32-bytes")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=60)
    jwt_refresh_token_expire_minutes: int = Field(default=60 * 24 * 7)  # 7 days

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_db_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_global_config() -> Config:
    return Config()
