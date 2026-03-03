"""
차량 일별 주행거리 기록 모델

GPS 로그 데이터를 기반으로 매일 자동 집계
"""
from sqlalchemy import Column, Integer, Float, Date, String, DateTime, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class VehicleDailyMileage(Base):
    """차량 일별 주행거리 및 운행 통계"""
    __tablename__ = "vehicle_daily_mileage"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, comment="차량 ID")
    date = Column(Date, nullable=False, comment="날짜")
    
    # 주행거리
    total_distance_km = Column(Float, default=0.0, comment="총 주행거리 (km)")
    
    # 운행 시간
    total_driving_minutes = Column(Integer, default=0, comment="총 운행 시간 (분)")
    engine_on_minutes = Column(Integer, default=0, comment="시동 ON 시간 (분)")
    idle_minutes = Column(Integer, default=0, comment="공회전 시간 (분)")
    
    # 운행 통계
    max_speed_kmh = Column(Integer, default=0, comment="최고 속도 (km/h)")
    avg_speed_kmh = Column(Float, default=0.0, comment="평균 속도 (km/h)")
    
    # GPS 포인트 수
    gps_point_count = Column(Integer, default=0, comment="수집된 GPS 포인트 수")
    
    # 운행 시작/종료 위치
    start_latitude = Column(Float, nullable=True, comment="시작 위도")
    start_longitude = Column(Float, nullable=True, comment="시작 경도")
    start_time = Column(DateTime(timezone=True), nullable=True, comment="운행 시작 시간")
    
    end_latitude = Column(Float, nullable=True, comment="종료 위도")
    end_longitude = Column(Float, nullable=True, comment="종료 경도")
    end_time = Column(DateTime(timezone=True), nullable=True, comment="운행 종료 시간")
    
    # 집계 상태
    is_calculated = Column(Boolean, default=False, comment="집계 완료 여부")
    calculation_method = Column(String(50), default="gps_distance", comment="계산 방법 (gps_distance, haversine 등)")
    
    # 메타 정보
    notes = Column(String(500), nullable=True, comment="비고")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")

    # 관계
    vehicle = relationship("Vehicle", back_populates="daily_mileages")

    # 인덱스
    __table_args__ = (
        Index('idx_vehicle_daily_mileage_vehicle_date', 'vehicle_id', 'date', unique=True),
        Index('idx_vehicle_daily_mileage_date', 'date'),
        Index('idx_vehicle_daily_mileage_calculated', 'is_calculated'),
    )

    def __repr__(self):
        return f"<VehicleDailyMileage(vehicle_id={self.vehicle_id}, date={self.date}, distance={self.total_distance_km}km)>"
