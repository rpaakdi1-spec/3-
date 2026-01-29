"""
UVIS GPS 관제 시스템 모델
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class UvisAccessKey(Base):
    """UVIS 실시간 인증키 관리"""
    __tablename__ = "uvis_access_keys"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    serial_key = Column(String(50), nullable=False, comment="업체 인증키")
    access_key = Column(String(100), nullable=False, comment="실시간 인증키")
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), comment="발급 시간")
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="만료 시간 (발급 후 5분)")
    is_active = Column(Boolean, default=True, comment="활성화 여부")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")

    # 인덱스
    __table_args__ = (
        Index('idx_uvis_access_key_expires', 'expires_at'),
        Index('idx_uvis_access_key_active', 'is_active'),
    )

    def __repr__(self):
        return f"<UvisAccessKey(id={self.id}, serial_key='{self.serial_key[:10]}...', expires_at={self.expires_at})>"


class VehicleGPSLog(Base):
    """차량 GPS 실시간 운행 정보"""
    __tablename__ = "vehicle_gps_logs"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True, comment="차량 ID")
    
    # UVIS 필드
    tid_id = Column(String(11), nullable=False, index=True, comment="단말기 ID")
    bi_date = Column(String(8), nullable=False, comment="날짜 (YYYYMMDD)")
    bi_time = Column(String(6), nullable=False, comment="시간 (HHMMSS)")
    cm_number = Column(String(30), nullable=True, comment="차량번호")
    bi_turn_onoff = Column(String(3), nullable=True, comment="시동 on/off")
    bi_x_position = Column(String(10), nullable=False, comment="위도")
    bi_y_position = Column(String(10), nullable=False, comment="경도")
    bi_gps_speed = Column(Integer, nullable=True, comment="속도 (km/h)")
    
    # 추가 필드
    latitude = Column(Float, nullable=True, comment="위도 (Float)")
    longitude = Column(Float, nullable=True, comment="경도 (Float)")
    is_engine_on = Column(Boolean, default=False, comment="시동 상태")
    speed_kmh = Column(Integer, default=0, comment="속도 (km/h)")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")

    # 관계
    vehicle = relationship("Vehicle", back_populates="gps_logs")

    # 인덱스
    __table_args__ = (
        Index('idx_vehicle_gps_tid', 'tid_id'),
        Index('idx_vehicle_gps_date_time', 'bi_date', 'bi_time'),
        Index('idx_vehicle_gps_vehicle_id', 'vehicle_id'),
        Index('idx_vehicle_gps_created', 'created_at'),
    )

    def __repr__(self):
        return f"<VehicleGPSLog(id={self.id}, tid={self.tid_id}, vehicle='{self.cm_number}', lat={self.latitude}, lng={self.longitude})>"


class VehicleTemperatureLog(Base):
    """차량 온도 실시간 정보 (냉동/냉장)"""
    __tablename__ = "vehicle_temperature_logs"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True, comment="차량 ID")
    
    # UVIS 필드
    off_key = Column(String(7), nullable=True, comment="고객 코드")
    tid_id = Column(String(11), nullable=False, index=True, comment="단말기 ID")
    tpl_date = Column(String(8), nullable=False, comment="날짜 (YYYYMMDD)")
    tpl_time = Column(String(6), nullable=False, comment="시간 (HHMMSS)")
    cm_number = Column(String(30), nullable=True, comment="차량번호")
    tpl_x_position = Column(String(10), nullable=True, comment="위도")
    tpl_y_position = Column(String(10), nullable=True, comment="경도")
    
    # 온도 A (예: 냉동실)
    tpl_signal_a = Column(Integer, nullable=True, comment="A 온도 부호 (0='+', 1='-')")
    tpl_degree_a = Column(String(5), nullable=True, comment="A 온도값")
    temperature_a = Column(Float, nullable=True, comment="A 온도 (℃)")
    
    # 온도 B (예: 냉장실)
    tpl_signal_b = Column(Integer, nullable=True, comment="B 온도 부호 (0='+', 1='-')")
    tpl_degree_b = Column(String(5), nullable=True, comment="B 온도값")
    temperature_b = Column(Float, nullable=True, comment="B 온도 (℃)")
    
    # 추가 필드
    latitude = Column(Float, nullable=True, comment="위도 (Float)")
    longitude = Column(Float, nullable=True, comment="경도 (Float)")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")

    # 관계
    vehicle = relationship("Vehicle", back_populates="temperature_logs")

    # 인덱스
    __table_args__ = (
        Index('idx_vehicle_temp_tid', 'tid_id'),
        Index('idx_vehicle_temp_date_time', 'tpl_date', 'tpl_time'),
        Index('idx_vehicle_temp_vehicle_id', 'vehicle_id'),
        Index('idx_vehicle_temp_created', 'created_at'),
    )

    def __repr__(self):
        return f"<VehicleTemperatureLog(id={self.id}, tid={self.tid_id}, vehicle='{self.cm_number}', temp_a={self.temperature_a}℃, temp_b={self.temperature_b}℃)>"


class UvisApiLog(Base):
    """UVIS API 호출 로그"""
    __tablename__ = "uvis_api_logs"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    api_type = Column(String(20), nullable=False, comment="API 유형 (auth/gps/temperature)")
    method = Column(String(10), nullable=False, comment="HTTP 메서드")
    url = Column(Text, nullable=False, comment="요청 URL")
    request_params = Column(Text, nullable=True, comment="요청 파라미터 (JSON)")
    response_status = Column(Integer, nullable=True, comment="응답 상태 코드")
    response_data = Column(Text, nullable=True, comment="응답 데이터 (JSON)")
    error_message = Column(Text, nullable=True, comment="에러 메시지")
    execution_time_ms = Column(Integer, nullable=True, comment="실행 시간 (ms)")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")

    # 인덱스
    __table_args__ = (
        Index('idx_uvis_log_type', 'api_type'),
        Index('idx_uvis_log_created', 'created_at'),
    )

    def __repr__(self):
        return f"<UvisApiLog(id={self.id}, type='{self.api_type}', status={self.response_status}, time={self.execution_time_ms}ms)>"
