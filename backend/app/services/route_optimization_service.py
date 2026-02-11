"""
Phase 11-B: Route Optimization Service
경로 최적화 엔진
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import math

from app.models.traffic import (
    RouteOptimization,
    RouteHistory,
    TrafficLevel,
    RouteStatus
)
from app.services.traffic_api_service import TrafficAPIService


class RouteOptimizationService:
    """경로 최적화 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.traffic_api = TrafficAPIService(db)
    
    def optimize_route(
        self,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float,
        dispatch_id: Optional[int] = None
    ) -> RouteOptimization:
        """
        경로 최적화 수행
        
        Args:
            origin_lat: 출발지 위도
            origin_lng: 출발지 경도
            destination_lat: 목적지 위도
            destination_lng: 목적지 경도
            dispatch_id: 배차 ID
        
        Returns:
            최적화된 경로
        """
        # 여러 API에서 경로 조회
        best_route = self.traffic_api.get_best_route(
            origin_lat, origin_lng,
            destination_lat, destination_lng
        )
        
        if not best_route:
            # Fallback: 직선 거리 계산
            distance = self._calculate_distance(
                origin_lat, origin_lng,
                destination_lat, destination_lng
            )
            duration = int(distance / 40 * 60)  # 40km/h 가정
            
            best_route = {
                "provider": "FALLBACK",
                "distance": distance,
                "duration": duration,
                "traffic_level": TrafficLevel.NORMAL,
                "toll_fee": 0
            }
        
        # 연료비 계산 (임시: km당 150원)
        fuel_cost = int(best_route.get("distance", 0) * 150)
        
        # 최적화 점수 계산
        optimization_score = self._calculate_optimization_score(best_route)
        
        # 경로 저장
        route_opt = RouteOptimization(
            dispatch_id=dispatch_id,
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            destination_lat=destination_lat,
            destination_lng=destination_lng,
            route_status=RouteStatus.OPTIMAL,
            distance=best_route.get("distance", 0),
            duration=best_route.get("duration", 0),
            duration_in_traffic=best_route.get("duration", 0),
            traffic_level=best_route.get("traffic_level", TrafficLevel.NORMAL),
            toll_fee=best_route.get("toll_fee", 0),
            fuel_cost=fuel_cost,
            optimization_score=optimization_score,
            is_optimal=True,
            api_provider=best_route.get("provider", "SYSTEM"),
            api_response=best_route,
            calculated_at=datetime.utcnow()
        )
        
        self.db.add(route_opt)
        self.db.commit()
        self.db.refresh(route_opt)
        
        return route_opt
    
    def get_alternative_routes(
        self,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float,
        count: int = 3
    ) -> List[RouteOptimization]:
        """
        대안 경로 조회
        
        Args:
            origin_lat: 출발지 위도
            origin_lng: 출발지 경도
            destination_lat: 목적지 위도
            destination_lng: 목적지 경도
            count: 경로 개수
        
        Returns:
            대안 경로 목록
        """
        routes = []
        
        # 기본 경로
        optimal_route = self.optimize_route(
            origin_lat, origin_lng,
            destination_lat, destination_lng
        )
        routes.append(optimal_route)
        
        # 대안 경로 생성 (시뮬레이션)
        for i in range(count - 1):
            alt_distance = optimal_route.distance * (1.0 + (i + 1) * 0.1)
            alt_duration = optimal_route.duration + (i + 1) * 5
            
            alt_route = RouteOptimization(
                origin_lat=origin_lat,
                origin_lng=origin_lng,
                destination_lat=destination_lat,
                destination_lng=destination_lng,
                route_name=f"대안 경로 {i+1}",
                route_status=RouteStatus.ALTERNATIVE,
                distance=alt_distance,
                duration=alt_duration,
                duration_in_traffic=alt_duration + 2,
                traffic_level=TrafficLevel.NORMAL,
                toll_fee=optimal_route.toll_fee,
                fuel_cost=int(alt_distance * 150),
                optimization_score=optimal_route.optimization_score - (i + 1) * 5,
                is_optimal=False,
                api_provider="SYSTEM",
                calculated_at=datetime.utcnow()
            )
            
            self.db.add(alt_route)
            routes.append(alt_route)
        
        self.db.commit()
        
        return routes
    
    def compare_routes(
        self,
        route_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        경로 비교
        
        Args:
            route_ids: 비교할 경로 ID 목록
        
        Returns:
            비교 결과
        """
        routes = self.db.query(RouteOptimization).filter(
            RouteOptimization.id.in_(route_ids)
        ).all()
        
        comparisons = []
        for route in routes:
            comparisons.append({
                "id": route.id,
                "route_name": route.route_name or "경로",
                "distance": route.distance,
                "duration": route.duration,
                "duration_in_traffic": route.duration_in_traffic,
                "traffic_level": route.traffic_level.value if route.traffic_level else None,
                "toll_fee": route.toll_fee,
                "fuel_cost": route.fuel_cost,
                "total_cost": route.toll_fee + (route.fuel_cost or 0),
                "optimization_score": route.optimization_score,
                "is_optimal": route.is_optimal
            })
        
        # 최적 경로 순으로 정렬
        comparisons.sort(key=lambda x: x.get("optimization_score", 0), reverse=True)
        
        return comparisons
    
    # ==================== 경로 이력 ====================
    
    def create_route_history(
        self,
        dispatch_id: int,
        vehicle_id: int,
        driver_id: int,
        route_optimization_id: Optional[int] = None,
        actual_distance: Optional[float] = None,
        actual_duration: Optional[int] = None
    ) -> RouteHistory:
        """
        경로 이력 생성
        
        Args:
            dispatch_id: 배차 ID
            vehicle_id: 차량 ID
            driver_id: 드라이버 ID
            route_optimization_id: 경로 최적화 ID
            actual_distance: 실제 거리
            actual_duration: 실제 소요시간
        
        Returns:
            생성된 이력
        """
        history = RouteHistory(
            dispatch_id=dispatch_id,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            route_optimization_id=route_optimization_id,
            actual_distance=actual_distance,
            actual_duration=actual_duration,
            started_at=datetime.utcnow()
        )
        
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        
        return history
    
    def complete_route_history(
        self,
        history_id: int,
        actual_distance: float,
        actual_duration: int,
        fuel_consumed: Optional[float] = None
    ) -> RouteHistory:
        """
        경로 이력 완료
        
        Args:
            history_id: 이력 ID
            actual_distance: 실제 거리
            actual_duration: 실제 소요시간
            fuel_consumed: 연료 소비량
        
        Returns:
            업데이트된 이력
        """
        history = self.db.query(RouteHistory).filter(
            RouteHistory.id == history_id
        ).first()
        
        if not history:
            return None
        
        history.actual_distance = actual_distance
        history.actual_duration = actual_duration
        history.fuel_consumed = fuel_consumed
        history.completed_at = datetime.utcnow()
        
        # 예측 vs 실제 비교
        if history.route_optimization_id:
            opt = self.db.query(RouteOptimization).filter(
                RouteOptimization.id == history.route_optimization_id
            ).first()
            
            if opt:
                history.distance_variance = (
                    (actual_distance - opt.distance) / opt.distance * 100
                ) if opt.distance > 0 else 0
                
                history.duration_variance = (
                    (actual_duration - opt.duration) / opt.duration * 100
                ) if opt.duration > 0 else 0
        
        self.db.commit()
        self.db.refresh(history)
        
        return history
    
    def get_route_statistics(
        self,
        vehicle_id: Optional[int] = None,
        driver_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        경로 통계
        
        Args:
            vehicle_id: 차량 ID
            driver_id: 드라이버 ID
            days: 기간 (일)
        
        Returns:
            통계 데이터
        """
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(RouteHistory).filter(
            RouteHistory.created_at >= start_date
        )
        
        if vehicle_id:
            query = query.filter(RouteHistory.vehicle_id == vehicle_id)
        
        if driver_id:
            query = query.filter(RouteHistory.driver_id == driver_id)
        
        histories = query.all()
        
        if not histories:
            return {
                "total_routes": 0,
                "total_distance": 0,
                "total_duration": 0,
                "avg_distance_variance": 0,
                "avg_duration_variance": 0
            }
        
        total_distance = sum([h.actual_distance or 0 for h in histories])
        total_duration = sum([h.actual_duration or 0 for h in histories])
        
        distance_variances = [h.distance_variance for h in histories if h.distance_variance is not None]
        duration_variances = [h.duration_variance for h in histories if h.duration_variance is not None]
        
        return {
            "total_routes": len(histories),
            "total_distance": total_distance,
            "total_duration": total_duration,
            "avg_distance": total_distance / len(histories) if histories else 0,
            "avg_duration": total_duration / len(histories) if histories else 0,
            "avg_distance_variance": sum(distance_variances) / len(distance_variances) if distance_variances else 0,
            "avg_duration_variance": sum(duration_variances) / len(duration_variances) if duration_variances else 0
        }
    
    # ==================== Helper Methods ====================
    
    def _calculate_distance(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """
        Haversine formula로 거리 계산 (km)
        """
        R = 6371  # 지구 반경 (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        
        return round(distance, 2)
    
    def _calculate_optimization_score(
        self,
        route: Dict[str, Any]
    ) -> float:
        """
        최적화 점수 계산 (0-100)
        """
        score = 100.0
        
        # 교통 혼잡도에 따라 점수 감소
        traffic_level = route.get("traffic_level", TrafficLevel.NORMAL)
        if traffic_level == TrafficLevel.SLOW:
            score -= 10
        elif traffic_level == TrafficLevel.CONGESTED:
            score -= 20
        elif traffic_level == TrafficLevel.BLOCKED:
            score -= 30
        
        # 통행료가 높으면 점수 감소
        toll_fee = route.get("toll_fee", 0)
        if toll_fee > 5000:
            score -= 5
        elif toll_fee > 10000:
            score -= 10
        
        return max(0, min(100, score))
