"""
고급 분석 & BI API
KPI, 트렌드, 상세 분석 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models import User
from app.services.analytics_service import (
    AnalyticsService,
    KPIResult,
    TrendData
)
from app.services.gps_optimization_analytics import GPSOptimizationAnalytics

logger = logging.getLogger(__name__)

router = APIRouter()


# ========================================
# Pydantic 스키마
# ========================================

class KPIResponse(BaseModel):
    """KPI 응답"""
    name: str
    value: float
    unit: str
    target: float
    status: str
    change: float
    trend: str


class TrendResponse(BaseModel):
    """트렌드 응답"""
    labels: List[str]
    values: List[float]
    period_type: str


class TopClientResponse(BaseModel):
    """상위 고객 응답"""
    client_id: int
    client_name: str
    order_count: int
    total_revenue: float
    percentage: float


class HourlyDistributionResponse(BaseModel):
    """시간대별 분포 응답"""
    hour: int
    count: int


class DashboardSummary(BaseModel):
    """대시보드 요약"""
    kpis: List[KPIResponse]
    revenue_trend: TrendResponse
    order_trend: TrendResponse
    top_clients: List[TopClientResponse]
    hourly_distribution: List[HourlyDistributionResponse]


# ========================================
# 유틸리티
# ========================================

def parse_date_range(period: str) -> tuple:
    """기간 문자열 파싱"""
    today = date.today()
    
    if period == 'today':
        return today, today
    elif period == 'yesterday':
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    elif period == 'last_7_days':
        return today - timedelta(days=6), today
    elif period == 'last_30_days':
        return today - timedelta(days=29), today
    elif period == 'this_week':
        # 이번 주 (월요일 시작)
        start = today - timedelta(days=today.weekday())
        return start, today
    elif period == 'this_month':
        return today.replace(day=1), today
    elif period == 'last_month':
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        return first_day_last_month, last_day_last_month
    else:
        # 기본: 최근 7일
        return today - timedelta(days=6), today


# ========================================
# API 엔드포인트
# ========================================

@router.get("/analytics/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    period: str = Query('last_7_days', description="기간: today, yesterday, last_7_days, last_30_days, this_week, this_month, last_month"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    경영진 대시보드 요약
    
    - **period**: 조회 기간
    
    Returns:
        KPI, 트렌드, 상위 고객, 시간대별 분포
    """
    try:
        start_date, end_date = parse_date_range(period)
        service = AnalyticsService(db)
        
        # KPI 조회
        kpis = service.get_all_kpis(start_date, end_date)
        
        # 트렌드 조회
        revenue_trend = service.get_revenue_trend(days=30)
        order_trend = service.get_order_trend(days=30)
        
        # 상위 고객
        top_clients = service.get_top_clients(start_date, end_date, limit=10)
        
        # 시간대별 분포
        hourly_dist = service.get_hourly_distribution(start_date, end_date)
        
        return DashboardSummary(
            kpis=[
                KPIResponse(
                    name=kpi.name,
                    value=kpi.value,
                    unit=kpi.unit,
                    target=kpi.target,
                    status=kpi.status,
                    change=kpi.change,
                    trend=kpi.trend
                )
                for kpi in kpis
            ],
            revenue_trend=TrendResponse(
                labels=revenue_trend.labels,
                values=revenue_trend.values,
                period_type=revenue_trend.period_type
            ),
            order_trend=TrendResponse(
                labels=order_trend.labels,
                values=order_trend.values,
                period_type=order_trend.period_type
            ),
            top_clients=[
                TopClientResponse(**client)
                for client in top_clients
            ],
            hourly_distribution=[
                HourlyDistributionResponse(**item)
                for item in hourly_dist
            ]
        )
        
    except Exception as e:
        logger.error(f"대시보드 요약 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/kpi/order-completion-rate", response_model=KPIResponse)
async def get_order_completion_rate(
    period: str = Query('last_7_days'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """주문 처리율 KPI"""
    try:
        start_date, end_date = parse_date_range(period)
        service = AnalyticsService(db)
        kpi = service.get_order_completion_rate(start_date, end_date)
        
        return KPIResponse(
            name=kpi.name,
            value=kpi.value,
            unit=kpi.unit,
            target=kpi.target,
            status=kpi.status,
            change=kpi.change,
            trend=kpi.trend
        )
    except Exception as e:
        logger.error(f"KPI 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/kpi/on-time-delivery-rate", response_model=KPIResponse)
async def get_on_time_delivery_rate(
    period: str = Query('last_7_days'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """정시 배송률 KPI"""
    try:
        start_date, end_date = parse_date_range(period)
        service = AnalyticsService(db)
        kpi = service.get_on_time_delivery_rate(start_date, end_date)
        
        return KPIResponse(
            name=kpi.name,
            value=kpi.value,
            unit=kpi.unit,
            target=kpi.target,
            status=kpi.status,
            change=kpi.change,
            trend=kpi.trend
        )
    except Exception as e:
        logger.error(f"KPI 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/kpi/vehicle-utilization", response_model=KPIResponse)
async def get_vehicle_utilization(
    period: str = Query('last_7_days'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """차량 가동률 KPI"""
    try:
        start_date, end_date = parse_date_range(period)
        service = AnalyticsService(db)
        kpi = service.get_vehicle_utilization(start_date, end_date)
        
        return KPIResponse(
            name=kpi.name,
            value=kpi.value,
            unit=kpi.unit,
            target=kpi.target,
            status=kpi.status,
            change=kpi.change,
            trend=kpi.trend
        )
    except Exception as e:
        logger.error(f"KPI 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/kpi/average-delivery-time", response_model=KPIResponse)
async def get_average_delivery_time(
    period: str = Query('last_7_days'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """평균 배송 시간 KPI"""
    try:
        start_date, end_date = parse_date_range(period)
        service = AnalyticsService(db)
        kpi = service.get_average_delivery_time(start_date, end_date)
        
        return KPIResponse(
            name=kpi.name,
            value=kpi.value,
            unit=kpi.unit,
            target=kpi.target,
            status=kpi.status,
            change=kpi.change,
            trend=kpi.trend
        )
    except Exception as e:
        logger.error(f"KPI 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/kpi/daily-orders", response_model=KPIResponse)
async def get_daily_orders(
    period: str = Query('last_7_days'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """1일 평균 주문 KPI"""
    try:
        start_date, end_date = parse_date_range(period)
        service = AnalyticsService(db)
        kpi = service.get_daily_orders(start_date, end_date)
        
        return KPIResponse(
            name=kpi.name,
            value=kpi.value,
            unit=kpi.unit,
            target=kpi.target,
            status=kpi.status,
            change=kpi.change,
            trend=kpi.trend
        )
    except Exception as e:
        logger.error(f"KPI 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/kpi/daily-revenue", response_model=KPIResponse)
async def get_daily_revenue(
    period: str = Query('last_7_days'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """일일 평균 매출 KPI"""
    try:
        start_date, end_date = parse_date_range(period)
        service = AnalyticsService(db)
        kpi = service.get_daily_revenue(start_date, end_date)
        
        return KPIResponse(
            name=kpi.name,
            value=kpi.value,
            unit=kpi.unit,
            target=kpi.target,
            status=kpi.status,
            change=kpi.change,
            trend=kpi.trend
        )
    except Exception as e:
        logger.error(f"KPI 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/kpi/average-order-value", response_model=KPIResponse)
async def get_average_order_value(
    period: str = Query('last_7_days'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """평균 주문 금액 KPI"""
    try:
        start_date, end_date = parse_date_range(period)
        service = AnalyticsService(db)
        kpi = service.get_average_order_value(start_date, end_date)
        
        return KPIResponse(
            name=kpi.name,
            value=kpi.value,
            unit=kpi.unit,
            target=kpi.target,
            status=kpi.status,
            change=kpi.change,
            trend=kpi.trend
        )
    except Exception as e:
        logger.error(f"KPI 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/trend/revenue", response_model=TrendResponse)
async def get_revenue_trend(
    days: int = Query(30, ge=7, le=365, description="조회 일수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """매출 트렌드"""
    try:
        service = AnalyticsService(db)
        trend = service.get_revenue_trend(days=days)
        
        return TrendResponse(
            labels=trend.labels,
            values=trend.values,
            period_type=trend.period_type
        )
    except Exception as e:
        logger.error(f"트렌드 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/trend/orders", response_model=TrendResponse)
async def get_order_trend(
    days: int = Query(30, ge=7, le=365, description="조회 일수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """주문 트렌드"""
    try:
        service = AnalyticsService(db)
        trend = service.get_order_trend(days=days)
        
        return TrendResponse(
            labels=trend.labels,
            values=trend.values,
            period_type=trend.period_type
        )
    except Exception as e:
        logger.error(f"트렌드 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/top-clients", response_model=List[TopClientResponse])
async def get_top_clients(
    period: str = Query('last_30_days'),
    limit: int = Query(10, ge=5, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """상위 고객 분석"""
    try:
        start_date, end_date = parse_date_range(period)
        service = AnalyticsService(db)
        clients = service.get_top_clients(start_date, end_date, limit=limit)
        
        return [TopClientResponse(**client) for client in clients]
    except Exception as e:
        logger.error(f"상위 고객 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/hourly-distribution", response_model=List[HourlyDistributionResponse])
async def get_hourly_distribution(
    period: str = Query('last_30_days'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """시간대별 주문 분포"""
    try:
        start_date, end_date = parse_date_range(period)
        service = AnalyticsService(db)
        distribution = service.get_hourly_distribution(start_date, end_date)
        
        return [HourlyDistributionResponse(**item) for item in distribution]
    except Exception as e:
        logger.error(f"시간대별 분포 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# GPS 최적화 분석 엔드포인트
# ========================================

@router.get("/analytics/gps-optimization/report")
async def get_gps_optimization_report(
    start_date: Optional[str] = Query(None, description="분석 시작일 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="분석 종료일 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GPS 실시간 위치 기반 배차 최적화 효과 분석 리포트
    
    - GPS 데이터 활용률
    - 배차 효율성
    - 거리/시간/비용 절감 효과
    - 데이터 품질
    - 개선 권장사항
    """
    try:
        # 날짜 파싱
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        service = GPSOptimizationAnalytics(db)
        report = await service.get_comprehensive_report(start_dt, end_dt)
        
        return report
    except Exception as e:
        logger.error(f"GPS 최적화 리포트 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/gps-optimization/compare")
async def compare_gps_optimization(
    before_start: str = Query(..., description="적용 전 시작일 (YYYY-MM-DD)"),
    before_end: str = Query(..., description="적용 전 종료일 (YYYY-MM-DD)"),
    after_start: str = Query(..., description="적용 후 시작일 (YYYY-MM-DD)"),
    after_end: str = Query(..., description="적용 후 종료일 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GPS 실시간 위치 적용 전후 비교 분석
    
    - 거리 개선율
    - 시간 개선율
    - 비용 절감 효과
    """
    try:
        # 날짜 파싱
        before_start_dt = datetime.fromisoformat(before_start)
        before_end_dt = datetime.fromisoformat(before_end)
        after_start_dt = datetime.fromisoformat(after_start)
        after_end_dt = datetime.fromisoformat(after_end)
        
        service = GPSOptimizationAnalytics(db)
        comparison = await service.compare_before_after(
            before_start_dt, before_end_dt,
            after_start_dt, after_end_dt
        )
        
        return comparison
    except Exception as e:
        logger.error(f"GPS 최적화 전후 비교 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# GPS 수집 최적화 엔드포인트
# ========================================

from app.services.gps_collection_optimizer import GPSCollectionOptimizer

@router.get("/analytics/gps-collection/strategy")
async def get_gps_collection_strategy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    차량별 GPS 수집 전략 분석
    
    - 차량 상태별 권장 수집 주기
    - 데이터 품질 평가
    - 주의 필요 차량 목록
    """
    try:
        optimizer = GPSCollectionOptimizer(db)
        strategy = await optimizer.get_collection_strategy()
        return strategy
    except Exception as e:
        logger.error(f"GPS 수집 전략 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/gps-collection/recommendations")
async def get_gps_collection_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GPS 데이터 수집 최적화 권장사항
    
    - 수집 주기 최적화
    - 데이터 품질 개선
    - 비용 절감 방안
    """
    try:
        optimizer = GPSCollectionOptimizer(db)
        recommendations = await optimizer.get_optimization_recommendations()
        return recommendations
    except Exception as e:
        logger.error(f"GPS 수집 권장사항 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# 차량 위치 예측 엔드포인트
# ========================================

from app.services.vehicle_location_predictor import VehicleLocationPredictor

@router.get("/analytics/vehicle-location/predict/{vehicle_id}")
async def predict_vehicle_location(
    vehicle_id: int,
    prediction_minutes: int = Query(30, ge=5, le=120, description="예측 시간 (5-120분)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 차량의 미래 위치 예측
    
    - 배차 경로 기반 예측 (배차 중일 경우)
    - 과거 이력 기반 예측 (배차 없을 경우)
    - 예측 신뢰도 포함
    """
    try:
        predictor = VehicleLocationPredictor(db)
        prediction = await predictor.predict_vehicle_location(vehicle_id, prediction_minutes)
        return prediction
    except Exception as e:
        logger.error(f"차량 위치 예측 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics/vehicle-location/predict-multiple")
async def predict_multiple_vehicle_locations(
    vehicle_ids: Optional[List[int]] = None,
    prediction_minutes: int = Query(30, ge=5, le=120),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    여러 차량의 미래 위치 일괄 예측
    
    - vehicle_ids가 null이면 모든 활성 차량 예측
    - 배차 중 차량 우선 예측
    """
    try:
        predictor = VehicleLocationPredictor(db)
        predictions = await predictor.predict_multiple_vehicles(vehicle_ids, prediction_minutes)
        return predictions
    except Exception as e:
        logger.error(f"여러 차량 위치 예측 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/vehicle-location/accuracy/{vehicle_id}")
async def evaluate_prediction_accuracy(
    vehicle_id: int,
    test_period_days: int = Query(7, ge=1, le=30, description="평가 기간 (1-30일)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    차량 위치 예측 정확도 평가
    
    - 과거 데이터로 예측 정확도 검증
    - 평균 오차, 정확도 비율 계산
    """
    try:
        predictor = VehicleLocationPredictor(db)
        evaluation = await predictor.evaluate_prediction_accuracy(vehicle_id, test_period_days)
        return evaluation
    except Exception as e:
        logger.error(f"예측 정확도 평가 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
