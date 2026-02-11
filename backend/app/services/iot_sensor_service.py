"""
IoT Sensor Service for Phase 13
Real-time sensor data collection and monitoring
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import json
import random

from app.models.iot_sensor import (
    VehicleSensor, SensorReading, SensorAlert,
    SensorType, AlertSeverity
)


class IoTSensorService:
    """IoT 센서 데이터 수집 및 모니터링 서비스"""

    def __init__(self, db: Session):
        self.db = db

    async def collect_sensor_data(
        self,
        vehicle_id: int,
        sensor_type: str,
        value: float,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        센서 데이터 수집
        
        Args:
            vehicle_id: 차량 ID
            sensor_type: 센서 타입
            value: 측정값
            latitude: 위도 (선택)
            longitude: 경도 (선택)
            metadata: 추가 메타데이터
            
        Returns:
            수집된 센서 데이터 및 이상 감지 결과
        """
        # 센서 조회
        sensor = self.db.query(VehicleSensor).filter(
            and_(
                VehicleSensor.vehicle_id == vehicle_id,
                VehicleSensor.sensor_type == sensor_type,
                VehicleSensor.is_active == True
            )
        ).first()

        if not sensor:
            raise ValueError(f"Active sensor not found for vehicle {vehicle_id}, type {sensor_type}")

        # 이상 감지
        is_anomaly = False
        anomaly_score = 0.0
        
        if sensor.min_threshold is not None and value < sensor.min_threshold:
            is_anomaly = True
            anomaly_score = (sensor.min_threshold - value) / sensor.min_threshold

        if sensor.max_threshold is not None and value > sensor.max_threshold:
            is_anomaly = True
            anomaly_score = (value - sensor.max_threshold) / sensor.max_threshold

        # 센서 리딩 저장
        reading = SensorReading(
            sensor_id=sensor.id,
            vehicle_id=vehicle_id,
            value=value,
            unit=sensor.unit,
            latitude=latitude,
            longitude=longitude,
            sensor_metadata=metadata,
            is_anomaly=is_anomaly,
            anomaly_score=min(anomaly_score, 1.0),
            recorded_at=datetime.utcnow()
        )
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)

        # 이상 감지 시 알림 생성
        alert = None
        if is_anomaly:
            alert = await self._create_alert(sensor, reading, value)

        return {
            "reading_id": reading.id,
            "vehicle_id": vehicle_id,
            "sensor_type": sensor_type,
            "value": value,
            "unit": sensor.unit,
            "is_anomaly": is_anomaly,
            "anomaly_score": reading.anomaly_score,
            "alert_created": alert is not None,
            "alert_id": alert.id if alert else None,
            "recorded_at": reading.recorded_at.isoformat()
        }

    async def _create_alert(
        self,
        sensor: VehicleSensor,
        reading: SensorReading,
        value: float
    ) -> SensorAlert:
        """알림 생성"""
        # 심각도 결정
        severity = AlertSeverity.WARNING
        threshold_value = None

        if sensor.min_threshold and value < sensor.min_threshold:
            threshold_value = sensor.min_threshold
            if value < sensor.min_threshold * 0.8:  # 20% 이상 초과
                severity = AlertSeverity.CRITICAL
        elif sensor.max_threshold and value > sensor.max_threshold:
            threshold_value = sensor.max_threshold
            if value > sensor.max_threshold * 1.2:  # 20% 이상 초과
                severity = AlertSeverity.CRITICAL

        # 알림 메시지 생성
        sensor_name_kr = {
            "temperature": "온도",
            "vibration": "진동",
            "fuel": "연료",
            "tire_pressure": "타이어 압력",
            "engine_oil": "엔진 오일",
            "battery": "배터리"
        }.get(sensor.sensor_type, sensor.sensor_type)

        title = f"차량 {sensor.vehicle_id} - {sensor_name_kr} 이상 감지"
        
        if threshold_value:
            message = (
                f"{sensor_name_kr} 센서에서 임계값을 벗어난 값이 감지되었습니다.\n"
                f"현재값: {value:.2f} {sensor.unit}\n"
                f"임계값: {threshold_value:.2f} {sensor.unit}\n"
                f"즉시 확인이 필요합니다."
            )
        else:
            message = f"{sensor_name_kr} 센서에서 이상 패턴이 감지되었습니다."

        alert = SensorAlert(
            sensor_id=sensor.id,
            vehicle_id=sensor.vehicle_id,
            reading_id=reading.id,
            severity=severity,
            title=title,
            message=message,
            sensor_value=value,
            threshold_value=threshold_value,
            created_at=datetime.utcnow()
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        return alert

    async def get_vehicle_sensors(
        self,
        vehicle_id: int,
        sensor_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """차량의 센서 목록 조회"""
        query = self.db.query(VehicleSensor).filter(
            VehicleSensor.vehicle_id == vehicle_id
        )

        if sensor_type:
            query = query.filter(VehicleSensor.sensor_type == sensor_type)

        if active_only:
            query = query.filter(VehicleSensor.is_active == True)

        sensors = query.all()

        return [
            {
                "id": s.id,
                "vehicle_id": s.vehicle_id,
                "sensor_type": s.sensor_type,
                "sensor_name": s.sensor_name,
                "manufacturer": s.manufacturer,
                "model": s.model,
                "min_threshold": s.min_threshold,
                "max_threshold": s.max_threshold,
                "unit": s.unit,
                "is_active": s.is_active,
                "last_calibration": s.last_calibration.isoformat() if s.last_calibration else None,
                "installed_at": s.installed_at.isoformat() if s.installed_at else None
            }
            for s in sensors
        ]

    async def get_latest_readings(
        self,
        vehicle_id: int,
        sensor_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """최신 센서 측정값 조회"""
        query = self.db.query(SensorReading).join(VehicleSensor).filter(
            SensorReading.vehicle_id == vehicle_id
        )

        if sensor_type:
            query = query.filter(VehicleSensor.sensor_type == sensor_type)

        readings = query.order_by(SensorReading.recorded_at.desc()).limit(limit).all()

        return [
            {
                "id": r.id,
                "sensor_id": r.sensor_id,
                "vehicle_id": r.vehicle_id,
                "value": r.value,
                "unit": r.unit,
                "is_anomaly": r.is_anomaly,
                "anomaly_score": r.anomaly_score,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "recorded_at": r.recorded_at.isoformat()
            }
            for r in readings
        ]

    async def get_sensor_statistics(
        self,
        vehicle_id: int,
        sensor_type: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """센서 통계 조회"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        readings = self.db.query(SensorReading).join(VehicleSensor).filter(
            and_(
                SensorReading.vehicle_id == vehicle_id,
                VehicleSensor.sensor_type == sensor_type,
                SensorReading.recorded_at >= cutoff_time
            )
        ).all()

        if not readings:
            return {
                "vehicle_id": vehicle_id,
                "sensor_type": sensor_type,
                "hours": hours,
                "count": 0,
                "avg": None,
                "min": None,
                "max": None,
                "anomaly_count": 0
            }

        values = [r.value for r in readings]
        anomaly_count = sum(1 for r in readings if r.is_anomaly)

        return {
            "vehicle_id": vehicle_id,
            "sensor_type": sensor_type,
            "hours": hours,
            "count": len(readings),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "anomaly_count": anomaly_count,
            "anomaly_rate": anomaly_count / len(readings) if readings else 0
        }

    async def get_active_alerts(
        self,
        vehicle_id: Optional[int] = None,
        severity: Optional[str] = None,
        unresolved_only: bool = True
    ) -> List[Dict[str, Any]]:
        """활성 알림 조회"""
        query = self.db.query(SensorAlert)

        if vehicle_id:
            query = query.filter(SensorAlert.vehicle_id == vehicle_id)

        if severity:
            query = query.filter(SensorAlert.severity == severity)

        if unresolved_only:
            query = query.filter(SensorAlert.is_resolved == False)

        alerts = query.order_by(SensorAlert.created_at.desc()).all()

        return [
            {
                "id": a.id,
                "vehicle_id": a.vehicle_id,
                "sensor_id": a.sensor_id,
                "severity": a.severity,
                "title": a.title,
                "message": a.message,
                "sensor_value": a.sensor_value,
                "threshold_value": a.threshold_value,
                "is_acknowledged": a.is_acknowledged,
                "is_resolved": a.is_resolved,
                "created_at": a.created_at.isoformat()
            }
            for a in alerts
        ]

    async def acknowledge_alert(
        self,
        alert_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """알림 확인"""
        alert = self.db.query(SensorAlert).filter(SensorAlert.id == alert_id).first()
        
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        alert.is_acknowledged = True
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)

        return {
            "alert_id": alert.id,
            "acknowledged": True,
            "acknowledged_by": user_id,
            "acknowledged_at": alert.acknowledged_at.isoformat()
        }

    async def resolve_alert(
        self,
        alert_id: int,
        resolution_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """알림 해결"""
        alert = self.db.query(SensorAlert).filter(SensorAlert.id == alert_id).first()
        
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolution_notes = resolution_notes
        
        self.db.commit()
        self.db.refresh(alert)

        return {
            "alert_id": alert.id,
            "resolved": True,
            "resolved_at": alert.resolved_at.isoformat(),
            "resolution_notes": resolution_notes
        }

    async def get_realtime_dashboard_data(
        self,
        vehicle_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """실시간 대시보드 데이터"""
        # 최근 1시간 데이터
        cutoff_time = datetime.utcnow() - timedelta(hours=1)

        query = self.db.query(SensorReading).filter(
            SensorReading.recorded_at >= cutoff_time
        )

        if vehicle_ids:
            query = query.filter(SensorReading.vehicle_id.in_(vehicle_ids))

        readings = query.all()

        # 차량별 최신 센서 값
        vehicle_data = {}
        for reading in readings:
            if reading.vehicle_id not in vehicle_data:
                vehicle_data[reading.vehicle_id] = {}
            
            sensor = self.db.query(VehicleSensor).filter(
                VehicleSensor.id == reading.sensor_id
            ).first()
            
            if sensor:
                vehicle_data[reading.vehicle_id][sensor.sensor_type] = {
                    "value": reading.value,
                    "unit": reading.unit,
                    "is_anomaly": reading.is_anomaly,
                    "recorded_at": reading.recorded_at.isoformat()
                }

        # 활성 알림 수
        active_alerts_count = self.db.query(func.count(SensorAlert.id)).filter(
            SensorAlert.is_resolved == False
        ).scalar()

        # 이상 감지 수
        anomaly_count = self.db.query(func.count(SensorReading.id)).filter(
            and_(
                SensorReading.recorded_at >= cutoff_time,
                SensorReading.is_anomaly == True
            )
        ).scalar()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "vehicle_count": len(vehicle_data),
            "total_readings": len(readings),
            "active_alerts": active_alerts_count,
            "anomaly_count": anomaly_count,
            "vehicle_data": vehicle_data
        }
