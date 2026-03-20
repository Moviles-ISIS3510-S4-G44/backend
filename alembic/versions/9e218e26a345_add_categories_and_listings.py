"""add categories and listings

Revision ID: 9e218e26a345
Revises: 8f3c0a4d2c1b
Create Date: 2026-03-19 20:20:46.863175

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

revision: str = '9e218e26a345'
down_revision: str | Sequence[str] | None = '8f3c0a4d2c1b'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'category',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'listing',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('seller_id', sa.Uuid(), nullable=False),
        sa.Column('category_id', sa.Uuid(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('price', sa.Numeric(), nullable=False),
        sa.Column('condition', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('images', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('location', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['category.id']),
        sa.ForeignKeyConstraint(['seller_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('listing')
    op.drop_table('category')