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
                    "client_name": order.client.name if order.client else None,
                    "pickup_address": order.pickup_address,
                    "delivery_address": order.delivery_address,
                    "pickup_time": order.pickup_start_time.isoformat() if order.pickup_start_time else None,
                    "cargo_weight": order.cargo_weight_kg,
                    "cargo_volume": order.cargo_volume_cbm,
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
        
        # 운전자 확인
        driver = self.db.query(Employee).filter(
            Employee.id == vehicle.assigned_driver_id
        ).first()
        
        if not driver:
            return None  # 배정된 운전자 없음
        
        # 현재 배차 상태 확인
        current_dispatch = self.db.query(Dispatch).filter(
            Dispatch.vehicle_id == vehicle.id,
            Dispatch.status.in_(['pending', 'in_transit', 'loading'])
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
            # 여기서는 간단히 차고지 주소 사용
            if order.pickup_latitude and order.pickup_longitude:
                # 실제로는 차량의 GPS 위치를 가져와야 함
                # 임시로 거리 0으로 설정 (개선 필요)
                distance_km = 0
                estimated_arrival_min = 30  # 기본 30분
                
                if distance_km <= max_distance_km:
                    reasons.append(f"📍 픽업지에서 {distance_km:.1f}km (범위 내)")
                else:
                    warnings.append(f"⚠️ 픽업지에서 {distance_km:.1f}km (범위 초과)")
                    return None  # 너무 멀면 제외
        
        # 2. 근처에서 하차 예정인 차량
        elif current_dispatch and current_dispatch.status == 'in_transit':
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
        
        # 3. 차량 용량 체크
        if order.cargo_weight_kg and vehicle.max_load_weight:
            if order.cargo_weight_kg <= vehicle.max_load_weight:
                score += 10
                reasons.append(f"✅ 적재 가능 (차량: {vehicle.max_load_weight}kg, 화물: {order.cargo_weight_kg}kg)")
            else:
                score -= 30
                warnings.append(f"❌ 중량 초과 (차량: {vehicle.max_load_weight}kg, 화물: {order.cargo_weight_kg}kg)")
        
        # 4. 지게차 필요 여부
        if order.requires_forklift:
            if driver.can_drive_forklift:
                score += 10
                reasons.append("✅ 지게차 운전 가능")
            else:
                score -= 20
                warnings.append("⚠️ 지게차 운전 불가 (필요함)")
        
        # 5. 냉장 기능 필요 여부
        if order.requires_refrigeration:
            if vehicle.has_refrigeration:
                score += 10
                reasons.append("✅ 냉장 기능 보유")
            else:
                score -= 30
                warnings.append("❌ 냉장 기능 없음 (필요함)")
                return None  # 냉장 필수인 경우 제외
        
        # 6. 운전자 경력/평가
        # TODO: 운전자 평점 시스템 추가
        
        return {
            "vehicle_id": vehicle.id,
            "vehicle_number": vehicle.vehicle_number,
            "vehicle_type": vehicle.vehicle_type,
            "vehicle_model": vehicle.model,
            "driver": {
                "id": driver.id,
                "name": driver.name,
                "phone": driver.phone,
                "employee_code": driver.employee_code,
            } if driver else None,
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
                "max_load_weight": vehicle.max_load_weight,
                "has_refrigeration": vehicle.has_refrigeration,
                "has_lift_gate": vehicle.has_lift_gate,
            }
        }
