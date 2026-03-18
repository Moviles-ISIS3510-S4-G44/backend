from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from ...shared.enums import ListingCondition, ListingStatus

if TYPE_CHECKING:
    from ..categories.models import Category
    from ..locations.models import Location
    from ..users.models import User


class Listing(SQLModel, table=True):
    __tablename__ = "listings"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    product_id: UUID
    seller_id: UUID = Field(foreign_key="users.id")
    category_id: UUID = Field(foreign_key="categories.id")
    location_id: UUID = Field(foreign_key="locations.id")
    price: float
    condition: ListingCondition
    status: ListingStatus
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    category: "Category" = Relationship(back_populates="listings")
    location: "Location" = Relationship(back_populates="listings")
    seller: "User" = Relationship(back_populates="listings")
    images: list["ListingImage"] = Relationship(
        back_populates="listing",
        sa_relationship_kwargs={"order_by": "ListingImage.order"},
    )


class ListingImage(SQLModel, table=True):
    __tablename__ = "listing_images"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    listing_id: UUID = Field(foreign_key="listings.id")
    url: str
    order: int = 0

    listing: Listing = Relationship(back_populates="images")
