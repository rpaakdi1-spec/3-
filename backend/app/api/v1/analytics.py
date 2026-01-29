"""
Analytics API Endpoints - Phase 10
고급 분석 및 BI API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.analytics import get_analytics_service
from app.services.vehicle_analytics import get_vehicle_performance_analytics
from app.services.driver_evaluation import get_driver_evaluation_system
from app.services.customer_analytics import get_customer_satisfaction_analytics
from app.services.route_efficiency import get_route_efficiency_analytics
from app.services.cost_optimization import get_cost_optimization_report

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/revenue")
async def get_revenue_analytics(
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """매출 분석 데이터 조회"""
    analytics_service = get_analytics_service(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return analytics_service.get_revenue_analytics(start_date, end_date)


@router.get("/roi")
async def get_roi_analytics(
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ROI 분석 데이터 조회"""
    analytics_service = get_analytics_service(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return analytics_service.get_roi_analytics(start_date, end_date)


@router.get("/kpi")
async def get_kpi_metrics(
    date: str = Query(..., description="Date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """KPI 지표 조회"""
    analytics_service = get_analytics_service(db)
    
    target_date = datetime.fromisoformat(date)
    
    return analytics_service.get_kpi_metrics(target_date)


@router.get("/vehicles/{vehicle_id}/performance")
async def get_vehicle_performance(
    vehicle_id: int,
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """개별 차량 성능 리포트"""
    vehicle_analytics = get_vehicle_performance_analytics(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return vehicle_analytics.get_vehicle_performance_report(
        vehicle_id,
        start_date,
        end_date
    )


@router.get("/vehicles/fleet-summary")
async def get_fleet_summary(
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """전체 차량 성능 요약"""
    vehicle_analytics = get_vehicle_performance_analytics(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return vehicle_analytics.get_fleet_performance_summary(start_date, end_date)


@router.get("/vehicles/maintenance-alerts")
async def get_maintenance_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """차량 유지보수 알림"""
    vehicle_analytics = get_vehicle_performance_analytics(db)
    
    return vehicle_analytics.get_vehicle_maintenance_alerts()


@router.get("/vehicles/compare")
async def compare_vehicles(
    vehicle_ids: str = Query(..., description="Comma-separated vehicle IDs"),
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """차량 간 성능 비교"""
    vehicle_analytics = get_vehicle_performance_analytics(db)
    
    ids = [int(id.strip()) for id in vehicle_ids.split(',')]
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return vehicle_analytics.compare_vehicles(ids, start_date, end_date)


@router.get("/drivers/{driver_id}/evaluation")
async def get_driver_evaluation(
    driver_id: int,
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """운전자 평가"""
    driver_system = get_driver_evaluation_system(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return driver_system.evaluate_driver(driver_id, start_date, end_date)


@router.get("/drivers/rankings")
async def get_driver_rankings(
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """운전자 랭킹"""
    driver_system = get_driver_evaluation_system(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return driver_system.get_driver_rankings(start_date, end_date)


@router.get("/drivers/{driver_id}/recommendations")
async def get_driver_recommendations(
    driver_id: int,
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """운전자 개선 권장사항"""
    driver_system = get_driver_evaluation_system(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return driver_system.get_improvement_recommendations(driver_id, start_date, end_date)


@router.get("/dashboard")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """대시보드 요약 데이터"""
    analytics_service = get_analytics_service(db)
    
    # 최근 30일 데이터
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    revenue = analytics_service.get_revenue_analytics(start_date, end_date)
    roi = analytics_service.get_roi_analytics(start_date, end_date)
    kpi = analytics_service.get_kpi_metrics(end_date)
    
    return {
        'revenue': revenue,
        'roi': roi,
        'kpi': kpi,
        'period': {
            'start': start_date.date().isoformat(),
            'end': end_date.date().isoformat()
        }
    }


# Customer Analytics Endpoints
@router.get("/customers/{partner_id}/satisfaction")
async def get_customer_satisfaction(
    partner_id: int,
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """고객 만족도 분석"""
    customer_analytics = get_customer_satisfaction_analytics(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return customer_analytics.analyze_customer_satisfaction(
        partner_id,
        start_date,
        end_date
    )


@router.get("/customers/top")
async def get_top_customers(
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    limit: int = Query(10, description="Number of top customers"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """주요 고객 분석"""
    customer_analytics = get_customer_satisfaction_analytics(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return customer_analytics.get_top_customers(start_date, end_date, limit)


@router.get("/customers/churn-risk")
async def get_churn_risk_customers(
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """이탈 위험 고객 식별"""
    customer_analytics = get_customer_satisfaction_analytics(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return customer_analytics.get_churn_risk_customers(start_date, end_date)


# Route Efficiency Endpoints
@router.get("/routes/{dispatch_id}/efficiency")
async def get_route_efficiency(
    dispatch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """개별 경로 효율성 분석"""
    route_analytics = get_route_efficiency_analytics(db)
    
    return route_analytics.analyze_route_efficiency(dispatch_id)


@router.get("/routes/fleet-efficiency")
async def get_fleet_route_efficiency(
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """전체 차량 경로 효율성 요약"""
    route_analytics = get_route_efficiency_analytics(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return route_analytics.get_fleet_route_efficiency_summary(start_date, end_date)


@router.get("/routes/inefficient")
async def get_inefficient_routes(
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    threshold: float = Query(70.0, description="Efficiency threshold (%)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """비효율적인 경로 식별"""
    route_analytics = get_route_efficiency_analytics(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return route_analytics.identify_inefficient_routes(start_date, end_date, threshold)


# Cost Optimization Endpoints
@router.get("/costs/report")
async def get_cost_report(
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """종합 비용 리포트"""
    cost_report = get_cost_optimization_report(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return cost_report.generate_cost_report(start_date, end_date)


@router.get("/costs/vehicles/{vehicle_id}")
async def get_vehicle_costs(
    vehicle_id: int,
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """개별 차량 비용 분석"""
    cost_report = get_cost_optimization_report(db)
    
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return cost_report.analyze_vehicle_costs(vehicle_id, start_date, end_date)


@router.get("/costs/vehicles/compare")
async def compare_vehicle_costs(
    vehicle_ids: str = Query(..., description="Comma-separated vehicle IDs"),
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """차량 간 비용 비교"""
    cost_report = get_cost_optimization_report(db)
    
    ids = [int(id.strip()) for id in vehicle_ids.split(',')]
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    
    return cost_report.compare_vehicle_costs(ids, start_date, end_date)
