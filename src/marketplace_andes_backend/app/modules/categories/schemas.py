from uuid import UUID

from sqlmodel import SQLModel


class CategoryResponse(SQLModel):
    id: UUID
    name: str

