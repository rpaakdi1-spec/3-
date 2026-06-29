"""
배차 템플릿 모델
Dispatch Template Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class DispatchTemplate(Base):
    """배차 파싱 템플릿 모델 (자동 파싱 규칙용)"""
    __tablename__ = "dispatch_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 감지 키워드 (JSON 배열)
    detection_keywords = Column(JSON, nullable=False)
    
    # 기본 주소
    default_pickup_address = Column(String(500))
    default_delivery_address = Column(String(500))
    
    # 좌표
    pickup_latitude = Column(Float)
    pickup_longitude = Column(Float)
    delivery_latitude = Column(Float)
    delivery_longitude = Column(Float)
    
    # 파싱 규칙 (JSON)
    parsing_rules = Column(JSON, nullable=False, default=dict)
    
    # 메타 정보
    usage_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DispatchTemplate(id={self.id}, name='{self.name}')>"


class DispatchFormTemplate(Base):
    """배차 폼 템플릿 모델 (배차 일괄 등록용)"""
    __tablename__ = "dispatch_form_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    client_name = Column(String(200), nullable=False, index=True)
    category = Column(String(100), index=True)
    description = Column(Text)
    
    # 템플릿 데이터 (JSON)
    template_data = Column(JSON, nullable=False)
    
    # 메타 정보
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    is_favorite = Column(Boolean, default=False, index=True)
    
    # 생성자 정보
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<DispatchFormTemplate(id={self.id}, name='{self.name}', client='{self.client_name}')>"
