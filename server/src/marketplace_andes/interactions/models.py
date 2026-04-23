from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, SQLModel


class UserListingInteraction(SQLModel, table=True):
    __tablename__ = "user_listing_interaction"
    __table_args__ = (
        sa.UniqueConstraint(
            "user_id",
            "listing_id",
            name="uq_user_listing_interaction",
        ),
        sa.CheckConstraint(
            "interaction_count >= 1", name="ck_interaction_count_positive"
        ),
        sa.Index("idx_user_listing_interaction_user_id", "user_id"),
        sa.Index("idx_user_listing_interaction_listing_id", "listing_id"),
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
    interaction_count: int = Field(
        default=1,
        sa_column=sa.Column(
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )
    last_interaction_at: datetime = Field(
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )


class InteractionEvent(SQLModel, table=True):
    __tablename__ = "interaction_events"
    __table_args__ = (
        sa.Index("idx_interaction_events_user_id", "user_id"),
        sa.Index("idx_interaction_events_listing_id", "listing_id"),
        sa.Index("idx_interaction_events_timestamp", "interaction_timestamp"),
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
    interaction_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(datetime.UTC),
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
