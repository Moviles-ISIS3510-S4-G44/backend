from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlmodel import Session, col, delete, select

from marketplace_andes.categories.models import Category
from marketplace_andes.users.models import User

from .models import Listing, ListingStatusHistory


class ListingService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, payload: Listing) -> Listing:
        self.session.add(payload)
        self.session.flush()

        history = ListingStatusHistory(
            id=uuid7(),
            listing_id=payload.id,
            from_status=None,
            to_status=payload.status,
            changed_at=payload.created_at,
        )
        self.session.add(history)
        self.session.commit()
        self.session.refresh(payload)
        return payload

    def list_all(self) -> list[Listing]:
        statement = select(Listing)
        return list(self.session.exec(statement).all())

    def get_by_id(self, listing_id: UUID) -> Listing | None:
        statement = select(Listing).where(Listing.id == listing_id)
        return self.session.exec(statement).first()

    def update_status(self, listing_id: UUID, new_status: str) -> Listing | None:
        listing = self.get_by_id(listing_id)
        if listing is None:
            return None

        now = datetime.now(UTC)
        old_status = listing.status

        history = ListingStatusHistory(
            id=uuid7(),
            listing_id=listing.id,
            from_status=old_status,
            to_status=new_status,
            changed_at=now,
        )
        self.session.add(history)

        listing.status = new_status
        listing.updated_at = now
        self.session.add(listing)
        self.session.commit()
        self.session.refresh(listing)
        return listing

    def get_history(self, listing_id: UUID) -> list[ListingStatusHistory]:
        statement = (
            select(ListingStatusHistory)
            .where(ListingStatusHistory.listing_id == listing_id)
            .order_by(col(ListingStatusHistory.changed_at))
        )
        return list(self.session.exec(statement).all())

    def seller_exists(self, seller_id: UUID) -> bool:
        statement = select(User).where(User.id == seller_id)
        return self.session.exec(statement).first() is not None

    def category_exists(self, category_id: UUID) -> bool:
        statement = select(Category).where(Category.id == category_id)
        return self.session.exec(statement).first() is not None

    def delete_all(self) -> int:
        statement = delete(Listing)
        result = self.session.exec(statement)
        self.session.commit()
        return result.rowcount or 0
