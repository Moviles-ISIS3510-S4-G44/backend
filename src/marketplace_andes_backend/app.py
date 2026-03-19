from fastapi import FastAPI
from contextlib import asynccontextmanager

from .health.routes import router as health_router
from .users.profile.routes import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(health_router)
app.include_router(users_router)
