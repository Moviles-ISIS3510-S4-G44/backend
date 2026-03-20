from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session, select

from ..users.models import User
from .models import (
    Category,
    Listing,
    ListingMedia,
    ListingStatusHistory,
    MarketplaceTransaction,
    Message,
    MessageThread,
    Program,
    Review,
    SearchEvent,
    University,
    UserActivityEvent,
)
from .schemas import (
    CategoryCreateRequest,
    ListingCreateRequest,
    MessageCreateRequest,
    MessageThreadCreateRequest,
    ProgramCreateRequest,
    ReviewCreateRequest,
    SearchEventCreateRequest,
    TransactionCreateRequest,
    UniversityCreateRequest,
)


class MarketplaceNotFoundError(Exception):
    pass


class MarketplaceConflictError(Exception):
    pass


class MarketplacePermissionError(Exception):
    pass


class MarketplaceService:
    def __init__(self, session: Session):
        self.session = session

    def create_university(self, payload: UniversityCreateRequest) -> University:
        university = University.model_validate(payload)
        self.session.add(university)
        self.session.commit()
        self.session.refresh(university)
        return university

    def create_program(self, payload: ProgramCreateRequest) -> Program:
        self._get_university(payload.university_id)
        program = Program.model_validate(payload)
        self.session.add(program)
        self.session.commit()
        self.session.refresh(program)
        return program

    def create_category(self, payload: CategoryCreateRequest) -> Category:
        if payload.parent_category_id is not None:
            self._get_category(payload.parent_category_id)
        existing_category = self.session.exec(
            select(Category).where(Category.slug == payload.slug)
        ).first()
        if existing_category is not None:
            raise MarketplaceConflictError()
        category = Category.model_validate(payload)
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def create_listing(self, seller: User, payload: ListingCreateRequest) -> Listing:
        self._get_category(payload.category_id)
        listing = Listing(
            seller_id=seller.id,
            category_id=payload.category_id,
            title=payload.title,
            description=payload.description,
            product_type=payload.product_type,
            condition=payload.condition,
            price=payload.price,
            currency=payload.currency,
            status=payload.status,
            is_negotiable=payload.is_negotiable,
            is_digital=payload.is_digital,
            quantity_available=payload.quantity_available,
            campus_pickup_point=payload.campus_pickup_point,
            published_at=datetime.now(UTC) if payload.status == "active" else None,
        )
        self.session.add(listing)
        self.session.flush()
        self.session.add(
            ListingStatusHistory(
                listing_id=listing.id,
                changed_by_user_id=seller.id,
                from_status=None,
                to_status=listing.status,
            )
        )
        for index, media_url in enumerate(payload.media_urls):
            self.session.add(
                ListingMedia(
                    listing_id=listing.id,
                    asset_url=media_url,
                    media_type="image",
                    sort_order=index,
                )
            )
        self._record_activity(user_id=seller.id, listing_id=listing.id, event_type="listing_created")
        self.session.commit()
        self.session.refresh(listing)
        return listing

    def create_transaction(
        self, buyer: User, payload: TransactionCreateRequest
    ) -> MarketplaceTransaction:
        listing = self._get_listing(payload.listing_id)
        if listing.seller_id == buyer.id:
            raise MarketplacePermissionError()
        transaction = MarketplaceTransaction(
            listing_id=listing.id,
            buyer_id=buyer.id,
            seller_id=listing.seller_id,
            listed_price=listing.price,
            agreed_price=payload.agreed_price,
            currency=payload.currency,
        )
        self.session.add(transaction)
        self.session.flush()
        self._record_activity(
            user_id=buyer.id,
            listing_id=listing.id,
            transaction_id=transaction.id,
            event_type="transaction",
        )
        self.session.commit()
        self.session.refresh(transaction)
        return transaction

    def complete_transaction(
        self, transaction_id: UUID, current_user: User
    ) -> MarketplaceTransaction:
        transaction = self._get_transaction(transaction_id)
        if transaction.seller_id != current_user.id:
            raise MarketplacePermissionError()
        transaction.status = "completed"
        transaction.completed_at = datetime.now(UTC)
        listing = self._get_listing(transaction.listing_id)
        previous_status = listing.status
        listing.status = "sold"
        listing.sold_at = transaction.completed_at
        self.session.add(
            ListingStatusHistory(
                listing_id=listing.id,
                changed_by_user_id=current_user.id,
                from_status=previous_status,
                to_status=listing.status,
                changed_at=transaction.completed_at,
            )
        )
        self._record_activity(
            user_id=current_user.id,
            listing_id=listing.id,
            transaction_id=transaction.id,
            event_type="transaction",
        )
        self.session.add(transaction)
        self.session.add(listing)
        self.session.commit()
        self.session.refresh(transaction)
        return transaction

    def cancel_transaction(
        self, transaction_id: UUID, current_user: User
    ) -> MarketplaceTransaction:
        transaction = self._get_transaction(transaction_id)
        if current_user.id not in {transaction.buyer_id, transaction.seller_id}:
            raise MarketplacePermissionError()
        transaction.status = "cancelled"
        transaction.cancelled_at = datetime.now(UTC)
        self.session.add(transaction)
        self.session.commit()
        self.session.refresh(transaction)
        return transaction

    def create_thread(self, buyer: User, payload: MessageThreadCreateRequest) -> MessageThread:
        listing = self._get_listing(payload.listing_id)
        existing_thread = self.session.exec(
            select(MessageThread).where(
                MessageThread.listing_id == listing.id,
                MessageThread.buyer_id == buyer.id,
                MessageThread.seller_id == listing.seller_id,
            )
        ).first()
        if existing_thread is not None:
            return existing_thread
        thread = MessageThread(
            listing_id=listing.id,
            buyer_id=buyer.id,
            seller_id=listing.seller_id,
        )
        self.session.add(thread)
        self.session.commit()
        self.session.refresh(thread)
        return thread

    def create_message(
        self, thread_id: UUID, sender: User, payload: MessageCreateRequest
    ) -> Message:
        thread = self._get_thread(thread_id)
        if sender.id not in {thread.buyer_id, thread.seller_id}:
            raise MarketplacePermissionError()
        message = Message(thread_id=thread.id, sender_id=sender.id, body=payload.body)
        thread.last_message_at = message.created_at
        self.session.add(message)
        self.session.add(thread)
        self._record_activity(user_id=sender.id, listing_id=thread.listing_id, event_type="message")
        self.session.commit()
        self.session.refresh(message)
        return message

    def create_review(self, reviewer: User, payload: ReviewCreateRequest) -> Review:
        transaction = self._get_transaction(payload.transaction_id)
        if transaction.status != "completed":
            raise MarketplaceConflictError()
        if reviewer.id not in {transaction.buyer_id, transaction.seller_id}:
            raise MarketplacePermissionError()
        reviewee_id = (
            transaction.seller_id if reviewer.id == transaction.buyer_id else transaction.buyer_id
        )
        review = Review(
            transaction_id=transaction.id,
            reviewer_id=reviewer.id,
            reviewee_id=reviewee_id,
            rating=payload.rating,
            comment=payload.comment,
        )
        self.session.add(review)
        reviewee = self._get_user(reviewee_id)
        existing_reviews = self.session.exec(
            select(Review).where(Review.reviewee_id == reviewee_id)
        ).all()
        total_rating = sum(item.rating for item in existing_reviews) + payload.rating
        reviewee.rating = round(total_rating / (len(existing_reviews) + 1))
        self.session.add(reviewee)
        self.session.commit()
        self.session.refresh(review)
        return review

    def create_search_event(self, user: User, payload: SearchEventCreateRequest) -> SearchEvent:
        if payload.category_id is not None:
            self._get_category(payload.category_id)
        search_event = SearchEvent(
            user_id=user.id,
            category_id=payload.category_id,
            query_text=payload.query_text,
            sort_mode=payload.sort_mode,
            results_count=payload.results_count,
        )
        self.session.add(search_event)
        self._record_activity(user_id=user.id, event_type="search")
        self.session.commit()
        self.session.refresh(search_event)
        return search_event

    def list_universities(self) -> list[University]:
        return list(self.session.exec(select(University)).all())

    def list_programs(self) -> list[Program]:
        return list(self.session.exec(select(Program)).all())

    def list_categories(self) -> list[Category]:
        return list(self.session.exec(select(Category)).all())

    def list_listings(self) -> list[Listing]:
        return list(self.session.exec(select(Listing)).all())

    def list_transactions(self) -> list[MarketplaceTransaction]:
        return list(self.session.exec(select(MarketplaceTransaction)).all())

    def list_threads(self) -> list[MessageThread]:
        return list(self.session.exec(select(MessageThread)).all())

    def list_messages(self) -> list[Message]:
        return list(self.session.exec(select(Message)).all())

    def list_reviews(self) -> list[Review]:
        return list(self.session.exec(select(Review)).all())

    def list_searches(self) -> list[SearchEvent]:
        return list(self.session.exec(select(SearchEvent)).all())

    def list_activities(self) -> list[UserActivityEvent]:
        return list(self.session.exec(select(UserActivityEvent)).all())

    def record_login(self, user: User) -> None:
        user.last_login_at = datetime.now(UTC)
        self.session.add(user)
        self._record_activity(user_id=user.id, event_type="login")
        self.session.commit()

    def _record_activity(
        self,
        user_id: UUID,
        event_type: str,
        listing_id: UUID | None = None,
        transaction_id: UUID | None = None,
    ) -> UserActivityEvent:
        activity = UserActivityEvent(
            user_id=user_id,
            listing_id=listing_id,
            transaction_id=transaction_id,
            event_type=event_type,
        )
        self.session.add(activity)
        self.session.flush()
        return activity

    def _get_university(self, university_id: UUID) -> University:
        university = self.session.get(University, university_id)
        if university is None:
            raise MarketplaceNotFoundError()
        return university

    def _get_category(self, category_id: UUID) -> Category:
        category = self.session.get(Category, category_id)
        if category is None:
            raise MarketplaceNotFoundError()
        return category

    def _get_listing(self, listing_id: UUID) -> Listing:
        listing = self.session.get(Listing, listing_id)
        if listing is None:
            raise MarketplaceNotFoundError()
        return listing

    def _get_transaction(self, transaction_id: UUID) -> MarketplaceTransaction:
        transaction = self.session.get(MarketplaceTransaction, transaction_id)
        if transaction is None:
            raise MarketplaceNotFoundError()
        return transaction

    def _get_thread(self, thread_id: UUID) -> MessageThread:
        thread = self.session.get(MessageThread, thread_id)
        if thread is None:
            raise MarketplaceNotFoundError()
        return thread

    def _get_user(self, user_id: UUID) -> User:
        user = self.session.get(User, user_id)
        if user is None:
            raise MarketplaceNotFoundError()
        return user
