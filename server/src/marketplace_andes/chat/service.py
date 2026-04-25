from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session
from uuid import uuid7

from .models import Conversation, Message
from .repository import ChatRepository
from .schemas import ConversationResponse, MessageResponse, ParticipantInfo


class MessageBodyEmptyError(ValueError):
    pass


class ChatService:
    def __init__(self, session: Session):
        self.repo = ChatRepository(session)
        self.session = session

    def get_or_create_conversation(
        self, buyer_id: UUID, listing_id: UUID
    ) -> tuple[Conversation, bool]:
        existing = self.repo.get_conversation_by_buyer_and_listing(buyer_id, listing_id)
        if existing:
            return existing, False

        listing = self.repo.get_listing(listing_id)
        if listing is None:
            raise ValueError("listing_not_found")
        if listing.seller_id == buyer_id:
            raise ValueError("cannot_message_own_listing")

        now = datetime.now(UTC)
        conversation = Conversation(
            id=uuid7(),
            listing_id=listing_id,
            buyer_id=buyer_id,
            seller_id=listing.seller_id,
            created_at=now,
            last_message_at=now,
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation, True

    def list_conversations_for_user(self, user_id: UUID) -> list[ConversationResponse]:
        conversations = self.repo.get_conversations_for_user(user_id)
        result = []
        for conv in conversations:
            other_user_id = (
                conv.seller_id if conv.buyer_id == user_id else conv.buyer_id
            )
            other_profile = self.repo.get_user_profile(other_user_id)
            listing = self.repo.get_listing(conv.listing_id)
            last_msg = self.repo.get_last_message(conv.id)
            result.append(
                ConversationResponse(
                    id=conv.id,
                    listing_id=conv.listing_id,
                    buyer_id=conv.buyer_id,
                    seller_id=conv.seller_id,
                    created_at=conv.created_at,
                    last_message_at=conv.last_message_at,
                    other_user=ParticipantInfo(
                        id=other_user_id,
                        name=other_profile.name if other_profile else "Unknown",
                    ),
                    listing_title=listing.title if listing else "Listing unavailable",
                    last_message_body=last_msg.body if last_msg else None,
                )
            )
        return result

    def get_conversation_for_user(
        self, conversation_id: UUID, user_id: UUID
    ) -> ConversationResponse | None:
        conv = self.repo.get_conversation_by_id(conversation_id)
        if conv is None:
            return None
        if conv.buyer_id != user_id and conv.seller_id != user_id:
            return None

        other_user_id = conv.seller_id if conv.buyer_id == user_id else conv.buyer_id
        other_profile = self.repo.get_user_profile(other_user_id)
        listing = self.repo.get_listing(conv.listing_id)
        last_msg = self.repo.get_last_message(conv.id)
        return ConversationResponse(
            id=conv.id,
            listing_id=conv.listing_id,
            buyer_id=conv.buyer_id,
            seller_id=conv.seller_id,
            created_at=conv.created_at,
            last_message_at=conv.last_message_at,
            other_user=ParticipantInfo(
                id=other_user_id,
                name=other_profile.name if other_profile else "Unknown",
            ),
            listing_title=listing.title if listing else "Listing unavailable",
            last_message_body=last_msg.body if last_msg else None,
        )

    def list_messages(self, conversation_id: UUID) -> list[MessageResponse]:
        messages = self.repo.get_messages_for_conversation(conversation_id)
        return [MessageResponse.model_validate(m) for m in messages]

    def get_conversation(self, conversation_id: UUID) -> Conversation | None:
        return self.repo.get_conversation_by_id(conversation_id)

    def conversation_exists(self, conversation_id: UUID) -> bool:
        return self.get_conversation(conversation_id) is not None

    def save_message(
        self, conversation_id: UUID, sender_id: UUID, body: str
    ) -> Message:
        normalized_body = body.strip()
        if not normalized_body:
            raise MessageBodyEmptyError(
                "Message body cannot be empty or contain only whitespace"
            )

        now = datetime.now(UTC)
        message = Message(
            id=uuid7(),
            conversation_id=conversation_id,
            sender_id=sender_id,
            body=normalized_body,
            sent_at=now,
        )
        self.session.add(message)

        conv = self.repo.get_conversation_by_id(conversation_id)
        if conv:
            conv.last_message_at = now
            self.session.add(conv)

        self.session.commit()
        self.session.refresh(message)
        return message

    def user_is_participant(self, conversation_id: UUID, user_id: UUID) -> bool:
        conv = self.get_conversation(conversation_id)
        if conv is None:
            return False
        return conv.buyer_id == user_id or conv.seller_id == user_id
