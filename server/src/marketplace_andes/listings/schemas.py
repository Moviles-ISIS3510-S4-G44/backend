from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .enums import ListingCondition


class ListingCreateRequest(BaseModel):
    seller_id: UUID
    category_id: UUID
    title: str
    description: str
    price: int
    condition: ListingCondition
    images: list[str]
    location: str


class ListingUpdateRequest(BaseModel):
    category_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    price: int | None = None
    condition: ListingCondition | None = None
    images: list[str] | None = None
    location: str | None = None


class ListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    seller_id: UUID
    category_id: UUID
    title: str
    description: str
    price: int
    condition: ListingCondition
    images: list[str]
    status: str
    location: str
    created_at: datetime
    updated_at: datetime


class StatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    listing_id: UUID
    from_status: str | None
    to_status: str
    changed_at: datetime


class DeleteAllListingsResponse(BaseModel):
    deleted_count: int
