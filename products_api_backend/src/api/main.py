from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers_products import router as products_router

app = FastAPI(
    title="Products API - Ocean Professional",
    description="A modern FastAPI service to manage products with CRUD operations.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Health", "description": "Service health and diagnostics"},
        {"name": "Products", "description": "CRUD operations for products"},
    ],
)

# Enable permissive CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize database and seed demo data on startup."""
    init_db(seed=True)


# PUBLIC_INTERFACE
@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Returns a simple JSON payload to confirm the service is running.",
)
def health_check():
    """Health endpoint to verify the service is up."""
    return {"message": "Healthy"}


# Register product routes
app.include_router(products_router)
