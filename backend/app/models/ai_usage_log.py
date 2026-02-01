"""
AI 사용량 로깅 모델 - 비용 모니터링용
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from .base import Base


class AIUsageLog(Base):
    """AI API 사용량 로깅"""
    __tablename__ = "ai_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # 사용자 정보
    user_id = Column(Integer, nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    
    # 모델 정보
    model_name = Column(String(100), nullable=False, index=True)  # gpt-4o, gpt-3.5-turbo, gemini-pro
    provider = Column(String(50), nullable=False, index=True)     # openai, google
    
    # 사용량 정보
    prompt_tokens = Column(Integer, nullable=False, default=0)    # 입력 토큰 수
    completion_tokens = Column(Integer, nullable=False, default=0)  # 출력 토큰 수
    total_tokens = Column(Integer, nullable=False, default=0)     # 총 토큰 수
    
    # 비용 정보 (USD)
    prompt_cost = Column(Float, nullable=False, default=0.0)      # 입력 비용
    completion_cost = Column(Float, nullable=False, default=0.0)  # 출력 비용
    total_cost = Column(Float, nullable=False, default=0.0)       # 총 비용
    
    # 응답 정보
    response_time_ms = Column(Integer, nullable=True)             # 응답 시간 (밀리초)
    status = Column(String(50), nullable=False, default="success")  # success, error
    error_message = Column(Text, nullable=True)                   # 에러 메시지
    
    # 컨텍스트 정보
    intent = Column(String(100), nullable=True, index=True)       # create_order, update_order 등
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    def __repr__(self):
        return f"<AIUsageLog(id={self.id}, model={self.model_name}, cost=${self.total_cost:.4f})>"
