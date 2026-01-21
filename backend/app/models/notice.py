from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from .base import Base

class Notice(Base):
    """공지사항 모델"""
    __tablename__ = "notices"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="공지사항 제목")
    content = Column(Text, nullable=False, comment="공지사항 내용")
    author = Column(String(100), nullable=False, comment="작성자")
    image_url = Column(String(500), nullable=True, comment="첨부 이미지 URL")
    is_important = Column(Boolean, default=False, comment="중요 공지 여부")
    views = Column(Integer, default=0, comment="조회수")
    is_active = Column(Boolean, default=True, comment="활성화 여부")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def __repr__(self):
        return f"<Notice(id={self.id}, title='{self.title}', author='{self.author}')>"
