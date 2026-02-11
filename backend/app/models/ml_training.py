"""
Phase 15: AI Auto-Learning Models
Reinforcement Learning for Dispatch Optimization
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class DispatchTrainingData(Base):
    """배차 학습 데이터 - 강화학습 경험 저장"""
    __tablename__ = "dispatch_training_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Episode 정보
    episode_id = Column(String(100), index=True)
    step = Column(Integer)
    
    # State (상태)
    state_features = Column(JSON)  # 차량 상태, 주문 특성, 시간, 환경
    
    # Action (행동)
    action_taken = Column(Integer)  # 선택한 차량 ID
    action_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    
    # Reward (보상)
    reward = Column(Float)
    immediate_reward = Column(Float)  # 즉시 보상
    long_term_reward = Column(Float, nullable=True)  # 장기 보상
    
    # Next State
    next_state_features = Column(JSON, nullable=True)
    
    # Episode 완료 여부
    done = Column(Boolean, default=False)
    
    # 실제 결과 (검증용)
    actual_dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=True)
    actual_completion_time = Column(Float, nullable=True)
    actual_distance = Column(Float, nullable=True)
    actual_success = Column(Boolean, nullable=True)
    
    # Metadata
    collected_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50), nullable=True)
    
    # Relationships
    vehicle = relationship("Vehicle", foreign_keys=[action_vehicle_id])
    dispatch = relationship("Dispatch", foreign_keys=[actual_dispatch_id])


class MLExperiment(Base):
    """ML 실험 추적"""
    __tablename__ = "ml_experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 실험 정보
    experiment_name = Column(String(200))
    experiment_type = Column(String(50))  # RL, supervised, etc.
    description = Column(Text, nullable=True)
    
    # 하이퍼파라미터
    hyperparameters = Column(JSON)
    
    # 학습 설정
    training_config = Column(JSON)
    
    # 상태
    status = Column(String(50))  # running, completed, failed
    
    # 메트릭
    metrics = Column(JSON, nullable=True)
    best_reward = Column(Float, nullable=True)
    best_epoch = Column(Integer, nullable=True)
    
    # 시간
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # 결과
    model_path = Column(String(500), nullable=True)
    result_summary = Column(JSON, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    model_versions = relationship("ModelVersion", back_populates="experiment")


class ModelVersion(Base):
    """모델 버전 관리"""
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 버전 정보
    version = Column(String(50), unique=True, index=True)
    model_name = Column(String(200))
    model_type = Column(String(50))  # PPO, DQN, A3C, etc.
    
    # 실험 연결
    experiment_id = Column(Integer, ForeignKey("ml_experiments.id"), nullable=True)
    
    # 모델 파일
    model_path = Column(String(500))
    model_size_mb = Column(Float, nullable=True)
    
    # 성능 메트릭
    performance_metrics = Column(JSON)
    validation_metrics = Column(JSON, nullable=True)
    
    # 학습 정보
    training_episodes = Column(Integer, nullable=True)
    training_steps = Column(Integer, nullable=True)
    training_duration_hours = Column(Float, nullable=True)
    
    # 배포 상태
    status = Column(String(50))  # training, validated, deployed, archived
    is_active = Column(Boolean, default=False)
    deployed_at = Column(DateTime, nullable=True)
    
    # A/B 테스트
    ab_test_group = Column(String(50), nullable=True)
    ab_test_traffic_percent = Column(Float, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    experiment = relationship("MLExperiment", back_populates="model_versions")


class DispatchFeature(Base):
    """배차 특성 스냅샷 - Feature Store"""
    __tablename__ = "dispatch_features"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 타임스탬프
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 차량 특성
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    vehicle_location_lat = Column(Float)
    vehicle_location_lon = Column(Float)
    vehicle_status = Column(String(50))
    vehicle_capacity_used = Column(Float)
    vehicle_temperature_type = Column(String(50))
    
    # 주문 특성
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    order_distance_km = Column(Float, nullable=True)
    order_priority = Column(Integer, nullable=True)
    order_temperature_requirement = Column(String(50), nullable=True)
    
    # 시간 특성
    hour_of_day = Column(Integer)
    day_of_week = Column(Integer)
    is_peak_hour = Column(Boolean)
    is_weekend = Column(Boolean)
    
    # 환경 특성
    weather_condition = Column(String(50), nullable=True)
    traffic_level = Column(String(50), nullable=True)
    
    # 집계 특성
    nearby_vehicles_count = Column(Integer, nullable=True)
    pending_orders_count = Column(Integer, nullable=True)
    avg_dispatch_time_last_hour = Column(Float, nullable=True)
    
    # Computed features
    features_vector = Column(JSON)  # 정규화된 feature 벡터
    
    # Relationships
    vehicle = relationship("Vehicle")
    order = relationship("Order")


class RLRewardHistory(Base):
    """강화학습 보상 이력"""
    __tablename__ = "rl_reward_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 배차 정보
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    
    # 보상 구성 요소
    time_reward = Column(Float)  # 배차 시간 기반
    success_reward = Column(Float)  # 성공/실패
    efficiency_reward = Column(Float)  # 효율성
    customer_satisfaction_reward = Column(Float, nullable=True)  # 고객 만족도
    
    # 총 보상
    total_reward = Column(Float)
    normalized_reward = Column(Float)  # -1 ~ 1 정규화
    
    # 컨텍스트
    state_features = Column(JSON)
    action_taken = Column(Integer)
    
    # 실제 결과
    actual_completion_time = Column(Float)
    predicted_completion_time = Column(Float, nullable=True)
    prediction_error = Column(Float, nullable=True)
    
    # 메타데이터
    model_version = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    dispatch = relationship("Dispatch")
    vehicle = relationship("Vehicle")
    order = relationship("Order")
