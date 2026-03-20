from fastapi import FastAPI
from contextlib import asynccontextmanager

from .auth.routes import router as auth_router
from .health.routes import router as health_router
from .marketplace.routes import router as marketplace_router
from .users.routes import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(marketplace_router)
app.include_router(users_router)
