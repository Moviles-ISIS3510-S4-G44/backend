from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CategoryCreateRequest(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class DeleteAllCategoriesResponse(BaseModel):
    deleted_count: int
