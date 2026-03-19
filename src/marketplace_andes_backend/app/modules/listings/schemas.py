from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel

from ...shared.enums import ListingCondition, ListingStatus
from ..categories.schemas import CategoryResponse
from ..locations.schemas import LocationResponse


class ListingListItemResponse(SQLModel):
    id: UUID
    price: float
    condition: ListingCondition
    status: ListingStatus
    images: list[str]
    created_at: datetime
    category: CategoryResponse
    location: LocationResponse


class ListingListResponse(SQLModel):
    items: list[ListingListItemResponse]
    total: int


class ListingCreate(SQLModel):
    product_id: UUID
    seller_id: UUID
    category_id: UUID
    location_id: UUID
    price: float
    condition: ListingCondition
    
class ListingCreateResponse(SQLModel):
    id: UUID
    price: float
    condition: ListingCondition
    status: ListingStatus
    created_at: datetime