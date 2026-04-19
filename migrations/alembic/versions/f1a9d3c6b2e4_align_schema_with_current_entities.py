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
USERS_LEGACY_BACKUP_TABLE = "_users_legacy_backup_f1a9d3c6b2e4"
USER_PROFILES_LEGACY_BACKUP_TABLE = "_user_profiles_legacy_backup_f1a9d3c6b2e4"


def upgrade() -> None:
    conn = op.get_bind()

    op.create_table(
        USERS_LEGACY_BACKUP_TABLE,
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
    )
    conn.execute(
        sa.text(
            f"""
            INSERT INTO {USERS_LEGACY_BACKUP_TABLE} (id, username, name, rating)
            SELECT id, username, name, rating
            FROM users
            """
        )
    )

    op.create_table(
        USER_PROFILES_LEGACY_BACKUP_TABLE,
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("surname", sa.String(length=63), nullable=True),
        sa.Column("status", sa.String(length=63), nullable=True),
        sa.Column("university", sa.String(length=63), nullable=True),
    )
    conn.execute(
        sa.text(
            f"""
            INSERT INTO {USER_PROFILES_LEGACY_BACKUP_TABLE} (id, surname, status, university)
            SELECT id, surname, status, university
            FROM user_profiles
            """
        )
    )

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
    conn = op.get_bind()

    op.alter_column("auth_sessions", "ip_address", nullable=True)

    op.alter_column("user_profiles", "rating", nullable=True, server_default=None)
    op.alter_column("user_profiles", "name", type_=sa.String(length=63), nullable=True)
    op.add_column("user_profiles", sa.Column("university", sa.String(length=63), nullable=True))
    op.add_column("user_profiles", sa.Column("status", sa.String(length=63), nullable=True))
    op.add_column("user_profiles", sa.Column("surname", sa.String(length=63), nullable=True))
    conn.execute(
        sa.text(
            f"""
            UPDATE user_profiles AS up
            SET
                surname = b.surname,
                status = b.status,
                university = b.university
            FROM {USER_PROFILES_LEGACY_BACKUP_TABLE} AS b
            WHERE b.id = up.id
            """
        )
    )
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
    conn.execute(
        sa.text(
            f"""
            UPDATE users AS u
            SET
                username = COALESCE(
                    b.username,
                    left(split_part(u.email, '@', 1), 20) || '_' || left(replace(u.id::text, '-', ''), 11)
                ),
                name = COALESCE(b.name, split_part(u.email, '@', 1)),
                rating = COALESCE(b.rating, 0)
            FROM {USERS_LEGACY_BACKUP_TABLE} AS b
            WHERE b.id = u.id
            """
        )
    )
    conn.execute(
        sa.text(
            f"""
            UPDATE users
            SET
                username = left(split_part(email, '@', 1), 20) || '_' || left(replace(id::text, '-', ''), 11),
                name = split_part(email, '@', 1),
                rating = 0
            WHERE id NOT IN (SELECT id FROM {USERS_LEGACY_BACKUP_TABLE})
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

    op.drop_table(USER_PROFILES_LEGACY_BACKUP_TABLE)
    op.drop_table(USERS_LEGACY_BACKUP_TABLE)
