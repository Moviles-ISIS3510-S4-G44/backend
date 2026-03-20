from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class UserListingInteraction(SQLModel, table=True):
    __tablename__ = "user_listing_interaction"
    __table_args__ = (
        UniqueConstraint("user_id", "listing_id", name="uq_user_listing_interaction"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    listing_id: UUID = Field(foreign_key="listing.id")
    interaction_count: int = Field(default=1, ge=1)
    last_interaction_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
