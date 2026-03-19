"""Add categories and listings

Revision ID: 3297ee9ed324
Revises: 3d567fecb68e
Create Date: 2026-03-19 22:40:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlmodel.sql.sqltypes import AutoString


revision: str = "3297ee9ed324"
down_revision: str | Sequence[str] | None = "3d567fecb68e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "listing",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("seller_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("title", AutoString(), nullable=False),
        sa.Column("description", AutoString(), nullable=False),
        sa.Column("price", sa.Numeric(), nullable=False),
        sa.Column("condition", AutoString(), nullable=False),
        sa.Column("images", AutoString(), nullable=False),
        sa.Column("status", AutoString(), nullable=False),
        sa.Column("location", AutoString(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("listing")
    op.drop_table("category")
