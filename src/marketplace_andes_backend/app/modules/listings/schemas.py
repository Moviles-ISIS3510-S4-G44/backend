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
    category: CategoryResponse
    location: LocationResponse


class ListingListResponse(SQLModel):
    items: list[ListingListItemResponse]
    total: int

