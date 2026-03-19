"""Add UserAuth

Revision ID: 8f3c0a4d2c1b
Revises: 3d567fecb68e
Create Date: 2026-03-19 00:00:00.000000

"""

from collections.abc import Sequence

revision: str = "8f3c0a4d2c1b"
down_revision: str | Sequence[str] | None = "3d567fecb68e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
