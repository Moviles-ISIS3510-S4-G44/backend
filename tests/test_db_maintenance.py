from sqlmodel import Session, select

from src.marketplace_andes_backend.categories.models import Category
from src.marketplace_andes_backend.db import get_engine
from src.marketplace_andes_backend.db_maintenance import (
    REQUIRED_CATEGORIES,
    REQUIRED_USERS,
    clear_database,
    seed_database,
)
from src.marketplace_andes_backend.listings.models import Listing
from src.marketplace_andes_backend.users.models import User


def test_seed_database_creates_required_records(setup_postgres):
    with Session(get_engine()) as session:
        clear_database(session)
        seed_database(session)

        users = session.exec(select(User)).all()
        categories = session.exec(select(Category)).all()
        listings = session.exec(select(Listing)).all()

        assert len(users) == len(REQUIRED_USERS)
        assert len(categories) == len(REQUIRED_CATEGORIES)
        assert len(listings) > 0

        user_names = {user.name for user in users}
        assert user_names == {str(user["name"]) for user in REQUIRED_USERS}

        category_names = {category.name for category in categories}
        assert category_names == set(REQUIRED_CATEGORIES)

        for listing in listings:
            assert any(user.id == listing.seller_id for user in users)
            assert any(category.id == listing.category_id for category in categories)


def test_seed_database_is_idempotent(setup_postgres):
    with Session(get_engine()) as session:
        clear_database(session)
        seed_database(session)
        first_users = len(session.exec(select(User)).all())
        first_categories = len(session.exec(select(Category)).all())
        first_listings = len(session.exec(select(Listing)).all())

        seed_database(session)
        second_users = len(session.exec(select(User)).all())
        second_categories = len(session.exec(select(Category)).all())
        second_listings = len(session.exec(select(Listing)).all())

        assert second_users == first_users
        assert second_categories == first_categories
        assert second_listings == first_listings


def test_clear_database_removes_all_records(setup_postgres):
    with Session(get_engine()) as session:
        seed_database(session)
        clear_database(session)

        assert len(session.exec(select(Listing)).all()) == 0
        assert len(session.exec(select(Category)).all()) == 0
        assert len(session.exec(select(User)).all()) == 0
