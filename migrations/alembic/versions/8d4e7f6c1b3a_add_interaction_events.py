"""Add interaction events table for tracking individual visits.

Revision ID: 8d4e7f6c1b3a
Revises: 7b3a1d2e9f40
Create Date: 2026-04-21 10:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "8d4e7f6c1b3a"
down_revision: str | Sequence[str] | None = "7b3a1d2e9f40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "interaction_events",
        sa.Column("id", postgresql.UUID(), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(), nullable=False),
        sa.Column("listing_id", postgresql.UUID(), nullable=False),
        sa.Column(
            "interaction_timestamp",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "idx_interaction_events_user_id",
        "interaction_events",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "idx_interaction_events_listing_id",
        "interaction_events",
        ["listing_id"],
        unique=False,
    )
    op.create_index(
        "idx_interaction_events_timestamp",
        "interaction_events",
        ["interaction_timestamp"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_interaction_events_timestamp",
        table_name="interaction_events",
    )
    op.drop_index(
        "idx_interaction_events_listing_id",
        table_name="interaction_events",
    )
    op.drop_index(
        "idx_interaction_events_user_id",
        table_name="interaction_events",
    )
    op.drop_table("interaction_events")
