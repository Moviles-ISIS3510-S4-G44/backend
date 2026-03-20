"""Add marketplace operational schema

Revision ID: c4b7e9a21f6d
Revises: 8f3c0a4d2c1b
Create Date: 2026-03-19 18:40:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlmodel.sql.sqltypes import AutoString


revision: str = "c4b7e9a21f6d"
down_revision: str | Sequence[str] | None = "8f3c0a4d2c1b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "university",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", AutoString(), nullable=False),
        sa.Column("country", AutoString(), nullable=False),
        sa.Column("city", AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_university_name"), "university", ["name"], unique=False)

    op.create_table(
        "program",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("university_id", sa.Uuid(), nullable=False),
        sa.Column("name", AutoString(), nullable=False),
        sa.Column("faculty", AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["university_id"], ["university.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_program_university_id"), "program", ["university_id"], unique=False)

    op.add_column("user", sa.Column("university_id", sa.Uuid(), nullable=True))
    op.add_column("user", sa.Column("program_id", sa.Uuid(), nullable=True))
    op.add_column(
        "user",
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("user", sa.Column("student_code", AutoString(), nullable=True))
    op.add_column(
        "user",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("TIMEZONE('utc', NOW())")),
    )
    op.add_column("user", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_user_university_id"), "user", ["university_id"], unique=False)
    op.create_index(op.f("ix_user_program_id"), "user", ["program_id"], unique=False)
    op.create_foreign_key(None, "user", "university", ["university_id"], ["id"])
    op.create_foreign_key(None, "user", "program", ["program_id"], ["id"])
    op.alter_column("user", "is_verified", server_default=None)
    op.alter_column("user", "created_at", server_default=None)

    op.create_table(
        "category",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("parent_category_id", sa.Uuid(), nullable=True),
        sa.Column("name", AutoString(), nullable=False),
        sa.Column("slug", AutoString(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["parent_category_id"], ["category.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_category_parent_category_id"), "category", ["parent_category_id"], unique=False)
    op.create_index(op.f("ix_category_slug"), "category", ["slug"], unique=True)

    op.create_table(
        "listing",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("seller_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("title", AutoString(), nullable=False),
        sa.Column("description", AutoString(), nullable=False),
        sa.Column("product_type", AutoString(), nullable=False),
        sa.Column("condition", AutoString(), nullable=False),
        sa.Column("price", sa.Numeric(), nullable=False),
        sa.Column("currency", AutoString(), nullable=False),
        sa.Column("status", AutoString(), nullable=False),
        sa.Column("is_negotiable", sa.Boolean(), nullable=False),
        sa.Column("is_digital", sa.Boolean(), nullable=False),
        sa.Column("quantity_available", sa.Integer(), nullable=False),
        sa.Column("campus_pickup_point", AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sold_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_listing_seller_id"), "listing", ["seller_id"], unique=False)
    op.create_index(op.f("ix_listing_category_id"), "listing", ["category_id"], unique=False)
    op.create_index(op.f("ix_listing_status"), "listing", ["status"], unique=False)

    op.create_table(
        "listing_media",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("asset_url", AutoString(), nullable=False),
        sa.Column("media_type", AutoString(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["listing.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_listing_media_listing_id"), "listing_media", ["listing_id"], unique=False)

    op.create_table(
        "listing_status_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("changed_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("from_status", AutoString(), nullable=True),
        sa.Column("to_status", AutoString(), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["changed_by_user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["listing_id"], ["listing.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_listing_status_history_listing_id"), "listing_status_history", ["listing_id"], unique=False)
    op.create_index(op.f("ix_listing_status_history_changed_by_user_id"), "listing_status_history", ["changed_by_user_id"], unique=False)

    op.create_table(
        "marketplace_transaction",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("buyer_id", sa.Uuid(), nullable=False),
        sa.Column("seller_id", sa.Uuid(), nullable=False),
        sa.Column("listed_price", sa.Numeric(), nullable=False),
        sa.Column("agreed_price", sa.Numeric(), nullable=False),
        sa.Column("currency", AutoString(), nullable=False),
        sa.Column("status", AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["buyer_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["listing_id"], ["listing.id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_marketplace_transaction_listing_id"), "marketplace_transaction", ["listing_id"], unique=False)
    op.create_index(op.f("ix_marketplace_transaction_buyer_id"), "marketplace_transaction", ["buyer_id"], unique=False)
    op.create_index(op.f("ix_marketplace_transaction_seller_id"), "marketplace_transaction", ["seller_id"], unique=False)
    op.create_index(op.f("ix_marketplace_transaction_status"), "marketplace_transaction", ["status"], unique=False)

    op.create_table(
        "message_thread",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("buyer_id", sa.Uuid(), nullable=False),
        sa.Column("seller_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["buyer_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["listing_id"], ["listing.id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_message_thread_listing_id"), "message_thread", ["listing_id"], unique=False)
    op.create_index(op.f("ix_message_thread_buyer_id"), "message_thread", ["buyer_id"], unique=False)
    op.create_index(op.f("ix_message_thread_seller_id"), "message_thread", ["seller_id"], unique=False)

    op.create_table(
        "message",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("thread_id", sa.Uuid(), nullable=False),
        sa.Column("sender_id", sa.Uuid(), nullable=False),
        sa.Column("body", AutoString(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["sender_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["thread_id"], ["message_thread.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_message_thread_id"), "message", ["thread_id"], unique=False)
    op.create_index(op.f("ix_message_sender_id"), "message", ["sender_id"], unique=False)

    op.create_table(
        "review",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("transaction_id", sa.Uuid(), nullable=False),
        sa.Column("reviewer_id", sa.Uuid(), nullable=False),
        sa.Column("reviewee_id", sa.Uuid(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["reviewee_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["reviewer_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["marketplace_transaction.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_review_transaction_id"), "review", ["transaction_id"], unique=False)
    op.create_index(op.f("ix_review_reviewer_id"), "review", ["reviewer_id"], unique=False)
    op.create_index(op.f("ix_review_reviewee_id"), "review", ["reviewee_id"], unique=False)

    op.create_table(
        "search_event",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("query_text", AutoString(), nullable=False),
        sa.Column("sort_mode", AutoString(), nullable=True),
        sa.Column("results_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_search_event_user_id"), "search_event", ["user_id"], unique=False)
    op.create_index(op.f("ix_search_event_category_id"), "search_event", ["category_id"], unique=False)

    op.create_table(
        "user_activity_event",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("listing_id", sa.Uuid(), nullable=True),
        sa.Column("transaction_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["listing.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["marketplace_transaction.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_activity_event_user_id"), "user_activity_event", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_activity_event_listing_id"), "user_activity_event", ["listing_id"], unique=False)
    op.create_index(op.f("ix_user_activity_event_transaction_id"), "user_activity_event", ["transaction_id"], unique=False)
    op.create_index(op.f("ix_user_activity_event_event_type"), "user_activity_event", ["event_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_activity_event_event_type"), table_name="user_activity_event")
    op.drop_index(op.f("ix_user_activity_event_transaction_id"), table_name="user_activity_event")
    op.drop_index(op.f("ix_user_activity_event_listing_id"), table_name="user_activity_event")
    op.drop_index(op.f("ix_user_activity_event_user_id"), table_name="user_activity_event")
    op.drop_table("user_activity_event")

    op.drop_index(op.f("ix_search_event_category_id"), table_name="search_event")
    op.drop_index(op.f("ix_search_event_user_id"), table_name="search_event")
    op.drop_table("search_event")

    op.drop_index(op.f("ix_review_reviewee_id"), table_name="review")
    op.drop_index(op.f("ix_review_reviewer_id"), table_name="review")
    op.drop_index(op.f("ix_review_transaction_id"), table_name="review")
    op.drop_table("review")

    op.drop_index(op.f("ix_message_sender_id"), table_name="message")
    op.drop_index(op.f("ix_message_thread_id"), table_name="message")
    op.drop_table("message")

    op.drop_index(op.f("ix_message_thread_seller_id"), table_name="message_thread")
    op.drop_index(op.f("ix_message_thread_buyer_id"), table_name="message_thread")
    op.drop_index(op.f("ix_message_thread_listing_id"), table_name="message_thread")
    op.drop_table("message_thread")

    op.drop_index(op.f("ix_marketplace_transaction_status"), table_name="marketplace_transaction")
    op.drop_index(op.f("ix_marketplace_transaction_seller_id"), table_name="marketplace_transaction")
    op.drop_index(op.f("ix_marketplace_transaction_buyer_id"), table_name="marketplace_transaction")
    op.drop_index(op.f("ix_marketplace_transaction_listing_id"), table_name="marketplace_transaction")
    op.drop_table("marketplace_transaction")

    op.drop_index(op.f("ix_listing_status_history_changed_by_user_id"), table_name="listing_status_history")
    op.drop_index(op.f("ix_listing_status_history_listing_id"), table_name="listing_status_history")
    op.drop_table("listing_status_history")

    op.drop_index(op.f("ix_listing_media_listing_id"), table_name="listing_media")
    op.drop_table("listing_media")

    op.drop_index(op.f("ix_listing_status"), table_name="listing")
    op.drop_index(op.f("ix_listing_category_id"), table_name="listing")
    op.drop_index(op.f("ix_listing_seller_id"), table_name="listing")
    op.drop_table("listing")

    op.drop_index(op.f("ix_category_slug"), table_name="category")
    op.drop_index(op.f("ix_category_parent_category_id"), table_name="category")
    op.drop_table("category")

    op.drop_constraint("user_program_id_fkey", "user", type_="foreignkey")
    op.drop_constraint("user_university_id_fkey", "user", type_="foreignkey")
    op.drop_index(op.f("ix_user_program_id"), table_name="user")
    op.drop_index(op.f("ix_user_university_id"), table_name="user")
    op.drop_column("user", "last_login_at")
    op.drop_column("user", "created_at")
    op.drop_column("user", "student_code")
    op.drop_column("user", "is_verified")
    op.drop_column("user", "program_id")
    op.drop_column("user", "university_id")

    op.drop_index(op.f("ix_program_university_id"), table_name="program")
    op.drop_table("program")

    op.drop_index(op.f("ix_university_name"), table_name="university")
    op.drop_table("university")
