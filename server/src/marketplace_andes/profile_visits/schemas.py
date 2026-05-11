from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProfileVisitCreatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    visited_at: datetime
