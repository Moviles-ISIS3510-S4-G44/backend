from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlmodel import Session, col, select

from marketplace_andes.listings.models import Listing
from marketplace_andes.listings.service import ListingService
from marketplace_andes.users.models import UserProfile

from .models import Purchase


class PurchaseService:
    def __init__(self, session: Session):
        self.session = session

    def get_listing(self, listing_id: UUID) -> Listing | None:
        statement = select(Listing).where(Listing.id == listing_id)
        return self.session.exec(statement).first()

    def get_purchase_by_id(self, purchase_id: UUID) -> Purchase | None:
        statement = select(Purchase).where(Purchase.id == purchase_id)
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

    def get_purchases_as_seller(self, seller_id: UUID) -> list[Purchase]:
        statement = (
            select(Purchase)
            .join(Listing, Purchase.listing_id == Listing.id)
            .where(Listing.seller_id == seller_id)
            .order_by(col(Purchase.purchased_at).desc())
        )
        return list(self.session.exec(statement).all())

    def rate_seller(self, purchase_id: UUID, buyer_id: UUID, rating: int) -> Purchase | None:
        purchase = self.get_purchase_by_id(purchase_id)
        if purchase is None or purchase.buyer_id != buyer_id:
            return None

        purchase.seller_rating = rating
        self.session.add(purchase)
        self.session.flush()

        listing = self.get_listing(purchase.listing_id)
        seller_id = listing.seller_id

        all_ratings = list(
            self.session.exec(
                select(Purchase.seller_rating)
                .join(Listing, Purchase.listing_id == Listing.id)
                .where(Listing.seller_id == seller_id)
                .where(col(Purchase.seller_rating).isnot(None))
            ).all()
        )

        new_rating = round(sum(all_ratings) / len(all_ratings)) if all_ratings else 0

        profile = self.session.exec(
            select(UserProfile).where(UserProfile.id == seller_id)
        ).first()
        if profile is not None:
            profile.rating = new_rating
            self.session.add(profile)

        self.session.commit()
        self.session.refresh(purchase)
        return purchase
