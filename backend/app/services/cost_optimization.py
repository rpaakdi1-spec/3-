"""
Cost Optimization Report - Phase 10
비용 최적화 리포트 시스템
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models import Dispatch, Order, Vehicle
import numpy as np


class CostOptimizationReport:
    """비용 최적화 리포트 시스템"""
    
    # 비용 상수 (실제 값으로 조정 필요)
    FUEL_COST_PER_LITER = 1800  # 원/리터
    DRIVER_COST_PER_HOUR = 15000  # 원/시간
    VEHICLE_MAINTENANCE_COST_PER_KM = 150  # 원/km
    FIXED_COST_PER_DISPATCH = 30000  # 원/배차 (기본 비용)
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_cost_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        종합 비용 리포트 생성
        
        분석 항목:
        - 연료비
        - 인건비
        - 유지보수비
        - 총 운영비용
        - 건당 비용
        - 비용 절감 기회
        """
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.created_at >= start_date,
                Dispatch.created_at <= end_date
            )
        ).all()
        
        if not dispatches:
            return {
                'period': {
                    'start': start_date.date().isoformat(),
                    'end': end_date.date().isoformat()
                },
                'message': 'No dispatches found for this period'
            }
        
        # 비용 계산
        fuel_cost = self._calculate_fuel_cost(dispatches)
        labor_cost = self._calculate_labor_cost(dispatches)
        maintenance_cost = self._calculate_maintenance_cost(dispatches)
        fixed_cost = len(dispatches) * self.FIXED_COST_PER_DISPATCH
        
        total_cost = fuel_cost + labor_cost + maintenance_cost + fixed_cost
        
        # 수익 계산
        total_deliveries = sum(len(d.orders) for d in dispatches)
        total_revenue = self._calculate_revenue(dispatches)
        
        # 비용 절감 기회 분석
        savings_opportunities = self._identify_savings_opportunities(
            dispatches,
            fuel_cost,
            labor_cost
        )
        
        # 주요 지표
        cost_per_delivery = total_cost / total_deliveries if total_deliveries > 0 else 0
        cost_per_km = total_cost / self._calculate_total_distance(dispatches) if self._calculate_total_distance(dispatches) > 0 else 0
        profit_margin = ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'period': {
                'start': start_date.date().isoformat(),
                'end': end_date.date().isoformat()
            },
            'costs': {
                'fuel_cost': round(fuel_cost, 0),
                'labor_cost': round(labor_cost, 0),
                'maintenance_cost': round(maintenance_cost, 0),
                'fixed_cost': round(fixed_cost, 0),
                'total_cost': round(total_cost, 0)
            },
            'revenue': {
                'total_revenue': round(total_revenue, 0),
                'profit': round(total_revenue - total_cost, 0),
                'profit_margin_percent': round(profit_margin, 2)
            },
            'metrics': {
                'total_dispatches': len(dispatches),
                'total_deliveries': total_deliveries,
                'total_distance_km': round(self._calculate_total_distance(dispatches), 2),
                'cost_per_delivery': round(cost_per_delivery, 0),
                'cost_per_km': round(cost_per_km, 0),
                'avg_revenue_per_delivery': round(total_revenue / total_deliveries, 0) if total_deliveries > 0 else 0
            },
            'cost_breakdown_percent': {
                'fuel': round(fuel_cost / total_cost * 100, 1) if total_cost > 0 else 0,
                'labor': round(labor_cost / total_cost * 100, 1) if total_cost > 0 else 0,
                'maintenance': round(maintenance_cost / total_cost * 100, 1) if total_cost > 0 else 0,
                'fixed': round(fixed_cost / total_cost * 100, 1) if total_cost > 0 else 0
            },
            'savings_opportunities': savings_opportunities,
            'recommendations': self._generate_cost_recommendations(
                profit_margin,
                cost_per_delivery,
                savings_opportunities
            )
        }
    
    def _calculate_fuel_cost(self, dispatches: List[Dispatch]) -> float:
        """연료비 계산"""
        total_distance = self._calculate_total_distance(dispatches)
        
        # 평균 연비 5.5 km/L (냉동차)
        fuel_efficiency = 5.5
        
        fuel_consumed = total_distance / fuel_efficiency
        fuel_cost = fuel_consumed * self.FUEL_COST_PER_LITER
        
        return fuel_cost
    
    def _calculate_labor_cost(self, dispatches: List[Dispatch]) -> float:
        """인건비 계산"""
        total_hours = 0
        
        for dispatch in dispatches:
            if hasattr(dispatch, 'started_at') and hasattr(dispatch, 'completed_at'):
                if dispatch.completed_at and dispatch.started_at:
                    duration = (dispatch.completed_at - dispatch.started_at).total_seconds() / 3600
                    total_hours += duration
                else:
                    # 추정: 주문당 0.5시간
                    total_hours += len(dispatch.orders) * 0.5
            else:
                # 추정: 주문당 0.5시간
                total_hours += len(dispatch.orders) * 0.5
        
        labor_cost = total_hours * self.DRIVER_COST_PER_HOUR
        
        return labor_cost
    
    def _calculate_maintenance_cost(self, dispatches: List[Dispatch]) -> float:
        """유지보수비 계산"""
        total_distance = self._calculate_total_distance(dispatches)
        maintenance_cost = total_distance * self.VEHICLE_MAINTENANCE_COST_PER_KM
        
        return maintenance_cost
    
    def _calculate_total_distance(self, dispatches: List[Dispatch]) -> float:
        """총 주행 거리"""
        total_distance = 0
        
        for dispatch in dispatches:
            for order in dispatch.orders:
                distance = getattr(order, 'distance_km', 0) or 0
                total_distance += distance
        
        return total_distance
    
    def _calculate_revenue(self, dispatches: List[Dispatch]) -> float:
        """총 수익 계산"""
        total_revenue = 0
        
        for dispatch in dispatches:
            for order in dispatch.orders:
                price = getattr(order, 'price', 0) or 0
                total_revenue += price
        
        return total_revenue
    
    def _identify_savings_opportunities(
        self,
        dispatches: List[Dispatch],
        fuel_cost: float,
        labor_cost: float
    ) -> List[Dict]:
        """비용 절감 기회 식별"""
        opportunities = []
        
        # 1. 주행 거리 최적화
        total_distance = self._calculate_total_distance(dispatches)
        estimated_waste = total_distance * 0.10  # 10% 낭비 추정
        
        if estimated_waste > 0:
            potential_fuel_savings = (estimated_waste / 5.5) * self.FUEL_COST_PER_LITER
            opportunities.append({
                'category': '경로 최적화',
                'description': '주행 거리를 10% 단축하여 연료비 절감',
                'potential_savings': round(potential_fuel_savings, 0),
                'implementation_difficulty': 'medium',
                'actions': [
                    'AI 경로 최적화 알고리즘 강화',
                    '실시간 교통 정보 활용',
                    '배송 순서 재조정'
                ]
            })
        
        # 2. 적재율 개선
        low_load_dispatches = 0
        for dispatch in dispatches:
            if dispatch.vehicle and dispatch.vehicle.pallet_capacity:
                load_rate = sum(o.pallet_count or 0 for o in dispatch.orders) / dispatch.vehicle.pallet_capacity
                if load_rate < 0.7:  # 70% 미만
                    low_load_dispatches += 1
        
        if low_load_dispatches > len(dispatches) * 0.2:  # 20% 이상
            potential_dispatch_reduction = low_load_dispatches * 0.3
            potential_savings_value = potential_dispatch_reduction * self.FIXED_COST_PER_DISPATCH
            
            opportunities.append({
                'category': '적재율 개선',
                'description': f'{low_load_dispatches}건의 낮은 적재율 배차를 개선하여 배차 횟수 감소',
                'potential_savings': round(potential_savings_value, 0),
                'implementation_difficulty': 'easy',
                'actions': [
                    '주문 통합 정책 수립',
                    '최소 적재율 기준 설정 (70%)',
                    '인근 주문 자동 그룹화'
                ]
            })
        
        # 3. 유휴 시간 감소
        if labor_cost > 0:
            # 유휴 시간 15% 추정
            potential_labor_savings = labor_cost * 0.15
            
            opportunities.append({
                'category': '업무 효율성',
                'description': '유휴 시간 감소를 통한 인건비 절감',
                'potential_savings': round(potential_labor_savings, 0),
                'implementation_difficulty': 'medium',
                'actions': [
                    '배차 스케줄 최적화',
                    '하역 시간 단축 방안',
                    '운전자 교육 프로그램'
                ]
            })
        
        # 4. 차량 유지보수 최적화
        maintenance_savings = self._calculate_maintenance_cost(dispatches) * 0.10
        
        opportunities.append({
            'category': '유지보수 최적화',
            'description': '예방 정비를 통한 유지보수 비용 절감',
            'potential_savings': round(maintenance_savings, 0),
            'implementation_difficulty': 'easy',
            'actions': [
                '정기 점검 스케줄 준수',
                '예측 정비 시스템 도입',
                '차량 상태 모니터링 강화'
            ]
        })
        
        # 절감 금액 순 정렬
        return sorted(opportunities, key=lambda x: x['potential_savings'], reverse=True)
    
    def _generate_cost_recommendations(
        self,
        profit_margin: float,
        cost_per_delivery: float,
        savings_opportunities: List[Dict]
    ) -> List[str]:
        """비용 최적화 권장사항"""
        recommendations = []
        
        # 수익성 분석
        if profit_margin < 10:
            recommendations.append(
                f'낮은 수익률 ({profit_margin:.1f}%). 비용 구조 개선이 시급합니다.'
            )
        elif profit_margin < 20:
            recommendations.append(
                f'수익률 개선 여지가 있습니다 (현재 {profit_margin:.1f}%).'
            )
        else:
            recommendations.append(
                f'양호한 수익률을 유지하고 있습니다 ({profit_margin:.1f}%).'
            )
        
        # 건당 비용 분석
        if cost_per_delivery > 50000:
            recommendations.append(
                f'건당 비용이 높습니다 (₩{cost_per_delivery:,.0f}). 배송 효율성 개선이 필요합니다.'
            )
        
        # 절감 기회 요약
        if savings_opportunities:
            total_potential_savings = sum(o['potential_savings'] for o in savings_opportunities)
            recommendations.append(
                f'연간 약 ₩{total_potential_savings * 12:,.0f} 절감 가능. '
                '우선순위: ' + ', '.join(o['category'] for o in savings_opportunities[:2])
            )
        
        return recommendations
    
    def analyze_vehicle_costs(
        self,
        vehicle_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """개별 차량 비용 분석"""
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.vehicle_id == vehicle_id,
                Dispatch.created_at >= start_date,
                Dispatch.created_at <= end_date
            )
        ).all()
        
        if not dispatches:
            return {
                'error': 'No dispatches found for this vehicle in the given period'
            }
        
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        
        # 비용 계산
        fuel_cost = self._calculate_fuel_cost(dispatches)
        labor_cost = self._calculate_labor_cost(dispatches)
        maintenance_cost = self._calculate_maintenance_cost(dispatches)
        fixed_cost = len(dispatches) * self.FIXED_COST_PER_DISPATCH
        
        total_cost = fuel_cost + labor_cost + maintenance_cost + fixed_cost
        
        # 수익
        total_revenue = self._calculate_revenue(dispatches)
        
        # 메트릭
        total_deliveries = sum(len(d.orders) for d in dispatches)
        total_distance = self._calculate_total_distance(dispatches)
        
        return {
            'vehicle_id': vehicle_id,
            'vehicle_number': vehicle.vehicle_number if vehicle else 'Unknown',
            'period': {
                'start': start_date.date().isoformat(),
                'end': end_date.date().isoformat()
            },
            'costs': {
                'fuel_cost': round(fuel_cost, 0),
                'labor_cost': round(labor_cost, 0),
                'maintenance_cost': round(maintenance_cost, 0),
                'fixed_cost': round(fixed_cost, 0),
                'total_cost': round(total_cost, 0)
            },
            'revenue': {
                'total_revenue': round(total_revenue, 0),
                'profit': round(total_revenue - total_cost, 0)
            },
            'metrics': {
                'total_dispatches': len(dispatches),
                'total_deliveries': total_deliveries,
                'total_distance_km': round(total_distance, 2),
                'cost_per_delivery': round(total_cost / total_deliveries, 0) if total_deliveries > 0 else 0,
                'cost_per_km': round(total_cost / total_distance, 0) if total_distance > 0 else 0
            }
        }
    
    def compare_vehicle_costs(
        self,
        vehicle_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """차량 간 비용 비교"""
        comparisons = []
        
        for vehicle_id in vehicle_ids:
            analysis = self.analyze_vehicle_costs(vehicle_id, start_date, end_date)
            
            if 'error' not in analysis:
                comparisons.append(analysis)
        
        if not comparisons:
            return {'error': 'No data available for comparison'}
        
        # 가장 경제적인/비경제적인 차량
        most_efficient = min(comparisons, key=lambda x: x['metrics']['cost_per_delivery'])
        least_efficient = max(comparisons, key=lambda x: x['metrics']['cost_per_delivery'])
        
        return {
            'vehicles': comparisons,
            'insights': {
                'most_cost_efficient': {
                    'vehicle_number': most_efficient['vehicle_number'],
                    'cost_per_delivery': most_efficient['metrics']['cost_per_delivery']
                },
                'least_cost_efficient': {
                    'vehicle_number': least_efficient['vehicle_number'],
                    'cost_per_delivery': least_efficient['metrics']['cost_per_delivery']
                },
                'cost_variance': round(
                    least_efficient['metrics']['cost_per_delivery'] -
                    most_efficient['metrics']['cost_per_delivery'],
                    0
                )
            }
        }


# 글로벌 인스턴스
def get_cost_optimization_report(db: Session) -> CostOptimizationReport:
    return CostOptimizationReport(db)
