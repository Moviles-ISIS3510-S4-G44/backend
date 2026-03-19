from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.marketplace_andes_backend.app import app
from src.marketplace_andes_backend.categories.models import Category
from src.marketplace_andes_backend.db import get_engine, get_session
from src.marketplace_andes_backend.listings.models import Listing
from src.marketplace_andes_backend.users.models import User


@pytest.fixture
def session():
    engine = get_engine()
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)
    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(session: Session):
    def get_test_session():
        yield session

    app.dependency_overrides[get_session] = get_test_session

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


@pytest.fixture
def listing_seller(session: Session) -> User:
    user = User(name="Seller", email="seller@example.com", rating=5)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def listing_category(session: Session) -> Category:
    category = Category(name="Technology")
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@pytest.fixture
def test_listing(
    session: Session, listing_seller: User, listing_category: Category
) -> Listing:
    listing = Listing(
        seller_id=listing_seller.id,  # ty: ignore[invalid-argument-type]
        category_id=listing_category.id,  # ty: ignore[invalid-argument-type]
        title="Macbook Pro",
        description="M3, 16GB RAM",
        price=Decimal("4500.00"),
        condition="used",
        images='["image1.jpg"]',
        status="active",
        location="Bogotá",
    )
    session.add(listing)
    session.commit()
    session.refresh(listing)
    return listing


class TestListings:
    def test_create_listing_successfully(
        self, client: TestClient, listing_seller: User, listing_category: Category
    ):
        response = client.post(
            "/listings",
            json={
                "seller_id": listing_seller.id,
                "category_id": listing_category.id,
                "title": "iPhone 15",
                "description": "128GB, excellent condition",
                "price": "3500.50",
                "condition": "used",
                "images": '["iphone.jpg"]',
                "status": "active",
                "location": "Bogotá",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] > 0
        assert data["title"] == "iPhone 15"
        assert data["seller_id"] == listing_seller.id
        assert data["category_id"] == listing_category.id
        assert data["price"] == "3500.50"

    def test_list_listings(self, client: TestClient, test_listing: Listing):
        response = client.get("/listings")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(item["id"] == test_listing.id for item in data)

    def test_get_listing_by_id(self, client: TestClient, test_listing: Listing):
        response = client.get(f"/listings/{test_listing.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_listing.id
        assert data["title"] == "Macbook Pro"

    def test_get_listing_not_found(self, client: TestClient):
        response = client.get("/listings/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Listing not found"

    def test_create_listing_fails_with_nonexistent_seller(
        self, client: TestClient, listing_category: Category
    ):
        response = client.post(
            "/listings",
            json={
                "seller_id": 99999,
                "category_id": listing_category.id,
                "title": "Table",
                "description": "Wooden table",
                "price": "100.00",
                "condition": "used",
                "images": '["table.jpg"]',
                "status": "active",
                "location": "Medellín",
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Seller not found"

    def test_create_listing_fails_with_nonexistent_category(
        self, client: TestClient, listing_seller: User
    ):
        response = client.post(
            "/listings",
            json={
                "seller_id": listing_seller.id,
                "category_id": 99999,
                "title": "Chair",
                "description": "Desk chair",
                "price": "80.00",
                "condition": "used",
                "images": '["chair.jpg"]',
                "status": "active",
                "location": "Cali",
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"
