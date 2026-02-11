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
    
    # Start vehicle tracking service
    logger.info("Starting vehicle tracking service...")
    from app.services.vehicle_tracking_service import vehicle_tracking_service
    await vehicle_tracking_service.start()
    
    logger.info("Application startup complete!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    from app.services.scheduler_service import scheduler_service
    from app.services.vehicle_tracking_service import vehicle_tracking_service
    await scheduler_service.stop()
    await vehicle_tracking_service.stop()
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
from app.api import auth, clients, vehicles, orders, dispatches, tracking, uvis, redispatch, notices, purchase_orders, band_messages, uvis_gps, delivery_tracking, traffic, monitoring, cache, emergency, ml_training, ai_chat, ai_usage, ml_dispatch, ab_test, recurring_orders, order_templates, driver_schedules, urgent_dispatches, notifications, temperature_monitoring, temperature_analytics, billing, vehicle_maintenance, ml_predictions, telemetry, dispatch_optimization, analytics, mobile, integrated_dispatch
from app.api.v1 import reports, realtime_monitoring, ml_models, fcm_notifications, performance, security, websocket, mobile_enhanced, billing_enhanced
from app.api.v1.endpoints import dispatch_rules, simulations
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
app.include_router(driver_schedules.router, prefix=f"{settings.API_PREFIX}/driver-schedules", tags=["Driver Schedules"])
app.include_router(urgent_dispatches.router, prefix=f"{settings.API_PREFIX}/urgent-dispatches", tags=["Urgent Dispatches"])
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
app.include_router(realtime_monitoring.router, prefix=f"{settings.API_PREFIX}/realtime", tags=["Realtime Monitoring"])
app.include_router(ml_models.router, prefix=f"{settings.API_PREFIX}/ml-models", tags=["ML Models"])
app.include_router(fcm_notifications.router, prefix=f"{settings.API_PREFIX}/notifications", tags=["Push Notifications"])
app.include_router(performance.router, prefix=f"{settings.API_PREFIX}/performance", tags=["Performance Monitoring"])
app.include_router(security.router, prefix=f"{settings.API_PREFIX}/security", tags=["Security"])
app.include_router(websocket.router, tags=["WebSocket"])  # WebSocket endpoints
app.include_router(notifications.router, prefix=f"{settings.API_PREFIX}/notifications-v2", tags=["Notifications"])  # New notification system
app.include_router(temperature_monitoring.router, prefix=f"{settings.API_PREFIX}", tags=["Temperature Monitoring"])  # Phase 3-A Part 4
app.include_router(temperature_analytics.router, prefix=f"{settings.API_PREFIX}", tags=["Temperature Analytics"])  # Phase 3-A Part 5
app.include_router(billing.router, prefix=f"{settings.API_PREFIX}/billing", tags=["Billing & Settlement"])  # Phase 3-B Week 1
app.include_router(vehicle_maintenance.router, prefix=f"{settings.API_PREFIX}", tags=["Vehicle Maintenance"])  # Phase 3-B Week 3
app.include_router(ml_predictions.router, prefix=f"{settings.API_PREFIX}", tags=["ML Predictions"])  # Phase 4 Week 1-2
app.include_router(telemetry.router, prefix=f"{settings.API_PREFIX}", tags=["Real-time Telemetry"])  # Phase 4 Week 3-4
app.include_router(dispatch_optimization.router, prefix=f"{settings.API_PREFIX}", tags=["Dispatch Optimization"])  # Phase 4 Week 5-6
app.include_router(analytics.router, prefix=f"{settings.API_PREFIX}", tags=["Analytics & BI"])  # Phase 4 Week 7-8
app.include_router(reports.router, prefix=f"{settings.API_PREFIX}")
app.include_router(mobile.router, prefix=f"{settings.API_PREFIX}/mobile", tags=["Mobile App"])  # Phase 4 Week 9-10
app.include_router(mobile_enhanced.router, prefix=f"{settings.API_PREFIX}", tags=["Mobile App Enhanced"])  # Phase 7: Mobile API Enhancements
app.include_router(billing_enhanced.router, prefix=f"{settings.API_PREFIX}", tags=["Billing Enhanced"])  # Phase 8: Billing Enhanced
app.include_router(dispatch_rules.router, prefix=f"{settings.API_PREFIX}/dispatch-rules", tags=["Dispatch Rules"])  # Phase 10: Smart Dispatch Rule Engine
app.include_router(simulations.router, prefix=f"{settings.API_PREFIX}/simulations", tags=["Simulations"])  # Phase 11-C: Rule Simulation
app.include_router(integrated_dispatch.router, prefix=f"{settings.API_PREFIX}", tags=["Integrated Dispatch"])  # Phase 12: 핵심 통합 (Naver Map + GPS + AI)

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
