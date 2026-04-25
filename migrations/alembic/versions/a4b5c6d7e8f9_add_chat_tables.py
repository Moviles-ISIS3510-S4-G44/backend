"""Add conversations and messages tables for chat.

Revision ID: a4b5c6d7e8f9
Revises: f1a9d3c6b2e4
Create Date: 2026-04-23 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a4b5c6d7e8f9"
down_revision: str | None = "f1a9d3c6b2e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(), primary_key=True, nullable=False),
        sa.Column("listing_id", postgresql.UUID(), nullable=False),
        sa.Column("buyer_id", postgresql.UUID(), nullable=False),
        sa.Column("seller_id", postgresql.UUID(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("last_message_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["buyer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("buyer_id", "listing_id", name="uq_conversations_buyer_listing"),
    )
    op.create_index("idx_conversations_buyer_id", "conversations", ["buyer_id"])
    op.create_index("idx_conversations_seller_id", "conversations", ["seller_id"])
    op.create_index("idx_conversations_listing_id", "conversations", ["listing_id"])

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(), primary_key=True, nullable=False),
        sa.Column("conversation_id", postgresql.UUID(), nullable=False),
        sa.Column("sender_id", postgresql.UUID(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["conversations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("idx_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index("idx_messages_sender_id", "messages", ["sender_id"])


def downgrade() -> None:
    op.drop_index("idx_messages_sender_id", table_name="messages")
    op.drop_index("idx_messages_conversation_id", table_name="messages")
    op.drop_table("messages")
    op.drop_index("idx_conversations_listing_id", table_name="conversations")
    op.drop_index("idx_conversations_seller_id", table_name="conversations")
    op.drop_index("idx_conversations_buyer_id", table_name="conversations")
    op.drop_table("conversations")
