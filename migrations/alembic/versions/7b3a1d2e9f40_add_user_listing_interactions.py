"""Add user listing interactions table.

Revision ID: 7b3a1d2e9f40
Revises: f1a9d3c6b2e4
Create Date: 2026-04-20 15:10:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "7b3a1d2e9f40"
down_revision: str | Sequence[str] | None = "f1a9d3c6b2e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_listing_interaction",
        sa.Column("id", postgresql.UUID(), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(), nullable=False),
        sa.Column("listing_id", postgresql.UUID(), nullable=False),
        sa.Column(
            "interaction_count",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column("last_interaction_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.CheckConstraint(
            "interaction_count >= 1", name="ck_interaction_count_positive"
        ),
        sa.UniqueConstraint(
            "user_id",
            "listing_id",
            name="uq_user_listing_interaction",
        ),
    )
    op.create_index(
        "idx_user_listing_interaction_user_id",
        "user_listing_interaction",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "idx_user_listing_interaction_listing_id",
        "user_listing_interaction",
        ["listing_id"],
        unique=False,
    )
def downgrade() -> None:
    op.drop_index(
        "idx_user_listing_interaction_listing_id",
        table_name="user_listing_interaction",
    )
    op.drop_index(
        "idx_user_listing_interaction_user_id",
        table_name="user_listing_interaction",
    )
    op.drop_table("user_listing_interaction")
