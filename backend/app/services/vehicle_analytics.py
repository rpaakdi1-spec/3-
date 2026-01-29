"""
Vehicle Performance Analytics - Phase 10
차량 성능 분석 (연비, 가동률, 효율성)
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models import Vehicle, Dispatch, Order
import numpy as np


class VehiclePerformanceAnalytics:
    """차량 성능 분석 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_vehicle_performance_report(
        self,
        vehicle_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        개별 차량 성능 리포트
        
        Returns:
            - 연비
            - 가동률
            - 효율성 점수
            - 배송 완료율
            - 평균 적재율
        """
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        
        if not vehicle:
            return {'error': 'Vehicle not found'}
        
        # 기간 내 배차 조회
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.vehicle_id == vehicle_id,
                Dispatch.created_at >= start_date,
                Dispatch.created_at <= end_date
            )
        ).all()
        
        # 연비 계산
        fuel_efficiency = self._calculate_fuel_efficiency(dispatches)
        
        # 가동률 계산
        utilization_rate = self._calculate_utilization_rate(
            vehicle_id, start_date, end_date
        )
        
        # 효율성 점수
        efficiency_score = self._calculate_efficiency_score(dispatches, vehicle)
        
        # 배송 완료율
        delivery_completion_rate = self._calculate_delivery_completion_rate(dispatches)
        
        # 평균 적재율
        average_load_rate = self._calculate_average_load_rate(dispatches, vehicle)
        
        # 총 주행 거리
        total_distance = self._calculate_total_distance(dispatches)
        
        # 배송 건수
        total_deliveries = sum([len(d.orders) for d in dispatches])
        
        return {
            'vehicle_number': vehicle.vehicle_number,
            'vehicle_type': vehicle.vehicle_type,
            'period': {
                'start': start_date.date().isoformat(),
                'end': end_date.date().isoformat()
            },
            'fuel_efficiency': round(fuel_efficiency, 2),
            'utilization_rate': round(utilization_rate, 2),
            'efficiency_score': round(efficiency_score, 2),
            'delivery_completion_rate': round(delivery_completion_rate, 2),
            'average_load_rate': round(average_load_rate, 2),
            'total_distance_km': round(total_distance, 2),
            'total_dispatches': len(dispatches),
            'total_deliveries': total_deliveries,
            'avg_deliveries_per_dispatch': round(total_deliveries / len(dispatches), 2) if dispatches else 0
        }
    
    def _calculate_fuel_efficiency(self, dispatches: List[Dispatch]) -> float:
        """
        연비 계산 (km/L)
        
        실제 시스템에서는 연료 소비량 데이터가 필요
        여기서는 추정치 사용
        """
        if not dispatches:
            return 0
        
        total_distance = self._calculate_total_distance(dispatches)
        
        # 평균 연비 추정치 (냉동/냉장 차량은 일반 차량보다 낮음)
        # 실제로는 차량 타입, 적재량, 주행 조건 등을 고려
        estimated_fuel_efficiency = 5.5  # km/L (냉동차 기준)
        
        return estimated_fuel_efficiency
    
    def _calculate_total_distance(self, dispatches: List[Dispatch]) -> float:
        """총 주행 거리"""
        total_distance = 0
        
        for dispatch in dispatches:
            for order in dispatch.orders:
                # 주문의 거리 정보 사용
                distance = getattr(order, 'distance_km', 0) or 0
                total_distance += distance
        
        return total_distance
    
    def _calculate_utilization_rate(
        self,
        vehicle_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        가동률 계산
        
        가동률 = (사용된 일수 / 전체 일수) * 100
        """
        total_days = (end_date - start_date).days + 1
        
        # 차량이 사용된 날짜들
        used_dates = self.db.query(
            func.date(Dispatch.created_at)
        ).filter(
            and_(
                Dispatch.vehicle_id == vehicle_id,
                Dispatch.created_at >= start_date,
                Dispatch.created_at <= end_date
            )
        ).distinct().all()
        
        used_days = len(used_dates)
        
        return (used_days / total_days) * 100 if total_days > 0 else 0
    
    def _calculate_efficiency_score(
        self,
        dispatches: List[Dispatch],
        vehicle: Vehicle
    ) -> float:
        """
        효율성 점수 (0-100)
        
        다음 요소를 고려:
        - 적재율
        - 배송 완료율
        - 거리 효율성 (실제 거리 vs 최적 거리)
        """
        if not dispatches:
            return 0
        
        # 적재율 점수 (0-40점)
        load_rate = self._calculate_average_load_rate(dispatches, vehicle)
        load_score = min(load_rate * 0.4, 40)
        
        # 배송 완료율 점수 (0-40점)
        completion_rate = self._calculate_delivery_completion_rate(dispatches)
        completion_score = completion_rate * 0.4
        
        # 거리 효율성 점수 (0-20점)
        distance_efficiency = self._calculate_distance_efficiency(dispatches)
        distance_score = distance_efficiency * 0.2
        
        total_score = load_score + completion_score + distance_score
        
        return min(total_score, 100)
    
    def _calculate_delivery_completion_rate(self, dispatches: List[Dispatch]) -> float:
        """배송 완료율"""
        if not dispatches:
            return 100.0
        
        total_orders = 0
        completed_orders = 0
        
        for dispatch in dispatches:
            for order in dispatch.orders:
                total_orders += 1
                if order.status == 'COMPLETED':
                    completed_orders += 1
        
        return (completed_orders / total_orders) * 100 if total_orders > 0 else 100.0
    
    def _calculate_average_load_rate(
        self,
        dispatches: List[Dispatch],
        vehicle: Vehicle
    ) -> float:
        """평균 적재율"""
        if not dispatches:
            return 0
        
        capacity = vehicle.pallet_capacity or 30
        total_load_rate = 0
        
        for dispatch in dispatches:
            loaded_pallets = sum([order.pallet_count or 0 for order in dispatch.orders])
            load_rate = (loaded_pallets / capacity) * 100
            total_load_rate += min(load_rate, 100)
        
        return total_load_rate / len(dispatches)
    
    def _calculate_distance_efficiency(self, dispatches: List[Dispatch]) -> float:
        """
        거리 효율성
        
        실제 주행 거리 대비 최적 거리의 비율
        (실제로는 GPS 데이터와 최적 경로 비교 필요)
        """
        # 간단한 추정: 85-95% 효율성 가정
        return 90.0
    
    def get_fleet_performance_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        전체 차량 성능 요약
        
        Returns:
            - 차량별 성능 랭킹
            - 평균 성능 지표
            - 우수/저조 차량
        """
        vehicles = self.db.query(Vehicle).all()
        
        vehicle_performances = []
        
        for vehicle in vehicles:
            performance = self.get_vehicle_performance_report(
                vehicle.id,
                start_date,
                end_date
            )
            
            if 'error' not in performance:
                vehicle_performances.append(performance)
        
        if not vehicle_performances:
            return {
                'total_vehicles': 0,
                'average_efficiency': 0,
                'top_performers': [],
                'low_performers': []
            }
        
        # 평균 계산
        avg_efficiency = np.mean([v['efficiency_score'] for v in vehicle_performances])
        avg_utilization = np.mean([v['utilization_rate'] for v in vehicle_performances])
        avg_load_rate = np.mean([v['average_load_rate'] for v in vehicle_performances])
        
        # 효율성 기준 정렬
        sorted_vehicles = sorted(
            vehicle_performances,
            key=lambda x: x['efficiency_score'],
            reverse=True
        )
        
        return {
            'total_vehicles': len(vehicles),
            'active_vehicles': len(vehicle_performances),
            'average_efficiency_score': round(avg_efficiency, 2),
            'average_utilization_rate': round(avg_utilization, 2),
            'average_load_rate': round(avg_load_rate, 2),
            'top_performers': sorted_vehicles[:5],  # 상위 5대
            'low_performers': sorted_vehicles[-5:],  # 하위 5대
            'all_vehicles': sorted_vehicles
        }
    
    def get_vehicle_maintenance_alerts(self) -> List[Dict]:
        """
        차량 유지보수 알림
        
        다음 기준으로 알림:
        - 누적 주행거리
        - 마지막 점검일
        - 성능 저하
        """
        vehicles = self.db.query(Vehicle).all()
        alerts = []
        
        for vehicle in vehicles:
            # 최근 30일 성능 분석
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            performance = self.get_vehicle_performance_report(
                vehicle.id,
                start_date,
                end_date
            )
            
            if 'error' in performance:
                continue
            
            # 유지보수 필요 여부 판단
            needs_maintenance = False
            reasons = []
            
            # 효율성이 낮은 경우
            if performance['efficiency_score'] < 60:
                needs_maintenance = True
                reasons.append(f"낮은 효율성 점수: {performance['efficiency_score']}")
            
            # 연비가 낮은 경우
            if performance['fuel_efficiency'] < 4.0:
                needs_maintenance = True
                reasons.append(f"낮은 연비: {performance['fuel_efficiency']} km/L")
            
            # 적재율이 낮은 경우 (차량 문제 가능성)
            if performance['average_load_rate'] < 50 and performance['total_dispatches'] > 5:
                needs_maintenance = True
                reasons.append(f"낮은 적재율: {performance['average_load_rate']}%")
            
            if needs_maintenance:
                alerts.append({
                    'vehicle_id': vehicle.id,
                    'vehicle_number': vehicle.vehicle_number,
                    'alert_level': 'warning' if performance['efficiency_score'] > 50 else 'critical',
                    'reasons': reasons,
                    'efficiency_score': performance['efficiency_score'],
                    'recommended_action': '정기 점검 및 유지보수 필요'
                })
        
        return sorted(alerts, key=lambda x: x['efficiency_score'])
    
    def compare_vehicles(
        self,
        vehicle_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        차량 간 성능 비교
        
        Args:
            vehicle_ids: 비교할 차량 ID 리스트
            
        Returns:
            차량별 성능 비교 데이터
        """
        comparison_data = []
        
        for vehicle_id in vehicle_ids:
            performance = self.get_vehicle_performance_report(
                vehicle_id,
                start_date,
                end_date
            )
            
            if 'error' not in performance:
                comparison_data.append(performance)
        
        if not comparison_data:
            return {'error': 'No data available for comparison'}
        
        # 지표별 최고/최저 차량
        best_efficiency = max(comparison_data, key=lambda x: x['efficiency_score'])
        worst_efficiency = min(comparison_data, key=lambda x: x['efficiency_score'])
        
        best_utilization = max(comparison_data, key=lambda x: x['utilization_rate'])
        best_load_rate = max(comparison_data, key=lambda x: x['average_load_rate'])
        
        return {
            'vehicles': comparison_data,
            'insights': {
                'most_efficient': best_efficiency['vehicle_number'],
                'least_efficient': worst_efficiency['vehicle_number'],
                'highest_utilization': best_utilization['vehicle_number'],
                'highest_load_rate': best_load_rate['vehicle_number']
            },
            'recommendations': self._generate_recommendations(comparison_data)
        }
    
    def _generate_recommendations(self, vehicle_data: List[Dict]) -> List[str]:
        """성능 데이터 기반 권장사항 생성"""
        recommendations = []
        
        # 평균 효율성 계산
        avg_efficiency = np.mean([v['efficiency_score'] for v in vehicle_data])
        
        # 저효율 차량 확인
        low_performers = [
            v for v in vehicle_data
            if v['efficiency_score'] < avg_efficiency * 0.8
        ]
        
        if low_performers:
            recommendations.append(
                f"{len(low_performers)}대 차량의 효율성이 평균 대비 낮습니다. "
                "정기 점검 및 운전자 교육을 권장합니다."
            )
        
        # 가동률 분석
        low_utilization = [
            v for v in vehicle_data
            if v['utilization_rate'] < 60
        ]
        
        if low_utilization:
            recommendations.append(
                f"{len(low_utilization)}대 차량의 가동률이 60% 미만입니다. "
                "배차 최적화 또는 차량 규모 조정을 고려하세요."
            )
        
        # 적재율 분석
        low_load_rate = [
            v for v in vehicle_data
            if v['average_load_rate'] < 70
        ]
        
        if low_load_rate:
            recommendations.append(
                f"{len(low_load_rate)}대 차량의 평균 적재율이 70% 미만입니다. "
                "주문 통합 및 경로 최적화를 권장합니다."
            )
        
        if not recommendations:
            recommendations.append("모든 차량이 양호한 성능을 보이고 있습니다.")
        
        return recommendations


# 글로벌 인스턴스
def get_vehicle_performance_analytics(db: Session) -> VehiclePerformanceAnalytics:
    return VehiclePerformanceAnalytics(db)
