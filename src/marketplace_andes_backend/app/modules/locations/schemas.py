from uuid import UUID

from sqlmodel import SQLModel


class LocationResponse(SQLModel):
    id: UUID
    name: str

