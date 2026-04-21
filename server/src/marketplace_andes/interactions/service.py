from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlmodel import Session, col, select

from marketplace_andes.listings.models import Listing
from marketplace_andes.users.models import User

from .models import UserListingInteraction


class InteractionService:
    def __init__(self, session: Session):
        self.session = session

    def register_interaction(
        self,
        user_id: UUID,
        listing_id: UUID,
    ) -> UserListingInteraction:
        statement = select(UserListingInteraction).where(
            UserListingInteraction.user_id == user_id,
            UserListingInteraction.listing_id == listing_id,
        )
        interaction = self.session.exec(statement).first()

        now = datetime.now(UTC)
        if interaction:
            interaction.interaction_count += 1
            interaction.last_interaction_at = now
            self.session.add(interaction)
        else:
            interaction = UserListingInteraction(
                id=uuid7(),
                user_id=user_id,
                listing_id=listing_id,
                interaction_count=1,
                first_interaction_at=now,
                last_interaction_at=now,
            )
            self.session.add(interaction)

        self.session.commit()
        self.session.refresh(interaction)
        return interaction

    def get_top_interactions_by_user(
        self,
        user_id: UUID,
        limit: int = 5,
    ) -> list[UserListingInteraction]:
        statement = (
            select(UserListingInteraction)
            .where(UserListingInteraction.user_id == user_id)
            .order_by(
                col(UserListingInteraction.interaction_count).desc(),
                col(UserListingInteraction.last_interaction_at).desc(),
            )
            .limit(limit)
        )
        return list(self.session.exec(statement).all())

    def user_exists(self, user_id: UUID) -> bool:
        statement = select(User).where(User.id == user_id)
        return self.session.exec(statement).first() is not None

    def listing_exists(self, listing_id: UUID) -> bool:
        statement = select(Listing).where(Listing.id == listing_id)
        return self.session.exec(statement).first() is not None
