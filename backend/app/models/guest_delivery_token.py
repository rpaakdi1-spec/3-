"""
게스트 배송 토큰 모델

1회용 링크로 기사님들이 회원가입 없이 배송 작업을 할 수 있게 함
- 토큰 기반 접근
- 24시간 자동 만료
- 1회 배차당 1개 토큰
"""

from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta
from typing import Optional
import secrets
from .base import Base, IDMixin, TimestampMixin


def generate_guest_token() -> str:
    """게스트 토큰 생성 (32자리 안전한 랜덤 문자열)"""
    return f"GUEST_{datetime.now().strftime('%Y%m%d')}_{secrets.token_urlsafe(16)}"


class GuestDeliveryToken(Base, IDMixin, TimestampMixin):
    """게스트 배송 토큰 테이블"""
    
    __tablename__ = "guest_delivery_tokens"
    
    # 토큰 정보
    token: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="게스트 접근 토큰"
    )
    
    # 배차 정보
    dispatch_id: Mapped[int] = mapped_column(
        ForeignKey("dispatches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="배차 ID"
    )
    
    # 만료 정보
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="토큰 만료 시각"
    )
    
    # 사용 여부
    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="토큰 사용 여부"
    )
    
    # 첫 접속 시각
    first_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="첫 접속 시각"
    )
    
    # 마지막 접속 시각
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="마지막 접속 시각"
    )
    
    # 접속 횟수
    access_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="접속 횟수"
    )
    
    # 기사 전화번호 (선택사항, SMS 발송용)
    driver_phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="기사 전화번호"
    )
    
    # 기사 이름 (선택사항)
    driver_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="기사 이름"
    )
    
    # IP 주소 (보안 로깅용)
    last_ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="마지막 접속 IP"
    )
    
    # Relationships
    dispatch: Mapped["Dispatch"] = relationship("Dispatch", back_populates="guest_tokens")
    
    def __repr__(self):
        return f"<GuestDeliveryToken {self.token[:20]}... for dispatch={self.dispatch_id}>"
    
    @property
    def is_expired(self) -> bool:
        """토큰 만료 여부 확인"""
        return datetime.now() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """토큰 유효성 확인 (만료되지 않고, 사용되지 않음)"""
        return not self.is_expired and not self.is_used
    
    @classmethod
    def create_token(cls, dispatch_id: int, hours_valid: int = 24, 
                     driver_phone: Optional[str] = None, 
                     driver_name: Optional[str] = None) -> "GuestDeliveryToken":
        """
        새 게스트 토큰 생성
        
        Args:
            dispatch_id: 배차 ID
            hours_valid: 토큰 유효 시간 (기본 24시간)
            driver_phone: 기사 전화번호 (선택)
            driver_name: 기사 이름 (선택)
        
        Returns:
            GuestDeliveryToken 인스턴스
        """
        return cls(
            token=generate_guest_token(),
            dispatch_id=dispatch_id,
            expires_at=datetime.now() + timedelta(hours=hours_valid),
            driver_phone=driver_phone,
            driver_name=driver_name
        )
    
    def mark_accessed(self, ip_address: Optional[str] = None):
        """토큰 접속 기록"""
        now = datetime.now()
        if self.first_accessed_at is None:
            self.first_accessed_at = now
        self.last_accessed_at = now
        self.access_count += 1
        if ip_address:
            self.last_ip_address = ip_address
    
    def mark_used(self):
        """토큰 사용 완료 처리"""
        self.is_used = True
