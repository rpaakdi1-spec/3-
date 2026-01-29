from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class BandMessage(Base):
    """밴드 메시지 모델 - 주기적으로 생성되는 화물 수배 메시지"""
    __tablename__ = "band_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=False, comment="배차 ID")
    
    # 메시지 내용
    message_content = Column(Text, nullable=False, comment="생성된 메시지 내용")
    message_type = Column(String(50), default="freight_dispatch", comment="메시지 타입")
    
    # 상태
    is_sent = Column(Boolean, default=False, comment="전송 여부 (수동 전송 확인)")
    sent_at = Column(DateTime(timezone=True), nullable=True, comment="전송 일시")
    
    # 메타데이터
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 일시")
    scheduled_for = Column(DateTime(timezone=True), nullable=True, comment="예약 전송 시간")
    
    # 변형 정보
    variation_seed = Column(Integer, comment="메시지 변형 시드")
    
    # Relationships
    dispatch = relationship("Dispatch", foreign_keys=[dispatch_id])
    
    def __repr__(self):
        return f"<BandMessage(id={self.id}, dispatch_id={self.dispatch_id}, sent={self.is_sent})>"


class BandChatRoom(Base):
    """밴드 채팅방 관리"""
    __tablename__ = "band_chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="채팅방 이름")
    band_url = Column(String(500), nullable=False, comment="밴드 URL")
    description = Column(Text, nullable=True, comment="설명")
    is_active = Column(Boolean, default=True, comment="활성화 여부")
    
    # 통계
    last_message_at = Column(DateTime(timezone=True), nullable=True, comment="마지막 메시지 전송 시간")
    total_messages = Column(Integer, default=0, comment="총 메시지 수")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def __repr__(self):
        return f"<BandChatRoom(id={self.id}, name='{self.name}')>"


class BandMessageSchedule(Base):
    """메시지 발송 스케줄"""
    __tablename__ = "band_message_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=False, comment="배차 ID")
    
    # 스케줄 설정
    is_active = Column(Boolean, default=True, comment="스케줄 활성화")
    start_time = Column(DateTime(timezone=True), nullable=False, comment="시작 시간")
    end_time = Column(DateTime(timezone=True), nullable=False, comment="종료 시간")
    
    # 간격 설정 (초)
    min_interval_seconds = Column(Integer, default=180, comment="최소 간격 (초)")  # 3분
    max_interval_seconds = Column(Integer, default=300, comment="최대 간격 (초)")  # 5분
    
    # 통계
    messages_generated = Column(Integer, default=0, comment="생성된 메시지 수")
    last_generated_at = Column(DateTime(timezone=True), nullable=True, comment="마지막 생성 시간")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    # Relationships
    dispatch = relationship("Dispatch", foreign_keys=[dispatch_id])
    
    def __repr__(self):
        return f"<BandMessageSchedule(id={self.id}, dispatch_id={self.dispatch_id}, active={self.is_active})>"
