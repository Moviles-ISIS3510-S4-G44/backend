"""Align schema with current entity models.

Revision ID: f1a9d3c6b2e4
Revises: e8c1b0a9f2d4
Create Date: 2026-04-19 23:50:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "f1a9d3c6b2e4"
down_revision: str | Sequence[str] | None = "e8c1b0a9f2d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UNKNOWN_IP_ADDRESS = "0.0.0.0"


def upgrade() -> None:
    conn = op.get_bind()

    op.drop_index("idx_user_username_active", table_name="users")
    op.drop_index("idx_user_email_active", table_name="users")
    op.create_index(
        "idx_users_email_active",
        "users",
        ["email"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.drop_column("users", "username")
    op.drop_column("users", "name")
    op.drop_column("users", "rating")

    op.drop_constraint("ck_user_profiles_rating_range", "user_profiles", type_="check")
    op.drop_column("user_profiles", "surname")
    op.drop_column("user_profiles", "status")
    op.drop_column("user_profiles", "university")
    op.execute(
        sa.text(
            """
            UPDATE user_profiles
            SET
                name = COALESCE(NULLIF(name, ''), 'Unknown'),
                rating = COALESCE(rating, 0)
            """
        )
    )
    op.alter_column("user_profiles", "name", type_=sa.String(length=100), nullable=False)
    op.alter_column("user_profiles", "rating", nullable=False, server_default=sa.text("0"))

    conn.execute(
        sa.text(
            """
            UPDATE auth_sessions
            SET ip_address = :unknown_ip
            WHERE ip_address IS NULL
            """,
        ),
        {"unknown_ip": UNKNOWN_IP_ADDRESS},
    )
    op.alter_column("auth_sessions", "ip_address", nullable=False)


def downgrade() -> None:
    op.alter_column("auth_sessions", "ip_address", nullable=True)

    op.alter_column("user_profiles", "rating", nullable=True, server_default=None)
    op.alter_column("user_profiles", "name", type_=sa.String(length=63), nullable=True)
    op.add_column("user_profiles", sa.Column("university", sa.String(length=63), nullable=True))
    op.add_column("user_profiles", sa.Column("status", sa.String(length=63), nullable=True))
    op.add_column("user_profiles", sa.Column("surname", sa.String(length=63), nullable=True))
    op.create_check_constraint(
        "ck_user_profiles_rating_range",
        "user_profiles",
        "rating IS NULL OR (rating >= 1 AND rating <= 5)",
    )

    op.add_column("users", sa.Column("rating", sa.Integer(), nullable=False, server_default=sa.text("0")))
    op.add_column("users", sa.Column("name", sa.String(length=100), nullable=False, server_default=sa.text("'unknown'")))
    op.add_column(
        "users",
        sa.Column("username", sa.String(length=32), nullable=False, server_default=sa.text("'unknown'")),
    )
    op.execute(
        sa.text(
            """
            UPDATE users
            SET
                username = left(split_part(email, '@', 1), 20) || '_' || left(replace(id::text, '-', ''), 11),
                name = split_part(email, '@', 1)
            """
        )
    )
    op.alter_column("users", "username", server_default=None)
    op.alter_column("users", "name", server_default=None)
    op.alter_column("users", "rating", server_default=None)

    op.drop_index("idx_users_email_active", table_name="users")
    op.create_index(
        "idx_user_email_active",
        "users",
        ["email"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_user_username_active",
        "users",
        ["username"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
