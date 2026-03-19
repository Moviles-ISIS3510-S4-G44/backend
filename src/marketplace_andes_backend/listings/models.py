from decimal import Decimal

from sqlmodel import Field, SQLModel


class Listing(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    seller_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    title: str
    description: str
    price: Decimal
    condition: str
    images: str
    status: str
    location: str
