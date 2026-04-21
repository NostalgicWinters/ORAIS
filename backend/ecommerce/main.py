from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import create_tables

from services.auth.router      import router as auth_router
from services.products.router  import router as products_router
from services.customers.router import router as customers_router
from services.orders.router    import router as orders_router
from services.payments.router  import router as payments_router
from services.suppliers.router import router as suppliers_router
from services.forecasting.router import router as forecasting_router
from services.stock.router     import router as stock_router
from services.analytics.router import router as analytics_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    create_tables()

# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": settings.APP_VERSION}

# ── Routers ───────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(auth_router,        prefix=PREFIX)
app.include_router(products_router,    prefix=PREFIX)
app.include_router(customers_router,   prefix=PREFIX)
app.include_router(orders_router,      prefix=PREFIX)
app.include_router(payments_router,    prefix=PREFIX)
app.include_router(suppliers_router,   prefix=PREFIX)
app.include_router(forecasting_router, prefix=PREFIX)
app.include_router(stock_router,       prefix=PREFIX)
app.include_router(analytics_router,   prefix=PREFIX)
