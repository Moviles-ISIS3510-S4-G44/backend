from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, SQLModel


class UserListingFavorite(SQLModel, table=True):
    __tablename__ = "user_listing_favorite"
    __table_args__ = (
        sa.UniqueConstraint(
            "user_id",
            "listing_id",
            name="uq_user_listing_favorite",
        ),
        sa.Index("idx_user_listing_favorite_user_id", "user_id"),
        sa.Index("idx_user_listing_favorite_listing_id", "listing_id"),
    )

    id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
    )
    user_id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
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
    created_at: datetime = Field(
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
