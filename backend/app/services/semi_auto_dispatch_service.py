"""
반자동 배차 서비스 (Semi-AI Dispatch)

사용자가 배차 오더를 주면:
1. 150km 이내 대기 중인 차량 목록 표시
2. 오더 시간에 맞게 근처에서 하차하는 차량 표시
3. 각 차량의 점수와 추천 이유 표시
4. 사용자가 최종 선택
"""
import logging
import math
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.models.order import Order
from app.models.vehicle import Vehicle
from app.models.employee import Employee
from app.models.dispatch import Dispatch
from app.models.uvis_gps import VehicleGPSLog
from app.services.naver_map_service import NaverMapService
from app.services.uvis_gps_service import UvisGPSService

logger = logging.getLogger(__name__)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    두 좌표 간의 직선 거리 계산 (Haversine 공식)
    Returns: 거리 (km)
    """
    # 지구 반지름 (km)
    R = 6371.0
    
    # 라디안으로 변환
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # 차이 계산
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine 공식
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


class SemiAutoDispatchService:
    """반자동 배차 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.map_service = NaverMapService()
        self.uvis_gps_service = UvisGPSService(db)
    
    async def suggest_vehicles(
        self,
        order_id: int,
        max_distance_km: int = 150,
        time_window_hours: int = 2
    ) -> Dict:
        """
        배차 가능한 차량 제안
        
        Args:
            order_id: 주문 ID
            max_distance_km: 최대 거리 (기본 150km)
            time_window_hours: 시간 여유 (기본 2시간)
            
        Returns:
            {
                "order": {...},
                "suggestions": [
                    {
                        "vehicle_id": int,
                        "vehicle_number": str,
                        "driver": {...},
                        "status": str,  # "waiting", "nearby_dropoff", "in_transit"
                        "current_location": {...},
                        "distance_km": float,
                        "estimated_arrival_min": int,
                        "score": float,  # 0-100 점수
                        "reasons": [str],  # 추천 이유
                        "warnings": [str],  # 주의사항
                    }
                ]
            }
        """
        try:
            # 1. 주문 조회
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {
                    "success": False,
                    "error": "주문을 찾을 수 없습니다",
                    "order_id": order_id
                }
            
            logger.info(f"🔍 배차 가능 차량 조회 시작: 주문 #{order_id}")
            
            # 2. GPS 데이터는 백그라운드 스케줄러가 5분마다 자동 수집
            # 여기서는 DB에 저장된 최근 데이터를 바로 사용 (응답 속도 최적화)
            logger.info("📡 DB에 저장된 최신 GPS 데이터 사용 (스케줄러가 5분마다 자동 수집)")
            
            # 3. 모든 활성 차량 조회
            # 3. 모든 활성 차량 조회
            vehicles = self.db.query(Vehicle).filter(
                Vehicle.is_active == True
            ).all()
            
            suggestions = []
            
            # 4. 각 차량 분석
            for vehicle in vehicles:
                try:
                    suggestion = await self._analyze_vehicle(
                        vehicle, order, max_distance_km, time_window_hours
                    )
                    if suggestion:
                        suggestions.append(suggestion)
                except Exception as e:
                    logger.error(f"차량 {vehicle.id} 분석 실패: {e}")
                    continue
            
            # 5. 점수순 정렬
            suggestions.sort(key=lambda x: x["score"], reverse=True)
            
            logger.info(f"✅ {len(suggestions)}개 차량 제안 완료")
            
            return {
                "success": True,
                "order": {
                    "id": order.id,
                    "order_number": order.order_number,
                    "product_name": order.product_name,
                    "pickup_address": order.pickup_address,
                    "delivery_address": order.delivery_address,
                    "pickup_time": order.pickup_start_time.isoformat() if order.pickup_start_time else None,
                    "pallet_count": order.pallet_count,
                    "temperature_zone": order.temperature_zone.value if hasattr(order.temperature_zone, 'value') else str(order.temperature_zone),
                },
                "suggestions": suggestions,
                "total_count": len(suggestions),
                "filter": {
                    "max_distance_km": max_distance_km,
                    "time_window_hours": time_window_hours
                }
            }
            
        except Exception as e:
            logger.error(f"배차 제안 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "order_id": order_id
            }
    
    def _get_vehicle_current_location(self, vehicle: Vehicle) -> Optional[tuple]:
        """
        차량의 현재 위치 가져오기 (우선순위: GPS > 차고지)
        Returns: (latitude, longitude) or None
        """
        # 1순위: 최신 GPS 위치 (최근 10분 이내) - 스케줄러가 5분마다 수집
        now_utc = datetime.now(timezone.utc)
        latest_gps = self.db.query(VehicleGPSLog).filter(
            VehicleGPSLog.vehicle_id == vehicle.id,
            VehicleGPSLog.latitude.isnot(None),
            VehicleGPSLog.longitude.isnot(None),
            VehicleGPSLog.created_at >= now_utc - timedelta(minutes=10)  # 6시간 → 10분으로 변경
        ).order_by(desc(VehicleGPSLog.created_at)).first()
        
        if latest_gps and latest_gps.latitude and latest_gps.longitude:
            age_minutes = int((now_utc - latest_gps.created_at).total_seconds() / 60)
            logger.info(f"차량 {vehicle.plate_number} GPS 위치 사용: ({latest_gps.latitude}, {latest_gps.longitude}) - {age_minutes}분 전")
            return (latest_gps.latitude, latest_gps.longitude)
        
        # 2순위: 차고지 위치
        if vehicle.garage_latitude and vehicle.garage_longitude:
            logger.info(f"차량 {vehicle.plate_number} 차고지 위치 사용: ({vehicle.garage_latitude}, {vehicle.garage_longitude})")
            return (vehicle.garage_latitude, vehicle.garage_longitude)
        
        logger.warning(f"차량 {vehicle.plate_number} 위치 정보 없음")
        return None
    
    async def _analyze_vehicle(
        self,
        vehicle: Vehicle,
        order: Order,
        max_distance_km: int,
        time_window_hours: int
    ) -> Optional[Dict]:
        """개별 차량 분석"""
        
        # 운전자 정보 (Vehicle 모델에 직접 저장됨)
        driver_info = {
            "name": vehicle.driver_name,
            "phone": vehicle.driver_phone
        } if vehicle.driver_name else None
        
        if not driver_info:
            return None  # 배정된 운전자 없음
        
        # 현재 배차 상태 확인 (DispatchStatus enum: DRAFT, CONFIRMED, IN_PROGRESS, COMPLETED, CANCELLED)
        current_dispatch = self.db.query(Dispatch).filter(
            Dispatch.vehicle_id == vehicle.id,
            Dispatch.status.in_(['확정', '진행중'])  # CONFIRMED, IN_PROGRESS
        ).first()
        
        status = "waiting"  # 대기중
        current_location = None
        distance_km = None
        estimated_arrival_min = None
        score = 50.0  # 기본 점수
        reasons = []
        warnings = []
        
        # 1. 대기 중인 차량 (가장 높은 우선순위)
        if not current_dispatch:
            status = "waiting"
            score += 30
            reasons.append("✅ 현재 대기 중 (즉시 배차 가능)")
            
            # 차량 위치: GPS 실시간 위치 또는 차고지 위치 사용
            # 기본값 설정
            distance_km = 0.0
            estimated_arrival_min = 30
            
            # 주문 픽업 위치 확인
            if order.pickup_latitude and order.pickup_longitude:
                # 차량의 현재 위치 가져오기 (GPS 우선, 차고지 대체)
                vehicle_location = self._get_vehicle_current_location(vehicle)
                
                if vehicle_location:
                    vehicle_lat, vehicle_lng = vehicle_location
                    
                    # 1단계: 직선 거리로 빠른 필터링 (Haversine 공식)
                    straight_distance_km = haversine_distance(
                        vehicle_lat, vehicle_lng,
                        order.pickup_latitude, order.pickup_longitude
                    )
                    
                    # 직선 거리가 max_distance_km * 1.5보다 크면 즉시 제외
                    # (도로 거리는 직선 거리의 1.3~1.5배 정도)
                    if straight_distance_km > max_distance_km * 1.5:
                        logger.debug(f"차량 {vehicle.plate_number}: 직선 거리 {straight_distance_km:.1f}km로 제외")
                        return None
                    
                    # 2단계: 직선 거리가 가까우면 네이버 맵 API로 정확한 거리 계산
                    # 단, 직선 거리가 매우 가까우면 (20km 이내) 네이버 맵 API 사용
                    # 그 외에는 직선 거리 * 1.3으로 추정
                    if straight_distance_km <= 20:
                        # 네이버 맵 API로 정확한 도로 거리 계산
                        distance_data = await self.map_service.calculate_distance_and_duration(
                            vehicle_lat, vehicle_lng,
                            order.pickup_latitude, order.pickup_longitude
                        )
                        
                        if distance_data and distance_data.get("distance_km") is not None:
                            distance_km = distance_data["distance_km"]
                            estimated_arrival_min = distance_data.get("duration_minutes", 30)
                        else:
                            # API 실패 시 직선 거리 * 1.3으로 추정
                            distance_km = straight_distance_km * 1.3
                            estimated_arrival_min = int(distance_km / 40 * 60)  # 평균 40km/h 가정
                            warnings.append("⚠️ 거리 계산 실패 (추정값 사용)")
                    else:
                        # 직선 거리가 멀면 네이버 API 호출 생략, 직선 거리 * 1.3으로 추정
                        distance_km = straight_distance_km * 1.3
                        estimated_arrival_min = int(distance_km / 60 * 60)  # 평균 60km/h 가정
                        logger.debug(f"차량 {vehicle.plate_number}: 직선 거리 기반 추정 {distance_km:.1f}km")
                    
                    if distance_km <= max_distance_km:
                        reasons.append(f"📍 현재 위치에서 상차지까지 {distance_km:.1f}km (약 {estimated_arrival_min}분)")
                    else:
                        warnings.append(f"⚠️ 현재 위치에서 상차지까지 {distance_km:.1f}km (최대거리 {max_distance_km}km 초과)")
                        return None  # 거리 범위 초과
                else:
                    # 차량 위치 정보 없음 - 기본값 유지
                    warnings.append("⚠️ 차량 위치 정보 없음 (기본값 사용)")
                    reasons.append(f"📍 상차지: {order.pickup_address or '위치 정보 없음'}")
            else:
                warnings.append("⚠️ 상차지 위치 정보 없음 (거리 계산 불가)")
        
        # 2. 근처에서 하차 예정인 차량
        elif current_dispatch and current_dispatch.status == '진행중':
            # 현재 배송 중
            delivery_time = current_dispatch.scheduled_dropoff_time
            order_pickup_time = order.pickup_start_time
            
            if delivery_time and order_pickup_time:
                time_diff = (order_pickup_time - delivery_time).total_seconds() / 3600
                
                # 오더 시간 전에 하차 완료 예상
                if 0 < time_diff < time_window_hours:
                    status = "nearby_dropoff"
                    score += 20
                    reasons.append(f"🚚 배송 완료 후 {int(time_diff * 60)}분 내 투입 가능")
                    
                    # 하차 위치와 픽업 위치 거리 계산 필요
                    if current_dispatch.delivery_latitude and current_dispatch.delivery_longitude:
                        if order.pickup_latitude and order.pickup_longitude:
                            # 1단계: 직선 거리로 빠른 필터링
                            straight_distance_km = haversine_distance(
                                current_dispatch.delivery_latitude, current_dispatch.delivery_longitude,
                                order.pickup_latitude, order.pickup_longitude
                            )
                            
                            # 직선 거리가 너무 멀면 즉시 제외
                            if straight_distance_km > max_distance_km * 1.5:
                                logger.debug(f"차량 {vehicle.plate_number}: 하차-픽업 직선 거리 {straight_distance_km:.1f}km로 제외")
                                return None
                            
                            # 2단계: 가까우면 정확한 거리 계산, 멀면 추정
                            if straight_distance_km <= 20:
                                # 네이버 맵 API로 거리 계산
                                distance_data = await self.map_service.calculate_distance_and_duration(
                                    current_dispatch.delivery_latitude, current_dispatch.delivery_longitude,
                                    order.pickup_latitude, order.pickup_longitude
                                )
                                
                                if distance_data and distance_data.get("distance_km") is not None:
                                    distance_km = distance_data["distance_km"]
                                    estimated_arrival_min = distance_data.get("duration_minutes", 30)
                                else:
                                    distance_km = straight_distance_km * 1.3
                                    estimated_arrival_min = int(distance_km / 40 * 60)
                            else:
                                # 멀면 추정값 사용 (네이버 API 호출 생략)
                                distance_km = straight_distance_km * 1.3
                                estimated_arrival_min = int(distance_km / 60 * 60)
                            
                            if distance_km <= max_distance_km:
                                score += 15
                                reasons.append(f"📍 하차지에서 픽업지까지 {distance_km:.1f}km")
                            else:
                                warnings.append(f"⚠️ 하차지에서 픽업지까지 {distance_km:.1f}km (범위 초과)")
                                return None
                else:
                    return None  # 시간이 맞지 않음
            else:
                return None
        
        else:
            return None  # 로딩 중 등 다른 상태는 제외
        
        # 3. 차량 용량 체크 (Order의 weight_kg 필드 사용)
        if order.weight_kg and vehicle.max_weight_kg:
            if order.weight_kg <= vehicle.max_weight_kg:
                score += 10
                reasons.append(f"✅ 적재 가능 (차량: {vehicle.max_weight_kg}kg, 화물: {order.weight_kg}kg)")
            else:
                score -= 30
                warnings.append(f"❌ 중량 초과 (차량: {vehicle.max_weight_kg}kg, 화물: {order.weight_kg}kg)")
        
        # 4. 지게차 기능 (참고용)
        if vehicle.forklift_operator_available:
            score += 5
            reasons.append("✅ 지게차 운전 가능")
        
        # 5. 온도 범위 확인 (Order의 temperature_zone 사용)
        # TemperatureZone: FROZEN(냉동), REFRIGERATED(냉장), AMBIENT(상온)
        # VehicleType: FROZEN(냉동), REFRIGERATED(냉장), DUAL(겸용), AMBIENT(상온)
        order_temp_zone = order.temperature_zone.value if hasattr(order.temperature_zone, 'value') else str(order.temperature_zone)
        vehicle_type = vehicle.vehicle_type.value if hasattr(vehicle.vehicle_type, 'value') else str(vehicle.vehicle_type)
        
        if order_temp_zone == "냉동":
            if vehicle_type in ["냉동", "겸용"]:
                score += 10
                reasons.append("✅ 냉동 기능 보유")
            else:
                score -= 30
                warnings.append("❌ 냉동 기능 없음 (필요함)")
                return None
        elif order_temp_zone == "냉장":
            if vehicle_type in ["냉장", "겸용", "냉동"]:
                score += 10
                reasons.append("✅ 냉장 기능 보유")
            else:
                score -= 30
                warnings.append("❌ 냉장 기능 없음 (필요함)")
                return None
        
        # 6. 운전자 경력/평가
        # TODO: 운전자 평점 시스템 추가
        
        return {
            "vehicle_id": vehicle.id,
            "vehicle_number": vehicle.plate_number,
            "vehicle_type": vehicle.vehicle_type.value if hasattr(vehicle.vehicle_type, 'value') else str(vehicle.vehicle_type),
            "vehicle_code": vehicle.code,
            "driver": {
                "name": driver_info["name"],
                "phone": driver_info["phone"],
            } if driver_info else None,
            "status": status,
            "status_label": {
                "waiting": "대기 중",
                "nearby_dropoff": "근처 하차 예정",
                "in_transit": "배송 중"
            }.get(status, status),
            "current_location": current_location,
            "distance_km": distance_km,
            "estimated_arrival_min": estimated_arrival_min,
            "score": round(score, 1),
            "reasons": reasons,
            "warnings": warnings,
            "vehicle_info": {
                "max_weight_kg": vehicle.max_weight_kg,
                "max_pallets": vehicle.max_pallets,
                "vehicle_type": vehicle.vehicle_type.value if hasattr(vehicle.vehicle_type, 'value') else str(vehicle.vehicle_type),
                "forklift_available": vehicle.forklift_operator_available,
            }
        }
