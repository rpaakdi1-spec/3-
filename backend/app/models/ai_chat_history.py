"""
AI 채팅 히스토리 모델
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from .base import Base


class AIChatHistory(Base):
    """AI 채팅 히스토리"""
    __tablename__ = "ai_chat_histories"

    id = Column(Integer, primary_key=True, index=True)
    
    # 사용자 정보 (나중에 사용자 관리 추가 시 사용)
    user_id = Column(Integer, nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)  # 세션 추적용
    
    # 대화 내용
    user_message = Column(Text, nullable=False)  # 사용자 입력
    assistant_message = Column(Text, nullable=False)  # AI 응답
    
    # 메타 정보
    intent = Column(String(100), nullable=True, index=True)  # create_order, create_multiple_orders 등
    action = Column(String(100), nullable=True)  # waiting_confirmation, order_created 등
    
    # 주문 정보 (JSON 형태로 저장)
    parsed_order = Column(JSON, nullable=True)  # 단일 주문 정보
    parsed_orders = Column(JSON, nullable=True)  # 다중 주문 정보
    
    # 배차 추천 정보
    dispatch_recommendation = Column(JSON, nullable=True)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    def __repr__(self):
        return f"<AIChatHistory(id={self.id}, intent={self.intent}, created_at={self.created_at})>"
