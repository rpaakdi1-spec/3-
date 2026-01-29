"""
Simple Backend Demo for Cold Chain System
Provides essential API endpoints for frontend demonstration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="Cold Chain Backend API",
    description="Enterprise Cold Chain Management System - Demo API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Cold Chain Backend API",
        "version": "2.0.0",
        "phase": "Phase 10 Complete - Advanced BI & Analytics",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "AI-Powered Auto-Dispatch",
            "Real-time GPS Tracking",
            "Temperature Monitoring",
            "Advanced Analytics & BI",
            "Multi-language Support",
            "Mobile PWA"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Cold Chain Backend",
        "phase": "Phase 10 - Advanced BI Complete",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/analytics/dashboard")
async def analytics_dashboard():
    return {
        "status": "success",
        "message": "Analytics Dashboard Data",
        "data": {
            "vehicle_analytics": {
                "total_vehicles": 40,
                "active_vehicles": 35,
                "average_utilization": 78.5,
                "fuel_efficiency": 5.5
            },
            "driver_evaluation": {
                "total_drivers": 40,
                "average_rating": 4.3,
                "top_performers": 5,
                "low_performers": 3
            },
            "customer_satisfaction": {
                "total_customers": 150,
                "satisfaction_rate": 92.5,
                "churn_risk": 8,
                "repeat_rate": 85.3
            },
            "route_efficiency": {
                "total_routes": 1250,
                "average_distance": 45.3,
                "time_efficiency": 88.7,
                "fuel_savings": "12%"
            },
            "cost_optimization": {
                "total_cost": 125000000,
                "savings_potential": "15%",
                "roi": 2.35,
                "optimization_score": 85
            }
        },
        "statistics": {
            "total_files": ">145",
            "total_code_lines": ">24,500",
            "api_endpoints": ">50",
            "tests": 127,
            "documentation": 25
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/docs-info")
async def docs_info():
    return {
        "swagger_ui": "https://8000-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai/docs",
        "redoc": "https://8000-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai/redoc",
        "note": "Full API documentation available at /docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
