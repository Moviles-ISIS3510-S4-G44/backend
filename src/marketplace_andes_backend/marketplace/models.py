from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid7

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class University(SQLModel, table=True):
    __tablename__ = "university"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    name: str = Field(index=True)
    country: str
    city: str
    created_at: datetime = Field(default_factory=utc_now)


class Program(SQLModel, table=True):
    __tablename__ = "program"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    university_id: UUID = Field(foreign_key="university.id", index=True)
    name: str
    faculty: str
    created_at: datetime = Field(default_factory=utc_now)


class Category(SQLModel, table=True):
    __tablename__ = "category"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    parent_category_id: UUID | None = Field(default=None, foreign_key="category.id", index=True)
    name: str
    slug: str = Field(index=True, unique=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)


class Listing(SQLModel, table=True):
    __tablename__ = "listing"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    seller_id: UUID = Field(foreign_key="user.id", index=True)
    category_id: UUID = Field(foreign_key="category.id", index=True)
    title: str
    description: str
    product_type: str
    condition: str
    price: Decimal
    currency: str = Field(default="COP")
    status: str = Field(default="active", index=True)
    is_negotiable: bool = Field(default=False)
    is_digital: bool = Field(default=False)
    quantity_available: int = Field(default=1, ge=0)
    campus_pickup_point: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    published_at: datetime | None = None
    sold_at: datetime | None = None
    archived_at: datetime | None = None


class ListingMedia(SQLModel, table=True):
    __tablename__ = "listing_media"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    listing_id: UUID = Field(foreign_key="listing.id", index=True)
    asset_url: str
    media_type: str
    sort_order: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=utc_now)


class ListingStatusHistory(SQLModel, table=True):
    __tablename__ = "listing_status_history"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    listing_id: UUID = Field(foreign_key="listing.id", index=True)
    changed_by_user_id: UUID = Field(foreign_key="user.id", index=True)
    from_status: str | None = None
    to_status: str
    changed_at: datetime = Field(default_factory=utc_now)


class MarketplaceTransaction(SQLModel, table=True):
    __tablename__ = "marketplace_transaction"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    listing_id: UUID = Field(foreign_key="listing.id", index=True)
    buyer_id: UUID = Field(foreign_key="user.id", index=True)
    seller_id: UUID = Field(foreign_key="user.id", index=True)
    listed_price: Decimal
    agreed_price: Decimal
    currency: str = Field(default="COP")
    status: str = Field(default="pending", index=True)
    created_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None


class MessageThread(SQLModel, table=True):
    __tablename__ = "message_thread"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    listing_id: UUID = Field(foreign_key="listing.id", index=True)
    buyer_id: UUID = Field(foreign_key="user.id", index=True)
    seller_id: UUID = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=utc_now)
    last_message_at: datetime | None = None


class Message(SQLModel, table=True):
    __tablename__ = "message"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    thread_id: UUID = Field(foreign_key="message_thread.id", index=True)
    sender_id: UUID = Field(foreign_key="user.id", index=True)
    body: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)


class Review(SQLModel, table=True):
    __tablename__ = "review"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    transaction_id: UUID = Field(foreign_key="marketplace_transaction.id", index=True)
    reviewer_id: UUID = Field(foreign_key="user.id", index=True)
    reviewee_id: UUID = Field(foreign_key="user.id", index=True)
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class SearchEvent(SQLModel, table=True):
    __tablename__ = "search_event"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    category_id: UUID | None = Field(default=None, foreign_key="category.id", index=True)
    query_text: str
    sort_mode: str | None = None
    results_count: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=utc_now)


class UserActivityEvent(SQLModel, table=True):
    __tablename__ = "user_activity_event"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    listing_id: UUID | None = Field(default=None, foreign_key="listing.id", index=True)
    transaction_id: UUID | None = Field(
        default=None,
        foreign_key="marketplace_transaction.id",
        index=True,
    )
    event_type: str = Field(index=True)
    created_at: datetime = Field(default_factory=utc_now)
