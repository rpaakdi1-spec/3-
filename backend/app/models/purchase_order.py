from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from .base import Base

class PurchaseOrder(Base):
    """발주서 모델 - 간소화 버전 (제목, 내용, 사진 최대 5개)"""
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="발주서 제목")
    content = Column(Text, nullable=True, comment="발주 내용")
    image_urls = Column(Text, nullable=True, comment="첨부 이미지 URL 목록 (JSON 배열, 최대 5개)")
    author = Column(String(100), nullable=False, comment="작성자")
    is_active = Column(Boolean, default=True, comment="활성화 여부")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def __repr__(self):
        return f"<PurchaseOrder(id={self.id}, title='{self.title}', author='{self.author}')>"
