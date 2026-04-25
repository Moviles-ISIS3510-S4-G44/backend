from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    __table_args__ = (
        sa.UniqueConstraint("buyer_id", "listing_id", name="uq_conversations_buyer_listing"),
        sa.Index("idx_conversations_buyer_id", "buyer_id"),
        sa.Index("idx_conversations_seller_id", "seller_id"),
        sa.Index("idx_conversations_listing_id", "listing_id"),
    )

    id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
    )
    listing_id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    buyer_id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    seller_id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    created_at: datetime = Field(
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
    last_message_at: datetime = Field(
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )


class Message(SQLModel, table=True):
    __tablename__ = "messages"
    __table_args__ = (
        sa.Index("idx_messages_conversation_id", "conversation_id"),
        sa.Index("idx_messages_sender_id", "sender_id"),
    )

    id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
    )
    conversation_id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    sender_id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    body: str = Field(
        sa_column=sa.Column(
            sa.Text(),
            nullable=False,
        ),
    )
    sent_at: datetime = Field(
        sa_column=sa.Column(
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
