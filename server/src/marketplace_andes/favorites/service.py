from uuid import UUID, uuid7

from sqlmodel import Session, select

from marketplace_andes.listings.models import Listing

from .models import UserListingFavorite


class FavoriteService:
    def __init__(self, session: Session):
        self.session = session

    def listing_exists(self, listing_id: UUID) -> bool:
        statement = select(Listing).where(Listing.id == listing_id)
        return self.session.exec(statement).first() is not None

    def add_favorite(self, user_id: UUID, listing_id: UUID) -> UserListingFavorite | None:
        statement = select(UserListingFavorite).where(
            UserListingFavorite.user_id == user_id,
            UserListingFavorite.listing_id == listing_id,
        )
        existing = self.session.exec(statement).first()
        if existing:
            return existing

        favorite = UserListingFavorite(
            id=uuid7(),
            user_id=user_id,
            listing_id=listing_id,
        )
        self.session.add(favorite)
        self.session.commit()
        self.session.refresh(favorite)
        return favorite

    def remove_favorite(self, user_id: UUID, listing_id: UUID) -> None:
        statement = select(UserListingFavorite).where(
            UserListingFavorite.user_id == user_id,
            UserListingFavorite.listing_id == listing_id,
        )
        row = self.session.exec(statement).first()
        if row is None:
            return
        self.session.delete(row)
        self.session.commit()

    def list_favorite_listing_ids(self, user_id: UUID) -> list[UUID]:
        statement = (
            select(UserListingFavorite)
            .where(UserListingFavorite.user_id == user_id)
            .order_by(UserListingFavorite.created_at)
        )
        rows = self.session.exec(statement).all()
        return [f.listing_id for f in rows]
