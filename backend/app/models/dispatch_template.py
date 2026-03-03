"""
거래처별 배차 템플릿 모델

거래처마다 고유한 배차 파싱 규칙을 저장하고 관리
"""
from sqlalchemy import String, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, IDMixin, TimestampMixin


class DispatchTemplate(Base, IDMixin, TimestampMixin):
    """거래처별 배차 템플릿"""
    
    __tablename__ = "dispatch_templates"
    
    # 기본 정보
    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        unique=True,
        comment="템플릿 이름 (예: 목우촌, 하림, 사조)"
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="템플릿 설명"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="활성화 여부"
    )
    
    # 식별 패턴
    detection_keywords: Mapped[str] = mapped_column(
        JSON,
        nullable=False,
        comment="배차 텍스트에서 이 템플릿을 식별하는 키워드 목록 (JSON array)"
    )
    
    # 기본 주소
    default_pickup_address: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="기본 상차지 주소"
    )
    
    default_delivery_address: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="기본 하차지 주소"
    )
    
    # 고정 좌표 (API 비용 절감)
    pickup_latitude: Mapped[float] = mapped_column(
        nullable=True,
        comment="상차지 위도 (고정값)"
    )
    
    pickup_longitude: Mapped[float] = mapped_column(
        nullable=True,
        comment="상차지 경도 (고정값)"
    )
    
    delivery_latitude: Mapped[float] = mapped_column(
        nullable=True,
        comment="하차지 위도 (고정값)"
    )
    
    delivery_longitude: Mapped[float] = mapped_column(
        nullable=True,
        comment="하차지 경도 (고정값)"
    )
    
    # 파싱 규칙
    parsing_rules: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="""
        파싱 규칙 (JSON):
        {
            "time_pattern": "정규식 패턴",
            "product_pattern": "정규식 패턴", 
            "tonnage_pattern": "정규식 패턴",
            "temperature_mapping": {
                "냉동": "FROZEN",
                "냉장": "REFRIGERATED"
            },
            "default_temperature": "REFRIGERATED",
            "pallet_calculation": {
                ">=18": 18,
                ">=11": 16,
                ">=5": 10,
                "default": "tonnage * 2"
            },
            "delivery_time_offset_hours": 4,
            "notes_template": "자동 파싱: {client_name} 배차"
        }
        """
    )
    
    # 사용 통계
    usage_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="사용 횟수"
    )
    
    def __repr__(self):
        return f"<DispatchTemplate(id={self.id}, name='{self.name}', active={self.is_active})>"
