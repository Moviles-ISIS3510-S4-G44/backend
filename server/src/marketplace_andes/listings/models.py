from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, SQLModel


class Listing(SQLModel, table=True):
    __tablename__ = "listings"
    __table_args__ = (
        sa.Index("idx_listings_seller_id", "seller_id"),
        sa.Index("idx_listings_category_id", "category_id"),
        sa.Index("idx_listings_status", "status"),
    )

    id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
    )
    seller_id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    category_id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("categories.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    title: str = Field(
        sa_column=sa.Column(sa.String(length=255), nullable=False),
    )
    description: str = Field(
        sa_column=sa.Column(sa.Text(), nullable=False),
    )
    condition: str = Field(
        sa_column=sa.Column(sa.String(length=32), nullable=False),
    )
    price: str = Field(
        sa_column=sa.Column(sa.String(length=64), nullable=False),
    )
    images: list[str] = Field(
        sa_column=sa.Column(postgresql.ARRAY(sa.Text()), nullable=False),
    )
    location: str = Field(
        sa_column=sa.Column(sa.String(length=255), nullable=False),
    )
    status: str = Field(
        sa_column=sa.Column(sa.String(length=32), nullable=False),
    )
    created_at: datetime = Field(
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )


class ListingStatusHistory(SQLModel, table=True):
    __tablename__ = "listing_status_history"
    __table_args__ = (
        sa.Index("idx_lsh_listing_id", "listing_id"),
        sa.Index("idx_lsh_to_status", "to_status"),
    )

    id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
    )
    listing_id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    from_status: str | None = Field(
        default=None,
        sa_column=sa.Column(sa.String(length=32), nullable=True),
    )
    to_status: str = Field(
        sa_column=sa.Column(sa.String(length=32), nullable=False),
    )
    changed_at: datetime = Field(
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
