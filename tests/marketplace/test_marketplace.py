import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from uuid import UUID

from src.marketplace_andes_backend.auth.service import AuthService
from src.marketplace_andes_backend.marketplace.models import (
    Listing,
    MarketplaceTransaction,
    Message,
    Review,
    SearchEvent,
    UserActivityEvent,
)
from src.marketplace_andes_backend.users.models import User


@pytest.fixture
def seller(session: Session) -> User:
    return AuthService(session).signup(
        name="Seller",
        email="seller@example.com",
        password="secret123",
    )


@pytest.fixture
def buyer(session: Session) -> User:
    return AuthService(session).signup(
        name="Buyer",
        email="buyer@example.com",
        password="secret123",
    )


@pytest.fixture
def seller_headers(client: TestClient, seller: User) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        data={"username": seller.email, "password": "secret123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def buyer_headers(client: TestClient, buyer: User) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        data={"username": buyer.email, "password": "secret123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


class TestMarketplaceRoutes:
    def test_marketplace_flow_captures_operational_events(
        self,
        client: TestClient,
        session: Session,
        seller: User,
        buyer: User,
        seller_headers: dict[str, str],
        buyer_headers: dict[str, str],
    ):
        university_response = client.post(
            "/marketplace/universities",
            json={"name": "Uniandes", "country": "Colombia", "city": "Bogota"},
            headers=seller_headers,
        )
        assert university_response.status_code == 201
        university_id = university_response.json()["id"]

        program_response = client.post(
            "/marketplace/programs",
            json={
                "university_id": university_id,
                "name": "Systems Engineering",
                "faculty": "Engineering",
            },
            headers=seller_headers,
        )
        assert program_response.status_code == 201

        category_response = client.post(
            "/marketplace/categories",
            json={"name": "Books", "slug": "books"},
            headers=seller_headers,
        )
        assert category_response.status_code == 201
        category_id = UUID(category_response.json()["id"])

        listing_response = client.post(
            "/marketplace/listings",
            json={
                "category_id": str(category_id),
                "title": "Calculus Notes",
                "description": "Complete set of notes",
                "product_type": "notes",
                "condition": "used",
                "price": "50000",
                "currency": "COP",
                "is_negotiable": True,
                "is_digital": True,
                "quantity_available": 1,
                "campus_pickup_point": "ML Building",
                "media_urls": ["https://example.com/notes.png"],
            },
            headers=seller_headers,
        )
        assert listing_response.status_code == 201
        listing_id = UUID(listing_response.json()["id"])

        thread_response = client.post(
            "/marketplace/threads",
            json={"listing_id": str(listing_id)},
            headers=buyer_headers,
        )
        assert thread_response.status_code == 201
        thread_id = UUID(thread_response.json()["id"])

        message_response = client.post(
            f"/marketplace/threads/{thread_id}/messages",
            json={"body": "Is this still available?"},
            headers=buyer_headers,
        )
        assert message_response.status_code == 201

        transaction_response = client.post(
            "/marketplace/transactions",
            json={"listing_id": str(listing_id), "agreed_price": "45000", "currency": "COP"},
            headers=buyer_headers,
        )
        assert transaction_response.status_code == 201
        transaction_id = UUID(transaction_response.json()["id"])

        complete_response = client.post(
            f"/marketplace/transactions/{transaction_id}/complete",
            headers=seller_headers,
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["status"] == "completed"

        review_response = client.post(
            "/marketplace/reviews",
            json={"transaction_id": str(transaction_id), "rating": 5, "comment": "Great seller"},
            headers=buyer_headers,
        )
        assert review_response.status_code == 201

        search_response = client.post(
            "/marketplace/searches",
            json={
                "category_id": str(category_id),
                "query_text": "calculus",
                "sort_mode": "recent",
                "results_count": 1,
            },
            headers=buyer_headers,
        )
        assert search_response.status_code == 201

        snapshot_response = client.get("/marketplace/snapshot", headers=seller_headers)
        assert snapshot_response.status_code == 200
        snapshot = snapshot_response.json()
        assert len(snapshot["universities"]) == 1
        assert len(snapshot["programs"]) == 1
        assert len(snapshot["categories"]) == 1
        assert len(snapshot["listings"]) == 1
        assert len(snapshot["transactions"]) == 1
        assert len(snapshot["threads"]) == 1
        assert len(snapshot["messages"]) == 1
        assert len(snapshot["reviews"]) == 1
        assert len(snapshot["searches"]) == 1
        assert len(snapshot["activities"]) >= 5

        listing = session.exec(select(Listing).where(Listing.id == listing_id)).first()
        assert listing is not None
        assert listing.status == "sold"
        assert listing.sold_at is not None

        transaction = session.exec(
            select(MarketplaceTransaction).where(MarketplaceTransaction.id == transaction_id)
        ).first()
        assert transaction is not None
        assert transaction.completed_at is not None

        stored_message = session.exec(select(Message)).first()
        assert stored_message is not None

        stored_review = session.exec(select(Review)).first()
        assert stored_review is not None
        assert stored_review.reviewee_id == seller.id

        stored_search = session.exec(select(SearchEvent)).first()
        assert stored_search is not None
        assert stored_search.query_text == "calculus"

        activities = session.exec(select(UserActivityEvent)).all()
        activity_types = {activity.event_type for activity in activities}
        assert {"login", "listing_created", "message", "transaction", "search"}.issubset(
            activity_types
        )

        refreshed_seller = session.exec(select(User).where(User.id == seller.id)).first()
        assert refreshed_seller is not None
        assert refreshed_seller.rating == 5
        assert refreshed_seller.last_login_at is not None

    def test_duplicate_category_slug_is_rejected(
        self,
        client: TestClient,
        seller_headers: dict[str, str],
    ):
        first_response = client.post(
            "/marketplace/categories",
            json={"name": "Books", "slug": "books"},
            headers=seller_headers,
        )
        assert first_response.status_code == 201

        second_response = client.post(
            "/marketplace/categories",
            json={"name": "Duplicate Books", "slug": "books"},
            headers=seller_headers,
        )
        assert second_response.status_code == 409
        assert second_response.json()["detail"] == "Resource conflict"
