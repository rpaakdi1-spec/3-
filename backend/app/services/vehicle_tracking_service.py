"""
Phase 12: 실시간 차량 위치 브로드캐스트 서비스
WebSocket을 통해 차량 위치 실시간 업데이트
"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.uvis_gps_service import UvisGPSService
from app.websocket.connection_manager import manager
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


class VehicleTrackingService:
    """
    실시간 차량 추적 서비스
    
    기능:
    - 주기적으로 모든 차량 위치 조회
    - WebSocket을 통해 클라이언트에 브로드캐스트
    - 위치 변경 감지 및 알림
    """
    
    def __init__(self):
        self.is_running = False
        self.update_interval = 30  # 30초마다 업데이트
        self.task: Optional[asyncio.Task] = None
        self.last_positions: Dict[int, tuple] = {}  # vehicle_id -> (lat, lng)
    
    async def start(self):
        """추적 서비스 시작"""
        if self.is_running:
            logger.warning("Vehicle tracking service already running")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._tracking_loop())
        logger.info("✅ Vehicle tracking service started")
    
    async def stop(self):
        """추적 서비스 중지"""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Vehicle tracking service stopped")
    
    async def _tracking_loop(self):
        """추적 루프 (주기적으로 위치 업데이트)"""
        while self.is_running:
            try:
                await self._update_vehicle_positions()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in tracking loop: {e}")
                await asyncio.sleep(self.update_interval)
    
    async def _update_vehicle_positions(self):
        """모든 차량 위치 업데이트 및 브로드캐스트"""
        db = SessionLocal()
        try:
            from app.models.vehicle import Vehicle
            from app.models.driver import Driver
            
            # 활성 차량 조회
            vehicles = db.query(Vehicle).filter(
                Vehicle.is_active == True
            ).all()
            
            if not vehicles:
                return
            
            gps_service = UvisGPSService(db)
            updates = []
            
            for vehicle in vehicles:
                try:
                    # GPS 위치 조회
                    location = await gps_service.get_vehicle_location(vehicle.id)
                    
                    if not location:
                        # 마지막 알려진 위치 사용
                        if vehicle.last_known_latitude and vehicle.last_known_longitude:
                            location = (vehicle.last_known_latitude, vehicle.last_known_longitude)
                        else:
                            continue
                    
                    # 위치 변경 감지
                    last_pos = self.last_positions.get(vehicle.id)
                    position_changed = (
                        not last_pos or
                        abs(last_pos[0] - location[0]) > 0.0001 or  # ~11m
                        abs(last_pos[1] - location[1]) > 0.0001
                    )
                    
                    if position_changed:
                        # 위치 저장
                        self.last_positions[vehicle.id] = location
                        
                        # 기사 정보
                        driver = db.query(Driver).filter(Driver.id == vehicle.driver_id).first()
                        
                        # 업데이트 데이터
                        update_data = {
                            "type": "vehicle_location_update",
                            "vehicle_id": vehicle.id,
                            "license_plate": vehicle.license_plate,
                            "driver_name": driver.name if driver else None,
                            "driver_phone": driver.phone if driver else None,
                            "latitude": location[0],
                            "longitude": location[1],
                            "status": vehicle.status,
                            "vehicle_type": vehicle.vehicle_type,
                            "temperature_type": vehicle.temperature_type,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        updates.append(update_data)
                
                except Exception as e:
                    logger.error(f"Error updating vehicle {vehicle.id}: {e}")
                    continue
            
            # WebSocket 브로드캐스트
            if updates:
                await manager.broadcast({
                    "type": "vehicle_positions",
                    "vehicles": updates,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                logger.info(f"📡 Broadcasted {len(updates)} vehicle position updates")
        
        finally:
            db.close()
    
    async def broadcast_dispatch_update(self, dispatch_data: Dict):
        """
        배차 완료 알림 브로드캐스트
        
        Args:
            dispatch_data: 배차 정보
        """
        await manager.broadcast({
            "type": "dispatch_update",
            "data": dispatch_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"📢 Broadcasted dispatch update: {dispatch_data.get('dispatch_id')}")


# 싱글톤 인스턴스
vehicle_tracking_service = VehicleTrackingService()
