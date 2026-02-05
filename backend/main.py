from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from loguru import logger
import sys
from pathlib import Path

from app.core.config import settings
from app.core.database import init_db
from app.services.excel_template_service import ExcelTemplateService
from app.middleware.security import setup_security_middleware
from app.middleware.compression import CompressionMiddleware
from app.middleware.performance import PerformanceMonitoringMiddleware

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
    
    # Initialize WebSocket manager
    logger.info("Initializing WebSocket manager...")
    from app.websocket.connection_manager import manager
    from app.services.realtime_metrics_service import metrics_service
    await manager.initialize()
    await metrics_service.start()
    
    # Start scheduler service
    logger.info("Starting scheduler service...")
    from app.services.scheduler_service import scheduler_service
    await scheduler_service.start()
    
    logger.info("Application startup complete!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    from app.services.scheduler_service import scheduler_service
    await scheduler_service.stop()
    await metrics_service.stop()
    await manager.shutdown()


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

# Configure Security Middleware
setup_security_middleware(app)

# Configure Performance Monitoring Middleware
# DISABLED: Also causes "Unexpected message received: http.request" error
# TODO: Fix PerformanceMonitoringMiddleware to properly handle ASGI messages
# app.add_middleware(
#     PerformanceMonitoringMiddleware,
#     slow_request_threshold=1.0,  # 1 second
#     enable_memory_tracking=True
# )

# Configure Compression Middleware
# DISABLED: Causes "Unexpected message received: http.request" error
# TODO: Fix CompressionMiddleware to properly handle ASGI messages
# app.add_middleware(
#     CompressionMiddleware,
#     minimum_size=500  # 500 bytes
# )


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
# from app.api import auth, clients, vehicles, orders, dispatches, tracking, uvis, redispatch, notices, purchase_orders, band_messages, uvis_gps, analytics, delivery_tracking, traffic, monitoring, cache
from app.api import auth, clients, vehicles, orders, dispatches, tracking, uvis, redispatch, notices, purchase_orders, band_messages, uvis_gps, delivery_tracking, traffic, monitoring, cache, emergency, ml_training, ai_chat, ai_usage, ml_dispatch, ab_test, recurring_orders, order_templates
from app.api.v1 import reports, realtime_monitoring, ml_models, fcm_notifications, performance, security, websocket
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
app.include_router(clients.router, prefix=f"{settings.API_PREFIX}/clients", tags=["Clients"])
app.include_router(vehicles.router, prefix=f"{settings.API_PREFIX}/vehicles", tags=["Vehicles"])
app.include_router(orders.router, prefix=f"{settings.API_PREFIX}/orders", tags=["Orders"])
app.include_router(order_templates.router, prefix=f"{settings.API_PREFIX}/order-templates", tags=["Order Templates"])
app.include_router(recurring_orders.router, prefix=f"{settings.API_PREFIX}/recurring-orders", tags=["Recurring Orders"])
app.include_router(ai_chat.router, prefix=f"{settings.API_PREFIX}/ai-chat", tags=["AI Chat"])
app.include_router(ai_usage.router, prefix=f"{settings.API_PREFIX}/ai-usage", tags=["AI Usage"])
app.include_router(ab_test.router, tags=["AB Test"])
app.include_router(dispatches.router, prefix=f"{settings.API_PREFIX}/dispatches", tags=["Dispatches"])
app.include_router(tracking.router, prefix=f"{settings.API_PREFIX}/tracking", tags=["Tracking"])
app.include_router(delivery_tracking.router, prefix=f"{settings.API_PREFIX}/delivery-tracking", tags=["Delivery Tracking"])
app.include_router(traffic.router, prefix=f"{settings.API_PREFIX}/traffic", tags=["Traffic Information"])
app.include_router(monitoring.router, prefix=f"{settings.API_PREFIX}/monitoring", tags=["Monitoring & Alerts"])
app.include_router(cache.router, prefix=f"{settings.API_PREFIX}/cache", tags=["Cache Management"])
app.include_router(uvis.router, prefix=f"{settings.API_PREFIX}/uvis", tags=["UVIS"])
app.include_router(redispatch.router, prefix=f"{settings.API_PREFIX}/redispatch", tags=["Redispatch"])
app.include_router(notices.router, prefix=f"{settings.API_PREFIX}/notices", tags=["Notices"])
app.include_router(purchase_orders.router, prefix=f"{settings.API_PREFIX}/purchase-orders", tags=["Purchase Orders"])
app.include_router(band_messages.router, prefix=f"{settings.API_PREFIX}/band", tags=["Band Messages"])
app.include_router(uvis_gps.router, prefix=f"{settings.API_PREFIX}", tags=["UVIS GPS"])
app.include_router(emergency.router, prefix=f"{settings.API_PREFIX}", tags=["Emergency Maintenance"])
app.include_router(ml_training.router, prefix=f"{settings.API_PREFIX}/ml", tags=["ML Training"])
app.include_router(ml_dispatch.router, tags=["ML Dispatch"])
# app.include_router(analytics.router, prefix=f"{settings.API_PREFIX}", tags=["Analytics"])  # Temporarily disabled due to Pydantic recursion issue
app.include_router(reports.router, prefix=f"{settings.API_PREFIX}/reports", tags=["Reports"])
app.include_router(realtime_monitoring.router, prefix=f"{settings.API_PREFIX}/realtime", tags=["Realtime Monitoring"])
app.include_router(ml_models.router, prefix=f"{settings.API_PREFIX}/ml-models", tags=["ML Models"])
app.include_router(fcm_notifications.router, prefix=f"{settings.API_PREFIX}/notifications", tags=["Push Notifications"])
app.include_router(performance.router, prefix=f"{settings.API_PREFIX}/performance", tags=["Performance Monitoring"])
app.include_router(security.router, prefix=f"{settings.API_PREFIX}/security", tags=["Security"])
app.include_router(websocket.router, tags=["WebSocket"])  # WebSocket endpoints

# Mount static files for uploads
import os
UPLOAD_BASE_DIR = os.getenv("UPLOAD_BASE_DIR", "./uploads")
UPLOAD_DIR = Path(UPLOAD_BASE_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_ENV == "development"
    )
