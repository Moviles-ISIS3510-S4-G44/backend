from fastapi import FastAPI
from .routes import health_router

app = FastAPI()

app.include_router(health_router)
