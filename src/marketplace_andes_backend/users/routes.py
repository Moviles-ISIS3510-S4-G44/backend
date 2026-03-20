from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from src.marketplace_andes_backend.db import get_session
from .models import User
from .profile.routes import router as profile_router

router = APIRouter(prefix="/users", tags=["users"])
router.include_router(profile_router)


@router.get("", response_model=list[User])
def get_users(session: Session = Depends(get_session)) -> list[User]:
    statement = select(User)
    users = session.exec(statement).all()
    return users