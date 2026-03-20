from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str