"""
Analytics API endpoints for dispatch history analysis and dashboard
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Optional
from app.core.database import get_db
from app.services.analytics_service import analytics_service
from app.schemas.analytics import (
    PeriodStatistics,
    VehicleAnalytics,
    ClientAnalytics,
    DashboardSummary
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dispatch-statistics", response_model=PeriodStatistics)
def get_dispatch_statistics(
    start_date: date = Query(..., description="시작 날짜 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="종료 날짜 (YYYY-MM-DD)"),
    period: str = Query("daily", regex="^(daily|weekly|monthly)$", description="집계 단위"),
    db: Session = Depends(get_db)
):
    """
    배차 통계 조회 (일별/주별/월별)
    
    - **start_date**: 시작 날짜
    - **end_date**: 종료 날짜
    - **period**: 집계 단위 (daily/weekly/monthly)
    
    Returns:
        기간별 배차 통계 (배차 건수, 주문 건수, 팔레트 수, 거리 등)
    """
    try:
        # Validate date range
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="시작 날짜가 종료 날짜보다 늦을 수 없습니다")
        
        # Limit to 1 year
        if (end_date - start_date).days > 365:
            raise HTTPException(status_code=400, detail="조회 기간은 최대 1년입니다")
        
        return analytics_service.get_dispatch_statistics(db, start_date, end_date, period)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dispatch statistics: {e}")
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}")


@router.get("/vehicle-analytics", response_model=VehicleAnalytics)
def get_vehicle_analytics(
    start_date: date = Query(..., description="시작 날짜 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    차량별 운행 분석
    
    - **start_date**: 시작 날짜
    - **end_date**: 종료 날짜
    
    Returns:
        차량별 운행 성과 (배차 횟수, 주행 거리, 적재율 등)
    """
    try:
        # Validate date range
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="시작 날짜가 종료 날짜보다 늦을 수 없습니다")
        
        if (end_date - start_date).days > 365:
            raise HTTPException(status_code=400, detail="조회 기간은 최대 1년입니다")
        
        return analytics_service.get_vehicle_analytics(db, start_date, end_date)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vehicle analytics: {e}")
        raise HTTPException(status_code=500, detail=f"차량 분석 중 오류가 발생했습니다: {str(e)}")


@router.get("/client-analytics", response_model=ClientAnalytics)
def get_client_analytics(
    start_date: date = Query(..., description="시작 날짜 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    거래처별 배송 통계
    
    - **start_date**: 시작 날짜
    - **end_date**: 종료 날짜
    
    Returns:
        거래처별 배송 통계 (주문 건수, 배송 빈도, 지역별 분포 등)
    """
    try:
        # Validate date range
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="시작 날짜가 종료 날짜보다 늦을 수 없습니다")
        
        if (end_date - start_date).days > 365:
            raise HTTPException(status_code=400, detail="조회 기간은 최대 1년입니다")
        
        return analytics_service.get_client_analytics(db, start_date, end_date)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client analytics: {e}")
        raise HTTPException(status_code=500, detail=f"거래처 분석 중 오류가 발생했습니다: {str(e)}")


@router.get("/dashboard-summary", response_model=DashboardSummary)
def get_dashboard_summary(
    target_date: Optional[date] = Query(None, description="기준 날짜 (기본값: 오늘)"),
    db: Session = Depends(get_db)
):
    """
    대시보드 요약 통계
    
    - **target_date**: 기준 날짜 (선택 사항, 기본값: 오늘)
    
    Returns:
        대시보드 요약 통계 (오늘/이번 주/이번 달 통계, 차량/거래처 현황, 증감율)
    """
    try:
        return analytics_service.get_dashboard_summary(db, target_date)
    
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=f"대시보드 요약 조회 중 오류가 발생했습니다: {str(e)}")


@router.get("/quick-stats")
def get_quick_stats(
    db: Session = Depends(get_db)
):
    """
    빠른 통계 (최근 7일)
    
    Returns:
        최근 7일간의 간단한 통계
    """
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        stats = analytics_service.get_dispatch_statistics(db, start_date, end_date, "daily")
        
        # Simplify response
        return {
            "period": "last_7_days",
            "start_date": start_date,
            "end_date": end_date,
            "daily_stats": [
                {
                    "date": s.date,
                    "dispatches": s.total_dispatches,
                    "orders": s.total_orders,
                    "pallets": s.total_pallets
                }
                for s in stats.statistics
            ],
            "summary": stats.summary
        }
    
    except Exception as e:
        logger.error(f"Error getting quick stats: {e}")
        raise HTTPException(status_code=500, detail=f"빠른 통계 조회 중 오류가 발생했습니다: {str(e)}")
