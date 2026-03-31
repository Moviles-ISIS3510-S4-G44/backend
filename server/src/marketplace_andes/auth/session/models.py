from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


class AuthSession(SQLModel, table=True):
    __tablename__ = "auth_sessions"

    id: UUID = Field(primary_key=True)
    user_id: UUID
    refresh_token_hash: str
    ip_address: str | None = Field(
        sa_column=sa.Column(postgresql.INET(), nullable=False),
    )
    expires_at: datetime
    created_at: datetime
    revoked_at: datetime | None = None
