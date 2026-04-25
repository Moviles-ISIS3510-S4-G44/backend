"""Merge remaining heads into a single final head.

Revision ID: fa12bc34de56
Revises: f9b8c7d6e5a4, 8d4e7f6c1b3a
Create Date: 2026-04-24 00:10:00.000000

"""

from collections.abc import Sequence


revision: str = "fa12bc34de56"
down_revision: str | Sequence[str] | None = (
    "f9b8c7d6e5a4",
    "8d4e7f6c1b3a",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Merge revision: no schema changes, only joins branches.
    pass


def downgrade() -> None:
    # Split branches again when downgrading past this merge point.
    pass