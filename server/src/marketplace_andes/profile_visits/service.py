from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlmodel import Session

from marketplace_andes.users.repository import UserRepository

from .models import ProfileVisitEvent


class ProfileVisitService:
    def __init__(self, session: Session):
        self.session = session
        self._users = UserRepository(session)

    def register_visit(
        self,
        *,
        visitor_user_id: UUID,
        visited_user_id: UUID,
    ) -> ProfileVisitEvent | None:
        """Insert a profile visit. Returns None if visited user does not exist."""
        if visitor_user_id == visited_user_id:
            raise ValueError("cannot_visit_self")

        if self._users.get_user_by_id(visited_user_id) is None:
            return None

        now = datetime.now(UTC)
        event = ProfileVisitEvent(
            id=uuid7(),
            visitor_user_id=visitor_user_id,
            visited_user_id=visited_user_id,
            visited_at=now,
        )
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event
