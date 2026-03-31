"""initial marketplace andes database schema

Revision ID: 93f888505946
Revises:
Create Date: 2026-03-20 21:54:55.739367

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "93f888505946"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(), primary_key=True),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    op.create_index(
        "idx_user_username_active",
        "users",
        ["username"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("idx_users_deleted_at", "users", ["deleted_at"], unique=False)

    op.create_table(
        "auth_users",
        sa.Column(
            "id",
            postgresql.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("hashed_password", sa.Text(), nullable=False),
    )

    op.create_table(
        "auth_sessions",
        sa.Column("id", postgresql.UUID(), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("refresh_token_hash", sa.Text(), nullable=False),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    op.create_index(
        "idx_auth_sessions_user_id", "auth_sessions", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("idx_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")

    op.drop_table("auth_users")

    op.drop_index("idx_users_deleted_at", table_name="users")
    op.drop_index("idx_user_username_active", table_name="users")
    op.drop_table("users")
