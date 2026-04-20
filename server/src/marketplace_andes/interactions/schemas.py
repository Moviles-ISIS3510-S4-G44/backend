from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InteractionRegisterRequest(BaseModel):
    user_id: UUID
    listing_id: UUID


class InteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    listing_id: UUID
    interaction_count: int
    last_interaction_at: datetime
