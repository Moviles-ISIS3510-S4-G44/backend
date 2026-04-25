from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlmodel import Session, col, select

from marketplace_andes.listings.models import Listing
from marketplace_andes.listings.service import ListingService

from .models import Purchase


class PurchaseService:
    def __init__(self, session: Session):
        self.session = session

    def get_listing(self, listing_id: UUID) -> Listing | None:
        statement = select(Listing).where(Listing.id == listing_id)
        return self.session.exec(statement).first()

    def already_purchased(self, listing_id: UUID) -> bool:
        statement = select(Purchase).where(Purchase.listing_id == listing_id)
        return self.session.exec(statement).first() is not None

    def create_purchase(self, buyer_id: UUID, listing_id: UUID) -> Purchase:
        listing = self.get_listing(listing_id)

        purchase = Purchase(
            id=uuid7(),
            listing_id=listing_id,
            buyer_id=buyer_id,
            price_at_purchase=listing.price,
            purchased_at=datetime.now(UTC),
        )
        self.session.add(purchase)
        self.session.flush()

        ListingService(self.session).update_status(listing_id, "sold")

        self.session.refresh(purchase)
        return purchase

    def get_purchases_by_buyer(self, buyer_id: UUID) -> list[Purchase]:
        statement = (
            select(Purchase)
            .where(Purchase.buyer_id == buyer_id)
            .order_by(col(Purchase.purchased_at).desc())
        )
        return list(self.session.exec(statement).all())
