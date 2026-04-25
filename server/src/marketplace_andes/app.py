from fastapi import FastAPI


from .lifecycle import lifespan
from .exception_handlers import register_exception_handlers
from .health.routes import router as health_router
from .auth.routes import router as auth_router
from .users.routes import router as users_router
from .categories.routes import router as categories_router
from .listings.routes import router as listings_router
from .interactions.routes import router as interactions_router
from .purchases.routes import router as purchases_router


app = FastAPI(lifespan=lifespan)
register_exception_handlers(app)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(listings_router)
app.include_router(interactions_router)
app.include_router(purchases_router)
