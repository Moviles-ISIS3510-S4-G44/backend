from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ListingCreateRequest(BaseModel):
    seller_id: UUID
    category_id: UUID
    title: str
    description: str
    price: str
    condition: str
    images: list[str]
    location: str


class ListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    seller_id: UUID
    category_id: UUID
    title: str
    description: str
    price: str
    condition: str
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
