from uuid import UUID

from sqlmodel import Session, col, select

from marketplace_andes.listings.models import Listing
from marketplace_andes.users.models import UserProfile

from .models import Conversation, Message


class ChatRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_conversation_by_id(self, conversation_id: UUID) -> Conversation | None:
        return self.session.exec(
            select(Conversation).where(Conversation.id == conversation_id)
        ).first()

    def get_conversation_by_buyer_and_listing(
        self, buyer_id: UUID, listing_id: UUID
    ) -> Conversation | None:
        return self.session.exec(
            select(Conversation).where(
                Conversation.buyer_id == buyer_id,
                Conversation.listing_id == listing_id,
            )
        ).first()

    def get_conversations_for_user(self, user_id: UUID) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(
                (Conversation.buyer_id == user_id) | (Conversation.seller_id == user_id)
            )
            .order_by(col(Conversation.last_message_at).desc())
        )
        return list(self.session.exec(stmt).all())

    def get_messages_for_conversation(
        self, conversation_id: UUID, limit: int = 50
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(col(Message.sent_at).asc())
            .limit(limit)
        )
        return list(self.session.exec(stmt).all())

    def get_last_message(self, conversation_id: UUID) -> Message | None:
        return self.session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(col(Message.sent_at).desc())
            .limit(1)
        ).first()

    def get_user_profile(self, user_id: UUID) -> UserProfile | None:
        return self.session.exec(
            select(UserProfile).where(UserProfile.id == user_id)
        ).first()

    def get_listing(self, listing_id: UUID) -> Listing | None:
        return self.session.exec(
            select(Listing).where(Listing.id == listing_id)
        ).first()
