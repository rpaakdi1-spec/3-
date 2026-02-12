"""
Phase 11-B: Traffic Information Models
교통 정보 연동을 위한 데이터 모델
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    Boolean, ForeignKey, Text, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TrafficLevel(str, enum.Enum):
    """교통 혼잡도"""
    SMOOTH = "SMOOTH"          # 원활
    NORMAL = "NORMAL"          # 보통
    SLOW = "SLOW"              # 서행
    CONGESTED = "CONGESTED"    # 혼잡
    BLOCKED = "BLOCKED"        # 정체


class AlertType(str, enum.Enum):
    """교통 알림 타입"""
    ACCIDENT = "ACCIDENT"      # 사고
    CONSTRUCTION = "CONSTRUCTION"  # 공사
    CONGESTION = "CONGESTION"  # 혼잡
    WEATHER = "WEATHER"        # 기상
    EVENT = "EVENT"            # 행사
    ROAD_CLOSURE = "ROAD_CLOSURE"  # 도로 폐쇄


class RouteStatus(str, enum.Enum):
    """경로 상태"""
    OPTIMAL = "OPTIMAL"        # 최적
    ALTERNATIVE = "ALTERNATIVE"  # 대안
    HISTORICAL = "HISTORICAL"  # 이력


class TrafficCondition(Base):
    """실시간 교통 상황"""
    __tablename__ = "traffic_conditions"

    id = Column(Integer, primary_key=True, index=True)
    
    # 위치 정보
    road_name = Column(String(200), nullable=False, comment="도로명")
    section_name = Column(String(200), nullable=True, comment="구간명")
    start_lat = Column(Float, nullable=False, comment="시작 위도")
    start_lng = Column(Float, nullable=False, comment="시작 경도")
    end_lat = Column(Float, nullable=False, comment="종료 위도")
    end_lng = Column(Float, nullable=False, comment="종료 경도")
    
    # 교통 상태
    traffic_level = Column(SQLEnum(TrafficLevel), nullable=False, comment="혼잡도")
    speed = Column(Float, nullable=True, comment="평균 속도 (km/h)")
    travel_time = Column(Integer, nullable=True, comment="통과 시간 (초)")
    
    # API 정보
    api_provider = Column(String(50), nullable=True, comment="API 제공자 (TMAP/KAKAO/GOOGLE)")
    api_response = Column(JSON, nullable=True, comment="원본 API 응답")
    
    # 시간 정보
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="수집 시각")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Metadata
    traffic_metadata = Column(JSON, nullable=True, comment="추가 메타데이터")


class RouteOptimization(Base):
    """최적 경로 정보"""
    __tablename__ = "route_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=True, index=True)
    
    # 출발지/목적지
    origin_lat = Column(Float, nullable=False, comment="출발지 위도")
    origin_lng = Column(Float, nullable=False, comment="출발지 경도")
    origin_address = Column(String(500), nullable=True, comment="출발지 주소")
    
    destination_lat = Column(Float, nullable=False, comment="목적지 위도")
    destination_lng = Column(Float, nullable=False, comment="목적지 경도")
    destination_address = Column(String(500), nullable=True, comment="목적지 주소")
    
    # 경로 정보
    route_name = Column(String(200), nullable=True, comment="경로명")
    route_status = Column(SQLEnum(RouteStatus), default=RouteStatus.OPTIMAL, comment="경로 상태")
    
    # 경로 데이터
    route_geometry = Column(JSON, nullable=True, comment="경로 좌표 (GeoJSON)")
    waypoints = Column(JSON, nullable=True, comment="경유지 목록")
    
    # 거리/시간
    distance = Column(Float, nullable=False, comment="거리 (km)")
    duration = Column(Integer, nullable=False, comment="예상 소요시간 (분)")
    duration_in_traffic = Column(Integer, nullable=True, comment="교통 고려 소요시간 (분)")
    
    # 교통 정보
    traffic_level = Column(SQLEnum(TrafficLevel), nullable=True, comment="전체 혼잡도")
    toll_fee = Column(Integer, default=0, comment="통행료 (원)")
    fuel_cost = Column(Integer, nullable=True, comment="예상 연료비 (원)")
    
    # 최적화 점수
    optimization_score = Column(Float, nullable=True, comment="최적화 점수 (0-100)")
    is_optimal = Column(Boolean, default=False, comment="최적 경로 여부")
    
    # API 정보
    api_provider = Column(String(50), nullable=True, comment="API 제공자")
    api_response = Column(JSON, nullable=True, comment="원본 API 응답")
    
    # 시간 정보
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    route_metadata = Column(JSON, nullable=True, comment="추가 메타데이터")
    
    # Relationships
    dispatch = relationship("Dispatch", back_populates="route_optimizations")


class TrafficAlert(Base):
    """교통 알림"""
    __tablename__ = "traffic_alerts"

    id = Column(Integer, primary_key=True, index=True)
    
    # 알림 정보
    alert_type = Column(SQLEnum(AlertType), nullable=False, index=True, comment="알림 타입")
    title = Column(String(200), nullable=False, comment="제목")
    description = Column(Text, nullable=True, comment="상세 설명")
    
    # 위치 정보
    road_name = Column(String(200), nullable=True, comment="도로명")
    location_lat = Column(Float, nullable=True, comment="위도")
    location_lng = Column(Float, nullable=True, comment="경도")
    location_address = Column(String(500), nullable=True, comment="주소")
    
    # 영향 범위
    affected_radius = Column(Float, nullable=True, comment="영향 반경 (km)")
    
    # 심각도
    severity = Column(String(20), nullable=True, comment="심각도 (LOW/MEDIUM/HIGH/CRITICAL)")
    
    # 시간 정보
    start_time = Column(DateTime, nullable=True, comment="시작 시각")
    end_time = Column(DateTime, nullable=True, comment="종료 예상 시각")
    
    # 상태
    is_active = Column(Boolean, default=True, comment="활성 여부")
    
    # API 정보
    api_provider = Column(String(50), nullable=True, comment="API 제공자")
    external_id = Column(String(200), nullable=True, comment="외부 ID")
    api_response = Column(JSON, nullable=True, comment="원본 API 응답")
    
    # 시간 정보
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    alert_metadata = Column(JSON, nullable=True, comment="추가 메타데이터")


class RouteHistory(Base):
    """경로 이력"""
    __tablename__ = "route_histories"

    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    
    # 경로 정보
    route_optimization_id = Column(Integer, ForeignKey("route_optimizations.id"), nullable=True)
    
    # 실제 주행 정보
    actual_distance = Column(Float, nullable=True, comment="실제 주행 거리 (km)")
    actual_duration = Column(Integer, nullable=True, comment="실제 소요시간 (분)")
    fuel_consumed = Column(Float, nullable=True, comment="연료 소비량 (L)")
    
    # 예측 vs 실제 비교
    distance_variance = Column(Float, nullable=True, comment="거리 오차 (%)")
    duration_variance = Column(Float, nullable=True, comment="시간 오차 (%)")
    
    # 교통 상황
    avg_traffic_level = Column(SQLEnum(TrafficLevel), nullable=True, comment="평균 혼잡도")
    
    # 시간 정보
    started_at = Column(DateTime, nullable=True, comment="출발 시각")
    completed_at = Column(DateTime, nullable=True, comment="도착 시각")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Metadata
    history_metadata = Column(JSON, nullable=True, comment="추가 메타데이터")
    
    # Relationships
    dispatch = relationship("Dispatch", back_populates="route_histories")
    vehicle = relationship("Vehicle", back_populates="route_histories")
    driver = relationship("Driver", back_populates="route_histories")
    route_optimization = relationship("RouteOptimization")


class TrafficRule(Base):
    """교통 기반 배차 규칙"""
    __tablename__ = "traffic_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    # 규칙 정보
    rule_name = Column(String(200), nullable=False, comment="규칙명")
    description = Column(Text, nullable=True, comment="설명")
    
    # 조건
    traffic_level_threshold = Column(SQLEnum(TrafficLevel), nullable=True, comment="혼잡도 임계값")
    congestion_duration_min = Column(Integer, nullable=True, comment="최소 혼잡 지속 시간 (분)")
    
    # 액션
    avoid_congested_routes = Column(Boolean, default=True, comment="혼잡 경로 회피")
    delay_dispatch = Column(Boolean, default=False, comment="배차 지연")
    delay_duration = Column(Integer, nullable=True, comment="지연 시간 (분)")
    increase_time_buffer = Column(Integer, nullable=True, comment="시간 버퍼 증가 (%)")
    
    # 우선순위
    priority = Column(Integer, default=50, comment="우선순위 (0-100)")
    
    # 상태
    is_active = Column(Boolean, default=True, comment="활성 여부")
    
    # 시간 정보
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    rule_metadata = Column(JSON, nullable=True, comment="추가 메타데이터")
