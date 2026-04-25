"""Merge chat and purchases branches into a single head.

Revision ID: f9b8c7d6e5a4
Revises: c2d3e4f5a6b7, a4b5c6d7e8f9
Create Date: 2026-04-24 00:00:00.000000

"""

from collections.abc import Sequence


revision: str = "f9b8c7d6e5a4"
down_revision: str | Sequence[str] | None = (
    "c2d3e4f5a6b7",
    "a4b5c6d7e8f9",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Merge revision: no schema changes, only joins branches.
    pass


def downgrade() -> None:
    # Split branches again when downgrading past this merge point.
    pass