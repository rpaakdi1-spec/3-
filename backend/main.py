from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import init_db
from app.services.excel_template_service import ExcelTemplateService

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
    level="INFO" if settings.APP_ENV == "production" else "DEBUG"
)
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} | {message}",
    level="INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Cold Chain Dispatch System...")
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Create Excel templates
    logger.info("Creating Excel templates...")
    try:
        templates = ExcelTemplateService.create_all_templates()
        for template_type, path in templates.items():
            logger.info(f"Created {template_type} template: {path}")
    except Exception as e:
        logger.error(f"Failed to create templates: {e}")
    
    logger.info("Application startup complete!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI 기반 냉동·냉장 화물 배차 시스템",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Cold Chain Dispatch System API",
        "docs": "/docs",
        "health": "/health"
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Import and include routers
from app.api import clients, vehicles, orders, dispatches, tracking, uvis
app.include_router(clients.router, prefix=f"{settings.API_PREFIX}/clients", tags=["Clients"])
app.include_router(vehicles.router, prefix=f"{settings.API_PREFIX}/vehicles", tags=["Vehicles"])
app.include_router(orders.router, prefix=f"{settings.API_PREFIX}/orders", tags=["Orders"])
app.include_router(dispatches.router, prefix=f"{settings.API_PREFIX}/dispatches", tags=["Dispatches"])
app.include_router(tracking.router, prefix=f"{settings.API_PREFIX}/tracking", tags=["Tracking"])
app.include_router(uvis.router, prefix=f"{settings.API_PREFIX}/uvis", tags=["UVIS"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_ENV == "development"
    )
