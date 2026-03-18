from uuid import UUID

from sqlmodel import Field, SQLModel


class UserCreate(SQLModel):
    name: str = Field(min_length=1)


class UserResponse(SQLModel):
    id: UUID
    name: str
