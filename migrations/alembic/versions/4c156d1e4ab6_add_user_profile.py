"""Add user profile

Revision ID: 4c156d1e4ab6
Revises: 93f888505946
Create Date: 2026-03-31 17:29:01.971949

"""

from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "4c156d1e4ab6"
down_revision: str | Sequence[str] | None = "93f888505946"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column(
            "id",
            postgresql.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("name", sa.String(length=63), nullable=True),
        sa.Column("surname", sa.String(length=63), nullable=True),
        sa.Column("status", sa.String(length=63), nullable=True),
        sa.Column("university", sa.String(length=63), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("user_profiles")
