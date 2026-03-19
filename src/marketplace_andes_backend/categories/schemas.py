from pydantic import BaseModel, ConfigDict


class CategoryCreateRequest(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
