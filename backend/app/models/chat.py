"""
실시간 채팅 메시지 모델
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class ChatRoom(Base):
    """채팅방 모델"""
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    name = Column(String(255), nullable=False, comment="채팅방 이름")
    room_type = Column(String(50), default="group", comment="채팅방 유형 (direct, group, support)")
    description = Column(Text, nullable=True, comment="채팅방 설명")
    is_active = Column(Boolean, default=True, comment="활성화 여부")
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="생성자 ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")

    # 관계
    creator = relationship("User", foreign_keys=[created_by])
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")
    participants = relationship("ChatParticipant", back_populates="room", cascade="all, delete-orphan")

    # 인덱스
    __table_args__ = (
        Index('idx_chat_room_type', 'room_type'),
        Index('idx_chat_room_active', 'is_active'),
    )

    def __repr__(self):
        return f"<ChatRoom(id={self.id}, name='{self.name}', type='{self.room_type}')>"


class ChatParticipant(Base):
    """채팅방 참가자 모델"""
    __tablename__ = "chat_participants"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False, comment="채팅방 ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="사용자 ID")
    role = Column(String(50), default="member", comment="역할 (admin, member)")
    
    # 마지막 읽은 메시지
    last_read_message_id = Column(Integer, nullable=True, comment="마지막 읽은 메시지 ID")
    last_read_at = Column(DateTime(timezone=True), nullable=True, comment="마지막 읽은 시간")
    
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), comment="참가일시")
    left_at = Column(DateTime(timezone=True), nullable=True, comment="퇴장일시")
    is_active = Column(Boolean, default=True, comment="활성화 여부")

    # 관계
    room = relationship("ChatRoom", back_populates="participants")
    user = relationship("User")

    # 인덱스
    __table_args__ = (
        Index('idx_chat_participant_room', 'room_id'),
        Index('idx_chat_participant_user', 'user_id'),
        Index('idx_chat_participant_active', 'is_active'),
    )

    def __repr__(self):
        return f"<ChatParticipant(room_id={self.room_id}, user_id={self.user_id})>"


class ChatMessage(Base):
    """채팅 메시지 모델"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False, comment="채팅방 ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="발신자 ID")
    
    message = Column(Text, nullable=False, comment="메시지 내용")
    message_type = Column(String(50), default="text", comment="메시지 유형 (text, image, file, system)")
    
    # 파일/이미지 관련
    file_url = Column(String(500), nullable=True, comment="파일 URL")
    file_name = Column(String(255), nullable=True, comment="파일명")
    file_size = Column(Integer, nullable=True, comment="파일 크기 (bytes)")
    
    # 답장 관련
    reply_to_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=True, comment="답장 대상 메시지 ID")
    
    # 읽음 상태
    is_read = Column(Boolean, default=False, comment="읽음 여부")
    read_count = Column(Integer, default=0, comment="읽은 사람 수")
    
    # 삭제/수정
    is_deleted = Column(Boolean, default=False, comment="삭제 여부")
    is_edited = Column(Boolean, default=False, comment="수정 여부")
    edited_at = Column(DateTime(timezone=True), nullable=True, comment="수정일시")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")

    # 관계
    room = relationship("ChatRoom", back_populates="messages")
    user = relationship("User")
    reply_to = relationship("ChatMessage", remote_side=[id], backref="replies")

    # 인덱스
    __table_args__ = (
        Index('idx_chat_message_room', 'room_id'),
        Index('idx_chat_message_user', 'user_id'),
        Index('idx_chat_message_created', 'created_at'),
        Index('idx_chat_message_deleted', 'is_deleted'),
    )

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, room_id={self.room_id}, user_id={self.user_id})>"
