from uuid import UUID

from sqlmodel import Field, SQLModel


class CategoryCreate(SQLModel):
    name: str = Field(min_length=1)


class CategoryResponse(SQLModel):
    id: UUID
    name: str
