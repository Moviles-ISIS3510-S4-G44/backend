from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ListingCreateRequest(BaseModel):
    seller_id: int
    category_id: int
    title: str
    description: str
    price: Decimal
    condition: str
    images: str
    status: str
    location: str


class ListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seller_id: int
    category_id: int
    title: str
    description: str
    price: Decimal
    condition: str
    images: str
    status: str
    location: str
