"""
Advanced Analytics Service - Phase 10
비즈니스 인텔리전스 및 고급 분석 기능
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
import pandas as pd
import numpy as np
from app.models import Order, Dispatch, Vehicle, User


class AnalyticsService:
    """고급 분석 및 BI 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== 매출 분석 ====================
    
    def get_revenue_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        매출 분석
        
        Returns:
            - 총 매출
            - 일별 매출
            - 온도대별 매출
            - 성장률
        """
        # 기간 내 완료된 주문
        orders = self.db.query(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                Order.status == 'COMPLETED'
            )
        ).all()
        
        if not orders:
            return {
                'total_revenue': 0,
                'daily_revenue': [],
                'revenue_by_temperature': {},
                'growth_rate': 0
            }
        
        # 총 매출 (예: 주문당 기본 요금 + 거리 요금)
        total_revenue = sum([
            self._calculate_order_revenue(order) for order in orders
        ])
        
        # 일별 매출
        daily_revenue = self._calculate_daily_revenue(orders, start_date, end_date)
        
        # 온도대별 매출
        revenue_by_temp = self._calculate_revenue_by_temperature(orders)
        
        # 성장률 (전월 대비)
        growth_rate = self._calculate_growth_rate(start_date, end_date)
        
        return {
            'total_revenue': round(total_revenue, 2),
            'average_order_value': round(total_revenue / len(orders), 2),
            'order_count': len(orders),
            'daily_revenue': daily_revenue,
            'revenue_by_temperature': revenue_by_temp,
            'growth_rate': round(growth_rate, 2)
        }
    
    def _calculate_order_revenue(self, order: Order) -> float:
        """주문 매출 계산"""
        base_price = 50000  # 기본 요금 (원)
        distance_rate = 1000  # km당 요금 (원)
        pallet_rate = 5000  # 팔레트당 요금 (원)
        
        # 온도대별 추가 요금
        temp_multiplier = {
            '냉동': 1.5,
            '냉장': 1.2,
            '상온': 1.0
        }
        
        distance = getattr(order, 'distance_km', 0) or 0
        pallet_count = order.pallet_count or 0
        temp_zone = order.temperature_zone or '상온'
        
        revenue = (
            base_price +
            (distance * distance_rate) +
            (pallet_count * pallet_rate)
        ) * temp_multiplier.get(temp_zone, 1.0)
        
        return revenue
    
    def _calculate_daily_revenue(
        self,
        orders: List[Order],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """일별 매출 계산"""
        daily_data = {}
        
        for order in orders:
            date_key = order.created_at.date().isoformat()
            revenue = self._calculate_order_revenue(order)
            
            if date_key not in daily_data:
                daily_data[date_key] = {'date': date_key, 'revenue': 0, 'orders': 0}
            
            daily_data[date_key]['revenue'] += revenue
            daily_data[date_key]['orders'] += 1
        
        return sorted(daily_data.values(), key=lambda x: x['date'])
    
    def _calculate_revenue_by_temperature(self, orders: List[Order]) -> Dict:
        """온도대별 매출"""
        temp_revenue = {}
        
        for order in orders:
            temp = order.temperature_zone or '상온'
            revenue = self._calculate_order_revenue(order)
            
            if temp not in temp_revenue:
                temp_revenue[temp] = {'revenue': 0, 'orders': 0}
            
            temp_revenue[temp]['revenue'] += revenue
            temp_revenue[temp]['orders'] += 1
        
        return temp_revenue
    
    def _calculate_growth_rate(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """성장률 계산 (전월 대비)"""
        period_days = (end_date - start_date).days
        previous_start = start_date - timedelta(days=period_days)
        previous_end = start_date
        
        # 현재 기간 매출
        current_orders = self.db.query(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                Order.status == 'COMPLETED'
            )
        ).all()
        
        current_revenue = sum([
            self._calculate_order_revenue(o) for o in current_orders
        ])
        
        # 이전 기간 매출
        previous_orders = self.db.query(Order).filter(
            and_(
                Order.created_at >= previous_start,
                Order.created_at < previous_end,
                Order.status == 'COMPLETED'
            )
        ).all()
        
        previous_revenue = sum([
            self._calculate_order_revenue(o) for o in previous_orders
        ])
        
        if previous_revenue == 0:
            return 0
        
        growth_rate = ((current_revenue - previous_revenue) / previous_revenue) * 100
        return growth_rate
    
    # ==================== ROI 분석 ====================
    
    def get_roi_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        ROI 분석
        
        Returns:
            - 총 수익
            - 총 비용
            - ROI
            - 차량별 ROI
        """
        # 매출
        revenue_data = self.get_revenue_analytics(start_date, end_date)
        total_revenue = revenue_data['total_revenue']
        
        # 비용
        cost_data = self._calculate_operational_costs(start_date, end_date)
        total_cost = cost_data['total_cost']
        
        # ROI 계산
        if total_cost == 0:
            roi = 0
        else:
            roi = ((total_revenue - total_cost) / total_cost) * 100
        
        # 차량별 ROI
        vehicle_roi = self._calculate_vehicle_roi(start_date, end_date)
        
        return {
            'total_revenue': round(total_revenue, 2),
            'total_cost': round(total_cost, 2),
            'net_profit': round(total_revenue - total_cost, 2),
            'roi_percentage': round(roi, 2),
            'cost_breakdown': cost_data['breakdown'],
            'vehicle_roi': vehicle_roi
        }
    
    def _calculate_operational_costs(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """운영 비용 계산"""
        # 차량 운영 비용
        vehicles = self.db.query(Vehicle).all()
        
        # 기간 내 배차 수
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.created_at >= start_date,
                Dispatch.created_at <= end_date
            )
        ).all()
        
        # 비용 구성
        fuel_cost = len(dispatches) * 15000  # 배차당 평균 연료비
        maintenance_cost = len(vehicles) * 50000  # 차량당 월 유지보수비
        labor_cost = len(vehicles) * 3000000  # 운전자당 월급
        insurance_cost = len(vehicles) * 100000  # 차량당 월 보험료
        
        total_cost = fuel_cost + maintenance_cost + labor_cost + insurance_cost
        
        return {
            'total_cost': total_cost,
            'breakdown': {
                'fuel': fuel_cost,
                'maintenance': maintenance_cost,
                'labor': labor_cost,
                'insurance': insurance_cost
            }
        }
    
    def _calculate_vehicle_roi(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """차량별 ROI"""
        vehicles = self.db.query(Vehicle).all()
        vehicle_roi_data = []
        
        for vehicle in vehicles:
            # 차량의 배차 조회
            dispatches = self.db.query(Dispatch).filter(
                and_(
                    Dispatch.vehicle_id == vehicle.id,
                    Dispatch.created_at >= start_date,
                    Dispatch.created_at <= end_date
                )
            ).all()
            
            if not dispatches:
                continue
            
            # 매출
            revenue = 0
            for dispatch in dispatches:
                orders = dispatch.orders
                for order in orders:
                    if order.status == 'COMPLETED':
                        revenue += self._calculate_order_revenue(order)
            
            # 비용
            cost = len(dispatches) * 15000 + 150000  # 연료비 + 고정비
            
            # ROI
            roi = ((revenue - cost) / cost * 100) if cost > 0 else 0
            
            vehicle_roi_data.append({
                'vehicle_number': vehicle.vehicle_number,
                'revenue': round(revenue, 2),
                'cost': round(cost, 2),
                'profit': round(revenue - cost, 2),
                'roi': round(roi, 2),
                'dispatch_count': len(dispatches)
            })
        
        return sorted(vehicle_roi_data, key=lambda x: x['roi'], reverse=True)
    
    # ==================== KPI ====================
    
    def get_kpi_metrics(self, date: datetime) -> Dict:
        """
        핵심 성과 지표 (KPI)
        
        Returns:
            - 배송 완료율
            - 평균 배송 시간
            - 차량 가동률
            - 주문 정시 도착률
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        # 배송 완료율
        total_orders = self.db.query(Order).filter(
            and_(
                Order.created_at >= start_of_day,
                Order.created_at < end_of_day
            )
        ).count()
        
        completed_orders = self.db.query(Order).filter(
            and_(
                Order.created_at >= start_of_day,
                Order.created_at < end_of_day,
                Order.status == 'COMPLETED'
            )
        ).count()
        
        completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
        
        # 평균 배송 시간
        avg_delivery_time = self._calculate_average_delivery_time(start_of_day, end_of_day)
        
        # 차량 가동률
        utilization_rate = self._calculate_vehicle_utilization(start_of_day, end_of_day)
        
        # 정시 도착률
        on_time_rate = self._calculate_on_time_delivery_rate(start_of_day, end_of_day)
        
        # 주문 처리량
        throughput = total_orders
        
        # 평균 적재율
        load_rate = self._calculate_average_load_rate(start_of_day, end_of_day)
        
        return {
            'date': date.date().isoformat(),
            'completion_rate': round(completion_rate, 2),
            'average_delivery_time': round(avg_delivery_time, 2),
            'vehicle_utilization': round(utilization_rate, 2),
            'on_time_delivery_rate': round(on_time_rate, 2),
            'daily_throughput': throughput,
            'average_load_rate': round(load_rate, 2),
            'total_orders': total_orders,
            'completed_orders': completed_orders
        }
    
    def _calculate_average_delivery_time(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """평균 배송 시간 (분)"""
        completed_orders = self.db.query(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at < end_date,
                Order.status == 'COMPLETED',
                Order.completed_at.isnot(None)
            )
        ).all()
        
        if not completed_orders:
            return 0
        
        total_time = sum([
            (order.completed_at - order.created_at).total_seconds() / 60
            for order in completed_orders
            if order.completed_at
        ])
        
        return total_time / len(completed_orders)
    
    def _calculate_vehicle_utilization(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """차량 가동률"""
        total_vehicles = self.db.query(Vehicle).count()
        
        if total_vehicles == 0:
            return 0
        
        # 사용된 차량 수
        used_vehicles = self.db.query(Dispatch.vehicle_id).filter(
            and_(
                Dispatch.created_at >= start_date,
                Dispatch.created_at < end_date
            )
        ).distinct().count()
        
        return (used_vehicles / total_vehicles) * 100
    
    def _calculate_on_time_delivery_rate(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """정시 도착률"""
        completed_orders = self.db.query(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at < end_date,
                Order.status == 'COMPLETED'
            )
        ).all()
        
        if not completed_orders:
            return 100.0
        
        on_time = sum([
            1 for order in completed_orders
            if self._is_on_time(order)
        ])
        
        return (on_time / len(completed_orders)) * 100
    
    def _is_on_time(self, order: Order) -> bool:
        """주문이 정시에 완료되었는지 확인"""
        if not order.completed_at or not order.expected_delivery_time:
            return True
        
        # 예상 배송 시간 + 30분 허용
        deadline = order.expected_delivery_time + timedelta(minutes=30)
        return order.completed_at <= deadline
    
    def _calculate_average_load_rate(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """평균 적재율"""
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.created_at >= start_date,
                Dispatch.created_at < end_date
            )
        ).all()
        
        if not dispatches:
            return 0
        
        total_load_rate = 0
        
        for dispatch in dispatches:
            vehicle = dispatch.vehicle
            if not vehicle:
                continue
            
            # 적재된 팔레트 수
            loaded_pallets = sum([order.pallet_count for order in dispatch.orders])
            
            # 차량 용량
            capacity = vehicle.pallet_capacity or 30
            
            # 적재율
            load_rate = (loaded_pallets / capacity) * 100
            total_load_rate += min(load_rate, 100)
        
        return total_load_rate / len(dispatches)


# 글로벌 인스턴스 (의존성 주입용)
def get_analytics_service(db: Session) -> AnalyticsService:
    return AnalyticsService(db)
