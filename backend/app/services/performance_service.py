"""
Phase 16: Driver Performance Service
드라이버 성과 분석 서비스
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.models.driver_app import DriverPerformance
from app.models.dispatch import Dispatch, DispatchStatus


class PerformanceService:
    """드라이버 성과 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_performance(
        self,
        driver_id: int,
        period_start: datetime,
        period_end: datetime,
        period_type: str = "DAILY"
    ) -> DriverPerformance:
        """
        드라이버 성과 계산
        
        Args:
            driver_id: 드라이버 ID
            period_start: 기간 시작
            period_end: 기간 종료
            period_type: 기간 타입 (DAILY/WEEKLY/MONTHLY)
        
        Returns:
            계산된 성과 데이터
        """
        # 해당 기간의 배차 조회
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.driver_id == driver_id,
                Dispatch.created_at >= period_start,
                Dispatch.created_at <= period_end
            )
        ).all()
        
        # 통계 계산
        total_dispatches = len(dispatches)
        completed_dispatches = len([d for d in dispatches if d.status == DispatchStatus.COMPLETED])
        cancelled_dispatches = len([d for d in dispatches if d.status == DispatchStatus.CANCELLED])
        
        completion_rate = (completed_dispatches / total_dispatches * 100) if total_dispatches > 0 else 0.0
        
        # 거리/시간
        total_distance = sum([d.distance or 0.0 for d in dispatches])
        total_duration = sum([d.duration or 0 for d in dispatches])
        avg_delivery_time = (total_duration // total_dispatches) if total_dispatches > 0 else 0
        
        # 수익 (간단한 계산 예시)
        total_revenue = total_distance * 1500  # km당 1,500원
        avg_revenue_per_dispatch = (total_revenue / total_dispatches) if total_dispatches > 0 else 0.0
        
        # 평가 (임시 데이터)
        avg_rating = 4.5
        total_reviews = completed_dispatches
        
        # 순위 계산
        rank = self._calculate_driver_rank(driver_id, period_start, period_end)
        
        # 기존 성과 데이터 조회
        existing = self.db.query(DriverPerformance).filter(
            and_(
                DriverPerformance.driver_id == driver_id,
                DriverPerformance.period_start == period_start,
                DriverPerformance.period_end == period_end,
                DriverPerformance.period_type == period_type
            )
        ).first()
        
        if existing:
            # 업데이트
            existing.total_dispatches = total_dispatches
            existing.completed_dispatches = completed_dispatches
            existing.cancelled_dispatches = cancelled_dispatches
            existing.completion_rate = completion_rate
            existing.total_distance = total_distance
            existing.total_duration = total_duration
            existing.avg_delivery_time = avg_delivery_time
            existing.total_revenue = total_revenue
            existing.avg_revenue_per_dispatch = avg_revenue_per_dispatch
            existing.avg_rating = avg_rating
            existing.total_reviews = total_reviews
            existing.rank = rank
            existing.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(existing)
            
            return existing
        else:
            # 새로 생성
            performance = DriverPerformance(
                driver_id=driver_id,
                period_start=period_start,
                period_end=period_end,
                period_type=period_type,
                total_dispatches=total_dispatches,
                completed_dispatches=completed_dispatches,
                cancelled_dispatches=cancelled_dispatches,
                completion_rate=completion_rate,
                total_distance=total_distance,
                total_duration=total_duration,
                avg_delivery_time=avg_delivery_time,
                total_revenue=total_revenue,
                avg_revenue_per_dispatch=avg_revenue_per_dispatch,
                avg_rating=avg_rating,
                total_reviews=total_reviews,
                rank=rank
            )
            
            self.db.add(performance)
            self.db.commit()
            self.db.refresh(performance)
            
            return performance
    
    def get_driver_performance(
        self,
        driver_id: int,
        period_type: str = "DAILY",
        limit: int = 30
    ) -> List[DriverPerformance]:
        """
        드라이버 성과 이력 조회
        
        Args:
            driver_id: 드라이버 ID
            period_type: 기간 타입
            limit: 조회 개수
        
        Returns:
            성과 이력 목록
        """
        performances = self.db.query(DriverPerformance).filter(
            and_(
                DriverPerformance.driver_id == driver_id,
                DriverPerformance.period_type == period_type
            )
        ).order_by(
            desc(DriverPerformance.period_start)
        ).limit(limit).all()
        
        return performances
    
    def get_today_performance(self, driver_id: int) -> Optional[DriverPerformance]:
        """
        오늘의 성과 조회/계산
        
        Args:
            driver_id: 드라이버 ID
        
        Returns:
            오늘의 성과
        """
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        return self.calculate_performance(
            driver_id=driver_id,
            period_start=today,
            period_end=tomorrow,
            period_type="DAILY"
        )
    
    def get_weekly_performance(self, driver_id: int) -> Optional[DriverPerformance]:
        """
        이번 주 성과 조회/계산
        
        Args:
            driver_id: 드라이버 ID
        
        Returns:
            이번 주 성과
        """
        today = datetime.utcnow()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)
        
        return self.calculate_performance(
            driver_id=driver_id,
            period_start=week_start,
            period_end=week_end,
            period_type="WEEKLY"
        )
    
    def get_monthly_performance(self, driver_id: int) -> Optional[DriverPerformance]:
        """
        이번 달 성과 조회/계산
        
        Args:
            driver_id: 드라이버 ID
        
        Returns:
            이번 달 성과
        """
        today = datetime.utcnow()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if today.month == 12:
            month_end = month_start.replace(year=today.year + 1, month=1)
        else:
            month_end = month_start.replace(month=today.month + 1)
        
        return self.calculate_performance(
            driver_id=driver_id,
            period_start=month_start,
            period_end=month_end,
            period_type="MONTHLY"
        )
    
    def get_performance_statistics(self, driver_id: int) -> Dict[str, Any]:
        """
        드라이버 성과 통계
        
        Args:
            driver_id: 드라이버 ID
        
        Returns:
            통계 데이터
        """
        today_perf = self.get_today_performance(driver_id)
        weekly_perf = self.get_weekly_performance(driver_id)
        monthly_perf = self.get_monthly_performance(driver_id)
        
        return {
            "today": self._performance_to_dict(today_perf) if today_perf else None,
            "weekly": self._performance_to_dict(weekly_perf) if weekly_perf else None,
            "monthly": self._performance_to_dict(monthly_perf) if monthly_perf else None
        }
    
    def get_leaderboard(
        self,
        period_type: str = "MONTHLY",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        드라이버 순위표
        
        Args:
            period_type: 기간 타입
            limit: 조회 개수
        
        Returns:
            순위표
        """
        # 현재 기간의 성과 조회
        today = datetime.utcnow()
        
        if period_type == "DAILY":
            period_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period_type == "WEEKLY":
            period_start = today - timedelta(days=today.weekday())
            period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # MONTHLY
            period_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        performances = self.db.query(DriverPerformance).filter(
            and_(
                DriverPerformance.period_type == period_type,
                DriverPerformance.period_start >= period_start
            )
        ).order_by(
            desc(DriverPerformance.total_revenue)
        ).limit(limit).all()
        
        leaderboard = []
        for idx, perf in enumerate(performances, start=1):
            leaderboard.append({
                "rank": idx,
                "driver_id": perf.driver_id,
                "total_revenue": perf.total_revenue,
                "total_dispatches": perf.total_dispatches,
                "completion_rate": perf.completion_rate,
                "avg_rating": perf.avg_rating
            })
        
        return leaderboard
    
    def _calculate_driver_rank(
        self,
        driver_id: int,
        period_start: datetime,
        period_end: datetime
    ) -> Optional[int]:
        """드라이버 순위 계산"""
        # 모든 드라이버의 수익 기준 순위
        performances = self.db.query(DriverPerformance).filter(
            and_(
                DriverPerformance.period_start == period_start,
                DriverPerformance.period_end == period_end
            )
        ).order_by(
            desc(DriverPerformance.total_revenue)
        ).all()
        
        for idx, perf in enumerate(performances, start=1):
            if perf.driver_id == driver_id:
                return idx
        
        return None
    
    def _performance_to_dict(self, performance: DriverPerformance) -> Dict[str, Any]:
        """성과 객체를 딕셔너리로 변환"""
        return {
            "id": performance.id,
            "driver_id": performance.driver_id,
            "period_start": performance.period_start.isoformat(),
            "period_end": performance.period_end.isoformat(),
            "period_type": performance.period_type,
            "total_dispatches": performance.total_dispatches,
            "completed_dispatches": performance.completed_dispatches,
            "cancelled_dispatches": performance.cancelled_dispatches,
            "completion_rate": performance.completion_rate,
            "total_distance": performance.total_distance,
            "total_duration": performance.total_duration,
            "avg_delivery_time": performance.avg_delivery_time,
            "total_revenue": performance.total_revenue,
            "avg_revenue_per_dispatch": performance.avg_revenue_per_dispatch,
            "avg_rating": performance.avg_rating,
            "total_reviews": performance.total_reviews,
            "rank": performance.rank
        }
