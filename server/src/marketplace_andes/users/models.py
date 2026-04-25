from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        sa.Index(
            "idx_users_email_active",
            "email",
            unique=True,
            postgresql_where=sa.text("deleted_at IS NULL"),
        ),
        sa.Index("idx_users_deleted_at", "deleted_at"),
    )

    id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
    )

    email: str = Field(
        sa_column=sa.Column(
            sa.String(length=255),
            nullable=False,
        ),
    )

    created_at: datetime = Field(
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )

    updated_at: datetime = Field(
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )

    deleted_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )


class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"

    id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
    )

    name: str = Field(
        sa_column=sa.Column(
            sa.String(length=100),
            nullable=False,
        ),
    )

    rating: int = Field(
        default=0,
        sa_column=sa.Column(
            sa.Integer,
            nullable=False,
            server_default="0",
        ),
    )
