from uuid import UUID

from sqlmodel import Session, select

from src.marketplace_andes_backend.categories.models import Category
from src.marketplace_andes_backend.users.models import User

from .models import Listing


class ListingService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, payload: Listing) -> Listing:
        self.session.add(payload)
        self.session.commit()
        self.session.refresh(payload)
        return payload

    def list_all(self) -> list[Listing]:
        statement = select(Listing)
        return list(self.session.exec(statement).all())

    def get_by_id(self, listing_id: UUID) -> Listing | None:
        statement = select(Listing).where(Listing.id == listing_id)
        return self.session.exec(statement).first()

    def user_exists(self, user_id: UUID) -> bool:
        statement = select(User).where(User.id == user_id)
        return self.session.exec(statement).first() is not None

    def category_exists(self, category_id: UUID) -> bool:
        statement = select(Category).where(Category.id == category_id)
        return self.session.exec(statement).first() is not None
