from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session, desc, select

from src.marketplace_andes_backend.listings.models import Listing
from src.marketplace_andes_backend.users.models import User

from .models import UserListingInteraction


class InteractionService:
    def __init__(self, session: Session):
        self.session = session

    def user_exists(self, user_id: UUID) -> bool:
        statement = select(User).where(User.id == user_id)
        return self.session.exec(statement).first() is not None

    def listing_exists(self, listing_id: UUID) -> bool:
        statement = select(Listing).where(Listing.id == listing_id)
        return self.session.exec(statement).first() is not None

    def get_by_user_and_listing(
        self, user_id: UUID, listing_id: UUID
    ) -> UserListingInteraction | None:
        statement = select(UserListingInteraction).where(
            UserListingInteraction.user_id == user_id,
            UserListingInteraction.listing_id == listing_id,
        )
        return self.session.exec(statement).first()

    def register_interaction(self, user_id: UUID, listing_id: UUID) -> UserListingInteraction:
        interaction = self.get_by_user_and_listing(user_id=user_id, listing_id=listing_id)

        if interaction:
            interaction.interaction_count += 1
            interaction.last_interaction_at = datetime.now(timezone.utc)
            self.session.add(interaction)
        else:
            interaction = UserListingInteraction(
                user_id=user_id,
                listing_id=listing_id,
                interaction_count=1,
                last_interaction_at=datetime.now(timezone.utc),
            )
            self.session.add(interaction)

        self.session.commit()
        self.session.refresh(interaction)
        return interaction

    def get_top_interactions_by_user(self, user_id: UUID) -> list[UserListingInteraction]:
        statement = (
            select(UserListingInteraction)
            .where(UserListingInteraction.user_id == user_id)
            .order_by(desc(UserListingInteraction.interaction_count))
            .limit(4)
        )
        return list(self.session.exec(statement).all())
