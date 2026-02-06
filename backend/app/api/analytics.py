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
