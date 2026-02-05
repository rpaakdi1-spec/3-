"""
IoT 센서 통합 - 데이터 검증기
2026-02-05

센서 데이터의 유효성을 검사합니다.
"""
from typing import Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger

from config import settings, TEMPERATURE_THRESHOLDS
from models import (
    TemperatureSensorData, GPSSensorData,
    DoorSensorData, AlertLevel
)


class SensorDataValidator:
    """센서 데이터 검증기"""
    
    @staticmethod
    def validate_temperature(
        data: TemperatureSensorData,
        vehicle_type: str = "frozen"
    ) -> Tuple[bool, Optional[str], Optional[AlertLevel]]:
        """
        온도 데이터 검증
        
        Args:
            data: 온도 센서 데이터
            vehicle_type: 차량 타입 (frozen/chilled/ambient)
            
        Returns:
            (유효성, 오류 메시지, 알림 레벨)
        """
        try:
            # 1. 기본 범위 체크
            if data.temperature < -50 or data.temperature > 60:
                return False, "온도 값이 센서 범위를 벗어났습니다", AlertLevel.CRITICAL
                
            # 2. 타입별 임계값 체크
            if vehicle_type not in TEMPERATURE_THRESHOLDS:
                logger.warning(f"알 수 없는 차량 타입: {vehicle_type}, 기본값(frozen) 사용")
                vehicle_type = "frozen"
                
            thresholds = TEMPERATURE_THRESHOLDS[vehicle_type]
            temp_min = thresholds["min"]
            temp_max = thresholds["max"]
            tolerance = settings.TEMP_TOLERANCE
            
            temp = data.temperature
            
            # 정상 범위
            if temp_min <= temp <= temp_max:
                return True, None, None
                
            # 경고 범위 (허용 오차 내)
            if (temp_min - tolerance) <= temp < temp_min or temp_max < temp <= (temp_max + tolerance):
                message = (
                    f"온도 경고: {temp}°C "
                    f"(정상 범위: {temp_min}~{temp_max}°C)"
                )
                return True, message, AlertLevel.WARNING
                
            # 위험 범위 (허용 오차 초과)
            message = (
                f"온도 위험: {temp}°C "
                f"(정상 범위: {temp_min}~{temp_max}°C)"
            )
            return True, message, AlertLevel.CRITICAL
            
        except Exception as e:
            logger.error(f"온도 검증 오류: {e}")
            return False, f"검증 오류: {str(e)}", None
            
    @staticmethod
    def validate_gps(data: GPSSensorData) -> Tuple[bool, Optional[str]]:
        """
        GPS 데이터 검증
        
        Args:
            data: GPS 센서 데이터
            
        Returns:
            (유효성, 오류 메시지)
        """
        try:
            # 1. 위도 범위 체크
            if not (-90 <= data.latitude <= 90):
                return False, f"잘못된 위도: {data.latitude}"
                
            # 2. 경도 범위 체크
            if not (-180 <= data.longitude <= 180):
                return False, f"잘못된 경도: {data.longitude}"
                
            # 3. 속도 체크 (최대 150km/h)
            if data.speed and data.speed > 150:
                logger.warning(f"비정상적인 속도: {data.speed}km/h")
                # 경고만 하고 통과
                
            # 4. 정확도 체크 (100m 이하 권장)
            if data.accuracy and data.accuracy > 100:
                logger.warning(f"낮은 GPS 정확도: {data.accuracy}m")
                
            return True, None
            
        except Exception as e:
            logger.error(f"GPS 검증 오류: {e}")
            return False, f"검증 오류: {str(e)}"
            
    @staticmethod
    def validate_door(
        data: DoorSensorData,
        max_open_duration: int = 300
    ) -> Tuple[bool, Optional[str], Optional[AlertLevel]]:
        """
        도어 센서 데이터 검증
        
        Args:
            data: 도어 센서 데이터
            max_open_duration: 최대 허용 열림 시간 (초)
            
        Returns:
            (유효성, 오류 메시지, 알림 레벨)
        """
        try:
            # 도어가 닫혀 있으면 OK
            if not data.is_open:
                return True, None, None
                
            # 도어가 열려 있고 duration이 있는 경우
            if data.duration:
                if data.duration > max_open_duration:
                    message = f"도어 장시간 열림: {data.duration}초 (최대: {max_open_duration}초)"
                    
                    # 10분 이상이면 위험
                    if data.duration > 600:
                        return True, message, AlertLevel.CRITICAL
                    # 5분 이상이면 경고
                    else:
                        return True, message, AlertLevel.WARNING
                        
            return True, None, None
            
        except Exception as e:
            logger.error(f"도어 검증 오류: {e}")
            return False, f"검증 오류: {str(e)}", None
            
    @staticmethod
    def validate_timestamp(
        timestamp: datetime,
        max_delay_seconds: int = 300
    ) -> Tuple[bool, Optional[str]]:
        """
        타임스탬프 검증 (데이터 지연 체크)
        
        Args:
            timestamp: 센서 타임스탬프
            max_delay_seconds: 최대 허용 지연 시간 (초)
            
        Returns:
            (유효성, 오류 메시지)
        """
        try:
            now = datetime.utcnow()
            delay = (now - timestamp).total_seconds()
            
            # 미래 시간 체크
            if delay < 0:
                return False, f"잘못된 타임스탬프: 미래 시간 ({timestamp})"
                
            # 지연 시간 체크
            if delay > max_delay_seconds:
                logger.warning(f"데이터 지연: {delay:.0f}초")
                return True, f"데이터 지연: {delay:.0f}초"
                
            return True, None
            
        except Exception as e:
            logger.error(f"타임스탬프 검증 오류: {e}")
            return False, f"검증 오류: {str(e)}"
            
    @staticmethod
    def validate_battery_level(
        battery_level: Optional[float],
        warning_threshold: float = 20.0,
        critical_threshold: float = 10.0
    ) -> Tuple[bool, Optional[str], Optional[AlertLevel]]:
        """
        배터리 잔량 검증
        
        Args:
            battery_level: 배터리 잔량 (%)
            warning_threshold: 경고 임계값
            critical_threshold: 위험 임계값
            
        Returns:
            (유효성, 오류 메시지, 알림 레벨)
        """
        if battery_level is None:
            return True, None, None
            
        try:
            if battery_level < 0 or battery_level > 100:
                return False, f"잘못된 배터리 잔량: {battery_level}%", None
                
            if battery_level <= critical_threshold:
                return True, f"배터리 위험: {battery_level}%", AlertLevel.CRITICAL
                
            if battery_level <= warning_threshold:
                return True, f"배터리 경고: {battery_level}%", AlertLevel.WARNING
                
            return True, None, None
            
        except Exception as e:
            logger.error(f"배터리 검증 오류: {e}")
            return False, f"검증 오류: {str(e)}", None


# ============================================================================
# 통합 검증 함수
# ============================================================================

def validate_sensor_data(data, vehicle_type: str = "frozen"):
    """
    센서 데이터 통합 검증
    
    Args:
        data: 센서 데이터 (TemperatureSensorData, GPSSensorData, DoorSensorData)
        vehicle_type: 차량 타입
        
    Returns:
        검증 결과 딕셔너리
    """
    validator = SensorDataValidator()
    results = {
        "valid": True,
        "messages": [],
        "alert_level": None
    }
    
    # 타임스탬프 검증
    is_valid, message = validator.validate_timestamp(data.timestamp)
    if not is_valid:
        results["valid"] = False
        results["messages"].append(message)
        return results
    if message:
        results["messages"].append(message)
        
    # 센서 타입별 검증
    if isinstance(data, TemperatureSensorData):
        is_valid, message, alert_level = validator.validate_temperature(data, vehicle_type)
        if not is_valid:
            results["valid"] = False
        if message:
            results["messages"].append(message)
        if alert_level:
            results["alert_level"] = alert_level
            
        # 배터리 검증
        if data.battery_level:
            is_valid, message, alert_level = validator.validate_battery_level(data.battery_level)
            if not is_valid:
                results["valid"] = False
            if message:
                results["messages"].append(message)
            if alert_level and (not results["alert_level"] or alert_level == AlertLevel.CRITICAL):
                results["alert_level"] = alert_level
                
    elif isinstance(data, GPSSensorData):
        is_valid, message = validator.validate_gps(data)
        if not is_valid:
            results["valid"] = False
            results["messages"].append(message)
            
    elif isinstance(data, DoorSensorData):
        is_valid, message, alert_level = validator.validate_door(data)
        if not is_valid:
            results["valid"] = False
        if message:
            results["messages"].append(message)
        if alert_level:
            results["alert_level"] = alert_level
            
    return results
