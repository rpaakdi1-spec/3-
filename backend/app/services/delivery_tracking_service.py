"""
배송 추적 서비스

이 모듈은 고객용 배송 추적 시스템을 제공합니다:
1. 추적번호 생성 및 관리
2. 실시간 배송 상태 조회
3. 배송 히스토리 타임라인
4. 위치 정보 제공
5. 예상 도착 시간 계산
6. SMS/이메일 알림 전송
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models.order import Order, OrderStatus
from app.models.dispatch import Dispatch, DispatchRoute, RouteType, DispatchStatus
from app.models.vehicle_location import VehicleLocation
from app.core.config import settings


class DeliveryTrackingService:
    """배송 추적 서비스"""
    
    @staticmethod
    def generate_tracking_number(order_id: int, order_number: str) -> str:
        """
        추적번호 생성
        
        형식: TRK-YYYYMMDD-{8자리 해시}
        - 생성일자 + 주문ID와 랜덤 솔트 조합의 해시
        - 추측 불가능하면서도 유일한 추적번호 생성
        
        Args:
            order_id: 주문 ID
            order_number: 주문번호
            
        Returns:
            str: 추적번호
        """
        today = datetime.now().strftime("%Y%m%d")
        salt = secrets.token_hex(4)
        raw = f"{order_id}:{order_number}:{salt}"
        hash_value = hashlib.sha256(raw.encode()).hexdigest()[:8].upper()
        
        return f"TRK-{today}-{hash_value}"
    
    @staticmethod
    def get_order_with_tracking(
        db: Session,
        tracking_number: Optional[str] = None,
        order_number: Optional[str] = None
    ) -> Optional[Order]:
        """
        추적번호 또는 주문번호로 주문 조회
        
        Args:
            db: 데이터베이스 세션
            tracking_number: 추적번호
            order_number: 주문번호
            
        Returns:
            Order: 주문 객체 또는 None
        """
        if tracking_number:
            # 추적번호는 현재 Order 모델에 없으므로
            # 실제로는 주문번호와 매핑 테이블이 필요
            # 여기서는 order_number로 대체
            pass
        
        if order_number:
            return db.query(Order).filter(Order.order_number == order_number).first()
        
        return None
    
    @staticmethod
    def get_delivery_status(db: Session, order_id: int) -> Dict[str, Any]:
        """
        배송 상태 조회
        
        Args:
            db: 데이터베이스 세션
            order_id: 주문 ID
            
        Returns:
            Dict: 배송 상태 정보
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        
        # 최근 배차 정보 조회
        route = db.query(DispatchRoute).join(Dispatch).filter(
            DispatchRoute.order_id == order_id
        ).order_by(desc(Dispatch.dispatch_date)).first()
        
        if not route:
            return {
                "status": OrderStatus.PENDING.value,
                "status_description": "배차 대기 중입니다",
                "estimated_delivery_date": order.requested_delivery_date,
                "current_location": None,
                "progress_percentage": 0
            }
        
        dispatch = route.dispatch
        
        # 현재 위치 정보 조회
        latest_location = db.query(VehicleLocation).filter(
            VehicleLocation.dispatch_id == dispatch.id
        ).order_by(desc(VehicleLocation.recorded_at)).first()
        
        # 진행률 계산
        progress = DeliveryTrackingService._calculate_progress(db, dispatch, order_id)
        
        return {
            "status": order.status.value,
            "status_description": DeliveryTrackingService._get_status_description(order.status),
            "dispatch_number": dispatch.dispatch_number,
            "dispatch_date": dispatch.dispatch_date,
            "vehicle_number": dispatch.vehicle.vehicle_number if dispatch.vehicle else None,
            "driver_name": dispatch.driver.name if dispatch.driver else None,
            "driver_phone": dispatch.driver.phone if dispatch.driver else None,
            "estimated_delivery_date": order.requested_delivery_date,
            "current_location": {
                "latitude": latest_location.latitude,
                "longitude": latest_location.longitude,
                "address": latest_location.address,
                "recorded_at": latest_location.recorded_at
            } if latest_location else None,
            "progress_percentage": progress
        }
    
    @staticmethod
    def get_delivery_timeline(db: Session, order_id: int) -> List[Dict[str, Any]]:
        """
        배송 타임라인 조회
        
        주문 생성부터 현재까지의 모든 이벤트를 시간순으로 반환
        
        Args:
            db: 데이터베이스 세션
            order_id: 주문 ID
            
        Returns:
            List[Dict]: 타임라인 이벤트 목록
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return []
        
        timeline = []
        
        # 1. 주문 생성
        timeline.append({
            "timestamp": order.created_at,
            "event_type": "ORDER_CREATED",
            "title": "주문 접수",
            "description": f"주문번호: {order.order_number}",
            "status": "completed"
        })
        
        # 2. 배차 할당
        route = db.query(DispatchRoute).join(Dispatch).filter(
            DispatchRoute.order_id == order_id
        ).order_by(desc(Dispatch.dispatch_date)).first()
        
        if route:
            dispatch = route.dispatch
            
            timeline.append({
                "timestamp": dispatch.created_at,
                "event_type": "DISPATCH_ASSIGNED",
                "title": "배차 완료",
                "description": f"배차번호: {dispatch.dispatch_number}\n차량: {dispatch.vehicle.vehicle_number if dispatch.vehicle else 'N/A'}",
                "status": "completed"
            })
            
            # 3. 상차 (픽업)
            pickup_route = db.query(DispatchRoute).filter(
                and_(
                    DispatchRoute.dispatch_id == dispatch.id,
                    DispatchRoute.order_id == order_id,
                    DispatchRoute.route_type == RouteType.PICKUP
                )
            ).first()
            
            if pickup_route:
                timeline.append({
                    "timestamp": None,  # 실제 상차 시간은 별도 기록 필요
                    "event_type": "PICKUP_SCHEDULED",
                    "title": "상차 예정",
                    "description": f"위치: {pickup_route.location_name}\n예상시간: {pickup_route.estimated_arrival_time}",
                    "status": "in_progress" if order.status == OrderStatus.IN_TRANSIT else "pending"
                })
            
            # 4. 운송 중
            if order.status in [OrderStatus.IN_TRANSIT, OrderStatus.DELIVERED]:
                timeline.append({
                    "timestamp": None,  # 운송 시작 시간
                    "event_type": "IN_TRANSIT",
                    "title": "운송 중",
                    "description": "고객님의 화물이 배송 중입니다",
                    "status": "completed" if order.status == OrderStatus.DELIVERED else "in_progress"
                })
            
            # 5. 하차 (배송)
            delivery_route = db.query(DispatchRoute).filter(
                and_(
                    DispatchRoute.dispatch_id == dispatch.id,
                    DispatchRoute.order_id == order_id,
                    DispatchRoute.route_type == RouteType.DELIVERY
                )
            ).first()
            
            if delivery_route:
                timeline.append({
                    "timestamp": None,  # 실제 배송 시간
                    "event_type": "DELIVERY_SCHEDULED",
                    "title": "배송 예정" if order.status != OrderStatus.DELIVERED else "배송 완료",
                    "description": f"위치: {delivery_route.location_name}\n예상시간: {delivery_route.estimated_arrival_time}",
                    "status": "completed" if order.status == OrderStatus.DELIVERED else "pending"
                })
        
        # 6. 배송 완료
        if order.status == OrderStatus.DELIVERED:
            timeline.append({
                "timestamp": order.updated_at,
                "event_type": "DELIVERED",
                "title": "배송 완료",
                "description": "화물이 성공적으로 배송되었습니다",
                "status": "completed"
            })
        
        return timeline
    
    @staticmethod
    def get_route_details(db: Session, order_id: int) -> Optional[Dict[str, Any]]:
        """
        배송 경로 상세 정보 조회
        
        Args:
            db: 데이터베이스 세션
            order_id: 주문 ID
            
        Returns:
            Dict: 경로 상세 정보
        """
        route = db.query(DispatchRoute).join(Dispatch).filter(
            DispatchRoute.order_id == order_id
        ).order_by(desc(Dispatch.dispatch_date)).first()
        
        if not route:
            return None
        
        dispatch = route.dispatch
        
        # 전체 경로 조회
        all_routes = db.query(DispatchRoute).filter(
            DispatchRoute.dispatch_id == dispatch.id
        ).order_by(DispatchRoute.sequence).all()
        
        # 경로 정보 구성
        routes = []
        for r in all_routes:
            routes.append({
                "sequence": r.sequence,
                "route_type": r.route_type.value,
                "location_name": r.location_name,
                "address": r.address,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "estimated_arrival": r.estimated_arrival_time,
                "is_current_order": r.order_id == order_id,
                "current_pallets": r.current_pallets,
                "current_weight": r.current_weight_kg
            })
        
        return {
            "dispatch_number": dispatch.dispatch_number,
            "dispatch_date": dispatch.dispatch_date,
            "vehicle": {
                "vehicle_number": dispatch.vehicle.vehicle_number if dispatch.vehicle else None,
                "vehicle_type": dispatch.vehicle.vehicle_type.value if dispatch.vehicle else None,
                "temperature_zone": dispatch.vehicle.temperature_zone.value if dispatch.vehicle else None
            },
            "driver": {
                "name": dispatch.driver.name if dispatch.driver else None,
                "phone": dispatch.driver.phone if dispatch.driver else None
            },
            "routes": routes,
            "total_distance": dispatch.total_distance_km,
            "estimated_duration": dispatch.estimated_duration_minutes
        }
    
    @staticmethod
    def get_estimated_arrival_time(db: Session, order_id: int) -> Optional[datetime]:
        """
        예상 도착 시간 계산
        
        실시간 교통 정보를 활용하여 더 정확한 예상 도착 시간 계산
        
        Args:
            db: 데이터베이스 세션
            order_id: 주문 ID
            
        Returns:
            datetime: 예상 도착 시간
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order or order.status == OrderStatus.DELIVERED:
            return None
        
        # 배차 경로 조회
        delivery_route = db.query(DispatchRoute).join(Dispatch).filter(
            and_(
                DispatchRoute.order_id == order_id,
                DispatchRoute.route_type == RouteType.DELIVERY
            )
        ).order_by(desc(Dispatch.dispatch_date)).first()
        
        if not delivery_route:
            return None
        
        dispatch = delivery_route.dispatch
        
        # 현재 위치 조회
        current_location = db.query(VehicleLocation).filter(
            VehicleLocation.dispatch_id == dispatch.id
        ).order_by(desc(VehicleLocation.recorded_at)).first()
        
        if not current_location:
            # 현재 위치 정보가 없으면 예정 시간 사용
            if delivery_route.estimated_arrival_time:
                today = datetime.now().date()
                arrival_time = datetime.strptime(delivery_route.estimated_arrival_time, "%H:%M").time()
                return datetime.combine(dispatch.dispatch_date, arrival_time)
            return None
        
        # 실시간 교통 정보 서비스 사용
        try:
            from app.services.traffic_service import TrafficService
            traffic_service = TrafficService()
            
            estimate = traffic_service.estimate_arrival_time(
                current_lat=current_location.latitude,
                current_lon=current_location.longitude,
                destination_lat=delivery_route.latitude,
                destination_lon=delivery_route.longitude,
                departure_time=current_location.recorded_at
            )
            
            return datetime.fromisoformat(estimate["estimated_arrival_time"])
            
        except Exception as e:
            logger.warning(f"Failed to use traffic service, falling back to basic calculation: {e}")
            
            # Fallback: 기본 Haversine 계산
            from math import radians, cos, sin, asin, sqrt
            
            def haversine(lon1, lat1, lon2, lat2):
                """두 지점 간 거리 계산 (km)"""
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                r = 6371  # 지구 반지름 (km)
                return c * r
            
            distance = haversine(
                current_location.longitude,
                current_location.latitude,
                delivery_route.longitude,
                delivery_route.latitude
            )
            
            # 평균 속도로 소요 시간 계산 (교통 상황 고려하여 +30% 추가)
            avg_speed = 40  # km/h
            hours = (distance / avg_speed) * 1.3
            
            estimated_time = current_location.recorded_at + timedelta(hours=hours)
            
            return estimated_time
    
    @staticmethod
    def send_notification(
        order_id: int,
        notification_type: str,
        recipient: str,
        channel: str = "SMS"
    ) -> bool:
        """
        알림 전송
        
        Args:
            order_id: 주문 ID
            notification_type: 알림 유형 (ORDER_CONFIRMED, DISPATCH_ASSIGNED, IN_TRANSIT, DELIVERED)
            recipient: 수신자 (전화번호 또는 이메일)
            channel: 전송 채널 (SMS, EMAIL)
            
        Returns:
            bool: 전송 성공 여부
        """
        # 실제 구현에서는 SMS API (알리고, 문자 API 등) 또는 이메일 서비스 연동
        # 여기서는 로그만 기록
        
        messages = {
            "ORDER_CONFIRMED": "주문이 접수되었습니다. 추적번호: {tracking_number}",
            "DISPATCH_ASSIGNED": "배차가 완료되었습니다. 배차번호: {dispatch_number}",
            "IN_TRANSIT": "화물이 출발했습니다. 예상 도착: {estimated_arrival}",
            "DELIVERED": "배송이 완료되었습니다. 감사합니다."
        }
        
        message = messages.get(notification_type, "알림")
        
        # 로그 기록 (실제로는 SMS/Email 전송)
        print(f"[NOTIFICATION] {channel} to {recipient}: {message}")
        
        return True
    
    @staticmethod
    def _calculate_progress(db: Session, dispatch: Dispatch, order_id: int) -> int:
        """
        배송 진행률 계산
        
        Args:
            db: 데이터베이스 세션
            dispatch: 배차 객체
            order_id: 주문 ID
            
        Returns:
            int: 진행률 (0-100)
        """
        # 전체 경로 수
        total_routes = db.query(DispatchRoute).filter(
            DispatchRoute.dispatch_id == dispatch.id
        ).count()
        
        if total_routes == 0:
            return 0
        
        # 현재 주문의 하차 경로 순서
        delivery_route = db.query(DispatchRoute).filter(
            and_(
                DispatchRoute.dispatch_id == dispatch.id,
                DispatchRoute.order_id == order_id,
                DispatchRoute.route_type == RouteType.DELIVERY
            )
        ).first()
        
        if not delivery_route:
            return 0
        
        # 순서 기반 진행률
        progress = int((delivery_route.sequence / total_routes) * 100)
        
        # 배송 완료 시 100%
        order = db.query(Order).filter(Order.id == order_id).first()
        if order and order.status == OrderStatus.DELIVERED:
            progress = 100
        
        return min(progress, 100)
    
    @staticmethod
    def _get_status_description(status: OrderStatus) -> str:
        """상태에 대한 설명 반환"""
        descriptions = {
            OrderStatus.PENDING: "배차 대기 중입니다",
            OrderStatus.ASSIGNED: "배차가 완료되었습니다",
            OrderStatus.IN_TRANSIT: "운송 중입니다",
            OrderStatus.DELIVERED: "배송이 완료되었습니다",
            OrderStatus.CANCELLED: "주문이 취소되었습니다"
        }
        return descriptions.get(status, "상태 정보 없음")
    
    @staticmethod
    def get_public_tracking_info(
        db: Session,
        tracking_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        공개 추적 정보 조회
        
        인증 없이 추적번호만으로 조회 가능한 제한된 정보 제공
        
        Args:
            db: 데이터베이스 세션
            tracking_number: 추적번호
            
        Returns:
            Dict: 공개 추적 정보
        """
        # 추적번호 파싱 (TRK-YYYYMMDD-HASH 형식)
        parts = tracking_number.split("-")
        if len(parts) != 3 or parts[0] != "TRK":
            return None
        
        # 실제로는 추적번호-주문 매핑 테이블에서 조회
        # 여기서는 데모를 위해 첫 번째 주문 사용
        order = db.query(Order).first()
        
        if not order:
            return None
        
        status = DeliveryTrackingService.get_delivery_status(db, order.id)
        timeline = DeliveryTrackingService.get_delivery_timeline(db, order.id)
        estimated_arrival = DeliveryTrackingService.get_estimated_arrival_time(db, order.id)
        
        return {
            "tracking_number": tracking_number,
            "order_number": order.order_number,
            "status": status,
            "timeline": timeline,
            "estimated_arrival": estimated_arrival,
            "pickup_address": order.pickup_address or (order.pickup_client.address if order.pickup_client else None),
            "delivery_address": order.delivery_address or (order.delivery_client.address if order.delivery_client else None),
            "temperature_zone": order.temperature_zone.value,
            "pallet_count": order.pallet_count
        }
