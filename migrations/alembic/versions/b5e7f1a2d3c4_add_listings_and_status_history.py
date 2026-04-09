"""Add listings and listing_status_history

Revision ID: b5e7f1a2d3c4
Revises: a1b2c3d4e5f6
Create Date: 2026-04-09 16:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b5e7f1a2d3c4"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "listings",
        sa.Column("id", postgresql.UUID(), primary_key=True),
        sa.Column(
            "seller_id",
            postgresql.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("condition", sa.String(length=32), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )

    op.create_index("idx_listings_seller_id", "listings", ["seller_id"], unique=False)
    op.create_index("idx_listings_status", "listings", ["status"], unique=False)

    op.create_table(
        "listing_status_history",
        sa.Column("id", postgresql.UUID(), primary_key=True),
        sa.Column(
            "listing_id",
            postgresql.UUID(),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=False),
        sa.Column("changed_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )

    op.create_index(
        "idx_lsh_listing_id",
        "listing_status_history",
        ["listing_id"],
        unique=False,
    )
    op.create_index(
        "idx_lsh_to_status",
        "listing_status_history",
        ["to_status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_lsh_to_status", table_name="listing_status_history")
    op.drop_index("idx_lsh_listing_id", table_name="listing_status_history")
    op.drop_table("listing_status_history")

    op.drop_index("idx_listings_status", table_name="listings")
    op.drop_index("idx_listings_seller_id", table_name="listings")
    op.drop_table("listings")
