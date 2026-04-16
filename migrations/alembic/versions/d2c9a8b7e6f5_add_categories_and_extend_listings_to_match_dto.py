"""Add categories and extend listings to match dto.

Revision ID: d2c9a8b7e6f5
Revises: c7f4e2a9d1b8
Create Date: 2026-04-16 23:50:00.000000

"""

from collections.abc import Sequence
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d2c9a8b7e6f5"
down_revision: str | Sequence[str] | None = "c7f4e2a9d1b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DEFAULT_CATEGORY_ID = str(uuid4())


def upgrade() -> None:
    conn = op.get_bind()

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
    op.create_index("idx_categories_name", "categories", ["name"], unique=True)

    op.add_column("listings", sa.Column("category_id", postgresql.UUID(), nullable=True))
    op.add_column(
        "listings",
        sa.Column(
            "images",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
    )
    op.add_column(
        "listings",
        sa.Column(
            "location",
            sa.String(length=255),
            nullable=False,
            server_default=sa.text("'Unknown'"),
        ),
    )
    conn.execute(
        sa.text(
            """
            INSERT INTO categories (id, name, created_at, updated_at)
            VALUES (:id, :name, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
        ),
        {"id": DEFAULT_CATEGORY_ID, "name": "General"},
    )
    conn.execute(
        sa.text("UPDATE listings SET category_id = :category_id WHERE category_id IS NULL"),
        {"category_id": DEFAULT_CATEGORY_ID},
    )

    op.alter_column("listings", "category_id", nullable=False)
    op.create_foreign_key(
        "fk_listings_category_id_categories",
        "listings",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("idx_listings_category_id", "listings", ["category_id"], unique=False)

    op.alter_column("listings", "images", server_default=None)
    op.alter_column("listings", "location", server_default=None)


def downgrade() -> None:
    op.drop_index("idx_listings_category_id", table_name="listings")
    op.drop_constraint(
        "fk_listings_category_id_categories",
        "listings",
        type_="foreignkey",
    )
    op.drop_column("listings", "location")
    op.drop_column("listings", "images")
    op.drop_column("listings", "category_id")

    op.drop_index("idx_categories_name", table_name="categories")
    op.drop_table("categories")
