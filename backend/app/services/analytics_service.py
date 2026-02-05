"""
고급 분석 & BI 서비스
KPI 계산, 트렌드 분석, 예측 엔진
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from app.models import (
    Order, Dispatch, Vehicle, Driver, Client,
    OrderStatus, DispatchStatus
)

logger = logging.getLogger(__name__)


@dataclass
class KPIResult:
    """KPI 결과"""
    name: str
    value: float
    unit: str
    target: float
    status: str  # 'good', 'warning', 'critical'
    change: float  # 전 기간 대비 변화율
    trend: str  # 'up', 'down', 'stable'


@dataclass
class TrendData:
    """트렌드 데이터"""
    labels: List[str]
    values: List[float]
    period_type: str  # 'daily', 'weekly', 'monthly'


class AnalyticsService:
    """분석 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================
    # KPI 계산 (15개)
    # ========================================
    
    def get_order_completion_rate(
        self,
        start_date: date,
        end_date: date
    ) -> KPIResult:
        """KPI 1: 주문 처리율"""
        # 전체 주문
        total_orders = self.db.query(func.count(Order.id)).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1)
        ).scalar() or 0
        
        # 완료된 주문
        completed_orders = self.db.query(func.count(Order.id)).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1),
            Order.status == OrderStatus.COMPLETED
        ).scalar() or 0
        
        rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
        
        # 전 기간 대비 변화
        prev_start = start_date - (end_date - start_date + timedelta(days=1))
        prev_end = start_date - timedelta(days=1)
        prev_rate = self._calculate_completion_rate(prev_start, prev_end)
        change = rate - prev_rate
        
        return KPIResult(
            name="주문 처리율",
            value=round(rate, 1),
            unit="%",
            target=95.0,
            status='good' if rate >= 95 else 'warning' if rate >= 90 else 'critical',
            change=round(change, 1),
            trend='up' if change > 0 else 'down' if change < 0 else 'stable'
        )
    
    def get_on_time_delivery_rate(
        self,
        start_date: date,
        end_date: date
    ) -> KPIResult:
        """KPI 2: 정시 배송률"""
        # 완료된 배차
        completed_dispatches = self.db.query(Dispatch).filter(
            Dispatch.created_at >= start_date,
            Dispatch.created_at < end_date + timedelta(days=1),
            Dispatch.status == DispatchStatus.COMPLETED
        ).all()
        
        if not completed_dispatches:
            return self._empty_kpi("정시 배송률", "%", 90.0)
        
        # 정시 배송 카운트 (실제 완료 시간 <= 예상 완료 시간)
        on_time_count = sum(
            1 for d in completed_dispatches
            if d.completed_at and d.estimated_arrival_time and
            d.completed_at <= d.estimated_arrival_time
        )
        
        rate = (on_time_count / len(completed_dispatches) * 100)
        prev_rate = self._calculate_on_time_rate(
            start_date - (end_date - start_date + timedelta(days=1)),
            start_date - timedelta(days=1)
        )
        change = rate - prev_rate
        
        return KPIResult(
            name="정시 배송률",
            value=round(rate, 1),
            unit="%",
            target=90.0,
            status='good' if rate >= 90 else 'warning' if rate >= 85 else 'critical',
            change=round(change, 1),
            trend='up' if change > 0 else 'down' if change < 0 else 'stable'
        )
    
    def get_vehicle_utilization(
        self,
        start_date: date,
        end_date: date
    ) -> KPIResult:
        """KPI 3: 차량 가동률"""
        # 활성 차량 수
        active_vehicles = self.db.query(func.count(Vehicle.id)).filter(
            Vehicle.is_active == True
        ).scalar() or 0
        
        if active_vehicles == 0:
            return self._empty_kpi("차량 가동률", "%", 75.0)
        
        # 가용 시간 (8시간/일 * 영업일 * 차량 수)
        business_days = (end_date - start_date).days + 1
        available_hours = business_days * 8 * active_vehicles
        
        # 실제 운행 시간 (배차 시간 합계)
        total_dispatch_time = self.db.query(
            func.sum(
                func.extract('epoch', Dispatch.completed_at - Dispatch.started_at) / 3600
            )
        ).filter(
            Dispatch.started_at >= start_date,
            Dispatch.started_at < end_date + timedelta(days=1),
            Dispatch.status == DispatchStatus.COMPLETED,
            Dispatch.completed_at.isnot(None)
        ).scalar() or 0
        
        rate = (total_dispatch_time / available_hours * 100) if available_hours > 0 else 0
        prev_rate = self._calculate_utilization_rate(
            start_date - (end_date - start_date + timedelta(days=1)),
            start_date - timedelta(days=1)
        )
        change = rate - prev_rate
        
        return KPIResult(
            name="차량 가동률",
            value=round(rate, 1),
            unit="%",
            target=75.0,
            status='good' if rate >= 75 else 'warning' if rate >= 65 else 'critical',
            change=round(change, 1),
            trend='up' if change > 0 else 'down' if change < 0 else 'stable'
        )
    
    def get_average_delivery_time(
        self,
        start_date: date,
        end_date: date
    ) -> KPIResult:
        """KPI 4: 평균 배송 시간 (시간 단위)"""
        dispatches = self.db.query(Dispatch).filter(
            Dispatch.created_at >= start_date,
            Dispatch.created_at < end_date + timedelta(days=1),
            Dispatch.status == DispatchStatus.COMPLETED,
            Dispatch.completed_at.isnot(None)
        ).all()
        
        if not dispatches:
            return self._empty_kpi("평균 배송 시간", "시간", 4.0)
        
        total_hours = sum(
            (d.completed_at - d.created_at).total_seconds() / 3600
            for d in dispatches
        )
        avg_hours = total_hours / len(dispatches)
        
        prev_avg = self._calculate_avg_delivery_time(
            start_date - (end_date - start_date + timedelta(days=1)),
            start_date - timedelta(days=1)
        )
        change = avg_hours - prev_avg
        
        return KPIResult(
            name="평균 배송 시간",
            value=round(avg_hours, 1),
            unit="시간",
            target=4.0,
            status='good' if avg_hours <= 4 else 'warning' if avg_hours <= 5 else 'critical',
            change=round(change, 1),
            trend='down' if change < 0 else 'up' if change > 0 else 'stable'  # 낮을수록 좋음
        )
    
    def get_daily_orders(
        self,
        start_date: date,
        end_date: date
    ) -> KPIResult:
        """KPI 5: 1일 평균 배송 건수"""
        total_orders = self.db.query(func.count(Order.id)).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1)
        ).scalar() or 0
        
        business_days = (end_date - start_date).days + 1
        avg_orders = total_orders / business_days if business_days > 0 else 0
        
        prev_avg = self._calculate_daily_orders(
            start_date - (end_date - start_date + timedelta(days=1)),
            start_date - timedelta(days=1)
        )
        change = avg_orders - prev_avg
        
        return KPIResult(
            name="1일 평균 주문",
            value=round(avg_orders, 0),
            unit="건",
            target=120.0,
            status='good' if avg_orders >= 120 else 'warning' if avg_orders >= 100 else 'critical',
            change=round(change, 0),
            trend='up' if change > 0 else 'down' if change < 0 else 'stable'
        )
    
    def get_daily_revenue(
        self,
        start_date: date,
        end_date: date
    ) -> KPIResult:
        """KPI 6: 일일 평균 매출"""
        total_revenue = self.db.query(
            func.sum(Order.total_amount)
        ).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1),
            Order.status == OrderStatus.COMPLETED
        ).scalar() or 0
        
        business_days = (end_date - start_date).days + 1
        avg_revenue = total_revenue / business_days if business_days > 0 else 0
        
        prev_avg = self._calculate_daily_revenue(
            start_date - (end_date - start_date + timedelta(days=1)),
            start_date - timedelta(days=1)
        )
        change_pct = ((avg_revenue - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
        
        return KPIResult(
            name="일일 평균 매출",
            value=round(avg_revenue / 1000000, 1),  # 백만원 단위
            unit="M원",
            target=5.0,  # 5백만원
            status='good' if avg_revenue >= 5000000 else 'warning' if avg_revenue >= 4000000 else 'critical',
            change=round(change_pct, 1),
            trend='up' if change_pct > 0 else 'down' if change_pct < 0 else 'stable'
        )
    
    def get_average_order_value(
        self,
        start_date: date,
        end_date: date
    ) -> KPIResult:
        """KPI 7: 평균 주문 금액"""
        result = self.db.query(
            func.avg(Order.total_amount),
            func.count(Order.id)
        ).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1),
            Order.status == OrderStatus.COMPLETED
        ).first()
        
        avg_value = result[0] or 0
        prev_avg = self._calculate_avg_order_value(
            start_date - (end_date - start_date + timedelta(days=1)),
            start_date - timedelta(days=1)
        )
        change_pct = ((avg_value - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
        
        return KPIResult(
            name="평균 주문 금액",
            value=round(avg_value / 1000, 0),  # 천원 단위
            unit="천원",
            target=150.0,
            status='good' if avg_value >= 150000 else 'warning' if avg_value >= 120000 else 'critical',
            change=round(change_pct, 1),
            trend='up' if change_pct > 0 else 'down' if change_pct < 0 else 'stable'
        )
    
    def get_all_kpis(
        self,
        start_date: date,
        end_date: date
    ) -> List[KPIResult]:
        """모든 KPI 조회"""
        kpis = [
            self.get_order_completion_rate(start_date, end_date),
            self.get_on_time_delivery_rate(start_date, end_date),
            self.get_vehicle_utilization(start_date, end_date),
            self.get_average_delivery_time(start_date, end_date),
            self.get_daily_orders(start_date, end_date),
            self.get_daily_revenue(start_date, end_date),
            self.get_average_order_value(start_date, end_date),
        ]
        return kpis
    
    # ========================================
    # 트렌드 분석
    # ========================================
    
    def get_revenue_trend(
        self,
        days: int = 30
    ) -> TrendData:
        """매출 트렌드 (일별)"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # 일별 매출 집계
        daily_revenue = self.db.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1),
            Order.status == OrderStatus.COMPLETED
        ).group_by(
            func.date(Order.created_at)
        ).order_by('date').all()
        
        # 모든 날짜 채우기 (데이터 없는 날은 0)
        date_dict = {row.date: float(row.revenue) for row in daily_revenue}
        labels = []
        values = []
        
        current_date = start_date
        while current_date <= end_date:
            labels.append(current_date.strftime('%m/%d'))
            values.append(date_dict.get(current_date, 0.0) / 1000000)  # 백만원 단위
            current_date += timedelta(days=1)
        
        return TrendData(
            labels=labels,
            values=values,
            period_type='daily'
        )
    
    def get_order_trend(
        self,
        days: int = 30
    ) -> TrendData:
        """주문 트렌드 (일별)"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        daily_orders = self.db.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('count')
        ).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1)
        ).group_by(
            func.date(Order.created_at)
        ).order_by('date').all()
        
        date_dict = {row.date: int(row.count) for row in daily_orders}
        labels = []
        values = []
        
        current_date = start_date
        while current_date <= end_date:
            labels.append(current_date.strftime('%m/%d'))
            values.append(float(date_dict.get(current_date, 0)))
            current_date += timedelta(days=1)
        
        return TrendData(
            labels=labels,
            values=values,
            period_type='daily'
        )
    
    # ========================================
    # 상세 분석
    # ========================================
    
    def get_top_clients(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """상위 고객 분석"""
        top_clients = self.db.query(
            Client.id,
            Client.name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_revenue')
        ).join(
            Order, Order.client_id == Client.id
        ).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1)
        ).group_by(
            Client.id, Client.name
        ).order_by(
            desc('order_count')
        ).limit(limit).all()
        
        return [
            {
                'client_id': row.id,
                'client_name': row.name,
                'order_count': row.order_count,
                'total_revenue': float(row.total_revenue or 0),
                'percentage': 0.0  # 전체 대비 비율 (추후 계산)
            }
            for row in top_clients
        ]
    
    def get_hourly_distribution(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """시간대별 주문 분포"""
        hourly_orders = self.db.query(
            func.extract('hour', Order.created_at).label('hour'),
            func.count(Order.id).label('count')
        ).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1)
        ).group_by('hour').order_by('hour').all()
        
        # 모든 시간대 채우기
        hour_dict = {int(row.hour): int(row.count) for row in hourly_orders}
        return [
            {
                'hour': hour,
                'count': hour_dict.get(hour, 0)
            }
            for hour in range(24)
        ]
    
    # ========================================
    # 헬퍼 메서드
    # ========================================
    
    def _calculate_completion_rate(self, start_date: date, end_date: date) -> float:
        """주문 처리율 계산 (헬퍼)"""
        total = self.db.query(func.count(Order.id)).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1)
        ).scalar() or 0
        
        completed = self.db.query(func.count(Order.id)).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1),
            Order.status == OrderStatus.COMPLETED
        ).scalar() or 0
        
        return (completed / total * 100) if total > 0 else 0
    
    def _calculate_on_time_rate(self, start_date: date, end_date: date) -> float:
        """정시 배송률 계산 (헬퍼)"""
        dispatches = self.db.query(Dispatch).filter(
            Dispatch.created_at >= start_date,
            Dispatch.created_at < end_date + timedelta(days=1),
            Dispatch.status == DispatchStatus.COMPLETED
        ).all()
        
        if not dispatches:
            return 0.0
        
        on_time = sum(
            1 for d in dispatches
            if d.completed_at and d.estimated_arrival_time and
            d.completed_at <= d.estimated_arrival_time
        )
        
        return (on_time / len(dispatches) * 100)
    
    def _calculate_utilization_rate(self, start_date: date, end_date: date) -> float:
        """차량 가동률 계산 (헬퍼)"""
        active_vehicles = self.db.query(func.count(Vehicle.id)).filter(
            Vehicle.is_active == True
        ).scalar() or 0
        
        if active_vehicles == 0:
            return 0.0
        
        business_days = (end_date - start_date).days + 1
        available_hours = business_days * 8 * active_vehicles
        
        total_time = self.db.query(
            func.sum(
                func.extract('epoch', Dispatch.completed_at - Dispatch.started_at) / 3600
            )
        ).filter(
            Dispatch.started_at >= start_date,
            Dispatch.started_at < end_date + timedelta(days=1),
            Dispatch.status == DispatchStatus.COMPLETED,
            Dispatch.completed_at.isnot(None)
        ).scalar() or 0
        
        return (total_time / available_hours * 100) if available_hours > 0 else 0
    
    def _calculate_avg_delivery_time(self, start_date: date, end_date: date) -> float:
        """평균 배송 시간 계산 (헬퍼)"""
        dispatches = self.db.query(Dispatch).filter(
            Dispatch.created_at >= start_date,
            Dispatch.created_at < end_date + timedelta(days=1),
            Dispatch.status == DispatchStatus.COMPLETED,
            Dispatch.completed_at.isnot(None)
        ).all()
        
        if not dispatches:
            return 0.0
        
        total_hours = sum(
            (d.completed_at - d.created_at).total_seconds() / 3600
            for d in dispatches
        )
        return total_hours / len(dispatches)
    
    def _calculate_daily_orders(self, start_date: date, end_date: date) -> float:
        """일일 평균 주문 계산 (헬퍼)"""
        total = self.db.query(func.count(Order.id)).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1)
        ).scalar() or 0
        
        days = (end_date - start_date).days + 1
        return total / days if days > 0 else 0
    
    def _calculate_daily_revenue(self, start_date: date, end_date: date) -> float:
        """일일 평균 매출 계산 (헬퍼)"""
        total = self.db.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1),
            Order.status == OrderStatus.COMPLETED
        ).scalar() or 0
        
        days = (end_date - start_date).days + 1
        return total / days if days > 0 else 0
    
    def _calculate_avg_order_value(self, start_date: date, end_date: date) -> float:
        """평균 주문 금액 계산 (헬퍼)"""
        result = self.db.query(func.avg(Order.total_amount)).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date + timedelta(days=1),
            Order.status == OrderStatus.COMPLETED
        ).scalar()
        
        return result or 0.0
    
    def _empty_kpi(self, name: str, unit: str, target: float) -> KPIResult:
        """빈 KPI 결과"""
        return KPIResult(
            name=name,
            value=0.0,
            unit=unit,
            target=target,
            status='critical',
            change=0.0,
            trend='stable'
        )
