"""Add listing status constraints and status history indexes.

Revision ID: c7f4e2a9d1b8
Revises: b5e7f1a2d3c4
Create Date: 2026-04-09 18:40:00.000000

"""

from collections.abc import Sequence

from alembic import op


revision: str = "c7f4e2a9d1b8"
down_revision: str | Sequence[str] | None = "b5e7f1a2d3c4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


STATUS_VALUES_SQL = "('draft', 'published', 'sold')"


def upgrade() -> None:
    op.create_check_constraint(
        "ck_listings_status_allowed",
        "listings",
        f"status IN {STATUS_VALUES_SQL}",
    )

    op.create_check_constraint(
        "ck_lsh_to_status_allowed",
        "listing_status_history",
        f"to_status IN {STATUS_VALUES_SQL}",
    )

    op.create_check_constraint(
        "ck_lsh_from_status_allowed",
        "listing_status_history",
        f"from_status IS NULL OR from_status IN {STATUS_VALUES_SQL}",
    )

    op.create_index(
        "idx_lsh_listing_changed_at",
        "listing_status_history",
        ["listing_id", "changed_at"],
        unique=False,
    )
    op.create_index(
        "idx_lsh_to_status_changed_at",
        "listing_status_history",
        ["to_status", "changed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_lsh_to_status_changed_at", table_name="listing_status_history")
    op.drop_index("idx_lsh_listing_changed_at", table_name="listing_status_history")

    op.drop_constraint("ck_lsh_from_status_allowed", "listing_status_history", type_="check")
    op.drop_constraint("ck_lsh_to_status_allowed", "listing_status_history", type_="check")
    op.drop_constraint("ck_listings_status_allowed", "listings", type_="check")
