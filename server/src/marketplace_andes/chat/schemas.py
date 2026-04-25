from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ConversationCreateRequest(BaseModel):
    listing_id: UUID


class ParticipantInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    listing_id: UUID
    buyer_id: UUID
    seller_id: UUID
    created_at: datetime
    last_message_at: datetime
    other_user: ParticipantInfo
    listing_title: str
    last_message_body: str | None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    sender_id: UUID
    body: str
    sent_at: datetime


class WsIncomingMessage(BaseModel):
    body: str


class WsOutgoingMessage(BaseModel):
    event: str = "new_message"
    id: str
    conversation_id: str
    sender_id: str
    body: str
    sent_at: str
