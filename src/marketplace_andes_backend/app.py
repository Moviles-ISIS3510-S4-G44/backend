from fastapi import FastAPI
from contextlib import asynccontextmanager

from .auth.routes import router as auth_router
from .categories.routes import router as categories_router
from .health.routes import router as health_router
from .interactions.routes import router as interactions_router
from .listings.routes import router as listings_router
from .users.routes import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(listings_router)
app.include_router(interactions_router)
