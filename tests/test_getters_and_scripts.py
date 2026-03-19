from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool

from marketplace_andes_backend.app.db.maintenance import clear_database, seed_database
from marketplace_andes_backend.app.db.session import get_session
from marketplace_andes_backend.app.main import app
from marketplace_andes_backend.app.modules.categories.models import Category
from marketplace_andes_backend.app.modules.listings.models import Listing, ListingImage
from marketplace_andes_backend.app.modules.locations.models import Location
from marketplace_andes_backend.app.modules.users.models import User


def test_get_users_categories_locations_returns_created_items() -> None:
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

    client = TestClient(app)
    user_response = client.post("/users", json={"name": "Ana"})
    category_response = client.post("/categories", json={"name": "Books"})
    location_response = client.post("/locations", json={"name": "Uniandes"})

    users_response = client.get("/users")
    categories_response = client.get("/categories")
    locations_response = client.get("/locations")
    client.close()

    app.dependency_overrides.clear()

    assert user_response.status_code == 200
    assert category_response.status_code == 200
    assert location_response.status_code == 200
    assert users_response.status_code == 200
    assert categories_response.status_code == 200
    assert locations_response.status_code == 200

    assert len(users_response.json()) == 1
    assert users_response.json()[0]["name"] == "Ana"
    assert len(categories_response.json()) == 1
    assert categories_response.json()[0]["name"] == "Books"
    assert len(locations_response.json()) == 1
    assert locations_response.json()[0]["name"] == "Uniandes"


def test_seed_and_clear_database_scripts_behaviour() -> None:
    db_file = Path.cwd() / "test_seed_and_clear.db"
    db_url = f"sqlite:///{db_file}"
    seed_database(db_url)

    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    with Session(engine) as session:
        assert session.exec(select(User)).first() is not None
        assert session.exec(select(Category)).first() is not None
        assert session.exec(select(Location)).first() is not None
        assert session.exec(select(Listing)).first() is not None
        assert session.exec(select(ListingImage)).first() is not None

    clear_database(db_url)

    with Session(engine) as session:
        assert session.exec(select(User)).first() is None
        assert session.exec(select(Category)).first() is None
        assert session.exec(select(Location)).first() is None
        assert session.exec(select(Listing)).first() is None
        assert session.exec(select(ListingImage)).first() is None

    db_file.unlink(missing_ok=True)
