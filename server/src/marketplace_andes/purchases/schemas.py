from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PurchaseCreateRequest(BaseModel):
    listing_id: UUID


class PurchaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    listing_id: UUID
    buyer_id: UUID
    price_at_purchase: int
    purchased_at: datetime
