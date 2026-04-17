"""Align users table with current user model.

Revision ID: e8c1b0a9f2d4
Revises: d2c9a8b7e6f5
Create Date: 2026-04-17 14:05:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "e8c1b0a9f2d4"
down_revision: str | Sequence[str] | None = "d2c9a8b7e6f5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column(
        "users",
        sa.Column("rating", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )

    op.execute(
        sa.text(
            """
            UPDATE users AS u
            SET
                name = COALESCE(NULLIF(up.name, ''), u.username),
                email = COALESCE(
                    NULLIF(lower(u.username), '') || '@marketplace.local',
                    'unknown@marketplace.local'
                ),
                rating = COALESCE(up.rating, 0)
            FROM user_profiles AS up
            WHERE up.id = u.id
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE users
            SET
                name = COALESCE(NULLIF(name, ''), username),
                email = COALESCE(
                    NULLIF(email, ''),
                    COALESCE(NULLIF(lower(username), ''), 'unknown') || '@marketplace.local'
                ),
                rating = COALESCE(rating, 0)
            """
        )
    )

    op.alter_column("users", "name", nullable=False)
    op.alter_column("users", "email", nullable=False)
    op.create_index(
        "idx_user_email_active",
        "users",
        ["email"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.alter_column("users", "rating", server_default=None)


def downgrade() -> None:
    op.drop_index("idx_user_email_active", table_name="users")
    op.drop_column("users", "rating")
    op.drop_column("users", "email")
    op.drop_column("users", "name")
