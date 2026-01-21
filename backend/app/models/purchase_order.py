from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Date, Float
from sqlalchemy.sql import func
from .base import Base

class PurchaseOrder(Base):
    """발주서 모델"""
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(50), unique=True, nullable=False, index=True, comment="발주서 번호")
    title = Column(String(200), nullable=False, comment="발주서 제목")
    supplier = Column(String(200), nullable=False, comment="공급업체")
    order_date = Column(Date, nullable=False, comment="발주일")
    delivery_date = Column(Date, nullable=True, comment="희망 납기일")
    total_amount = Column(Float, default=0.0, comment="총 금액")
    status = Column(String(50), default="작성중", comment="상태: 작성중, 발송완료, 승인, 취소")
    content = Column(Text, nullable=True, comment="발주 내용 및 특이사항")
    image_url = Column(String(500), nullable=True, comment="첨부 이미지 URL")
    author = Column(String(100), nullable=False, comment="작성자")
    is_active = Column(Boolean, default=True, comment="활성화 여부")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def __repr__(self):
        return f"<PurchaseOrder(id={self.id}, po_number='{self.po_number}', supplier='{self.supplier}')>"
