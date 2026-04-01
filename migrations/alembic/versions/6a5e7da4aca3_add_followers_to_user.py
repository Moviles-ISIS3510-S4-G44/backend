"""Add followers to user

Revision ID: 6a5e7da4aca3
Revises: 4c156d1e4ab6
Create Date: 2026-04-01 16:12:37.150583

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "6a5e7da4aca3"
down_revision: str | Sequence[str] | None = "4c156d1e4ab6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_follows",
        sa.Column(
            "follower_id",
            postgresql.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "followed_id",
            postgresql.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("follower_id", "followed_id"),
    )


def downgrade() -> None:
    op.drop_table("follows")
