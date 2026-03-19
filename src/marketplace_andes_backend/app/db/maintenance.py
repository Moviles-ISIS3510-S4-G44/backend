from urllib.parse import urlparse
from uuid import uuid4

from sqlmodel import SQLModel, Session, create_engine, delete, select

from ..modules.categories.models import Category
from ..modules.listings.models import Listing, ListingImage
from ..modules.locations.models import Location
from ..modules.users.models import User
from ..shared.enums import ListingCondition, ListingStatus


def _is_local_database_url(database_url: str) -> bool:
    if database_url.startswith("sqlite"):
        return True

    parsed_url = urlparse(database_url)
    host = parsed_url.hostname
    return host in {"localhost", "127.0.0.1", "db"}


def seed_database(database_url: str) -> None:
    engine = create_engine(database_url)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing_user = session.exec(select(User.id).limit(1)).first()
        if existing_user is not None:
            return

        users = [User(id=uuid4(), name="Ana"), User(id=uuid4(), name="Carlos")]
        categories = [Category(id=uuid4(), name="Books"), Category(id=uuid4(), name="Electronics")]
        locations = [Location(id=uuid4(), name="Uniandes"), Location(id=uuid4(), name="Chapinero")]

        session.add_all(users + categories + locations)
        session.commit()

        listings = [
            Listing(
                id=uuid4(),
                product_id=uuid4(),
                seller_id=users[0].id,
                category_id=categories[0].id,
                location_id=locations[0].id,
                price=50000,
                condition=ListingCondition.NEW,
                status=ListingStatus.ACTIVE,
            ),
            Listing(
                id=uuid4(),
                product_id=uuid4(),
                seller_id=users[1].id,
                category_id=categories[1].id,
                location_id=locations[1].id,
                price=1200000,
                condition=ListingCondition.USED,
                status=ListingStatus.ACTIVE,
            ),
        ]
        session.add_all(listings)
        session.commit()

        images = [
            ListingImage(listing_id=listings[0].id, url="https://picsum.photos/id/10/600/600", order=1),
            ListingImage(listing_id=listings[0].id, url="https://picsum.photos/id/11/600/600", order=2),
            ListingImage(listing_id=listings[1].id, url="https://picsum.photos/id/20/600/600", order=1),
        ]
        session.add_all(images)
        session.commit()


def clear_database(database_url: str) -> None:
    if not _is_local_database_url(database_url):
        raise ValueError("clear_database is allowed only for local database URLs.")

    engine = create_engine(database_url)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.exec(delete(ListingImage))
        session.exec(delete(Listing))
        session.exec(delete(User))
        session.exec(delete(Category))
        session.exec(delete(Location))
        session.commit()
