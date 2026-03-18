from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text

from .db import get_engine
from .health.routes import router as health_router


def test_db():
    print("Testing database connection...")
    with get_engine().connect() as connection:
        pg_version = connection.execute(text("SELECT version()"))
        print(f"PostgreSQL version: {pg_version.scalar_one()}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    test_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(health_router)
