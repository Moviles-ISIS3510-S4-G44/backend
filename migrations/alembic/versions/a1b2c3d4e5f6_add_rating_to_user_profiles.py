"""Add rating to user profiles

Revision ID: a1b2c3d4e5f6
Revises: 4c156d1e4ab6
Create Date: 2026-04-08 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "4c156d1e4ab6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column(
            "rating",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.create_check_constraint(
        "ck_user_profiles_rating_range",
        "user_profiles",
        "rating IS NULL OR (rating >= 1 AND rating <= 5)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_user_profiles_rating_range", "user_profiles")
    op.drop_column("user_profiles", "rating")