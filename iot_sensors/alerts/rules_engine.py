"""
IoT 센서 통합 - 알림 규칙 엔진
2026-02-05

센서 데이터를 기반으로 알림을 생성하고 관리합니다.
"""
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from loguru import logger
import asyncio

from config import settings
from models import (
    AlertBase, TemperatureAlert, DoorAlert, SensorOfflineAlert,
    AlertLevel, TemperatureSensorData, DoorSensorData
)


class AlertRulesEngine:
    """알림 규칙 엔진"""
    
    def __init__(self):
        self.alert_history: Dict[str, datetime] = {}  # 알림 쿨다운 관리
        self.sensor_last_seen: Dict[str, datetime] = {}  # 센서 마지막 수신 시간
        
    def should_send_alert(self, sensor_id: str, alert_type: str) -> bool:
        """
        알림 쿨다운 체크
        
        Args:
            sensor_id: 센서 ID
            alert_type: 알림 타입
            
        Returns:
            알림 전송 여부
        """
        key = f"{sensor_id}:{alert_type}"
        
        if key not in self.alert_history:
            return True
            
        last_alert_time = self.alert_history[key]
        cooldown = timedelta(seconds=settings.ALERT_COOLDOWN_SECONDS)
        
        if datetime.utcnow() - last_alert_time > cooldown:
            return True
            
        return False
        
    def mark_alert_sent(self, sensor_id: str, alert_type: str):
        """알림 전송 기록"""
        key = f"{sensor_id}:{alert_type}"
        self.alert_history[key] = datetime.utcnow()
        
    def update_sensor_last_seen(self, sensor_id: str):
        """센서 마지막 수신 시간 업데이트"""
        self.sensor_last_seen[sensor_id] = datetime.utcnow()
        
    async def check_temperature_alert(
        self,
        data: TemperatureSensorData,
        vehicle_type: str = "frozen",
        vehicle_id: Optional[str] = None
    ) -> Optional[TemperatureAlert]:
        """
        온도 알림 체크
        
        Args:
            data: 온도 센서 데이터
            vehicle_type: 차량 타입
            vehicle_id: 차량 ID
            
        Returns:
            온도 알림 객체 (필요시)
        """
        from config import TEMPERATURE_THRESHOLDS
        from processors.validator import SensorDataValidator
        
        # 센서 마지막 수신 시간 업데이트
        self.update_sensor_last_seen(data.sensor_id)
        
        # 온도 검증
        validator = SensorDataValidator()
        is_valid, message, alert_level = validator.validate_temperature(data, vehicle_type)
        
        if not is_valid or not alert_level:
            return None
            
        # 쿨다운 체크
        if not self.should_send_alert(data.sensor_id, "temperature_anomaly"):
            logger.debug(f"온도 알림 쿨다운: {data.sensor_id}")
            return None
            
        # 알림 생성
        thresholds = TEMPERATURE_THRESHOLDS.get(vehicle_type, TEMPERATURE_THRESHOLDS["frozen"])
        
        alert = TemperatureAlert(
            level=alert_level,
            message=message or "온도 이상",
            sensor_id=data.sensor_id,
            vehicle_id=vehicle_id or data.vehicle_id,
            current_temperature=data.temperature,
            threshold_min=thresholds["min"],
            threshold_max=thresholds["max"],
            temperature_category=thresholds["name"]
        )
        
        # 알림 전송 기록
        self.mark_alert_sent(data.sensor_id, "temperature_anomaly")
        
        logger.warning(f"🚨 온도 알림 생성: {alert.message}")
        
        return alert
        
    async def check_door_alert(
        self,
        data: DoorSensorData,
        vehicle_id: Optional[str] = None
    ) -> Optional[DoorAlert]:
        """
        도어 알림 체크
        
        Args:
            data: 도어 센서 데이터
            vehicle_id: 차량 ID
            
        Returns:
            도어 알림 객체 (필요시)
        """
        from processors.validator import SensorDataValidator
        
        # 센서 마지막 수신 시간 업데이트
        self.update_sensor_last_seen(data.sensor_id)
        
        # 도어가 닫혀 있으면 알림 없음
        if not data.is_open:
            return None
            
        # 도어 검증
        validator = SensorDataValidator()
        is_valid, message, alert_level = validator.validate_door(data)
        
        if not is_valid or not alert_level:
            return None
            
        # 쿨다운 체크
        if not self.should_send_alert(data.sensor_id, "door_open"):
            logger.debug(f"도어 알림 쿨다운: {data.sensor_id}")
            return None
            
        # 알림 생성
        alert = DoorAlert(
            level=alert_level,
            message=message or "도어 열림",
            sensor_id=data.sensor_id,
            vehicle_id=vehicle_id or data.vehicle_id,
            duration=data.duration or 0
        )
        
        # 알림 전송 기록
        self.mark_alert_sent(data.sensor_id, "door_open")
        
        logger.warning(f"🚨 도어 알림 생성: {alert.message}")
        
        return alert
        
    async def check_sensor_offline(
        self,
        timeout_seconds: int = 600  # 10분
    ) -> List[SensorOfflineAlert]:
        """
        센서 오프라인 체크 (백그라운드 작업)
        
        Args:
            timeout_seconds: 타임아웃 시간 (초)
            
        Returns:
            오프라인 센서 알림 리스트
        """
        alerts = []
        now = datetime.utcnow()
        timeout = timedelta(seconds=timeout_seconds)
        
        for sensor_id, last_seen in self.sensor_last_seen.items():
            if now - last_seen > timeout:
                # 쿨다운 체크
                if not self.should_send_alert(sensor_id, "sensor_offline"):
                    continue
                    
                alert = SensorOfflineAlert(
                    level=AlertLevel.WARNING,
                    message=f"센서 오프라인: {sensor_id}",
                    sensor_id=sensor_id,
                    last_seen=last_seen
                )
                
                alerts.append(alert)
                
                # 알림 전송 기록
                self.mark_alert_sent(sensor_id, "sensor_offline")
                
                logger.warning(f"🚨 센서 오프라인: {sensor_id} (마지막: {last_seen})")
                
        return alerts
        
    async def start_offline_checker(self, interval_seconds: int = 300):
        """
        센서 오프라인 체크 백그라운드 작업 시작
        
        Args:
            interval_seconds: 체크 주기 (초)
        """
        logger.info(f"센서 오프라인 체크 시작 (주기: {interval_seconds}초)")
        
        while True:
            try:
                await asyncio.sleep(interval_seconds)
                alerts = await self.check_sensor_offline()
                
                if alerts:
                    logger.info(f"오프라인 센서 {len(alerts)}개 발견")
                    # TODO: 알림 전송
                    
            except asyncio.CancelledError:
                logger.info("센서 오프라인 체크 중단")
                break
            except Exception as e:
                logger.error(f"센서 오프라인 체크 오류: {e}")


# ============================================================================
# 전역 인스턴스
# ============================================================================

alert_engine = AlertRulesEngine()
