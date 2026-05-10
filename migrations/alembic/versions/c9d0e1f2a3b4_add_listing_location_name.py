"""Add location_name to listings.

Revision ID: c9d0e1f2a3b4
Revises: b8e4c1a9f3d2
Create Date: 2026-05-10 14:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "c9d0e1f2a3b4"
down_revision: str | Sequence[str] | None = "b8e4c1a9f3d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "listings",
        sa.Column("location_name", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("listings", "location_name")
