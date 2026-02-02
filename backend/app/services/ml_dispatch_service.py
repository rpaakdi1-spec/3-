"""
ML-based Dispatch Optimization Service

Multi-Agent 학습 시스템을 활용한 스마트 배차 최적화
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import math
from loguru import logger

from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.vehicle import Vehicle, VehicleType, VehicleStatus
from app.models.order import Order, TemperatureZone, OrderStatus
from app.models.dispatch import Dispatch, DispatchRoute, DispatchStatus
from app.models.uvis_gps import VehicleGPSLog


# ============================================
# Data Structures
# ============================================

@dataclass
class AgentScore:
    """Agent별 점수 저장"""
    distance: float = 0.0
    rotation: float = 0.0
    time_window: float = 0.0
    preference: float = 0.0
    voltage: float = 1.0  # 기본값 1.0 (안전)


@dataclass
class VehicleRanking:
    """차량 순위 정보"""
    vehicle: Vehicle
    total_score: float
    agent_scores: AgentScore
    reason: str  # 선택 이유


# ============================================
# Utility Functions
# ============================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """두 지점 간 Haversine 거리 계산 (km)"""
    R = 6371  # 지구 반지름 (km)
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def is_temperature_compatible(vehicle: Vehicle, temp_zone: TemperatureZone) -> bool:
    """온도대 호환성 체크"""
    # Phase 1에서 추가된 필드 사용
    if not hasattr(vehicle, 'supports_frozen'):
        # Fallback: vehicle_type 기반 판단
        if temp_zone == TemperatureZone.FROZEN:
            return vehicle.vehicle_type in [VehicleType.FROZEN, VehicleType.DUAL]
        elif temp_zone == TemperatureZone.REFRIGERATED:
            return vehicle.vehicle_type in [VehicleType.REFRIGERATED, VehicleType.DUAL]
        else:  # AMBIENT
            return vehicle.vehicle_type in [VehicleType.AMBIENT, VehicleType.DUAL]
    
    # Phase 1 필드 사용
    if temp_zone == TemperatureZone.FROZEN:
        return vehicle.supports_frozen
    elif temp_zone == TemperatureZone.REFRIGERATED:
        return vehicle.supports_chilled
    else:  # AMBIENT
        return vehicle.supports_ambient


def check_pallet_capacity(vehicle: Vehicle, pallet_type: str, pallet_count: int) -> bool:
    """팔렛트 용량 체크"""
    # Phase 1에서 추가된 필드 사용
    if pallet_type == "11형":
        if hasattr(vehicle, 'max_pallets_11type') and vehicle.max_pallets_11type:
            return pallet_count <= vehicle.max_pallets_11type
        else:
            return pallet_count <= vehicle.max_pallets
    elif pallet_type == "12형":
        if hasattr(vehicle, 'max_pallets_12type') and vehicle.max_pallets_12type:
            return pallet_count <= vehicle.max_pallets_12type
        else:
            # Fallback: 12형은 11형의 85% 용량
            return pallet_count <= int(vehicle.max_pallets * 0.85)
    
    return pallet_count <= vehicle.max_pallets


# ============================================
# Hard Rules Filter
# ============================================

class HardRulesFilter:
    """필수 제약조건 필터링 (ML 불필요)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def filter_vehicles(
        self, 
        order: Order, 
        vehicles: List[Vehicle]
    ) -> Tuple[List[Vehicle], List[str]]:
        """
        주문에 대해 배차 가능한 차량만 필터링
        
        Returns:
            (eligible_vehicles, rejection_reasons)
        """
        eligible = []
        rejected = []
        
        for vehicle in vehicles:
            reason = self._check_vehicle_eligibility(order, vehicle)
            
            if reason is None:
                eligible.append(vehicle)
            else:
                rejected.append(f"{vehicle.code}: {reason}")
        
        logger.info(f"Order {order.order_number}: {len(eligible)}/{len(vehicles)} vehicles eligible")
        
        return eligible, rejected
    
    def _check_vehicle_eligibility(self, order: Order, vehicle: Vehicle) -> Optional[str]:
        """
        차량 배차 가능 여부 체크
        
        Returns:
            None if eligible, rejection reason string otherwise
        """
        # 1. 차량 상태 체크
        if vehicle.status not in [VehicleStatus.AVAILABLE]:
            return f"차량 상태 불가: {vehicle.status.value}"
        
        # 2. 온도대 호환성
        if not is_temperature_compatible(vehicle, order.temperature_zone):
            return f"온도대 불일치: {order.temperature_zone.value} 불가"
        
        # 3. 팔렛트 용량
        pallet_type = getattr(order, 'pallet_type', '11형')
        if not check_pallet_capacity(vehicle, pallet_type, order.pallet_count):
            return f"용량 초과: {order.pallet_count}팔렛트({pallet_type}) > 최대"
        
        # 4. 기피 차량 체크
        if hasattr(order, 'delivery_client') and order.delivery_client:
            blocked_vehicles = getattr(order.delivery_client, 'blocked_vehicles', [])
            if vehicle.id in blocked_vehicles:
                return "거래처 기피 차량"
        
        # 5. 고정배차 우선권
        # (이 단계에서는 제외하지 않고, 점수에 반영)
        
        return None


# ============================================
# ML Agent 1: Distance Optimizer
# ============================================

class DistanceOptimizer:
    """공차 거리 최소화 Agent"""
    
    def __init__(self, max_empty_distance_km: float = 150.0):
        self.max_empty_distance_km = max_empty_distance_km
    
    async def compute_score(
        self, 
        vehicle: Vehicle, 
        order: Order,
        db: Session
    ) -> float:
        """
        거리 점수 계산 (0~1, 낮을수록 좋음)
        
        Returns:
            0.0 = 최적 (거리 0km)
            1.0 = 기준치 (150km)
            2.0 = 매우 불리 (300km 이상)
        """
        # 차량 현위치 가져오기
        vehicle_loc = await self._get_vehicle_location(vehicle, db)
        
        if not vehicle_loc:
            logger.warning(f"Vehicle {vehicle.code}: No location, using garage")
            vehicle_loc = (vehicle.garage_latitude, vehicle.garage_longitude)
        
        if not vehicle_loc[0] or not vehicle_loc[1]:
            logger.warning(f"Vehicle {vehicle.code}: No garage location")
            return 1.5  # 페널티
        
        # 공차 거리: 차량 위치 → 상차지
        if not order.pickup_latitude or not order.pickup_longitude:
            logger.warning(f"Order {order.order_number}: No pickup location")
            return 1.0
        
        empty_distance = haversine_distance(
            vehicle_loc[0], vehicle_loc[1],
            order.pickup_latitude, order.pickup_longitude
        )
        
        # 실제 운행 거리: 상차지 → 하차지
        if order.delivery_latitude and order.delivery_longitude:
            loaded_distance = haversine_distance(
                order.pickup_latitude, order.pickup_longitude,
                order.delivery_latitude, order.delivery_longitude
            )
        else:
            loaded_distance = 0.0
        
        # 복귀 거리: 하차지 → 차고지
        if order.delivery_latitude and vehicle.garage_latitude:
            return_distance = haversine_distance(
                order.delivery_latitude, order.delivery_longitude,
                vehicle.garage_latitude, vehicle.garage_longitude
            )
        else:
            return_distance = 0.0
        
        # 총 거리
        total_distance = empty_distance + loaded_distance + return_distance
        
        # 정규화: 150km 기준
        # 공차 거리에 더 높은 가중치 (2배)
        weighted_distance = empty_distance * 2.0 + loaded_distance + return_distance
        
        score = min(weighted_distance / (self.max_empty_distance_km * 3.0), 2.0)
        
        logger.debug(
            f"Vehicle {vehicle.code} → Order {order.order_number}: "
            f"공차={empty_distance:.1f}km, 실차={loaded_distance:.1f}km, "
            f"복귀={return_distance:.1f}km, score={score:.3f}"
        )
        
        return score
    
    async def _get_vehicle_location(
        self, 
        vehicle: Vehicle, 
        db: Session
    ) -> Optional[Tuple[float, float]]:
        """차량 현재 위치 가져오기 (GPS 최우선)"""
        latest_gps = (
            db.query(VehicleGPSLog)
            .filter(VehicleGPSLog.vehicle_id == vehicle.id)
            .order_by(VehicleGPSLog.created_at.desc())
            .first()
        )
        
        if latest_gps and latest_gps.latitude and latest_gps.longitude:
            # GPS 데이터가 1시간 이내인지 확인
            if (datetime.now() - latest_gps.created_at).total_seconds() < 3600:
                return (latest_gps.latitude, latest_gps.longitude)
        
        # Fallback: 차고지
        if vehicle.garage_latitude and vehicle.garage_longitude:
            return (vehicle.garage_latitude, vehicle.garage_longitude)
        
        return None


# ============================================
# ML Agent 2: Rotation Equalizer
# ============================================

class RotationEqualizer:
    """회전수 평준화 Agent"""
    
    def compute_score(
        self, 
        vehicle: Vehicle,
        all_vehicles: List[Vehicle]
    ) -> float:
        """
        회전수 공정성 점수 (0~1, 낮을수록 배차 필요)
        
        Returns:
            0.0 = 가장 적게 운행 (우선 배차)
            1.0 = 가장 많이 운행 (후순위)
        """
        # 차량별 회전수 수집
        rotation_counts = []
        for v in all_vehicles:
            count = getattr(v, 'rotation_count_this_month', 0)
            rotation_counts.append(count)
        
        if not rotation_counts:
            return 0.5
        
        current_rotation = getattr(vehicle, 'rotation_count_this_month', 0)
        max_rotation = max(rotation_counts)
        min_rotation = min(rotation_counts)
        
        # 정규화
        if max_rotation == min_rotation:
            return 0.5  # 모두 동일
        
        score = (current_rotation - min_rotation) / (max_rotation - min_rotation)
        
        logger.debug(
            f"Vehicle {vehicle.code}: 회전수={current_rotation}, "
            f"범위=[{min_rotation}, {max_rotation}], score={score:.3f}"
        )
        
        return score


# ============================================
# ML Agent 3: Time Window Checker
# ============================================

class TimeWindowChecker:
    """하차 시간 준수 Agent"""
    
    def compute_score(
        self, 
        vehicle: Vehicle,
        order: Order,
        estimated_arrival: Optional[datetime] = None
    ) -> float:
        """
        시간 여유도 점수 (0~1, 높을수록 여유)
        
        Returns:
            1.0 = 충분한 여유 (2시간 이상)
            0.5 = 적정 여유 (30분~2시간)
            0.0 = 시간 부족 (30분 미만)
        """
        # 하차 가능 시간
        if not hasattr(order.delivery_client, 'unload_start_time'):
            return 0.8  # 기본 점수
        
        unload_start = order.delivery_client.unload_start_time
        unload_end = order.delivery_client.unload_end_time
        
        if not unload_start or not unload_end:
            return 0.8
        
        # 예상 도착 시간 계산
        if estimated_arrival is None:
            # 간단한 추정: 현재 시간 + 상차 30분 + 운행 시간
            estimated_arrival = datetime.now() + timedelta(minutes=30)
            
            # 운행 거리 기반 시간 추정 (평균 40km/h)
            if order.pickup_latitude and order.delivery_latitude:
                distance = haversine_distance(
                    order.pickup_latitude, order.pickup_longitude,
                    order.delivery_latitude, order.delivery_longitude
                )
                drive_hours = distance / 40.0
                estimated_arrival += timedelta(hours=drive_hours)
        
        # 하차 시간과 비교
        arrival_time = estimated_arrival.time()
        
        # 시간을 분 단위로 변환
        arrival_minutes = arrival_time.hour * 60 + arrival_time.minute
        unload_start_minutes = int(unload_start.split(':')[0]) * 60 + int(unload_start.split(':')[1])
        unload_end_minutes = int(unload_end.split(':')[0]) * 60 + int(unload_end.split(':')[1])
        
        # 24시간 넘는 케이스 처리
        if unload_start_minutes > unload_end_minutes:
            # 예: 22:00 ~ 06:00
            if arrival_minutes >= unload_start_minutes or arrival_minutes <= unload_end_minutes:
                slack = 120  # 충분한 여유
            else:
                slack = min(
                    abs(arrival_minutes - unload_start_minutes),
                    abs(arrival_minutes - unload_end_minutes)
                )
        else:
            # 정상 케이스
            if unload_start_minutes <= arrival_minutes <= unload_end_minutes:
                slack = min(
                    arrival_minutes - unload_start_minutes,
                    unload_end_minutes - arrival_minutes
                )
            else:
                slack = -60  # 시간 외
        
        # 점수 변환
        if slack >= 120:
            score = 1.0
        elif slack >= 30:
            score = 0.5 + (slack - 30) / 180.0  # 0.5 ~ 1.0
        elif slack >= 0:
            score = slack / 60.0  # 0.0 ~ 0.5
        else:
            score = 0.0
        
        logger.debug(
            f"Vehicle {vehicle.code} → Order {order.order_number}: "
            f"도착={arrival_time}, 하차={unload_start}~{unload_end}, "
            f"여유={slack}분, score={score:.3f}"
        )
        
        return score


# ============================================
# ML Agent 4: Preference Matcher
# ============================================

class PreferenceMatcher:
    """고정배차 및 선호 매칭 Agent"""
    
    def compute_score(
        self, 
        vehicle: Vehicle,
        order: Order
    ) -> float:
        """
        선호도 점수 (0~1, 높을수록 선호)
        
        Returns:
            1.0 = 고정배차 최우선
            0.7 = 선호 하차지
            0.5 = 일반
            0.3 = 비선호
        """
        score = 0.5  # 기본 점수
        
        # 고정배차 체크
        if hasattr(order, 'is_fixed_dispatch') and order.is_fixed_dispatch:
            fixed_vehicles = getattr(order, 'fixed_vehicles', [])
            if vehicle.id in fixed_vehicles:
                logger.info(f"Vehicle {vehicle.code}: 고정배차 매칭!")
                return 1.0
        
        # 선호 하차지 체크
        if hasattr(vehicle, 'preferred_delivery_clients'):
            preferred_clients = vehicle.preferred_delivery_clients or []
            if order.delivery_client_id in preferred_clients:
                logger.info(f"Vehicle {vehicle.code}: 선호 하차지 매칭!")
                score = 0.7
        
        # 편도 고정차량
        if hasattr(vehicle, 'is_one_way_fixed') and vehicle.is_one_way_fixed:
            if order.delivery_client_id in getattr(vehicle, 'preferred_delivery_clients', []):
                score = max(score, 0.8)
        
        # 상온 전용 차량 우선순위
        if vehicle.vehicle_type == VehicleType.AMBIENT:
            if order.temperature_zone == TemperatureZone.AMBIENT:
                score = max(score, 0.6)
        
        return score


# ============================================
# ML Agent 5: Voltage Safety Checker
# ============================================

class VoltageSafetyChecker:
    """저전압 차량 배제 Agent"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def compute_score(
        self, 
        vehicle: Vehicle
    ) -> float:
        """
        전압 안전성 점수 (0 or 1)
        
        Returns:
            1.0 = 안전
            0.0 = 저전압 (배차 불가)
        """
        # UVIS GPS 데이터 조회
        latest_gps = (
            self.db.query(VehicleGPSLog)
            .filter(VehicleGPSLog.vehicle_id == vehicle.id)
            .order_by(VehicleGPSLog.created_at.desc())
            .first()
        )
        
        if not latest_gps:
            return 1.0  # 데이터 없으면 안전으로 간주
        
        voltage = getattr(latest_gps, 'voltage', None)
        engine_on = getattr(latest_gps, 'engine_on', False)
        
        if voltage is None:
            return 1.0
        
        # 시동 ON: 26V 미만 경고
        if engine_on and voltage < 26.0:
            logger.warning(f"Vehicle {vehicle.code}: 저전압 {voltage}V (시동 ON)")
            return 0.0
        
        # 시동 OFF: 24V 미만 경고
        if not engine_on and voltage < 24.0:
            logger.warning(f"Vehicle {vehicle.code}: 저전압 {voltage}V (시동 OFF)")
            return 0.0
        
        return 1.0


# ============================================
# Meta Coordinator
# ============================================

class MetaCoordinator:
    """Agent 점수 통합 및 최종 결정"""
    
    def __init__(self):
        # 가중치 (합=1.0)
        self.weights = {
            'distance': 0.30,      # 거리 (가장 중요)
            'rotation': 0.20,      # 회전수 평등
            'time_window': 0.25,   # 시간 준수
            'preference': 0.20,    # 선호 매칭
            'voltage': 0.05        # 안전 (pass/fail)
        }
    
    def compute_final_score(self, agent_scores: AgentScore) -> float:
        """최종 점수 계산 (0~1, 높을수록 좋음)"""
        # 전압이 0이면 즉시 배제
        if agent_scores.voltage == 0.0:
            return 0.0
        
        # 각 점수를 "높을수록 좋음" 형태로 변환
        distance_score = 1.0 - min(agent_scores.distance, 1.0)  # 반전
        rotation_score = 1.0 - agent_scores.rotation             # 반전
        time_score = agent_scores.time_window                    # 그대로
        preference_score = agent_scores.preference               # 그대로
        voltage_score = agent_scores.voltage                     # 그대로
        
        # 가중 합
        final_score = (
            self.weights['distance'] * distance_score +
            self.weights['rotation'] * rotation_score +
            self.weights['time_window'] * time_score +
            self.weights['preference'] * preference_score +
            self.weights['voltage'] * voltage_score
        )
        
        return final_score
    
    def rank_vehicles(
        self,
        eligible_vehicles: List[Vehicle],
        all_vehicles: List[Vehicle],
        order: Order,
        agent_scores_map: Dict[int, AgentScore]
    ) -> List[VehicleRanking]:
        """차량 순위 결정"""
        rankings = []
        
        for vehicle in eligible_vehicles:
            agent_scores = agent_scores_map.get(vehicle.id)
            if not agent_scores:
                continue
            
            final_score = self.compute_final_score(agent_scores)
            
            # 선택 이유 생성
            reason = self._generate_reason(agent_scores, final_score)
            
            rankings.append(VehicleRanking(
                vehicle=vehicle,
                total_score=final_score,
                agent_scores=agent_scores,
                reason=reason
            ))
        
        # 점수 높은 순 정렬
        rankings.sort(key=lambda x: x.total_score, reverse=True)
        
        return rankings
    
    def _generate_reason(self, scores: AgentScore, final_score: float) -> str:
        """선택 이유 텍스트 생성"""
        reasons = []
        
        if scores.preference >= 0.7:
            reasons.append("선호매칭")
        if scores.distance < 0.5:
            reasons.append("근거리")
        if scores.rotation < 0.3:
            reasons.append("회전수적음")
        if scores.time_window >= 0.8:
            reasons.append("시간여유")
        
        if not reasons:
            reasons.append("일반배차")
        
        return f"{', '.join(reasons)} (점수: {final_score:.3f})"


# ============================================
# Main Service
# ============================================

class MLDispatchService:
    """ML 기반 배차 최적화 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Agents 초기화
        self.hard_filter = HardRulesFilter(db)
        self.distance_optimizer = DistanceOptimizer()
        self.rotation_equalizer = RotationEqualizer()
        self.time_window_checker = TimeWindowChecker()
        self.preference_matcher = PreferenceMatcher()
        self.voltage_checker = VoltageSafetyChecker(db)
        
        # Coordinator
        self.meta_coordinator = MetaCoordinator()
    
    async def optimize_dispatch(
        self,
        orders: List[Order],
        vehicles: List[Vehicle]
    ) -> List[VehicleRanking]:
        """
        주문들에 대한 최적 배차 결정
        
        Returns:
            각 주문별 차량 순위 리스트
        """
        logger.info(f"ML Dispatch: {len(orders)} orders, {len(vehicles)} vehicles")
        
        results = []
        
        for order in orders:
            ranking = await self.optimize_single_order(order, vehicles)
            results.append({
                'order': order,
                'rankings': ranking
            })
        
        return results
    
    async def optimize_single_order(
        self,
        order: Order,
        vehicles: List[Vehicle]
    ) -> List[VehicleRanking]:
        """단일 주문에 대한 차량 순위 결정"""
        
        # Step 1: Hard Rules Filtering
        eligible_vehicles, rejected = self.hard_filter.filter_vehicles(order, vehicles)
        
        if not eligible_vehicles:
            logger.warning(f"Order {order.order_number}: No eligible vehicles!")
            logger.warning(f"Rejection reasons: {rejected}")
            return []
        
        # Step 2: ML Agent 점수 계산
        agent_scores_map = {}
        
        for vehicle in eligible_vehicles:
            scores = AgentScore()
            
            # Distance
            scores.distance = await self.distance_optimizer.compute_score(vehicle, order, self.db)
            
            # Rotation
            scores.rotation = self.rotation_equalizer.compute_score(vehicle, vehicles)
            
            # Time Window
            scores.time_window = self.time_window_checker.compute_score(vehicle, order)
            
            # Preference
            scores.preference = self.preference_matcher.compute_score(vehicle, order)
            
            # Voltage
            scores.voltage = await self.voltage_checker.compute_score(vehicle)
            
            agent_scores_map[vehicle.id] = scores
        
        # Step 3: Meta Coordinator로 순위 결정
        rankings = self.meta_coordinator.rank_vehicles(
            eligible_vehicles,
            vehicles,
            order,
            agent_scores_map
        )
        
        # 로그 출력
        if rankings:
            top3 = rankings[:3]
            logger.info(f"Order {order.order_number} Top 3:")
            for i, rank in enumerate(top3, 1):
                logger.info(
                    f"  {i}. {rank.vehicle.code}: {rank.total_score:.3f} - {rank.reason}"
                )
        
        return rankings
