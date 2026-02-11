"""
Phase 12: 통합 배차 서비스
네이버 맵 + UVIS GPS + AI 배차를 하나로 통합
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.order import Order
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.dispatch import Dispatch
from app.models.dispatch_rule import DispatchRule
from app.services.naver_map_service import NaverMapService
from app.services.uvis_gps_service import UvisGPSService
from app.core.config import settings

logger = logging.getLogger(__name__)


class IntegratedDispatchService:
    """
    통합 배차 서비스
    
    기능:
    1. 가용 차량 자동 조회 (UVIS GPS)
    2. 거리/시간 자동 계산 (네이버 맵)
    3. 배차 규칙 자동 적용 (Phase 10)
    4. 최적 기사 자동 선택 (AI)
    5. 경로 자동 생성 (네이버 맵)
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.map_service = NaverMapService()
        self.gps_service = UvisGPSService(db)
    
    async def auto_dispatch(
        self,
        order_id: int,
        apply_rules: bool = True,
        simulate: bool = False
    ) -> Dict:
        """
        자동 배차 실행
        
        Args:
            order_id: 주문 ID
            apply_rules: 배차 규칙 적용 여부
            simulate: 시뮬레이션 모드 (실제 배차하지 않음)
            
        Returns:
            {
                "success": bool,
                "dispatch_id": int,
                "vehicle": {...},
                "driver": {...},
                "route": {...},
                "distance_km": float,
                "estimated_time_min": int,
                "reasoning": str
            }
        """
        try:
            # 1. 주문 조회
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {
                    "success": False,
                    "error": "Order not found",
                    "order_id": order_id
                }
            
            logger.info(f"🚀 Auto dispatch started for order {order_id}")
            
            # 2. 가용 차량 조회
            available_vehicles = await self.get_available_vehicles(order)
            if not available_vehicles:
                return {
                    "success": False,
                    "error": "No available vehicles",
                    "order_id": order_id
                }
            
            logger.info(f"✅ Found {len(available_vehicles)} available vehicles")
            
            # 3. 각 차량에 대해 거리/시간 계산
            candidates = []
            for vehicle_data in available_vehicles:
                vehicle = vehicle_data["vehicle"]
                driver = vehicle_data["driver"]
                current_location = vehicle_data["location"]
                
                # 거리 계산
                distance_data = await self.calculate_distance(
                    current_location,
                    (order.pickup_latitude, order.pickup_longitude)
                )
                
                if distance_data:
                    candidates.append({
                        "vehicle": vehicle,
                        "driver": driver,
                        "location": current_location,
                        "distance_km": distance_data["distance_km"],
                        "estimated_time_min": distance_data["duration_min"],
                        "route": distance_data.get("route")
                    })
            
            if not candidates:
                return {
                    "success": False,
                    "error": "Cannot calculate routes for any vehicle",
                    "order_id": order_id
                }
            
            logger.info(f"✅ Calculated routes for {len(candidates)} vehicles")
            
            # 4. 배차 규칙 적용
            if apply_rules:
                ranked_candidates = await self.apply_dispatch_rules(order, candidates)
            else:
                # 규칙 없이 거리만으로 정렬
                ranked_candidates = sorted(candidates, key=lambda x: x["distance_km"])
            
            # 5. 최적 후보 선택
            best_candidate = ranked_candidates[0]
            
            logger.info(
                f"✅ Best candidate: Vehicle {best_candidate['vehicle'].id}, "
                f"Distance: {best_candidate['distance_km']}km, "
                f"Time: {best_candidate['estimated_time_min']}min"
            )
            
            # 6. 시뮬레이션 모드가 아니면 실제 배차 생성
            if not simulate:
                dispatch = Dispatch(
                    order_id=order_id,
                    vehicle_id=best_candidate['vehicle'].id,
                    driver_id=best_candidate['driver'].id,
                    status='assigned',
                    assigned_at=datetime.utcnow(),
                    estimated_distance_km=best_candidate['distance_km'],
                    estimated_duration_min=best_candidate['estimated_time_min']
                )
                self.db.add(dispatch)
                
                # 주문 상태 업데이트
                order.status = 'assigned'
                order.assigned_vehicle_id = best_candidate['vehicle'].id
                order.assigned_driver_id = best_candidate['driver'].id
                
                self.db.commit()
                self.db.refresh(dispatch)
                
                dispatch_id = dispatch.id
            else:
                dispatch_id = None
            
            # 7. 결과 반환
            return {
                "success": True,
                "dispatch_id": dispatch_id,
                "order_id": order_id,
                "vehicle": {
                    "id": best_candidate['vehicle'].id,
                    "license_plate": best_candidate['vehicle'].license_plate,
                    "vehicle_type": best_candidate['vehicle'].vehicle_type,
                    "temperature_type": best_candidate['vehicle'].temperature_type
                },
                "driver": {
                    "id": best_candidate['driver'].id,
                    "name": best_candidate['driver'].name,
                    "phone": best_candidate['driver'].phone,
                    "rating": best_candidate['driver'].rating
                },
                "location": {
                    "latitude": best_candidate['location'][0],
                    "longitude": best_candidate['location'][1]
                },
                "distance_km": best_candidate['distance_km'],
                "estimated_time_min": best_candidate['estimated_time_min'],
                "route": best_candidate.get('route'),
                "alternatives": [
                    {
                        "vehicle_id": c['vehicle'].id,
                        "distance_km": c['distance_km'],
                        "estimated_time_min": c['estimated_time_min']
                    }
                    for c in ranked_candidates[1:4]  # 상위 3개 대안
                ],
                "reasoning": self._generate_reasoning(order, best_candidate, ranked_candidates),
                "simulated": simulate
            }
        
        except Exception as e:
            logger.error(f"❌ Auto dispatch failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "order_id": order_id
            }
    
    async def get_available_vehicles(self, order: Order) -> List[Dict]:
        """
        가용 차량 조회 (UVIS GPS + 데이터베이스)
        
        Returns:
            [
                {
                    "vehicle": Vehicle,
                    "driver": Driver,
                    "location": (lat, lng),
                    "status": str
                },
                ...
            ]
        """
        # 1. 데이터베이스에서 활성 차량 조회
        vehicles = self.db.query(Vehicle).filter(
            Vehicle.is_active == True,
            Vehicle.status.in_(['available', 'idle'])
        ).all()
        
        available = []
        
        for vehicle in vehicles:
            # 기사 조회
            driver = self.db.query(Driver).filter(
                Driver.id == vehicle.driver_id,
                Driver.is_active == True
            ).first()
            
            if not driver:
                continue
            
            # 차량 타입 체크 (온도 요구사항)
            if order.temperature_min or order.temperature_max:
                if not self._check_temperature_capability(vehicle, order):
                    continue
            
            # GPS 위치 조회
            location = await self.gps_service.get_vehicle_location(vehicle.id)
            
            # 위치가 없으면 차량 등록 주소 사용
            if not location:
                if vehicle.last_known_latitude and vehicle.last_known_longitude:
                    location = (vehicle.last_known_latitude, vehicle.last_known_longitude)
                else:
                    # 주소를 좌표로 변환
                    if vehicle.base_address:
                        coords = await self.map_service.geocode_address(vehicle.base_address)
                        if coords:
                            location = coords
            
            if location:
                available.append({
                    "vehicle": vehicle,
                    "driver": driver,
                    "location": location,
                    "status": vehicle.status
                })
        
        return available
    
    async def calculate_distance(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Optional[Dict]:
        """
        거리 및 소요시간 계산 (네이버 맵 API)
        
        Args:
            origin: (lat, lng) 출발지
            destination: (lat, lng) 도착지
            
        Returns:
            {
                "distance_km": float,
                "duration_min": int,
                "route": {...}  # 경로 좌표
            }
        """
        result = await self.map_service.calculate_distance_and_duration(
            origin[0], origin[1],
            destination[0], destination[1]
        )
        
        if result:
            return {
                "distance_km": result["distance_km"],
                "duration_min": result["duration_min"],
                "route": result.get("route")
            }
        
        return None
    
    async def apply_dispatch_rules(
        self,
        order: Order,
        candidates: List[Dict]
    ) -> List[Dict]:
        """
        배차 규칙 적용 (Phase 10 통합)
        
        Returns:
            정렬된 후보 리스트
        """
        # 활성 규칙 조회
        rules = self.db.query(DispatchRule).filter(
            DispatchRule.is_active == True
        ).order_by(DispatchRule.priority.desc()).all()
        
        if not rules:
            # 규칙이 없으면 거리순 정렬
            return sorted(candidates, key=lambda x: x["distance_km"])
        
        # 각 후보에 점수 부여
        scored_candidates = []
        for candidate in candidates:
            score = self._calculate_score(order, candidate, rules)
            scored_candidates.append({
                **candidate,
                "score": score
            })
        
        # 점수순 정렬 (높은 점수 = 더 좋음)
        return sorted(scored_candidates, key=lambda x: x["score"], reverse=True)
    
    def _calculate_score(
        self,
        order: Order,
        candidate: Dict,
        rules: List[DispatchRule]
    ) -> float:
        """
        후보 점수 계산
        
        점수 구성:
        - 거리: 가까울수록 높음
        - 평점: 높을수록 높음
        - 규칙: 조건 만족하면 가산점
        """
        score = 100.0
        
        # 1. 거리 점수 (최대 40점)
        # 5km 이내: 40점, 10km: 30점, 20km: 20점, 그 이상: 10점
        distance_km = candidate["distance_km"]
        if distance_km <= 5:
            score += 40
        elif distance_km <= 10:
            score += 30
        elif distance_km <= 20:
            score += 20
        else:
            score += 10
        
        # 2. 평점 점수 (최대 30점)
        driver = candidate["driver"]
        if driver.rating:
            score += driver.rating * 6  # 5점 만점 * 6 = 30점
        
        # 3. 규칙 점수 (규칙당 최대 10점)
        for rule in rules:
            if self._check_rule_condition(order, candidate, rule):
                score += rule.priority * 2  # priority 1-5 → 2-10점
        
        return score
    
    def _check_rule_condition(
        self,
        order: Order,
        candidate: Dict,
        rule: DispatchRule
    ) -> bool:
        """
        배차 규칙 조건 체크
        
        간단한 조건 평가 (Phase 11-C ConditionParser 활용 가능)
        """
        try:
            # 규칙 조건이 없으면 항상 True
            if not rule.conditions:
                return True
            
            # 조건 평가 (간단한 버전)
            # TODO: Phase 11-C의 ConditionParser 통합
            
            # 예: distance 조건
            if "distance" in rule.conditions:
                max_distance = rule.conditions["distance"].get("max_km")
                if max_distance and candidate["distance_km"] > max_distance:
                    return False
            
            # 예: rating 조건
            if "rating" in rule.conditions:
                min_rating = rule.conditions["rating"].get("min")
                driver = candidate["driver"]
                if min_rating and (not driver.rating or driver.rating < min_rating):
                    return False
            
            # 예: vehicle_type 조건
            if "vehicle_type" in rule.conditions:
                required_type = rule.conditions["vehicle_type"].get("type")
                vehicle = candidate["vehicle"]
                if required_type and vehicle.vehicle_type != required_type:
                    return False
            
            return True
        
        except Exception as e:
            logger.warning(f"Rule condition check failed: {e}")
            return False
    
    def _check_temperature_capability(self, vehicle: Vehicle, order: Order) -> bool:
        """
        차량 온도 능력 체크
        """
        if not vehicle.temperature_type:
            return False
        
        # 냉동 요구 → 냉동차 필요
        if order.temperature_min and order.temperature_min < 0:
            return vehicle.temperature_type in ['frozen', 'both']
        
        # 냉장 요구 → 냉장차 이상 필요
        if order.temperature_min and order.temperature_min < 10:
            return vehicle.temperature_type in ['refrigerated', 'both']
        
        # 상온 → 모든 차량 가능
        return True
    
    def _generate_reasoning(
        self,
        order: Order,
        best: Dict,
        all_candidates: List[Dict]
    ) -> str:
        """
        배차 결정 이유 생성 (설명 가능한 AI)
        """
        reasons = []
        
        # 1. 거리
        reasons.append(f"가장 가까운 차량 ({best['distance_km']:.1f}km, 약 {best['estimated_time_min']}분)")
        
        # 2. 기사 평점
        if best['driver'].rating:
            reasons.append(f"우수 기사 (평점 {best['driver'].rating:.1f}/5.0)")
        
        # 3. 차량 타입
        vehicle = best['vehicle']
        if vehicle.temperature_type:
            temp_names = {
                'frozen': '냉동',
                'refrigerated': '냉장',
                'both': '냉동/냉장',
                'ambient': '상온'
            }
            reasons.append(f"{temp_names.get(vehicle.temperature_type, '일반')} 차량")
        
        # 4. 대안 차량 수
        if len(all_candidates) > 1:
            reasons.append(f"다른 {len(all_candidates)-1}개 차량과 비교")
        
        return " | ".join(reasons)
    
    async def get_vehicle_route(
        self,
        vehicle_id: int,
        order_id: int
    ) -> Optional[Dict]:
        """
        차량 경로 조회 (현재 위치 → 픽업 → 배송)
        
        Returns:
            {
                "current_to_pickup": {...},
                "pickup_to_delivery": {...},
                "total_distance_km": float,
                "total_duration_min": int
            }
        """
        try:
            # 차량 & 주문 조회
            vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            order = self.db.query(Order).filter(Order.id == order_id).first()
            
            if not vehicle or not order:
                return None
            
            # 현재 위치
            current_location = await self.gps_service.get_vehicle_location(vehicle_id)
            if not current_location:
                return None
            
            # 1. 현재 → 픽업
            route1 = await self.calculate_distance(
                current_location,
                (order.pickup_latitude, order.pickup_longitude)
            )
            
            # 2. 픽업 → 배송
            route2 = await self.calculate_distance(
                (order.pickup_latitude, order.pickup_longitude),
                (order.delivery_latitude, order.delivery_longitude)
            )
            
            if route1 and route2:
                return {
                    "current_to_pickup": route1,
                    "pickup_to_delivery": route2,
                    "total_distance_km": route1["distance_km"] + route2["distance_km"],
                    "total_duration_min": route1["duration_min"] + route2["duration_min"]
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Get vehicle route failed: {e}")
            return None
