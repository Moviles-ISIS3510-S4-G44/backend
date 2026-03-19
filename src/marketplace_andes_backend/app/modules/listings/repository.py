from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .models import Listing


class ListingRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_listings(self) -> list[Listing]:
        statement = (
            select(Listing)
            .options(
                selectinload(Listing.images),
                selectinload(Listing.category),
                selectinload(Listing.location),
            )
            .order_by(Listing.created_at.desc())
        )
        return list(self.session.exec(statement))
    def create_listing(self, listing: Listing) -> Listing:
        self.session.add(listing)
        self.session.commit()
        self.session.refresh(listing)
        return listing

