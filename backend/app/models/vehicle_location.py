"""
Vehicle Location Model
실시간 차량 위치 및 온도 이력 모델
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from .base import Base


class VehicleLocation(Base):
    """차량 실시간 위치 이력"""
    __tablename__ = "vehicle_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=True, index=True)
    
    # 위치 정보
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)  # GPS 정확도 (미터)
    altitude = Column(Float, nullable=True)  # 고도 (미터)
    speed = Column(Float, nullable=True)  # 속도 (km/h)
    heading = Column(Float, nullable=True)  # 방향 (0-360도)
    
    # 온도 정보
    temperature_celsius = Column(Float, nullable=True)  # 화물칸 온도
    humidity_percent = Column(Float, nullable=True)  # 습도 (%)
    
    # UVIS 정보
    uvis_device_id = Column(String(100), nullable=True)
    uvis_timestamp = Column(DateTime, nullable=True)  # UVIS API 타임스탬프
    
    # 메타데이터
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    is_ignition_on = Column(Boolean, default=True)  # 시동 상태
    battery_voltage = Column(Float, nullable=True)  # 배터리 전압 (V)
    fuel_level_percent = Column(Float, nullable=True)  # 연료 잔량 (%)
    odometer_km = Column(Float, nullable=True)  # 주행거리 (km)
    
    # 추가 정보
    address = Column(String(500), nullable=True)  # 역지오코딩 주소
    notes = Column(Text, nullable=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="locations")
    dispatch = relationship("Dispatch", back_populates="vehicle_locations")
    
    def __repr__(self):
        return f"<VehicleLocation(vehicle_id={self.vehicle_id}, lat={self.latitude}, lon={self.longitude}, temp={self.temperature_celsius}°C, at={self.recorded_at})>"


class TemperatureAlert(Base):
    """온도 이상 알림 이력"""
    __tablename__ = "temperature_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=True, index=True)
    location_id = Column(Integer, ForeignKey("vehicle_locations.id"), nullable=True)
    
    # 알림 정보
    alert_type = Column(String(50), nullable=False)  # "TOO_HOT", "TOO_COLD", "SENSOR_ERROR"
    severity = Column(String(20), nullable=False)  # "WARNING", "CRITICAL"
    temperature_celsius = Column(Float, nullable=False)
    threshold_min = Column(Float, nullable=True)
    threshold_max = Column(Float, nullable=True)
    
    # 메타데이터
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    is_resolved = Column(Boolean, default=False, index=True)
    
    # 알림 발송 정보
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(String(200), nullable=True)  # "email,sms,push"
    
    message = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="temperature_alerts")
    dispatch = relationship("Dispatch", back_populates="temperature_alerts")
    location = relationship("VehicleLocation")
    
    def __repr__(self):
        return f"<TemperatureAlert(vehicle_id={self.vehicle_id}, type={self.alert_type}, temp={self.temperature_celsius}°C, at={self.detected_at})>"
