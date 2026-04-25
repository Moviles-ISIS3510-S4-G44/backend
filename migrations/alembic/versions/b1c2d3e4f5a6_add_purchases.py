"""Add purchases table.

Revision ID: b1c2d3e4f5a6
Revises: a3f5b8c9d0e1
Create Date: 2026-04-23 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b1c2d3e4f5a6"
down_revision: str | Sequence[str] | None = "a3f5b8c9d0e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "purchases",
        sa.Column("id", postgresql.UUID(), primary_key=True, nullable=False),
        sa.Column("listing_id", postgresql.UUID(), nullable=False),
        sa.Column("buyer_id", postgresql.UUID(), nullable=False),
        sa.Column("price_at_purchase", sa.Integer(), nullable=False),
        sa.Column("purchased_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["listings.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["buyer_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("listing_id", name="uq_purchases_listing_id"),
        sa.CheckConstraint(
            "price_at_purchase > 0",
            name="ck_purchases_price_positive",
        ),
    )
    op.create_index(
        "idx_purchases_buyer_id",
        "purchases",
        ["buyer_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_purchases_buyer_id", table_name="purchases")
    op.drop_table("purchases")
