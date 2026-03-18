from uuid import UUID

from sqlmodel import Field, SQLModel


class LocationCreate(SQLModel):
    name: str = Field(min_length=1)


class LocationResponse(SQLModel):
    id: UUID
    name: str
