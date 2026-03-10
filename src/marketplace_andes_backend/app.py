from fastapi import FastAPI
from .health.routes import router as health_router

app = FastAPI()

app.include_router(health_router)
