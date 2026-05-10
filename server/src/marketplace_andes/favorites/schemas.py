from uuid import UUID

from pydantic import BaseModel


class FavoriteCreateRequest(BaseModel):
    listing_id: UUID


class FavoritesListResponse(BaseModel):
    listing_ids: list[UUID]
