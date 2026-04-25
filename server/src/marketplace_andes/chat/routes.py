from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    Path,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from sqlmodel import Session

from marketplace_andes.auth.dependencies import CurrentUserDep
from marketplace_andes.auth.jwt.dependencies import JWTServiceDep
from marketplace_andes.db.dependencies import EngineDep, SessionDep

from .schemas import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageCreateRequest,
    MessageResponse,
    WsOutgoingMessage,
)
from .service import ChatService, MessageBodyEmptyError
from .ws_manager import manager

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/conversations", status_code=201)
async def create_or_get_conversation(
    payload: ConversationCreateRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> ConversationResponse:
    service = ChatService(session)
    try:
        conversation, _ = service.get_or_create_conversation(
            buyer_id=current_user.id,
            listing_id=payload.listing_id,
        )
    except ValueError as exc:
        detail_map = {
            "listing_not_found": (404, "Listing not found"),
            "cannot_message_own_listing": (403, "You cannot message your own listing"),
        }
        status_code, detail = detail_map.get(str(exc), (400, "Bad request"))
        raise HTTPException(status_code=status_code, detail=detail)

    response = service.get_conversation_for_user(conversation.id, current_user.id)
    if response is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversation details after creation",
        )
    return response


@router.get("/conversations")
async def list_conversations(
    session: SessionDep,
    current_user: CurrentUserDep,
) -> list[ConversationResponse]:
    return ChatService(session).list_conversations_for_user(current_user.id)


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: Annotated[UUID, Path()],
    session: SessionDep,
    current_user: CurrentUserDep,
) -> ConversationResponse:
    result = ChatService(session).get_conversation_for_user(
        conversation_id, current_user.id
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: Annotated[UUID, Path()],
    session: SessionDep,
    current_user: CurrentUserDep,
) -> list[MessageResponse]:
    service = ChatService(session)
    if not service.user_is_participant(conversation_id, current_user.id):
        raise HTTPException(
            status_code=403, detail="Not a participant of this conversation"
        )
    return service.list_messages(conversation_id)


@router.post("/conversations/{conversation_id}/messages", status_code=201)
async def post_message(
    conversation_id: Annotated[UUID, Path()],
    payload: MessageCreateRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> MessageResponse:
    service = ChatService(session)
    conversation = service.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not service.is_participant(conversation, current_user.id):
        raise HTTPException(
            status_code=403, detail="Not a participant of this conversation"
        )

    try:
        message = service.save_message(
            conversation_id=conversation_id,
            sender_id=current_user.id,
            body=payload.body,
        )
    except MessageBodyEmptyError:
        raise HTTPException(
            status_code=422,
            detail="Message body cannot be empty or contain only whitespace",
        )
    outgoing = WsOutgoingMessage(
        id=str(message.id),
        conversation_id=str(message.conversation_id),
        sender_id=str(message.sender_id),
        body=message.body,
        sent_at=message.sent_at.isoformat(),
    )
    await manager.broadcast(conversation_id, outgoing.model_dump())

    return MessageResponse.model_validate(message)


@router.websocket("/conversations/{conversation_id}/ws")
async def websocket_endpoint(
    conversation_id: UUID,
    websocket: WebSocket,
    engine: EngineDep,
    jwt_service: JWTServiceDep,
    token: str = Query(...),
):
    try:
        user_id = jwt_service.verify_access_token(token)
    except Exception:
        await websocket.close(code=4001)
        return

    with Session(engine) as session:
        is_participant = ChatService(session).user_is_participant(
            conversation_id, user_id
        )

    if not is_participant:
        await websocket.close(code=4003)
        return

    await manager.connect(conversation_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            body = (data.get("body") or "").strip()
            if not body:
                continue

            with Session(engine) as session:
                message = ChatService(session).save_message(
                    conversation_id=conversation_id,
                    sender_id=user_id,
                    body=body,
                )
                outgoing = WsOutgoingMessage(
                    id=str(message.id),
                    conversation_id=str(message.conversation_id),
                    sender_id=str(message.sender_id),
                    body=message.body,
                    sent_at=message.sent_at.isoformat(),
                )

            await manager.broadcast(conversation_id, outgoing.model_dump())

    except WebSocketDisconnect:
        manager.disconnect(conversation_id, websocket)
