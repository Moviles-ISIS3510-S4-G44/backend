from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Listing(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    seller_id: UUID = Field(foreign_key="user.id")
    category_id: UUID = Field(foreign_key="category.id")
    title: str
    description: str
    price: Decimal
    condition: str
    images: list[str] = Field(sa_column=Column(JSONB))
    status: str
    location: str