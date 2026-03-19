"""Add User

Revision ID: 3d567fecb68e
Revises:
Create Date: 2026-03-18 20:01:43.265452

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlmodel.sql.sqltypes import AutoString


revision: str = "3d567fecb68e"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", AutoString(), nullable=False),
        sa.Column("email", AutoString(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
