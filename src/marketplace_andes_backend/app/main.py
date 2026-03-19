from fastapi import FastAPI

from ..health.routes import router as health_router
from .modules.categories.router import router as categories_router
from .modules.listings.router import router as listings_router
from .modules.locations.router import router as locations_router
from .modules.users.router import router as users_router
# 👇 SOLO PARA REGISTRAR MODELOS EN SQLALCHEMY
from marketplace_andes_backend.app.modules.categories import models as _
from marketplace_andes_backend.app.modules.locations import models as _
from marketplace_andes_backend.app.modules.listings import models as _
from marketplace_andes_backend.app.modules.users import models as _
from marketplace_andes_backend.app.core.database import create_db_and_tables
app = FastAPI()

app.include_router(health_router)
app.include_router(listings_router)
app.include_router(categories_router)
app.include_router(locations_router)
app.include_router(users_router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()