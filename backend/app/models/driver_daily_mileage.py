"""
운전자 일별 주행거리 모델
"""
from sqlalchemy import Column, Integer, Float, Date, String, Boolean, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class DriverDailyMileage(Base):
    """운전자 일별 주행거리 통계"""
    __tablename__ = "driver_daily_mileage"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, comment="운전자 ID")
    date = Column(Date, nullable=False, comment="날짜")
    
    # 주행 통계
    total_distance_km = Column(Float, nullable=False, default=0.0, comment="총 주행거리(km)")
    total_driving_minutes = Column(Integer, nullable=False, default=0, comment="총 운행시간(분)")
    engine_on_minutes = Column(Integer, nullable=True, comment="엔진 가동 시간(분)")
    idle_minutes = Column(Integer, nullable=True, comment="공회전 시간(분)")
    
    # 속도 통계
    max_speed_kmh = Column(Float, nullable=True, comment="최고 속도(km/h)")
    avg_speed_kmh = Column(Float, nullable=True, comment="평균 속도(km/h)")
    
    # GPS 데이터 품질
    gps_point_count = Column(Integer, nullable=True, comment="GPS 포인트 수")
    
    # 운행 시간대
    start_time = Column(DateTime(timezone=True), nullable=True, comment="운행 시작 시간")
    end_time = Column(DateTime(timezone=True), nullable=True, comment="운행 종료 시간")
    
    # 운행한 차량들 (여러 차량을 운전할 수 있음)
    vehicle_ids = Column(String(200), nullable=True, comment="운행 차량 ID 목록 (콤마 구분)")
    vehicle_count = Column(Integer, default=1, comment="운행한 차량 수")
    
    # 계산 정보
    is_calculated = Column(Boolean, default=False, comment="계산 완료 여부")
    calculation_method = Column(String(50), nullable=True, comment="계산 방법")
    
    # 메모
    notes = Column(Text, nullable=True, comment="특이사항")
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="생성일시")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="수정일시")
    
    # Relationships
    driver = relationship("Driver", backref="daily_mileages")
    
    # 인덱스
    __table_args__ = (
        Index('idx_driver_daily_mileage_driver_date', 'driver_id', 'date', unique=True),
        Index('idx_driver_daily_mileage_date', 'date'),
        Index('idx_driver_daily_mileage_calculated', 'is_calculated'),
    )

    def __repr__(self):
        return f"<DriverDailyMileage(driver_id={self.driver_id}, date={self.date}, distance={self.total_distance_km}km)>"
