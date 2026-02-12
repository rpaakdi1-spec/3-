"""
Simulation models for dispatch rule testing and optimization
"""
from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class RuleSimulation(Base):
    """규칙 시뮬레이션 실행 기록"""
    __tablename__ = "rule_simulations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="시뮬레이션 이름")
    description = Column(Text, nullable=True, comment="시뮬레이션 설명")
    
    # 시뮬레이션 설정
    rule_id = Column(Integer, ForeignKey("dispatch_rules.id"), nullable=True, comment="테스트할 규칙 ID")
    rule_config = Column(JSON, nullable=False, comment="규칙 설정 (임시 규칙 또는 저장된 규칙)")
    
    # 시뮬레이션 시나리오
    scenario_data = Column(JSON, nullable=False, comment="테스트 시나리오 데이터")
    scenario_type = Column(String(50), default="custom", comment="시나리오 타입: custom, historical, generated")
    
    # 실행 설정
    iterations = Column(Integer, default=1, comment="반복 실행 횟수")
    randomize_data = Column(Boolean, default=False, comment="데이터 랜덤화 여부")
    
    # 실행 결과
    status = Column(String(50), default="pending", comment="상태: pending, running, completed, failed")
    
    # 성능 지표
    total_matches = Column(Integer, nullable=True, comment="총 매칭 수")
    successful_matches = Column(Integer, nullable=True, comment="성공한 매칭 수")
    failed_matches = Column(Integer, nullable=True, comment="실패한 매칭 수")
    match_rate = Column(Float, nullable=True, comment="매칭 성공률 (%)")
    
    avg_response_time_ms = Column(Float, nullable=True, comment="평균 응답 시간 (ms)")
    min_response_time_ms = Column(Float, nullable=True, comment="최소 응답 시간 (ms)")
    max_response_time_ms = Column(Float, nullable=True, comment="최대 응답 시간 (ms)")
    
    # 비용 분석
    estimated_cost = Column(Float, nullable=True, comment="예상 비용")
    estimated_distance_km = Column(Float, nullable=True, comment="예상 총 거리 (km)")
    estimated_time_minutes = Column(Float, nullable=True, comment="예상 총 시간 (분)")
    
    # 상세 결과
    results = Column(JSON, nullable=True, comment="상세 시뮬레이션 결과")
    errors = Column(JSON, nullable=True, comment="오류 내역")
    
    # 메타데이터
    created_by = Column(String(100), nullable=True, comment="생성자")
    started_at = Column(DateTime, nullable=True, comment="시작 시각")
    completed_at = Column(DateTime, nullable=True, comment="완료 시각")
    duration_seconds = Column(Float, nullable=True, comment="실행 시간 (초)")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성 시각")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정 시각")
    
    # Relationships
    rule = relationship("DispatchRule", back_populates="simulations")


class SimulationComparison(Base):
    """규칙 A/B 비교 테스트"""
    __tablename__ = "simulation_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="비교 테스트 이름")
    description = Column(Text, nullable=True, comment="비교 테스트 설명")
    
    # 비교할 시뮬레이션들
    simulation_a_id = Column(Integer, ForeignKey("rule_simulations.id"), nullable=False, comment="시뮬레이션 A")
    simulation_b_id = Column(Integer, ForeignKey("rule_simulations.id"), nullable=False, comment="시뮬레이션 B")
    
    # 비교 결과
    winner = Column(String(1), nullable=True, comment="승자: A, B, tie")
    comparison_metrics = Column(JSON, nullable=True, comment="비교 지표")
    
    # 추천
    recommendation = Column(Text, nullable=True, comment="AI 추천 내용")
    confidence_score = Column(Float, nullable=True, comment="추천 신뢰도 (0-1)")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성 시각")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정 시각")
    
    # Relationships
    simulation_a = relationship("RuleSimulation", foreign_keys=[simulation_a_id])
    simulation_b = relationship("RuleSimulation", foreign_keys=[simulation_b_id])


class SimulationTemplate(Base):
    """시뮬레이션 템플릿 (사전 정의된 시나리오)"""
    __tablename__ = "simulation_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="템플릿 이름")
    description = Column(Text, nullable=True, comment="템플릿 설명")
    category = Column(String(50), nullable=True, comment="카테고리: peak_hours, weather, distance 등")
    
    # 템플릿 시나리오
    scenario_data = Column(JSON, nullable=False, comment="시나리오 데이터")
    expected_results = Column(JSON, nullable=True, comment="예상 결과 (벤치마크)")
    
    # 난이도
    difficulty = Column(String(20), default="medium", comment="난이도: easy, medium, hard")
    complexity_score = Column(Float, nullable=True, comment="복잡도 점수 (1-10)")
    
    # 사용 통계
    usage_count = Column(Integer, default=0, comment="사용 횟수")
    avg_success_rate = Column(Float, nullable=True, comment="평균 성공률")
    
    is_active = Column(Boolean, default=True, comment="활성 여부")
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성 시각")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정 시각")
