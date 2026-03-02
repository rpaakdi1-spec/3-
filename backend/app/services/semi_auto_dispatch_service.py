"""
반자동 배차 서비스 (Semi-AI Dispatch)

사용자가 배차 오더를 주면:
1. 150km 이내 대기 중인 차량 목록 표시
2. 오더 시간에 맞게 근처에서 하차하는 차량 표시
3. 각 차량의 점수와 추천 이유 표시
4. 사용자가 최종 선택
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.order import Order
from app.models.vehicle import Vehicle
from app.models.employee import Employee
from app.models.dispatch import Dispatch
from app.services.naver_map_service import NaverMapService

logger = logging.getLogger(__name__)


class SemiAutoDispatchService:
    """반자동 배차 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.map_service = NaverMapService()
    
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
            
            # 2. 모든 활성 차량 조회
            vehicles = self.db.query(Vehicle).filter(
                Vehicle.is_active == True
            ).all()
            
            suggestions = []
            
            # 3. 각 차량 분석
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
            
            # 4. 점수순 정렬
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
            
            # 차량 위치: 차고지 또는 마지막 알려진 위치
            # 기본값 설정 (위치 정보가 없어도 차량 표시)
            distance_km = 0.0
            estimated_arrival_min = 30
            
            # 픽업 위치가 있으면 거리 계산 (향후 차량 GPS 위치 활용)
            if order.pickup_latitude and order.pickup_longitude:
                # 실제로는 차량의 GPS 위치를 가져와야 함
                # 현재는 기본값 사용
                reasons.append(f"📍 상차지 주소: {order.pickup_address or '위치 정보 없음'}")
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
                            # 네이버 맵 API로 거리 계산
                            distance_data = await self.map_service.get_distance_and_duration(
                                (current_dispatch.delivery_latitude, current_dispatch.delivery_longitude),
                                (order.pickup_latitude, order.pickup_longitude)
                            )
                            
                            if distance_data["success"]:
                                distance_km = distance_data["distance_km"]
                                estimated_arrival_min = distance_data["duration_min"]
                                
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
