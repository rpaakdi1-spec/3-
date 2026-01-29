from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# ==================== BandMessage 스키마 ====================

class BandMessageBase(BaseModel):
    """밴드 메시지 기본 스키마"""
    dispatch_id: int = Field(..., description="배차 ID")
    message_content: str = Field(..., description="메시지 내용")
    message_type: str = Field(default="freight_dispatch", description="메시지 타입")

class BandMessageCreate(BandMessageBase):
    """밴드 메시지 생성 스키마"""
    scheduled_for: Optional[datetime] = Field(None, description="예약 전송 시간")

class BandMessageUpdate(BaseModel):
    """밴드 메시지 수정 스키마"""
    is_sent: Optional[bool] = Field(None, description="전송 여부")
    sent_at: Optional[datetime] = Field(None, description="전송 일시")

class BandMessageResponse(BaseModel):
    """밴드 메시지 응답 스키마"""
    id: int
    dispatch_id: int
    message_content: str
    message_type: str
    is_sent: bool
    sent_at: Optional[datetime] = None
    generated_at: datetime
    scheduled_for: Optional[datetime] = None
    variation_seed: Optional[int] = None
    
    model_config = {"from_attributes": True}

class BandMessageListResponse(BaseModel):
    """밴드 메시지 목록 응답 스키마"""
    total: int
    items: List[BandMessageResponse]


# ==================== BandChatRoom 스키마 ====================

class BandChatRoomBase(BaseModel):
    """밴드 채팅방 기본 스키마"""
    name: str = Field(..., max_length=200, description="채팅방 이름")
    band_url: str = Field(..., max_length=500, description="밴드 URL")
    description: Optional[str] = Field(None, description="설명")

class BandChatRoomCreate(BandChatRoomBase):
    """밴드 채팅방 생성 스키마"""
    pass

class BandChatRoomUpdate(BaseModel):
    """밴드 채팅방 수정 스키마"""
    name: Optional[str] = Field(None, max_length=200, description="채팅방 이름")
    band_url: Optional[str] = Field(None, max_length=500, description="밴드 URL")
    description: Optional[str] = Field(None, description="설명")
    is_active: Optional[bool] = Field(None, description="활성화 여부")

class BandChatRoomResponse(BaseModel):
    """밴드 채팅방 응답 스키마"""
    id: int
    name: str
    band_url: str
    description: Optional[str] = None
    is_active: bool
    last_message_at: Optional[datetime] = None
    total_messages: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class BandChatRoomListResponse(BaseModel):
    """밴드 채팅방 목록 응답 스키마"""
    total: int
    items: List[BandChatRoomResponse]


# ==================== BandMessageSchedule 스키마 ====================

class BandMessageScheduleBase(BaseModel):
    """메시지 스케줄 기본 스키마"""
    dispatch_id: int = Field(..., description="배차 ID")
    start_time: datetime = Field(..., description="시작 시간")
    end_time: datetime = Field(..., description="종료 시간")
    min_interval_seconds: int = Field(default=180, ge=60, le=600, description="최소 간격 (초, 1-10분)")
    max_interval_seconds: int = Field(default=300, ge=120, le=900, description="최대 간격 (초, 2-15분)")

class BandMessageScheduleCreate(BandMessageScheduleBase):
    """메시지 스케줄 생성 스키마"""
    pass

class BandMessageScheduleUpdate(BaseModel):
    """메시지 스케줄 수정 스키마"""
    is_active: Optional[bool] = Field(None, description="스케줄 활성화")
    start_time: Optional[datetime] = Field(None, description="시작 시간")
    end_time: Optional[datetime] = Field(None, description="종료 시간")
    min_interval_seconds: Optional[int] = Field(None, ge=60, le=600, description="최소 간격 (초)")
    max_interval_seconds: Optional[int] = Field(None, ge=120, le=900, description="최대 간격 (초)")

class BandMessageScheduleResponse(BaseModel):
    """메시지 스케줄 응답 스키마"""
    id: int
    dispatch_id: int
    is_active: bool
    start_time: datetime
    end_time: datetime
    min_interval_seconds: int
    max_interval_seconds: int
    messages_generated: int
    last_generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class BandMessageScheduleListResponse(BaseModel):
    """메시지 스케줄 목록 응답 스키마"""
    total: int
    items: List[BandMessageScheduleResponse]


# ==================== 메시지 생성 요청/응답 ====================

class MessageGenerateRequest(BaseModel):
    """메시지 생성 요청"""
    dispatch_id: int = Field(..., description="배차 ID")
    chat_room_ids: Optional[List[int]] = Field(None, description="대상 채팅방 ID 목록")

class MessageGenerateResponse(BaseModel):
    """메시지 생성 응답"""
    message: str = Field(..., description="생성된 메시지")
    dispatch_id: int
    generated_at: datetime
    next_schedule: Optional[datetime] = Field(None, description="다음 예정 시간")
