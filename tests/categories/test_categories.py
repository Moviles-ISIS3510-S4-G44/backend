import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.marketplace_andes_backend.app import app
from src.marketplace_andes_backend.categories.models import Category
from src.marketplace_andes_backend.db import get_engine, get_session


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
def test_category(session: Session) -> Category:
    category = Category(name="Books")
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


class TestCategories:
    def test_create_category_successfully(self, client: TestClient):
        response = client.post("/categories", json={"name": "Electronics"})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] > 0
        assert data["name"] == "Electronics"

    def test_list_categories(self, client: TestClient, test_category: Category):
        response = client.get("/categories")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(item["id"] == test_category.id for item in data)

    def test_get_category_by_id(self, client: TestClient, test_category: Category):
        response = client.get(f"/categories/{test_category.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_category.id
        assert data["name"] == "Books"

    def test_get_category_not_found(self, client: TestClient):
        response = client.get("/categories/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"
