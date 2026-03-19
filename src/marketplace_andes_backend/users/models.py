from uuid import UUID, uuid7

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid7, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    rating: int = Field(default=0, ge=0, le=5)
