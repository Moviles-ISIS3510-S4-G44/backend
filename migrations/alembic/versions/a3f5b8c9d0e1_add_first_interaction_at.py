"""Add first_interaction_at to user_listing_interaction.

Revision ID: a3f5b8c9d0e1
Revises: 7b3a1d2e9f40
Create Date: 2026-04-21 10:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "a3f5b8c9d0e1"
down_revision: str | Sequence[str] | None = "7b3a1d2e9f40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "user_listing_interaction",
        sa.Column(
            "first_interaction_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )
    op.execute(
        sa.text(
            """
            UPDATE user_listing_interaction
            SET first_interaction_at = last_interaction_at
            WHERE first_interaction_at IS NULL
            """
        )
    )
    op.alter_column(
        "user_listing_interaction",
        "first_interaction_at",
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("user_listing_interaction", "first_interaction_at")
