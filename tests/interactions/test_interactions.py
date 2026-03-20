from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.marketplace_andes_backend.categories.models import Category
from src.marketplace_andes_backend.listings.models import Listing
from src.marketplace_andes_backend.users.models import User


def _create_user(session: Session, name: str, email: str, rating: int = 5) -> User:
    user = User(name=name, email=email, rating=rating)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _create_listing(
    session: Session,
    seller_id,
    category_id,
    title: str,
) -> Listing:
    listing = Listing(
        seller_id=seller_id,
        category_id=category_id,
        title=title,
        description="desc",
        price=Decimal("100.00"),
        condition="used",
        images='["img.jpg"]',
        status="active",
        location="Bogotá",
    )
    session.add(listing)
    session.commit()
    session.refresh(listing)
    return listing


class TestInteractions:
    def test_register_interaction_creates_new_record(
        self,
        client: TestClient,
        session: Session,
    ):
        user = _create_user(session, "Buyer", "buyer@example.com")
        seller = _create_user(session, "Seller", "seller@example.com")

        category = Category(name="Technology")
        session.add(category)
        session.commit()
        session.refresh(category)

        listing = _create_listing(session, seller.id, category.id, "Laptop")

        response = client.post(
            "/interactions",
            json={"user_id": str(user.id), "listing_id": str(listing.id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(user.id)
        assert data["listing_id"] == str(listing.id)
        assert data["interaction_count"] == 1

    def test_register_interaction_increments_existing_record(
        self,
        client: TestClient,
        session: Session,
    ):
        user = _create_user(session, "Buyer2", "buyer2@example.com")
        seller = _create_user(session, "Seller2", "seller2@example.com")

        category = Category(name="Home")
        session.add(category)
        session.commit()
        session.refresh(category)

        listing = _create_listing(session, seller.id, category.id, "Chair")

        first_response = client.post(
            "/interactions",
            json={"user_id": str(user.id), "listing_id": str(listing.id)},
        )
        first_time = datetime.fromisoformat(
            first_response.json()["last_interaction_at"].replace("Z", "+00:00")
        )

        second_response = client.post(
            "/interactions",
            json={"user_id": str(user.id), "listing_id": str(listing.id)},
        )

        assert second_response.status_code == 200
        data = second_response.json()
        second_time = datetime.fromisoformat(
            data["last_interaction_at"].replace("Z", "+00:00")
        )

        assert data["interaction_count"] == 2
        assert second_time >= first_time

    def test_get_top_four_interactions_by_user(
        self,
        client: TestClient,
        session: Session,
    ):
        user = _create_user(session, "Buyer3", "buyer3@example.com")
        seller = _create_user(session, "Seller3", "seller3@example.com")

        category = Category(name="Mixed")
        session.add(category)
        session.commit()
        session.refresh(category)

        listings = [
            _create_listing(session, seller.id, category.id, f"Item {index}")
            for index in range(5)
        ]

        for listing_index, listing in enumerate(listings, start=1):
            for _ in range(listing_index):
                response = client.post(
                    "/interactions",
                    json={"user_id": str(user.id), "listing_id": str(listing.id)},
                )
                assert response.status_code == 200

        response = client.get(f"/interactions/users/{user.id}/top")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

        counts = [item["interaction_count"] for item in data]
        assert counts == sorted(counts, reverse=True)
        assert counts == [5, 4, 3, 2]

    def test_register_interaction_fails_when_user_not_found(
        self,
        client: TestClient,
        session: Session,
    ):
        seller = _create_user(session, "Seller4", "seller4@example.com")
        category = Category(name="Sports")
        session.add(category)
        session.commit()
        session.refresh(category)

        listing = _create_listing(session, seller.id, category.id, "Ball")

        response = client.post(
            "/interactions",
            json={
                "user_id": "00000000-0000-0000-0000-000000000001",
                "listing_id": str(listing.id),
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_register_interaction_fails_when_listing_not_found(
        self,
        client: TestClient,
        session: Session,
    ):
        user = _create_user(session, "Buyer5", "buyer5@example.com")

        response = client.post(
            "/interactions",
            json={
                "user_id": str(user.id),
                "listing_id": "00000000-0000-0000-0000-000000000001",
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Listing not found"

    def test_get_top_interactions_fails_when_user_not_found(self, client: TestClient):
        response = client.get(
            "/interactions/users/00000000-0000-0000-0000-000000000001/top"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"
