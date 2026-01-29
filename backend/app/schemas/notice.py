from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class NoticeBase(BaseModel):
    """공지사항 기본 스키마"""
    title: str = Field(..., max_length=200, description="공지사항 제목")
    content: str = Field(..., description="공지사항 내용")
    author: str = Field(..., max_length=100, description="작성자")
    image_url: Optional[str] = Field(None, max_length=500, description="첨부 이미지 URL")
    is_important: bool = Field(default=False, description="중요 공지 여부")

class NoticeCreate(NoticeBase):
    """공지사항 생성 스키마"""
    pass

class NoticeUpdate(BaseModel):
    """공지사항 수정 스키마"""
    title: Optional[str] = Field(None, max_length=200, description="공지사항 제목")
    content: Optional[str] = Field(None, description="공지사항 내용")
    author: Optional[str] = Field(None, max_length=100, description="작성자")
    image_url: Optional[str] = Field(None, max_length=500, description="첨부 이미지 URL")
    is_important: Optional[bool] = Field(None, description="중요 공지 여부")
    is_active: Optional[bool] = Field(None, description="활성화 여부")

class NoticeResponse(NoticeBase):
    """공지사항 응답 스키마"""
    id: int
    views: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class NoticeListResponse(BaseModel):
    """공지사항 목록 응답 스키마"""
    total: int
    items: list[NoticeResponse]
