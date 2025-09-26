from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, products, stock_movements, stock_transfers, warehouses
from app.api import scraped_products
from app.core.logger import configure_logging
import logging

# Configure centralized logging (writes to logs/app.log)
configure_logging(level=logging.INFO)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Return a simple JSON welcome instead of redirecting to /docs"""
    return {
        "message": f"{settings.PROJECT_NAME} API - visit /docs for documentation",
        "version": settings.VERSION
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix=settings.API_V1_STR)
app.include_router(stock_movements.router, prefix=settings.API_V1_STR)
app.include_router(stock_transfers.router, prefix=settings.API_V1_STR)
app.include_router(warehouses.router, prefix=settings.API_V1_STR)
app.include_router(scraped_products.router, prefix=settings.API_V1_STR)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"Global exception handler caught: {exc}")
    return HTTPException(
        status_code=500,
        detail="Internal server error"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )