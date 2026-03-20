from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ListingCreateRequest(BaseModel):
    seller_id: UUID
    category_id: UUID
    title: str
    description: str
    price: Decimal
    condition: str
    images: list[str]
    status: str
    location: str


class ListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    seller_id: UUID
    category_id: UUID
    title: str
    description: str
    price: Decimal
    condition: str
    images: list[str]
    status: str
    location: str