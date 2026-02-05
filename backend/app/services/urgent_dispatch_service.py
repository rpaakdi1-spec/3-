"""
Urgent Dispatch Service
긴급 배차 서비스 - 긴급 주문 자동 배정
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List, Dict
from datetime import date, datetime
from loguru import logger

from app.models.order import Order, OrderStatus
from app.models.dispatch import Dispatch, DispatchStatus
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.driver_schedule import DriverSchedule, ScheduleType
from app.services.naver_map_service import NaverMapService
import math


class UrgentDispatchService:
    """긴급 배차 서비스"""
    
    @staticmethod
    def find_nearest_available_vehicle(
        db: Session,
        order: Order,
        target_date: date,
        max_distance_km: float = 50.0
    ) -> Optional[Dict]:
        """가장 가까운 가용 차량 찾기
        
        Args:
            db: 데이터베이스 세션
            order: 긴급 주문
            target_date: 배차 날짜
            max_distance_km: 최대 거리 (km)
            
        Returns:
            {
                'vehicle': Vehicle,
                'driver': Driver,
                'distance_km': float,
                'reason': str
            }
        """
        # 1. 해당 날짜에 배차되지 않은 차량 조회
        already_dispatched = (
            db.query(Dispatch.vehicle_id)
            .filter(
                Dispatch.dispatch_date == target_date,
                Dispatch.status.in_([DispatchStatus.CONFIRMED, DispatchStatus.IN_PROGRESS])
            )
            .all()
        )
        dispatched_vehicle_ids = [v[0] for v in already_dispatched]
        
        # 2. 가용 차량 조회 (온도대 일치, 용량 충분)
        available_vehicles = (
            db.query(Vehicle)
            .filter(
                Vehicle.is_active == True,
                Vehicle.id.notin_(dispatched_vehicle_ids),
                Vehicle.status == "AVAILABLE"
            )
            .all()
        )
        
        if not available_vehicles:
            logger.warning("No available vehicles found")
            return None
        
        # 3. 온도대 필터링
        temp_zone = order.temperature_zone
        compatible_vehicles = []
        
        for vehicle in available_vehicles:
            # 냉동 주문
            if temp_zone == "FROZEN":
                if vehicle.vehicle_type in ["FROZEN", "BOTH"]:
                    compatible_vehicles.append(vehicle)
            # 냉장 주문
            elif temp_zone == "REFRIGERATED":
                if vehicle.vehicle_type in ["REFRIGERATED", "BOTH"]:
                    compatible_vehicles.append(vehicle)
            # 상온 주문 (모든 차량 가능)
            else:
                compatible_vehicles.append(vehicle)
        
        if not compatible_vehicles:
            logger.warning(f"No compatible vehicles for temperature zone: {temp_zone}")
            return None
        
        # 4. 거리 계산 (상차지 기준)
        if not order.pickup_latitude or not order.pickup_longitude:
            # 좌표가 없으면 첫 번째 차량 반환
            logger.warning("Order has no pickup coordinates, returning first vehicle")
            return {
                'vehicle': compatible_vehicles[0],
                'driver': None,
                'distance_km': 0,
                'reason': '좌표 정보 없음 - 첫 번째 가용 차량'
            }
        
        nearest_vehicle = None
        min_distance = float('inf')
        
        for vehicle in compatible_vehicles:
            if vehicle.current_location_lat and vehicle.current_location_lon:
                # 거리 계산 (하버사인 공식)
                distance = UrgentDispatchService._calculate_distance(
                    vehicle.current_location_lat,
                    vehicle.current_location_lon,
                    order.pickup_latitude,
                    order.pickup_longitude
                )
                
                if distance < min_distance and distance <= max_distance_km:
                    min_distance = distance
                    nearest_vehicle = vehicle
        
        if not nearest_vehicle:
            # 거리 조건을 만족하는 차량이 없으면 첫 번째 차량 반환
            logger.warning(f"No vehicle within {max_distance_km}km, returning first")
            nearest_vehicle = compatible_vehicles[0]
            min_distance = 0
        
        # 5. 해당 날짜에 근무 가능한 기사 찾기
        available_driver = UrgentDispatchService._find_available_driver(
            db, target_date
        )
        
        return {
            'vehicle': nearest_vehicle,
            'driver': available_driver,
            'distance_km': min_distance,
            'reason': f'{min_distance:.1f}km 거리의 가장 가까운 차량'
        }
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """두 좌표 간 거리 계산 (하버사인 공식)
        
        Returns:
            거리 (km)
        """
        R = 6371  # 지구 반지름 (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def _find_available_driver(db: Session, target_date: date) -> Optional[Driver]:
        """해당 날짜에 근무 가능한 기사 찾기"""
        # 1. 해당 날짜 근무 일정이 있는 기사
        working_schedules = (
            db.query(DriverSchedule)
            .filter(
                DriverSchedule.schedule_date == target_date,
                DriverSchedule.schedule_type == ScheduleType.WORK,
                DriverSchedule.is_available == True
            )
            .all()
        )
        
        if working_schedules:
            driver_id = working_schedules[0].driver_id
            return db.query(Driver).filter(Driver.id == driver_id).first()
        
        # 2. 일정이 없는 활성 기사 중 첫 번째
        driver = db.query(Driver).filter(Driver.is_active == True).first()
        return driver
    
    @staticmethod
    def create_urgent_dispatch(
        db: Session,
        order: Order,
        vehicle_id: int,
        driver_id: Optional[int],
        urgency_level: int = 5,
        urgent_reason: str = "긴급 배차"
    ) -> Dispatch:
        """긴급 배차 생성
        
        Args:
            db: 데이터베이스 세션
            order: 주문
            vehicle_id: 차량 ID
            driver_id: 기사 ID (Optional)
            urgency_level: 긴급도 (1-5)
            urgent_reason: 긴급 사유
            
        Returns:
            생성된 Dispatch
        """
        # 배차번호 생성
        timestamp = int(datetime.now().timestamp() * 1000)
        dispatch_number = f"URGENT-{timestamp}"
        
        # 배차 생성
        dispatch = Dispatch(
            dispatch_number=dispatch_number,
            dispatch_date=order.order_date,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            total_orders=1,
            total_pallets=order.pallet_count,
            total_weight_kg=order.weight_kg or 0,
            status=DispatchStatus.CONFIRMED,  # 긴급은 즉시 확정
            is_urgent=True,
            urgency_level=urgency_level,
            urgent_reason=urgent_reason,
            notes=f"긴급 배차 - {urgent_reason}"
        )
        
        db.add(dispatch)
        
        # 주문 상태 업데이트
        order.status = OrderStatus.ASSIGNED
        
        db.commit()
        db.refresh(dispatch)
        
        logger.info(
            f"Created urgent dispatch: {dispatch_number}, "
            f"Order: {order.order_number}, Vehicle: {vehicle_id}, Urgency: {urgency_level}"
        )
        
        return dispatch
    
    @staticmethod
    def auto_assign_urgent_order(
        db: Session,
        order: Order,
        urgency_level: int = 5,
        urgent_reason: str = "긴급 주문"
    ) -> Dict:
        """긴급 주문 자동 배정
        
        가장 가까운 가용 차량을 찾아 자동으로 배차를 생성합니다.
        
        Returns:
            {
                'success': bool,
                'dispatch': Dispatch or None,
                'message': str
            }
        """
        try:
            # 1. 가장 가까운 차량 찾기
            result = UrgentDispatchService.find_nearest_available_vehicle(
                db, order, order.order_date
            )
            
            if not result:
                return {
                    'success': False,
                    'dispatch': None,
                    'message': '가용 차량을 찾을 수 없습니다'
                }
            
            # 2. 긴급 배차 생성
            dispatch = UrgentDispatchService.create_urgent_dispatch(
                db,
                order,
                result['vehicle'].id,
                result['driver'].id if result['driver'] else None,
                urgency_level,
                urgent_reason
            )
            
            return {
                'success': True,
                'dispatch': dispatch,
                'message': f"긴급 배차 완료 - {result['reason']}",
                'vehicle_name': result['vehicle'].license_plate,
                'driver_name': result['driver'].name if result['driver'] else '미배정',
                'distance_km': result['distance_km']
            }
            
        except Exception as e:
            logger.error(f"Error in auto_assign_urgent_order: {e}")
            db.rollback()
            return {
                'success': False,
                'dispatch': None,
                'message': f'긴급 배차 생성 실패: {str(e)}'
            }
