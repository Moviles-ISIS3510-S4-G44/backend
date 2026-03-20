from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UniversityCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    country: str = Field(min_length=1)
    city: str = Field(min_length=1)


class UniversityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    country: str
    city: str
    created_at: datetime


class ProgramCreateRequest(BaseModel):
    university_id: UUID
    name: str = Field(min_length=1)
    faculty: str = Field(min_length=1)


class ProgramResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    university_id: UUID
    name: str
    faculty: str
    created_at: datetime


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    parent_category_id: UUID | None = None
    is_active: bool = True


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    parent_category_id: UUID | None
    name: str
    slug: str
    is_active: bool
    created_at: datetime


class ListingCreateRequest(BaseModel):
    category_id: UUID
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    product_type: str = Field(min_length=1)
    condition: str = Field(min_length=1)
    price: Decimal = Field(gt=0)
    currency: str = Field(default="COP", min_length=1)
    status: str = Field(default="active", min_length=1)
    is_negotiable: bool = False
    is_digital: bool = False
    quantity_available: int = Field(default=1, ge=0)
    campus_pickup_point: str | None = None
    media_urls: list[str] = Field(default_factory=list)


class ListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    seller_id: UUID
    category_id: UUID
    title: str
    description: str
    product_type: str
    condition: str
    price: Decimal
    currency: str
    status: str
    is_negotiable: bool
    is_digital: bool
    quantity_available: int
    campus_pickup_point: str | None
    created_at: datetime
    published_at: datetime | None
    sold_at: datetime | None
    archived_at: datetime | None


class ListingStatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    listing_id: UUID
    changed_by_user_id: UUID
    from_status: str | None
    to_status: str
    changed_at: datetime


class TransactionCreateRequest(BaseModel):
    listing_id: UUID
    agreed_price: Decimal = Field(gt=0)
    currency: str = Field(default="COP", min_length=1)


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    listing_id: UUID
    buyer_id: UUID
    seller_id: UUID
    listed_price: Decimal
    agreed_price: Decimal
    currency: str
    status: str
    created_at: datetime
    completed_at: datetime | None
    cancelled_at: datetime | None


class MessageThreadCreateRequest(BaseModel):
    listing_id: UUID


class MessageThreadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    listing_id: UUID
    buyer_id: UUID
    seller_id: UUID
    created_at: datetime
    last_message_at: datetime | None


class MessageCreateRequest(BaseModel):
    body: str = Field(min_length=1)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    thread_id: UUID
    sender_id: UUID
    body: str
    is_read: bool
    created_at: datetime


class ReviewCreateRequest(BaseModel):
    transaction_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    transaction_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    rating: int
    comment: str | None
    created_at: datetime


class SearchEventCreateRequest(BaseModel):
    category_id: UUID | None = None
    query_text: str = Field(min_length=1)
    sort_mode: str | None = None
    results_count: int = Field(default=0, ge=0)


class SearchEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    category_id: UUID | None
    query_text: str
    sort_mode: str | None
    results_count: int
    created_at: datetime


class UserActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    listing_id: UUID | None
    transaction_id: UUID | None
    event_type: str
    created_at: datetime


class MarketplaceSnapshotResponse(BaseModel):
    universities: list[UniversityResponse]
    programs: list[ProgramResponse]
    categories: list[CategoryResponse]
    listings: list[ListingResponse]
    transactions: list[TransactionResponse]
    threads: list[MessageThreadResponse]
    messages: list[MessageResponse]
    reviews: list[ReviewResponse]
    searches: list[SearchEventResponse]
    activities: list[UserActivityResponse]
