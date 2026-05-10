"""Add user_listing_favorite table.

Revision ID: b8e4c1a9f3d2
Revises: fa12bc34de56
Create Date: 2026-05-10 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b8e4c1a9f3d2"
down_revision: str | Sequence[str] | None = "fa12bc34de56"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_listing_favorite",
        sa.Column("id", postgresql.UUID(), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(), nullable=False),
        sa.Column("listing_id", postgresql.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "user_id",
            "listing_id",
            name="uq_user_listing_favorite",
        ),
    )
    op.create_index(
        "idx_user_listing_favorite_user_id",
        "user_listing_favorite",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "idx_user_listing_favorite_listing_id",
        "user_listing_favorite",
        ["listing_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_user_listing_favorite_listing_id",
        table_name="user_listing_favorite",
    )
    op.drop_index(
        "idx_user_listing_favorite_user_id",
        table_name="user_listing_favorite",
    )
    op.drop_table("user_listing_favorite")
