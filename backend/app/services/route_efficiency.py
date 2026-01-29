"""
Route Efficiency Analytics - Phase 10
경로 효율성 분석 시스템
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models import Dispatch, Order, Vehicle
import numpy as np


class RouteEfficiencyAnalytics:
    """경로 효율성 분석 시스템"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_route_efficiency(
        self,
        dispatch_id: int
    ) -> Dict:
        """
        개별 배차 경로 효율성 분석
        
        분석 항목:
        - 실제 거리 vs 최적 거리
        - 소요 시간 vs 예상 시간
        - 배송 순서 최적화 정도
        - 적재율
        """
        dispatch = self.db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        
        if not dispatch:
            return {'error': 'Dispatch not found'}
        
        if not dispatch.orders:
            return {'error': 'No orders in this dispatch'}
        
        # 경로 분석
        total_distance = self._calculate_total_distance(dispatch.orders)
        optimal_distance = self._estimate_optimal_distance(dispatch.orders)
        distance_efficiency = (optimal_distance / total_distance * 100) if total_distance > 0 else 100
        
        # 시간 분석
        if hasattr(dispatch, 'started_at') and hasattr(dispatch, 'completed_at'):
            if dispatch.completed_at and dispatch.started_at:
                actual_duration = (dispatch.completed_at - dispatch.started_at).total_seconds() / 3600
                estimated_duration = self._estimate_duration(dispatch.orders)
                time_efficiency = (estimated_duration / actual_duration * 100) if actual_duration > 0 else 100
            else:
                actual_duration = 0
                estimated_duration = self._estimate_duration(dispatch.orders)
                time_efficiency = 0
        else:
            actual_duration = 0
            estimated_duration = self._estimate_duration(dispatch.orders)
            time_efficiency = 0
        
        # 배송 순서 효율성
        sequence_efficiency = self._analyze_delivery_sequence(dispatch.orders)
        
        # 적재율
        vehicle = dispatch.vehicle
        load_efficiency = self._calculate_load_efficiency(dispatch.orders, vehicle)
        
        # 종합 효율성 점수
        overall_efficiency = (
            distance_efficiency * 0.3 +
            time_efficiency * 0.3 +
            sequence_efficiency * 0.2 +
            load_efficiency * 0.2
        )
        
        return {
            'dispatch_id': dispatch_id,
            'vehicle_number': vehicle.vehicle_number if vehicle else 'Unknown',
            'date': dispatch.created_at.date().isoformat(),
            'overall_efficiency_score': round(overall_efficiency, 2),
            'metrics': {
                'distance_efficiency': round(distance_efficiency, 2),
                'time_efficiency': round(time_efficiency, 2),
                'sequence_efficiency': round(sequence_efficiency, 2),
                'load_efficiency': round(load_efficiency, 2)
            },
            'details': {
                'total_distance_km': round(total_distance, 2),
                'optimal_distance_km': round(optimal_distance, 2),
                'distance_waste_km': round(total_distance - optimal_distance, 2),
                'actual_duration_hours': round(actual_duration, 2),
                'estimated_duration_hours': round(estimated_duration, 2),
                'time_waste_hours': round(max(actual_duration - estimated_duration, 0), 2),
                'delivery_count': len(dispatch.orders),
                'pallets_loaded': sum(o.pallet_count or 0 for o in dispatch.orders)
            },
            'recommendations': self._generate_route_recommendations(
                distance_efficiency,
                time_efficiency,
                sequence_efficiency,
                load_efficiency
            )
        }
    
    def _calculate_total_distance(self, orders: List[Order]) -> float:
        """총 주행 거리 계산"""
        total_distance = 0
        
        for order in orders:
            distance = getattr(order, 'distance_km', 0) or 0
            total_distance += distance
        
        return total_distance
    
    def _estimate_optimal_distance(self, orders: List[Order]) -> float:
        """
        최적 거리 추정
        
        실제로는 TSP(Traveling Salesman Problem) 알고리즘 필요
        여기서는 실제 거리의 85-95% 범위로 추정
        """
        total_distance = self._calculate_total_distance(orders)
        
        # 주문 수가 많을수록 최적화 여지가 큼
        optimization_potential = min(len(orders) * 2, 15) / 100
        
        optimal_distance = total_distance * (1 - optimization_potential)
        
        return optimal_distance
    
    def _estimate_duration(self, orders: List[Order]) -> float:
        """예상 소요 시간 추정 (시간 단위)"""
        # 기본 시간: 주문당 30분 (이동 + 하역)
        base_time = len(orders) * 0.5
        
        # 거리 기반 추가 시간
        total_distance = self._calculate_total_distance(orders)
        travel_time = total_distance / 40  # 평균 40km/h 가정
        
        return base_time + travel_time
    
    def _analyze_delivery_sequence(self, orders: List[Order]) -> float:
        """
        배송 순서 효율성 분석
        
        실제로는 지리적 좌표 기반 분석 필요
        여기서는 간단한 추정
        """
        if len(orders) <= 1:
            return 100.0
        
        # 주문이 5개 이상이면 최적화 효과가 큼
        if len(orders) >= 5:
            # 간단한 추정: 75-90% 효율성
            return 82.0
        else:
            # 주문이 적으면 순서가 덜 중요
            return 90.0
    
    def _calculate_load_efficiency(self, orders: List[Order], vehicle: Vehicle) -> float:
        """적재 효율성 계산"""
        if not vehicle or not vehicle.pallet_capacity:
            return 0
        
        total_pallets = sum(order.pallet_count or 0 for order in orders)
        load_rate = (total_pallets / vehicle.pallet_capacity) * 100
        
        # 최적 적재율: 80-95%
        if 80 <= load_rate <= 95:
            return 100.0
        elif load_rate > 95:
            # 과적재는 감점
            return max(100 - (load_rate - 95) * 5, 70)
        else:
            # 저적재는 효율성 낮음
            return load_rate * 1.25  # 80%를 100점으로 환산
    
    def _generate_route_recommendations(
        self,
        distance_efficiency: float,
        time_efficiency: float,
        sequence_efficiency: float,
        load_efficiency: float
    ) -> List[str]:
        """경로 개선 권장사항"""
        recommendations = []
        
        if distance_efficiency < 85:
            recommendations.append(
                '주행 거리 최적화가 필요합니다. 경로 재계획을 권장합니다.'
            )
        
        if time_efficiency < 80:
            recommendations.append(
                '소요 시간이 예상보다 깁니다. 교통 패턴 분석 및 출발 시간 조정을 고려하세요.'
            )
        
        if sequence_efficiency < 80:
            recommendations.append(
                '배송 순서 최적화가 필요합니다. TSP 알고리즘 활용을 권장합니다.'
            )
        
        if load_efficiency < 70:
            recommendations.append(
                '적재율이 낮습니다. 주문 통합 또는 차량 크기 조정을 고려하세요.'
            )
        elif load_efficiency < 80 and load_efficiency >= 70:
            recommendations.append(
                '적재율 개선 여지가 있습니다. 인근 주문 추가를 검토하세요.'
            )
        
        if not recommendations:
            recommendations.append('현재 경로는 효율적으로 운영되고 있습니다.')
        
        return recommendations
    
    def get_fleet_route_efficiency_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        전체 차량 경로 효율성 요약
        """
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.created_at >= start_date,
                Dispatch.created_at <= end_date
            )
        ).all()
        
        if not dispatches:
            return {
                'message': 'No dispatches found for this period',
                'total_dispatches': 0
            }
        
        efficiency_scores = []
        total_distance = 0
        total_optimal_distance = 0
        total_deliveries = 0
        
        for dispatch in dispatches:
            if not dispatch.orders:
                continue
            
            analysis = self.analyze_route_efficiency(dispatch.id)
            
            if 'error' not in analysis:
                efficiency_scores.append(analysis['overall_efficiency_score'])
                total_distance += analysis['details']['total_distance_km']
                total_optimal_distance += analysis['details']['optimal_distance_km']
                total_deliveries += analysis['details']['delivery_count']
        
        if not efficiency_scores:
            return {
                'message': 'No valid route data available',
                'total_dispatches': len(dispatches)
            }
        
        avg_efficiency = np.mean(efficiency_scores)
        distance_waste = total_distance - total_optimal_distance
        distance_waste_percent = (distance_waste / total_distance * 100) if total_distance > 0 else 0
        
        # 효율성 분포
        high_efficiency = sum(1 for s in efficiency_scores if s >= 85)
        medium_efficiency = sum(1 for s in efficiency_scores if 70 <= s < 85)
        low_efficiency = sum(1 for s in efficiency_scores if s < 70)
        
        return {
            'period': {
                'start': start_date.date().isoformat(),
                'end': end_date.date().isoformat()
            },
            'summary': {
                'total_dispatches': len(dispatches),
                'analyzed_dispatches': len(efficiency_scores),
                'average_efficiency_score': round(avg_efficiency, 2),
                'total_distance_km': round(total_distance, 2),
                'optimal_distance_km': round(total_optimal_distance, 2),
                'distance_waste_km': round(distance_waste, 2),
                'distance_waste_percent': round(distance_waste_percent, 2),
                'total_deliveries': total_deliveries
            },
            'distribution': {
                'high_efficiency_count': high_efficiency,
                'medium_efficiency_count': medium_efficiency,
                'low_efficiency_count': low_efficiency
            },
            'insights': self._generate_fleet_insights(
                avg_efficiency,
                distance_waste_percent,
                low_efficiency,
                len(efficiency_scores)
            )
        }
    
    def _generate_fleet_insights(
        self,
        avg_efficiency: float,
        distance_waste_percent: float,
        low_efficiency_count: int,
        total_count: int
    ) -> List[str]:
        """전체 차량 인사이트 생성"""
        insights = []
        
        if avg_efficiency >= 85:
            insights.append('전체 경로 효율성이 우수합니다.')
        elif avg_efficiency >= 75:
            insights.append('전체 경로 효율성이 양호하나 개선 여지가 있습니다.')
        else:
            insights.append('전체 경로 효율성이 낮습니다. 긴급 개선이 필요합니다.')
        
        if distance_waste_percent > 10:
            potential_saving = distance_waste_percent
            insights.append(
                f'주행 거리를 {potential_saving:.1f}% 단축할 수 있습니다. '
                '연료비 절감 효과가 기대됩니다.'
            )
        
        if low_efficiency_count > 0:
            low_percent = (low_efficiency_count / total_count * 100)
            if low_percent > 20:
                insights.append(
                    f'효율성이 낮은 배차가 {low_percent:.1f}%입니다. '
                    '경로 최적화 시스템 개선이 필요합니다.'
                )
        
        return insights
    
    def identify_inefficient_routes(
        self,
        start_date: datetime,
        end_date: datetime,
        threshold: float = 70.0
    ) -> List[Dict]:
        """
        비효율적인 경로 식별
        
        Args:
            threshold: 효율성 임계값 (기본 70%)
        """
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.created_at >= start_date,
                Dispatch.created_at <= end_date
            )
        ).all()
        
        inefficient_routes = []
        
        for dispatch in dispatches:
            if not dispatch.orders:
                continue
            
            analysis = self.analyze_route_efficiency(dispatch.id)
            
            if 'error' not in analysis:
                if analysis['overall_efficiency_score'] < threshold:
                    inefficient_routes.append({
                        'dispatch_id': dispatch.id,
                        'vehicle_number': analysis['vehicle_number'],
                        'date': analysis['date'],
                        'efficiency_score': analysis['overall_efficiency_score'],
                        'main_issues': self._identify_main_issues(analysis['metrics']),
                        'potential_improvements': analysis['recommendations']
                    })
        
        # 효율성 낮은 순으로 정렬
        return sorted(inefficient_routes, key=lambda x: x['efficiency_score'])
    
    def _identify_main_issues(self, metrics: Dict) -> List[str]:
        """주요 문제점 식별"""
        issues = []
        
        if metrics['distance_efficiency'] < 80:
            issues.append('주행 거리 비효율')
        
        if metrics['time_efficiency'] < 80:
            issues.append('소요 시간 초과')
        
        if metrics['sequence_efficiency'] < 80:
            issues.append('배송 순서 비최적')
        
        if metrics['load_efficiency'] < 70:
            issues.append('낮은 적재율')
        
        return issues if issues else ['전반적 효율성 저하']


# 글로벌 인스턴스
def get_route_efficiency_analytics(db: Session) -> RouteEfficiencyAnalytics:
    return RouteEfficiencyAnalytics(db)
