"""
UVIS API Tracking Service
Samsung UVIS API 연동 서비스
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List
import httpx
from loguru import logger

from ..core.config import get_settings
from ..models import VehicleLocation, TemperatureAlert, Vehicle, Dispatch
from ..schemas.vehicle_location import VehicleLocationCreate, TemperatureAlertCreate
from sqlalchemy.orm import Session


settings = get_settings()


class UVISTrackingService:
    """Samsung UVIS API 연동 서비스"""
    
    def __init__(self):
        self.base_url = settings.UVIS_API_BASE_URL
        self.api_key = settings.UVIS_API_KEY
        self.api_secret = settings.UVIS_API_SECRET
        self.timeout = 30.0
        
    async def get_vehicle_location(
        self, 
        uvis_device_id: str
    ) -> Optional[Dict]:
        """
        UVIS API에서 차량 실시간 위치 조회
        
        Args:
            uvis_device_id: UVIS 단말기 ID
            
        Returns:
            Dict: 위치 정보 (latitude, longitude, speed, heading, temperature, timestamp 등)
            None: 조회 실패 시
        """
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "X-API-SECRET": self.api_secret,
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/api/v1/vehicles/{uvis_device_id}/location"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"UVIS API 오류: status={response.status_code}, device={uvis_device_id}")
                    return None
                    
                data = response.json()
                
                if data.get("status") != "success":
                    logger.error(f"UVIS API 응답 오류: {data.get('message')}, device={uvis_device_id}")
                    return None
                
                location_data = data.get("data", {})
                logger.info(f"UVIS 위치 조회 성공: device={uvis_device_id}, lat={location_data.get('latitude')}, lon={location_data.get('longitude')}")
                
                return location_data
                
        except httpx.TimeoutException:
            logger.error(f"UVIS API 타임아웃: device={uvis_device_id}")
            return None
        except Exception as e:
            logger.error(f"UVIS 위치 조회 실패: device={uvis_device_id}, error={str(e)}")
            return None
    
    async def get_vehicle_temperature(
        self, 
        uvis_device_id: str
    ) -> Optional[Dict]:
        """
        UVIS API에서 차량 온도 정보 조회
        
        Args:
            uvis_device_id: UVIS 단말기 ID
            
        Returns:
            Dict: 온도 정보 (temperature, humidity, sensor_status, timestamp 등)
            None: 조회 실패 시
        """
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "X-API-SECRET": self.api_secret,
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/api/v1/vehicles/{uvis_device_id}/temperature"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"UVIS 온도 API 오류: status={response.status_code}, device={uvis_device_id}")
                    return None
                    
                data = response.json()
                
                if data.get("status") != "success":
                    logger.error(f"UVIS 온도 API 응답 오류: {data.get('message')}, device={uvis_device_id}")
                    return None
                
                temp_data = data.get("data", {})
                logger.info(f"UVIS 온도 조회 성공: device={uvis_device_id}, temp={temp_data.get('temperature')}°C")
                
                return temp_data
                
        except httpx.TimeoutException:
            logger.error(f"UVIS 온도 API 타임아웃: device={uvis_device_id}")
            return None
        except Exception as e:
            logger.error(f"UVIS 온도 조회 실패: device={uvis_device_id}, error={str(e)}")
            return None
    
    async def get_vehicle_full_status(
        self, 
        uvis_device_id: str
    ) -> Optional[Dict]:
        """
        UVIS API에서 차량 전체 상태 조회 (위치 + 온도 + 기타)
        
        Args:
            uvis_device_id: UVIS 단말기 ID
            
        Returns:
            Dict: 전체 상태 정보
            None: 조회 실패 시
        """
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "X-API-SECRET": self.api_secret,
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/api/v1/vehicles/{uvis_device_id}/status"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"UVIS 상태 API 오류: status={response.status_code}, device={uvis_device_id}")
                    return None
                    
                data = response.json()
                
                if data.get("status") != "success":
                    logger.error(f"UVIS 상태 API 응답 오류: {data.get('message')}, device={uvis_device_id}")
                    return None
                
                status_data = data.get("data", {})
                logger.info(f"UVIS 상태 조회 성공: device={uvis_device_id}")
                
                return status_data
                
        except httpx.TimeoutException:
            logger.error(f"UVIS 상태 API 타임아웃: device={uvis_device_id}")
            return None
        except Exception as e:
            logger.error(f"UVIS 상태 조회 실패: device={uvis_device_id}, error={str(e)}")
            return None
    
    async def batch_get_vehicles_status(
        self, 
        uvis_device_ids: List[str]
    ) -> Dict[str, Dict]:
        """
        여러 차량의 상태를 배치로 조회
        
        Args:
            uvis_device_ids: UVIS 단말기 ID 목록
            
        Returns:
            Dict[device_id, status_data]: 차량별 상태 정보
        """
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "X-API-SECRET": self.api_secret,
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/api/v1/vehicles/batch-status"
            payload = {
                "device_ids": uvis_device_ids
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    logger.error(f"UVIS 배치 API 오류: status={response.status_code}")
                    return {}
                    
                data = response.json()
                
                if data.get("status") != "success":
                    logger.error(f"UVIS 배치 API 응답 오류: {data.get('message')}")
                    return {}
                
                results = data.get("data", {})
                logger.info(f"UVIS 배치 조회 성공: {len(results)}대 차량")
                
                return results
                
        except httpx.TimeoutException:
            logger.error("UVIS 배치 API 타임아웃")
            return {}
        except Exception as e:
            logger.error(f"UVIS 배치 조회 실패: error={str(e)}")
            return {}
    
    def save_vehicle_location(
        self,
        db: Session,
        vehicle_id: int,
        location_data: Dict,
        dispatch_id: Optional[int] = None
    ) -> VehicleLocation:
        """
        UVIS 위치 데이터를 DB에 저장
        
        Args:
            db: DB 세션
            vehicle_id: 차량 ID
            location_data: UVIS API에서 받은 위치 데이터
            dispatch_id: 배차 ID (선택)
            
        Returns:
            VehicleLocation: 저장된 위치 레코드
        """
        try:
            # UVIS 타임스탬프 파싱
            uvis_timestamp = None
            if location_data.get("timestamp"):
                uvis_timestamp = datetime.fromisoformat(location_data["timestamp"].replace("Z", "+00:00"))
            
            location = VehicleLocation(
                vehicle_id=vehicle_id,
                dispatch_id=dispatch_id,
                latitude=location_data.get("latitude", 0.0),
                longitude=location_data.get("longitude", 0.0),
                accuracy=location_data.get("accuracy"),
                altitude=location_data.get("altitude"),
                speed=location_data.get("speed"),
                heading=location_data.get("heading"),
                temperature_celsius=location_data.get("temperature"),
                humidity_percent=location_data.get("humidity"),
                uvis_device_id=location_data.get("device_id"),
                uvis_timestamp=uvis_timestamp,
                is_ignition_on=location_data.get("ignition_on", True),
                battery_voltage=location_data.get("battery_voltage"),
                fuel_level_percent=location_data.get("fuel_level"),
                odometer_km=location_data.get("odometer"),
                recorded_at=datetime.utcnow()
            )
            
            db.add(location)
            db.commit()
            db.refresh(location)
            
            logger.info(f"차량 위치 저장 완료: vehicle_id={vehicle_id}, location_id={location.id}")
            return location
            
        except Exception as e:
            db.rollback()
            logger.error(f"차량 위치 저장 실패: vehicle_id={vehicle_id}, error={str(e)}")
            raise
    
    def check_temperature_alert(
        self,
        db: Session,
        vehicle_id: int,
        temperature: float,
        vehicle_type: str,
        dispatch_id: Optional[int] = None,
        location_id: Optional[int] = None
    ) -> Optional[TemperatureAlert]:
        """
        온도 임계값 체크 및 알림 생성
        
        Args:
            db: DB 세션
            vehicle_id: 차량 ID
            temperature: 현재 온도
            vehicle_type: 차량 온도대 (냉동/냉장/상온)
            dispatch_id: 배차 ID (선택)
            location_id: 위치 ID (선택)
            
        Returns:
            TemperatureAlert: 생성된 알림 (임계값 초과 시) 또는 None
        """
        # 온도대별 임계값 설정
        thresholds = {
            "냉동": {"min": -25.0, "max": -18.0},
            "냉장": {"min": 0.0, "max": 6.0},
            "상온": {"min": 10.0, "max": 30.0},
        }
        
        threshold = thresholds.get(vehicle_type)
        if not threshold:
            return None
        
        threshold_min = threshold["min"]
        threshold_max = threshold["max"]
        
        # 임계값 체크
        alert_type = None
        severity = None
        
        if temperature < threshold_min - 5.0:  # 너무 낮음 (위험)
            alert_type = "TOO_COLD"
            severity = "CRITICAL"
        elif temperature < threshold_min:  # 낮음 (경고)
            alert_type = "TOO_COLD"
            severity = "WARNING"
        elif temperature > threshold_max + 5.0:  # 너무 높음 (위험)
            alert_type = "TOO_HOT"
            severity = "CRITICAL"
        elif temperature > threshold_max:  # 높음 (경고)
            alert_type = "TOO_HOT"
            severity = "WARNING"
        
        if not alert_type:
            return None  # 정상 범위
        
        try:
            # 최근 같은 유형 알림이 있는지 확인 (중복 방지)
            recent_alert = db.query(TemperatureAlert).filter(
                TemperatureAlert.vehicle_id == vehicle_id,
                TemperatureAlert.alert_type == alert_type,
                TemperatureAlert.is_resolved == False,
                TemperatureAlert.detected_at >= datetime.utcnow() - timedelta(minutes=30)
            ).first()
            
            if recent_alert:
                logger.info(f"최근 알림 존재: vehicle_id={vehicle_id}, alert_type={alert_type}")
                return recent_alert
            
            # 새 알림 생성
            message = f"{vehicle_type} 차량 온도 {alert_type.replace('TOO_', '').lower()}: {temperature:.1f}°C (허용 범위: {threshold_min}~{threshold_max}°C)"
            
            alert = TemperatureAlert(
                vehicle_id=vehicle_id,
                dispatch_id=dispatch_id,
                location_id=location_id,
                alert_type=alert_type,
                severity=severity,
                temperature_celsius=temperature,
                threshold_min=threshold_min,
                threshold_max=threshold_max,
                message=message,
                detected_at=datetime.utcnow()
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            logger.warning(f"온도 알림 생성: vehicle_id={vehicle_id}, type={alert_type}, severity={severity}, temp={temperature}°C")
            return alert
            
        except Exception as e:
            db.rollback()
            logger.error(f"온도 알림 생성 실패: vehicle_id={vehicle_id}, error={str(e)}")
            return None
