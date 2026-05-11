from datetime import UTC, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, SQLModel


class ProfileVisitEvent(SQLModel, table=True):
    __tablename__ = "profile_visit_events"
    __table_args__ = (
        sa.Index("idx_profile_visit_events_visited_user_id", "visited_user_id"),
        sa.Index("idx_profile_visit_events_visitor_user_id", "visitor_user_id"),
        sa.Index("idx_profile_visit_events_visited_at", "visited_at"),
    )

    id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
    )
    visitor_user_id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    visited_user_id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    visited_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
