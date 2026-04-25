from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlmodel import Session, col, delete, select

from marketplace_andes.categories.models import Category
from marketplace_andes.users.models import User

from .enums import ListingCondition
from .models import Listing, ListingStatusHistory
from .schemas import ListingUpdateRequest


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

    def search(
        self,
        q: str | None = None,
        category_id: UUID | None = None,
        condition: ListingCondition | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        location: str | None = None,
        status: str | None = None,
    ) -> list[Listing]:
        statement = select(Listing)
        if q is not None:
            statement = statement.where(col(Listing.title).ilike(f"%{q}%"))
        if category_id is not None:
            statement = statement.where(Listing.category_id == category_id)
        if condition is not None:
            statement = statement.where(Listing.condition == condition)
        if min_price is not None:
            statement = statement.where(Listing.price >= min_price)
        if max_price is not None:
            statement = statement.where(Listing.price <= max_price)
        if location is not None:
            statement = statement.where(col(Listing.location).ilike(f"%{location}%"))
        if status is not None:
            statement = statement.where(Listing.status == status)
        return list(self.session.exec(statement).all())

    def get_by_id(self, listing_id: UUID) -> Listing | None:
        statement = select(Listing).where(Listing.id == listing_id)
        return self.session.exec(statement).first()

    def get_by_seller(self, seller_id: UUID) -> list[Listing]:
        statement = (
            select(Listing)
            .where(Listing.seller_id == seller_id)
            .order_by(col(Listing.created_at).desc())
        )
        return list(self.session.exec(statement).all())

    def update_listing(self, listing_id: UUID, payload: ListingUpdateRequest) -> Listing | None:
        listing = self.get_by_id(listing_id)
        if listing is None:
            return None

        now = datetime.now(UTC)
        if payload.category_id is not None:
            listing.category_id = payload.category_id
        if payload.title is not None:
            listing.title = payload.title
        if payload.description is not None:
            listing.description = payload.description
        if payload.price is not None:
            listing.price = payload.price
        if payload.condition is not None:
            listing.condition = payload.condition
        if payload.images is not None:
            listing.images = payload.images
        if payload.location is not None:
            listing.location = payload.location

        listing.updated_at = now
        self.session.add(listing)
        self.session.commit()
        self.session.refresh(listing)
        return listing

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
