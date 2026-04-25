from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, SQLModel


class Purchase(SQLModel, table=True):
    __tablename__ = "purchases"
    __table_args__ = (
        sa.UniqueConstraint("listing_id", name="uq_purchases_listing_id"),
        sa.CheckConstraint("price_at_purchase > 0", name="ck_purchases_price_positive"),
        sa.Index("idx_purchases_buyer_id", "buyer_id"),
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
            sa.ForeignKey("listings.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    buyer_id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    price_at_purchase: int = Field(
        sa_column=sa.Column(
            sa.Integer(),
            nullable=False,
        ),
    )
    purchased_at: datetime = Field(
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
