"""
Real-time Vehicle Telemetry Service
Phase 4 Week 3-4: 실시간 차량 텔레메트리 모니터링

실시간으로 차량의 GPS 위치, 온도, 속도, 연료 등을 모니터링하고
이상 상황을 감지하여 즉각 알림을 전송합니다.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.vehicle import Vehicle
from app.models.dispatch import Dispatch
from app.models.vehicle_location import VehicleLocation
from app.models.temperature_alert import TemperatureAlert
from app.services.notification_service import NotificationService


class TelemetryData:
    """텔레메트리 데이터 모델"""
    
    def __init__(
        self,
        vehicle_id: int,
        latitude: float,
        longitude: float,
        speed: float = 0.0,
        temperature: Optional[float] = None,
        fuel_level: Optional[float] = None,
        engine_status: str = "ON",
        timestamp: Optional[datetime] = None
    ):
        self.vehicle_id = vehicle_id
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed
        self.temperature = temperature
        self.fuel_level = fuel_level
        self.engine_status = engine_status
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "vehicle_id": self.vehicle_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "speed": self.speed,
            "temperature": self.temperature,
            "fuel_level": self.fuel_level,
            "engine_status": self.engine_status,
            "timestamp": self.timestamp.isoformat()
        }


class AnomalyType:
    """이상 유형"""
    SPEEDING = "speeding"                    # 과속
    HARSH_BRAKING = "harsh_braking"          # 급정거
    HARSH_ACCELERATION = "harsh_acceleration"  # 급가속
    ROUTE_DEVIATION = "route_deviation"      # 경로 이탈
    TEMPERATURE_VIOLATION = "temperature_violation"  # 온도 이상
    LONG_IDLE = "long_idle"                  # 장시간 정차
    LOW_FUEL = "low_fuel"                    # 연료 부족
    ETA_DELAY = "eta_delay"                  # 예상 도착 시간 지연


class VehicleTelemetryService:
    """실시간 차량 텔레메트리 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        
        # 이상 감지 임계값
        self.SPEED_LIMIT = 110  # km/h
        self.HARSH_BRAKING_THRESHOLD = -8  # m/s²
        self.HARSH_ACCELERATION_THRESHOLD = 5  # m/s²
        self.ROUTE_DEVIATION_THRESHOLD = 500  # meters
        self.IDLE_TIME_THRESHOLD = 30  # minutes
        self.LOW_FUEL_THRESHOLD = 15  # %
        self.ETA_DELAY_THRESHOLD = 30  # minutes
        
        # 차량별 이전 데이터 캐시 (이상 감지용)
        self.previous_data: Dict[int, TelemetryData] = {}
    
    def process_telemetry(self, data: TelemetryData) -> Dict[str, Any]:
        """
        텔레메트리 데이터 처리
        
        1. 데이터베이스 저장
        2. 이상 감지
        3. 알림 전송
        4. 실시간 브로드캐스트
        """
        vehicle_id = data.vehicle_id
        
        # 1. 위치 데이터 저장
        self._save_location(data)
        
        # 2. 이상 감지
        anomalies = self._detect_anomalies(data)
        
        # 3. 이상 발견 시 알림 전송
        if anomalies:
            self._send_anomaly_alerts(data, anomalies)
        
        # 4. 이전 데이터 캐시 업데이트
        self.previous_data[vehicle_id] = data
        
        # 5. 응답 데이터
        return {
            "vehicle_id": vehicle_id,
            "received_at": datetime.now().isoformat(),
            "saved": True,
            "anomalies": anomalies,
            "status": "warning" if anomalies else "normal"
        }
    
    def _save_location(self, data: TelemetryData):
        """위치 데이터 저장"""
        try:
            location = VehicleLocation(
                vehicle_id=data.vehicle_id,
                latitude=data.latitude,
                longitude=data.longitude,
                speed=data.speed,
                timestamp=data.timestamp
            )
            self.db.add(location)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to save location for vehicle {data.vehicle_id}: {e}")
            self.db.rollback()
    
    def _detect_anomalies(self, data: TelemetryData) -> List[Dict]:
        """이상 감지"""
        anomalies = []
        
        # 1. 과속 감지
        if data.speed > self.SPEED_LIMIT:
            anomalies.append({
                "type": AnomalyType.SPEEDING,
                "severity": "high",
                "message": f"과속 감지: {data.speed:.1f} km/h (제한: {self.SPEED_LIMIT} km/h)",
                "value": data.speed,
                "threshold": self.SPEED_LIMIT
            })
        
        # 2. 급정거/급가속 감지 (이전 데이터와 비교)
        if data.vehicle_id in self.previous_data:
            prev = self.previous_data[data.vehicle_id]
            time_diff = (data.timestamp - prev.timestamp).total_seconds()
            
            if time_diff > 0 and time_diff < 10:  # 10초 이내
                speed_change = data.speed - prev.speed  # km/h
                acceleration = speed_change / time_diff  # km/h/s → m/s²로 변환
                acceleration_ms2 = acceleration * 1000 / 3600
                
                # 급정거
                if acceleration_ms2 < self.HARSH_BRAKING_THRESHOLD:
                    anomalies.append({
                        "type": AnomalyType.HARSH_BRAKING,
                        "severity": "medium",
                        "message": f"급정거 감지: {acceleration_ms2:.2f} m/s²",
                        "value": acceleration_ms2,
                        "threshold": self.HARSH_BRAKING_THRESHOLD
                    })
                
                # 급가속
                elif acceleration_ms2 > self.HARSH_ACCELERATION_THRESHOLD:
                    anomalies.append({
                        "type": AnomalyType.HARSH_ACCELERATION,
                        "severity": "medium",
                        "message": f"급가속 감지: {acceleration_ms2:.2f} m/s²",
                        "value": acceleration_ms2,
                        "threshold": self.HARSH_ACCELERATION_THRESHOLD
                    })
        
        # 3. 온도 이상 감지
        if data.temperature is not None:
            vehicle = self.db.query(Vehicle).filter(Vehicle.id == data.vehicle_id).first()
            if vehicle:
                if vehicle.min_temp_celsius is not None and data.temperature < vehicle.min_temp_celsius:
                    anomalies.append({
                        "type": AnomalyType.TEMPERATURE_VIOLATION,
                        "severity": "critical",
                        "message": f"온도 하한 이탈: {data.temperature:.1f}°C (최소: {vehicle.min_temp_celsius}°C)",
                        "value": data.temperature,
                        "threshold": vehicle.min_temp_celsius
                    })
                
                if vehicle.max_temp_celsius is not None and data.temperature > vehicle.max_temp_celsius:
                    anomalies.append({
                        "type": AnomalyType.TEMPERATURE_VIOLATION,
                        "severity": "critical",
                        "message": f"온도 상한 이탈: {data.temperature:.1f}°C (최대: {vehicle.max_temp_celsius}°C)",
                        "value": data.temperature,
                        "threshold": vehicle.max_temp_celsius
                    })
        
        # 4. 연료 부족 감지
        if data.fuel_level is not None and data.fuel_level < self.LOW_FUEL_THRESHOLD:
            anomalies.append({
                "type": AnomalyType.LOW_FUEL,
                "severity": "medium",
                "message": f"연료 부족: {data.fuel_level:.1f}% (최소: {self.LOW_FUEL_THRESHOLD}%)",
                "value": data.fuel_level,
                "threshold": self.LOW_FUEL_THRESHOLD
            })
        
        # 5. 장시간 정차 감지
        if data.speed < 1.0:  # 거의 정차
            if data.vehicle_id in self.previous_data:
                prev = self.previous_data[data.vehicle_id]
                if prev.speed < 1.0:  # 이전에도 정차
                    idle_time = (data.timestamp - prev.timestamp).total_seconds() / 60  # minutes
                    if idle_time > self.IDLE_TIME_THRESHOLD:
                        anomalies.append({
                            "type": AnomalyType.LONG_IDLE,
                            "severity": "low",
                            "message": f"장시간 정차: {idle_time:.0f}분",
                            "value": idle_time,
                            "threshold": self.IDLE_TIME_THRESHOLD
                        })
        
        return anomalies
    
    def _send_anomaly_alerts(self, data: TelemetryData, anomalies: List[Dict]):
        """이상 알림 전송"""
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == data.vehicle_id).first()
        if not vehicle:
            return
        
        for anomaly in anomalies:
            severity = anomaly["severity"]
            message = anomaly["message"]
            
            # 심각도에 따른 알림 채널 결정
            if severity == "critical":
                channels = ["SMS", "PUSH", "EMAIL"]
            elif severity == "high":
                channels = ["SMS", "PUSH"]
            elif severity == "medium":
                channels = ["PUSH"]
            else:
                channels = ["PUSH"]
            
            # 알림 전송
            try:
                self.notification_service.send_notification(
                    title=f"🚨 {vehicle.plate_number} 이상 감지",
                    message=message,
                    notification_type=anomaly["type"],
                    channels=channels,
                    priority="HIGH" if severity in ["critical", "high"] else "MEDIUM",
                    data={
                        "vehicle_id": data.vehicle_id,
                        "vehicle_plate": vehicle.plate_number,
                        "anomaly_type": anomaly["type"],
                        "severity": severity,
                        "latitude": data.latitude,
                        "longitude": data.longitude,
                        "timestamp": data.timestamp.isoformat()
                    }
                )
                logger.info(f"✅ Anomaly alert sent: {vehicle.plate_number} - {anomaly['type']}")
            except Exception as e:
                logger.error(f"Failed to send anomaly alert: {e}")
    
    def get_vehicle_telemetry(self, vehicle_id: int, minutes: int = 60) -> Dict:
        """
        차량 텔레메트리 히스토리 조회
        
        Args:
            vehicle_id: 차량 ID
            minutes: 조회 기간 (분)
        """
        since = datetime.now() - timedelta(minutes=minutes)
        
        # 위치 데이터
        locations = self.db.query(VehicleLocation).filter(
            and_(
                VehicleLocation.vehicle_id == vehicle_id,
                VehicleLocation.timestamp >= since
            )
        ).order_by(VehicleLocation.timestamp).all()
        
        # 온도 알림
        temp_alerts = self.db.query(TemperatureAlert).filter(
            and_(
                TemperatureAlert.vehicle_id == vehicle_id,
                TemperatureAlert.created_at >= since
            )
        ).order_by(desc(TemperatureAlert.created_at)).all()
        
        # 최신 데이터
        latest_location = locations[-1] if locations else None
        
        return {
            "vehicle_id": vehicle_id,
            "period_minutes": minutes,
            "data_points": len(locations),
            "latest": {
                "latitude": latest_location.latitude if latest_location else None,
                "longitude": latest_location.longitude if latest_location else None,
                "speed": latest_location.speed if latest_location else None,
                "timestamp": latest_location.timestamp.isoformat() if latest_location else None
            } if latest_location else None,
            "locations": [
                {
                    "latitude": loc.latitude,
                    "longitude": loc.longitude,
                    "speed": loc.speed,
                    "timestamp": loc.timestamp.isoformat()
                }
                for loc in locations
            ],
            "temperature_alerts": [
                {
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "temperature": alert.temperature,
                    "threshold_min": alert.threshold_min,
                    "threshold_max": alert.threshold_max,
                    "message": alert.message,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in temp_alerts
            ]
        }
    
    def get_all_vehicles_status(self) -> List[Dict]:
        """전체 차량 실시간 상태 조회"""
        vehicles = self.db.query(Vehicle).filter(Vehicle.is_active == True).all()
        
        result = []
        for vehicle in vehicles:
            # 최근 위치 (5분 이내)
            recent_location = self.db.query(VehicleLocation).filter(
                and_(
                    VehicleLocation.vehicle_id == vehicle.id,
                    VehicleLocation.timestamp >= datetime.now() - timedelta(minutes=5)
                )
            ).order_by(desc(VehicleLocation.timestamp)).first()
            
            # 활성 배차
            active_dispatch = self.db.query(Dispatch).filter(
                and_(
                    Dispatch.vehicle_id == vehicle.id,
                    Dispatch.status.in_(['ASSIGNED', 'IN_PROGRESS'])
                )
            ).first()
            
            # 상태 판단
            if recent_location:
                if recent_location.speed > 5:
                    status = "moving"
                else:
                    status = "idle"
            else:
                status = "offline"
            
            result.append({
                "vehicle_id": vehicle.id,
                "plate_number": vehicle.plate_number,
                "code": vehicle.code,
                "vehicle_type": vehicle.vehicle_type,
                "status": status,
                "location": {
                    "latitude": recent_location.latitude if recent_location else None,
                    "longitude": recent_location.longitude if recent_location else None,
                    "speed": recent_location.speed if recent_location else None,
                    "timestamp": recent_location.timestamp.isoformat() if recent_location else None
                } if recent_location else None,
                "active_dispatch": {
                    "dispatch_id": active_dispatch.id,
                    "order_number": active_dispatch.order.order_number if active_dispatch.order else None,
                    "status": active_dispatch.status
                } if active_dispatch else None
            })
        
        return result


# 싱글톤 인스턴스 (DB 세션이 필요하므로 함수로 제공)
def get_telemetry_service(db: Session) -> VehicleTelemetryService:
    """텔레메트리 서비스 인스턴스 생성"""
    return VehicleTelemetryService(db)
