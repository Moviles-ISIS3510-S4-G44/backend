from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from ..auth.dependencies import CurrentUserDep
from ..db import SessionDep
from .schemas import (
    CategoryCreateRequest,
    CategoryResponse,
    ListingCreateRequest,
    ListingResponse,
    MarketplaceSnapshotResponse,
    MessageCreateRequest,
    MessageResponse,
    MessageThreadCreateRequest,
    MessageThreadResponse,
    ProgramCreateRequest,
    ProgramResponse,
    ReviewCreateRequest,
    ReviewResponse,
    SearchEventCreateRequest,
    SearchEventResponse,
    TransactionCreateRequest,
    TransactionResponse,
    UniversityCreateRequest,
    UniversityResponse,
    UserActivityResponse,
)
from .service import (
    MarketplaceConflictError,
    MarketplaceNotFoundError,
    MarketplacePermissionError,
    MarketplaceService,
)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


def _service(session: SessionDep) -> MarketplaceService:
    return MarketplaceService(session)


def _handle_marketplace_error(exc: Exception) -> None:
    if isinstance(exc, MarketplaceNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found") from exc
    if isinstance(exc, MarketplaceConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Resource conflict") from exc
    if isinstance(exc, MarketplacePermissionError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not allowed") from exc
    raise exc


@router.post("/universities", status_code=status.HTTP_201_CREATED)
def create_university(
    payload: UniversityCreateRequest,
    _current_user: CurrentUserDep,
    session: SessionDep,
) -> UniversityResponse:
    service = _service(session)
    return UniversityResponse.model_validate(service.create_university(payload))


@router.post("/programs", status_code=status.HTTP_201_CREATED)
def create_program(
    payload: ProgramCreateRequest,
    _current_user: CurrentUserDep,
    session: SessionDep,
) -> ProgramResponse:
    service = _service(session)
    try:
        return ProgramResponse.model_validate(service.create_program(payload))
    except Exception as exc:
        _handle_marketplace_error(exc)
        raise


@router.post("/categories", status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreateRequest,
    _current_user: CurrentUserDep,
    session: SessionDep,
) -> CategoryResponse:
    service = _service(session)
    try:
        return CategoryResponse.model_validate(service.create_category(payload))
    except Exception as exc:
        _handle_marketplace_error(exc)
        raise


@router.post("/listings", status_code=status.HTTP_201_CREATED)
def create_listing(
    payload: ListingCreateRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> ListingResponse:
    service = _service(session)
    try:
        return ListingResponse.model_validate(service.create_listing(current_user, payload))
    except Exception as exc:
        _handle_marketplace_error(exc)
        raise


@router.post("/transactions", status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreateRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TransactionResponse:
    service = _service(session)
    try:
        return TransactionResponse.model_validate(service.create_transaction(current_user, payload))
    except Exception as exc:
        _handle_marketplace_error(exc)
        raise


@router.post("/transactions/{transaction_id}/complete")
def complete_transaction(
    transaction_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TransactionResponse:
    service = _service(session)
    try:
        return TransactionResponse.model_validate(
            service.complete_transaction(transaction_id, current_user)
        )
    except Exception as exc:
        _handle_marketplace_error(exc)
        raise


@router.post("/transactions/{transaction_id}/cancel")
def cancel_transaction(
    transaction_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TransactionResponse:
    service = _service(session)
    try:
        return TransactionResponse.model_validate(
            service.cancel_transaction(transaction_id, current_user)
        )
    except Exception as exc:
        _handle_marketplace_error(exc)
        raise


@router.post("/threads", status_code=status.HTTP_201_CREATED)
def create_thread(
    payload: MessageThreadCreateRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> MessageThreadResponse:
    service = _service(session)
    try:
        return MessageThreadResponse.model_validate(service.create_thread(current_user, payload))
    except Exception as exc:
        _handle_marketplace_error(exc)
        raise


@router.post("/threads/{thread_id}/messages", status_code=status.HTTP_201_CREATED)
def create_message(
    thread_id: UUID,
    payload: MessageCreateRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> MessageResponse:
    service = _service(session)
    try:
        return MessageResponse.model_validate(
            service.create_message(thread_id, current_user, payload)
        )
    except Exception as exc:
        _handle_marketplace_error(exc)
        raise


@router.post("/reviews", status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreateRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> ReviewResponse:
    service = _service(session)
    try:
        return ReviewResponse.model_validate(service.create_review(current_user, payload))
    except Exception as exc:
        _handle_marketplace_error(exc)
        raise


@router.post("/searches", status_code=status.HTTP_201_CREATED)
def create_search_event(
    payload: SearchEventCreateRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> SearchEventResponse:
    service = _service(session)
    try:
        return SearchEventResponse.model_validate(service.create_search_event(current_user, payload))
    except Exception as exc:
        _handle_marketplace_error(exc)
        raise


@router.get("/snapshot")
def read_snapshot(
    _current_user: CurrentUserDep,
    session: SessionDep,
) -> MarketplaceSnapshotResponse:
    service = _service(session)
    return MarketplaceSnapshotResponse(
        universities=[UniversityResponse.model_validate(item) for item in service.list_universities()],
        programs=[ProgramResponse.model_validate(item) for item in service.list_programs()],
        categories=[CategoryResponse.model_validate(item) for item in service.list_categories()],
        listings=[ListingResponse.model_validate(item) for item in service.list_listings()],
        transactions=[TransactionResponse.model_validate(item) for item in service.list_transactions()],
        threads=[MessageThreadResponse.model_validate(item) for item in service.list_threads()],
        messages=[MessageResponse.model_validate(item) for item in service.list_messages()],
        reviews=[ReviewResponse.model_validate(item) for item in service.list_reviews()],
        searches=[SearchEventResponse.model_validate(item) for item in service.list_searches()],
        activities=[UserActivityResponse.model_validate(item) for item in service.list_activities()],
    )
