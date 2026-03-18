from collections.abc import Generator
from uuid import UUID
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from marketplace_andes_backend.app.db.session import get_session
from marketplace_andes_backend.app.main import app
from marketplace_andes_backend.app.modules.listings.models import Listing, ListingImage
from marketplace_andes_backend.app.shared.enums import ListingCondition, ListingStatus


def test_post_users_categories_locations_and_use_ids_in_listing() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        user_response = client.post("/users", json={"name": "Ana"})
        category_response = client.post("/categories", json={"name": "Books"})
        location_response = client.post("/locations", json={"name": "Uniandes"})

    assert user_response.status_code == 200
    assert category_response.status_code == 200
    assert location_response.status_code == 200

    user_data = user_response.json()
    category_data = category_response.json()
    location_data = location_response.json()

    user_id = UUID(user_data["id"])
    category_id = UUID(category_data["id"])
    location_id = UUID(location_data["id"])

    assert user_data["name"] == "Ana"
    assert category_data["name"] == "Books"
    assert location_data["name"] == "Uniandes"

    with Session(engine) as session:
        listing = Listing(
            product_id=uuid4(),
            seller_id=user_id,
            category_id=category_id,
            location_id=location_id,
            price=50000,
            condition=ListingCondition.NEW,
            status=ListingStatus.ACTIVE,
        )
        image = ListingImage(listing_id=listing.id, url="url1", order=1)
        session.add(listing)
        session.add(image)
        session.commit()

    with TestClient(app) as client:
        listings_response = client.get("/listings")

    app.dependency_overrides.clear()

    assert listings_response.status_code == 200
    data = listings_response.json()
    assert data["total"] == 1
    assert data["items"][0]["category"]["name"] == "Books"
    assert data["items"][0]["location"]["name"] == "Uniandes"
