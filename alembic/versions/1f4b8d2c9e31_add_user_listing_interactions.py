"""add user listing interactions

Revision ID: 1f4b8d2c9e31
Revises: 9e218e26a345
Create Date: 2026-03-20 22:45:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "1f4b8d2c9e31"
down_revision: str | Sequence[str] | None = "9e218e26a345"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_listing_interaction",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("interaction_count", sa.Integer(), nullable=False),
        sa.Column("last_interaction_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["listing.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "listing_id", name="uq_user_listing_interaction"),
    )


def downgrade() -> None:
    op.drop_table("user_listing_interaction")
