from fastapi import APIRouter

from .profile.routes import router as profile_router

router = APIRouter(prefix="/users", tags=["users"])
router.include_router(profile_router)
