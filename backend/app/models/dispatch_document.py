"""
배차 서류 관리 모델

기사님이 업로드하는 배송 관련 서류:
- 거래명세표 (출발/도착)
- 온도기록지 (출발/도착)
- 서명/확인서
"""

from enum import Enum
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import Base, IDMixin, TimestampMixin


class DocumentType(str, Enum):
    """서류 유형"""
    TRANSACTION_STATEMENT = "거래명세표"  # 거래명세표
    TEMPERATURE_RECORD = "온도기록지"    # 온도기록지
    SIGNATURE = "서명"                  # 서명/확인서
    DELIVERY_PROOF = "배송증빙"         # 기타 배송 증빙
    OTHER = "기타"


class DocumentStage(str, Enum):
    """서류 단계"""
    DEPARTURE = "출발"    # 출발 시
    ARRIVAL = "도착"      # 도착 시
    IN_TRANSIT = "운송중"  # 운송 중


class DispatchDocument(Base, IDMixin, TimestampMixin):
    """배차 서류 테이블"""
    
    __tablename__ = "dispatch_documents"
    
    # 배차 정보
    dispatch_id: Mapped[int] = mapped_column(
        ForeignKey("dispatches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="배차 ID"
    )
    
    # 경로 정보 (특정 경로에 대한 서류인 경우)
    route_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("dispatch_routes.id", ondelete="CASCADE"),
        index=True,
        comment="배차 경로 ID"
    )
    
    # 주문 정보 (특정 주문에 대한 서류인 경우)
    order_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL"),
        index=True,
        comment="주문 ID"
    )
    
    # 서류 유형 및 단계
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType),
        nullable=False,
        index=True,
        comment="서류 유형"
    )
    
    stage: Mapped[DocumentStage] = mapped_column(
        SQLEnum(DocumentStage),
        nullable=False,
        index=True,
        comment="서류 단계"
    )
    
    # 파일 정보
    file_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="파일 URL"
    )
    
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="원본 파일명"
    )
    
    file_size: Mapped[int] = mapped_column(
        Integer,
        comment="파일 크기 (bytes)"
    )
    
    mime_type: Mapped[str] = mapped_column(
        String(100),
        comment="MIME 타입"
    )
    
    # 업로드 정보
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="업로드한 사용자 ID (기사)"
    )
    
    uploaded_at_location: Mapped[Optional[str]] = mapped_column(
        String(500),
        comment="업로드 위치 (주소)"
    )
    
    uploaded_lat: Mapped[Optional[float]] = mapped_column(
        comment="업로드 위도"
    )
    
    uploaded_lon: Mapped[Optional[float]] = mapped_column(
        comment="업로드 경도"
    )
    
    # 추가 정보
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="메모"
    )
    
    is_verified: Mapped[bool] = mapped_column(
        default=False,
        comment="확인 여부"
    )
    
    verified_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="확인한 사용자 ID"
    )
    
    verified_at: Mapped[Optional[str]] = mapped_column(
        String(30),
        comment="확인 시간"
    )
    
    # 고객 공개 여부
    is_public: Mapped[bool] = mapped_column(
        default=True,
        comment="고객 공개 여부"
    )
    
    # Relationships
    dispatch = relationship("Dispatch", backref="documents")
    route = relationship("DispatchRoute", backref="documents")
    order = relationship("Order", backref="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by], backref="uploaded_documents")
    verifier = relationship("User", foreign_keys=[verified_by], backref="verified_documents")
    
    def __repr__(self):
        return f"<DispatchDocument(dispatch_id={self.dispatch_id}, type={self.document_type}, stage={self.stage})>"


class DispatchTracking(Base, IDMixin, TimestampMixin):
    """배차 추적 정보 (고객 공개용)"""
    
    __tablename__ = "dispatch_tracking"
    
    # 배차 정보
    dispatch_id: Mapped[int] = mapped_column(
        ForeignKey("dispatches.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="배차 ID"
    )
    
    # 추적 번호 (공개용, 고유)
    tracking_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="추적 번호"
    )
    
    # 공개 설정
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment="추적 활성화 여부"
    )
    
    expires_at: Mapped[Optional[str]] = mapped_column(
        String(30),
        comment="만료 일시"
    )
    
    # 고객 정보 (옵션)
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        comment="고객사명"
    )
    
    customer_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="고객 이메일"
    )
    
    customer_phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="고객 전화번호"
    )
    
    # 알림 설정
    notify_on_departure: Mapped[bool] = mapped_column(
        default=True,
        comment="출발 시 알림"
    )
    
    notify_on_arrival: Mapped[bool] = mapped_column(
        default=True,
        comment="도착 시 알림"
    )
    
    notify_on_document_upload: Mapped[bool] = mapped_column(
        default=True,
        comment="서류 업로드 시 알림"
    )
    
    # 조회 통계
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="조회 수"
    )
    
    last_viewed_at: Mapped[Optional[str]] = mapped_column(
        String(30),
        comment="최근 조회 일시"
    )
    
    # 메모
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="메모"
    )
    
    # Relationships
    dispatch = relationship("Dispatch", backref="tracking")
    
    def __repr__(self):
        return f"<DispatchTracking(tracking_number={self.tracking_number}, dispatch_id={self.dispatch_id})>"
