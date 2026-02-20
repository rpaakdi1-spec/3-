"""
Dispatch Rule Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, Time, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base, IDMixin, TimestampMixin


class DispatchRule(Base, IDMixin, TimestampMixin):
    """배차 규칙 모델"""
    __tablename__ = "dispatch_rules"
    
    name = Column(String(200), nullable=False, comment="규칙 이름")
    description = Column(Text, comment="규칙 설명")
    rule_type = Column(String(50), nullable=False, comment="assignment, constraint, optimization")
    priority = Column(Integer, default=0, nullable=False, comment="우선순위 (높을수록 우선)")
    is_active = Column(Boolean, default=True, nullable=False, comment="활성화 여부")
    
    # JSON 필드
    conditions = Column(JSONB, nullable=False, comment="규칙 조건 (JSON)")
    actions = Column(JSONB, nullable=False, comment="규칙 액션 (JSON)")
    
    # 적용 시간
    apply_time_start = Column(Time, comment="적용 시작 시간")
    apply_time_end = Column(Time, comment="적용 종료 시간")
    apply_days = Column(String(20), comment="적용 요일 (MON,TUE,WED or WEEKEND)")
    
    # 메타데이터
    version = Column(Integer, default=1, nullable=False, comment="규칙 버전")
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), comment="생성자 ID")
    
    # 성능 추적
    execution_count = Column(Integer, default=0, nullable=False, comment="실행 횟수")
    avg_execution_time_ms = Column(Float, comment="평균 실행 시간 (ms)")
    success_rate = Column(Float, comment="성공률")
    
    # Relationships
    constraints = relationship("RuleConstraint", back_populates="rule", cascade="all, delete-orphan")
    execution_logs = relationship("RuleExecutionLog", back_populates="rule")
    # simulations = relationship("RuleSimulation", back_populates="rule")  # TODO: Define RuleSimulation model
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<DispatchRule(id={self.id}, name='{self.name}', type='{self.rule_type}', priority={self.priority})>"


class RuleConstraint(Base, IDMixin):
    """규칙 제약 조건 모델"""
    __tablename__ = "rule_constraints"
    
    rule_id = Column(Integer, ForeignKey("dispatch_rules.id", ondelete="CASCADE"), nullable=False)
    constraint_type = Column(String(50), nullable=False, comment="hard, soft")
    constraint_name = Column(String(200), nullable=False, comment="제약 조건 이름")
    constraint_definition = Column(JSONB, nullable=False, comment="제약 조건 정의 (JSON)")
    penalty_weight = Column(Float, default=1.0, nullable=False, comment="페널티 가중치 (soft constraint)")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    rule = relationship("DispatchRule", back_populates="constraints")
    
    def __repr__(self):
        return f"<RuleConstraint(id={self.id}, rule_id={self.rule_id}, type='{self.constraint_type}')>"


class RuleExecutionLog(Base, IDMixin):
    """규칙 실행 로그 모델"""
    __tablename__ = "rule_execution_logs"
    
    rule_id = Column(Integer, ForeignKey("dispatch_rules.id", ondelete="SET NULL"))
    dispatch_id = Column(Integer, ForeignKey("dispatches.id", ondelete="SET NULL"))
    executed_at = Column(DateTime, server_default=func.now(), nullable=False)
    execution_time_ms = Column(Integer, comment="실행 시간 (ms)")
    
    input_data = Column(JSONB, comment="입력 데이터")
    output_data = Column(JSONB, comment="출력 데이터")
    
    success = Column(Boolean, nullable=False, comment="성공 여부")
    error_message = Column(Text, comment="에러 메시지")
    
    # 성능 메트릭
    distance_saved_km = Column(Float, comment="절감 거리 (km)")
    cost_saved = Column(Float, comment="절감 비용")
    time_saved_minutes = Column(Integer, comment="절감 시간 (분)")
    
    # Relationships
    rule = relationship("DispatchRule", back_populates="execution_logs")
    dispatch = relationship("Dispatch")
    
    def __repr__(self):
        return f"<RuleExecutionLog(id={self.id}, rule_id={self.rule_id}, success={self.success})>"


class OptimizationConfig(Base, IDMixin):
    """최적화 설정 모델"""
    __tablename__ = "optimization_configs"
    
    name = Column(String(200), nullable=False, comment="설정 이름")
    description = Column(Text, comment="설명")
    objective = Column(String(50), nullable=False, comment="minimize_distance, minimize_cost, minimize_time, balanced")
    weights = Column(JSONB, nullable=False, comment="가중치 설정 (JSON)")
    algorithm = Column(String(50), default="or_tools", nullable=False, comment="알고리즘")
    max_computation_time_seconds = Column(Integer, default=60, nullable=False, comment="최대 계산 시간")
    is_default = Column(Boolean, default=False, nullable=False, comment="기본 설정 여부")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<OptimizationConfig(id={self.id}, name='{self.name}', objective='{self.objective}')>"
