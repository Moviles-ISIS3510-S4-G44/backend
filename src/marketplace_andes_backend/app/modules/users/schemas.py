from uuid import UUID

from sqlmodel import SQLModel


class UserResponse(SQLModel):
    id: UUID
    name: str

