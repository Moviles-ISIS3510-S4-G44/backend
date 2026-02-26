from fastapi import FastAPI
from contextlib import asynccontextmanager

from backend.auth.routes import router as auth_router
from backend.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Marketplace Andes Backend", lifespan=lifespan)
app.include_router(auth_router)
