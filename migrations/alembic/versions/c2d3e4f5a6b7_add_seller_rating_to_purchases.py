"""Add seller_rating to purchases.

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-04-23 00:01:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "c2d3e4f5a6b7"
down_revision: str | Sequence[str] | None = "b1c2d3e4f5a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "purchases",
        sa.Column("seller_rating", sa.Integer(), nullable=True),
    )
    op.create_check_constraint(
        "ck_purchases_seller_rating_range",
        "purchases",
        "seller_rating BETWEEN 1 AND 5",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_purchases_seller_rating_range",
        "purchases",
        type_="check",
    )
    op.drop_column("purchases", "seller_rating")
