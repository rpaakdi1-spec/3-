from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
import json

class PurchaseOrderBase(BaseModel):
    """발주서 기본 스키마 - 다중 이미지 지원 (최대 5개)"""
    title: str = Field(..., max_length=200, description="발주서 제목")
    content: Optional[str] = Field(None, description="발주 내용")
    image_urls: Optional[List[str]] = Field(default=None, max_length=5, description="첨부 이미지 URL 목록 (최대 5개)")
    author: str = Field(..., max_length=100, description="작성자")
    
    @field_validator('image_urls')
    @classmethod
    def validate_image_urls(cls, v):
        if v is not None and len(v) > 5:
            raise ValueError('이미지는 최대 5개까지만 업로드 가능합니다')
        return v

class PurchaseOrderCreate(PurchaseOrderBase):
    """발주서 생성 스키마"""
    pass

class PurchaseOrderUpdate(BaseModel):
    """발주서 수정 스키마"""
    title: Optional[str] = Field(None, max_length=200, description="발주서 제목")
    content: Optional[str] = Field(None, description="발주 내용")
    image_urls: Optional[List[str]] = Field(None, max_length=5, description="첨부 이미지 URL 목록")
    author: Optional[str] = Field(None, max_length=100, description="작성자")
    is_active: Optional[bool] = Field(None, description="활성화 여부")
    
    @field_validator('image_urls')
    @classmethod
    def validate_image_urls(cls, v):
        if v is not None and len(v) > 5:
            raise ValueError('이미지는 최대 5개까지만 업로드 가능합니다')
        return v

class PurchaseOrderResponse(BaseModel):
    """발주서 응답 스키마"""
    id: int
    title: str
    content: Optional[str] = None
    image_urls: Optional[List[str]] = None
    author: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}
    
    @model_validator(mode='before')
    @classmethod
    def parse_image_urls(cls, data):
        """데이터베이스에서 가져온 JSON 문자열을 파싱"""
        if isinstance(data, dict):
            # dict인 경우 (이미 파싱된 경우)
            if 'image_urls' in data and isinstance(data['image_urls'], str):
                try:
                    data['image_urls'] = json.loads(data['image_urls']) if data['image_urls'] else None
                except (json.JSONDecodeError, TypeError):
                    data['image_urls'] = None
        else:
            # SQLAlchemy 모델 객체인 경우
            if hasattr(data, 'image_urls') and isinstance(data.image_urls, str):
                try:
                    parsed_urls = json.loads(data.image_urls) if data.image_urls else None
                    # 새로운 dict를 만들어서 반환
                    data_dict = {
                        'id': data.id,
                        'title': data.title,
                        'content': data.content,
                        'image_urls': parsed_urls,
                        'author': data.author,
                        'is_active': data.is_active,
                        'created_at': data.created_at,
                        'updated_at': data.updated_at
                    }
                    return data_dict
                except (json.JSONDecodeError, TypeError):
                    pass
        return data

class PurchaseOrderListResponse(BaseModel):
    """발주서 목록 응답 스키마"""
    total: int
    items: list[PurchaseOrderResponse]
