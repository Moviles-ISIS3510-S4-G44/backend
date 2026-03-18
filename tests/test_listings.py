from collections.abc import Generator
from uuid import UUID
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from marketplace_andes_backend.app.db.session import get_session
from marketplace_andes_backend.app.main import app
from marketplace_andes_backend.app.modules.categories.models import Category
from marketplace_andes_backend.app.modules.listings.models import Listing, ListingImage
from marketplace_andes_backend.app.modules.locations.models import Location
from marketplace_andes_backend.app.modules.users.models import User
from marketplace_andes_backend.app.shared.enums import ListingCondition, ListingStatus


def test_get_listings_returns_expected_shape() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        category = Category(name="Books")
        location = Location(name="Uniandes")
        user = User(name="Ana")

        listing = Listing(
            product_id=uuid4(),
            seller_id=user.id,
            category_id=category.id,
            location_id=location.id,
            price=50000,
            condition=ListingCondition.NEW,
            status=ListingStatus.ACTIVE,
        )
        image_1 = ListingImage(listing_id=listing.id, url="url1", order=1)
        image_2 = ListingImage(listing_id=listing.id, url="url2", order=2)

        session.add(category)
        session.add(location)
        session.add(user)
        session.add(listing)
        session.add(image_1)
        session.add(image_2)
        session.commit()

    def override_get_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        response = client.get("/listings")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1

    first_item = data["items"][0]
    UUID(first_item["id"])
    assert first_item["price"] == 50000
    assert first_item["condition"] == "new"
    assert first_item["status"] == "active"
    assert first_item["images"] == ["url1", "url2"]
    UUID(first_item["category"]["id"])
    assert first_item["category"]["name"] == "Books"
    UUID(first_item["location"]["id"])
    assert first_item["location"]["name"] == "Uniandes"
