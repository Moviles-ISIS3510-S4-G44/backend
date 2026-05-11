"""Add profile_visit_events for seller profile analytics.

Revision ID: e7a8b9c0d1e2
Revises: c9d0e1f2a3b4
Create Date: 2026-05-10 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "e7a8b9c0d1e2"
down_revision: str | Sequence[str] | None = "c9d0e1f2a3b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "profile_visit_events",
        sa.Column("id", postgresql.UUID(), primary_key=True, nullable=False),
        sa.Column("visitor_user_id", postgresql.UUID(), nullable=False),
        sa.Column("visited_user_id", postgresql.UUID(), nullable=False),
        sa.Column(
            "visited_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["visitor_user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["visited_user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "idx_profile_visit_events_visited_user_id",
        "profile_visit_events",
        ["visited_user_id"],
        unique=False,
    )
    op.create_index(
        "idx_profile_visit_events_visitor_user_id",
        "profile_visit_events",
        ["visitor_user_id"],
        unique=False,
    )
    op.create_index(
        "idx_profile_visit_events_visited_at",
        "profile_visit_events",
        ["visited_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_profile_visit_events_visited_at",
        table_name="profile_visit_events",
    )
    op.drop_index(
        "idx_profile_visit_events_visitor_user_id",
        table_name="profile_visit_events",
    )
    op.drop_index(
        "idx_profile_visit_events_visited_user_id",
        table_name="profile_visit_events",
    )
    op.drop_table("profile_visit_events")
