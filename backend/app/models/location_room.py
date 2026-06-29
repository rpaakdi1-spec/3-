"""
위치공유 방(Room) 모델

배차와 독립적으로 방을 생성하여 기사 위치를 공유하는 기능:
- 관리자가 방 생성 → 고유 코드 발급
- 기사: 방 코드로 입장 → GPS 자동 전송
- 고객사: 고객용 링크로 실시간 위치 조회
- 기사: 출발/도착 시 거래명세표, 온도기록지 사진 업로드
"""

from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean, Text, Float, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta
from typing import Optional, List
import secrets
from enum import Enum
from .base import Base, IDMixin, TimestampMixin


class RoomStatus(str, Enum):
    """방 상태"""
    WAITING = "대기중"        # 기사 미입장
    ACTIVE = "진행중"         # 기사 입장 후 운행 중
    COMPLETED = "완료"        # 운행 완료
    CANCELLED = "취소"        # 취소됨


class RoomDocumentType(str, Enum):
    """문서 유형"""
    TRANSACTION_STATEMENT = "거래명세표"
    TEMPERATURE_RECORD = "온도기록지"
    OTHER = "기타"


class RoomDocumentStage(str, Enum):
    """문서 단계"""
    DEPARTURE = "출발"
    ARRIVAL = "도착"


def generate_room_code() -> str:
    """방 코드 생성 (8자리 대문자+숫자)"""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))


def generate_client_token() -> str:
    """고객사용 조회 토큰 생성"""
    return f"CLT_{secrets.token_urlsafe(20)}"


def generate_driver_token() -> str:
    """기사용 입장 토큰 생성"""
    return f"DRV_{secrets.token_urlsafe(20)}"


class LocationRoom(Base, IDMixin, TimestampMixin):
    """위치공유 방 테이블"""

    __tablename__ = "location_rooms"

    # 방 기본 정보
    room_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="방 입장 코드 (기사용)"
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="방 제목 (예: 2026-03-13 서울→부산 냉동운송)"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="방 설명"
    )

    # 상태
    status: Mapped[RoomStatus] = mapped_column(
        SQLEnum(RoomStatus, native_enum=False, length=20),
        default=RoomStatus.WAITING,
        nullable=False,
        index=True,
        comment="방 상태"
    )

    # 생성자 정보
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="생성한 관리자 ID"
    )

    # 기사 정보 (입력용)
    driver_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="기사 이름"
    )

    driver_phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="기사 전화번호"
    )

    vehicle_plate: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="차량 번호"
    )

    # 고객사 정보
    client_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="고객사명"
    )

    # 토큰들
    driver_token: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="기사용 접근 토큰 (URL 공유용)"
    )

    client_token: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="고객사용 조회 토큰"
    )

    # 만료 설정
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="방 만료 시각 (None이면 무제한)"
    )

    # 기사 입장 정보
    driver_joined_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="기사 최초 입장 시각"
    )

    driver_last_seen: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="기사 마지막 활동 시각"
    )

    # 완료 정보
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="완료 처리 시각"
    )

    # ── 상차지 정보 ──────────────────────────────────────────
    loading_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="상차지 명칭 (예: 김해센터)"
    )
    loading_address: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="상차지 주소"
    )
    loading_lat: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="상차지 위도"
    )
    loading_lng: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="상차지 경도"
    )

    # ── 하차지 정보 (복수 가능, 최초 1개만 자동체크) ────────
    unloading_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="하차지 명칭 (예: 광주저온)"
    )
    unloading_address: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="하차지 주소"
    )
    unloading_lat: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="하차지 위도"
    )
    unloading_lng: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="하차지 경도"
    )

    # ── 운행 타임라인 자동기록 ────────────────────────────────
    # 상차지 도착: 차량이 상차지 반경(geofence) 내로 최초 진입한 시각
    arrived_at_loading: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="상차지 도착 시각"
    )
    # 상차지 출차: 차량이 상차지 반경을 벗어난 시각 (상차 완료)
    departed_loading: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="상차지 출차 시각"
    )
    # 하차지 도착: 차량이 하차지 반경 내로 최초 진입한 시각
    arrived_at_unloading: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="하차지 도착 시각"
    )
    # 하차지 출차(하차 완료): 차량이 하차지 반경을 벗어난 시각
    departed_unloading: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="하차지 출차(완료) 시각"
    )

    # geofence 내부 여부 (중복 트리거 방지용 내부 플래그)
    _in_loading_zone: Mapped[bool] = mapped_column(
        "in_loading_zone", Boolean, default=False, nullable=False,
        comment="현재 상차지 반경 내 여부"
    )
    _in_unloading_zone: Mapped[bool] = mapped_column(
        "in_unloading_zone", Boolean, default=False, nullable=False,
        comment="현재 하차지 반경 내 여부"
    )

    # GPS 최근 위치 (빠른 조회용 캐시)
    last_latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="마지막 위도"
    )

    last_longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="마지막 경도"
    )

    last_location_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="마지막 위치 수신 시각"
    )

    # 고객사 조회 통계
    client_view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="고객사 조회 횟수"
    )

    # 메모
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="관리자 메모"
    )

    # Relationships
    creator = relationship("User", foreign_keys=[created_by], backref="created_rooms")
    locations: Mapped[List["RoomLocation"]] = relationship(
        "RoomLocation", back_populates="room", cascade="all, delete-orphan",
        order_by="RoomLocation.recorded_at"
    )
    documents: Mapped[List["RoomDocument"]] = relationship(
        "RoomDocument", back_populates="room", cascade="all, delete-orphan",
        order_by="RoomDocument.created_at"
    )

    def __repr__(self):
        return f"<LocationRoom {self.room_code}: {self.title} [{self.status}]>"

    @staticmethod
    def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """두 좌표 사이의 거리(미터) 계산 (Haversine)"""
        import math
        R = 6_371_000  # 지구 반지름(m)
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lng2 - lng1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at.replace(tzinfo=None) if self.expires_at.tzinfo else datetime.now() > self.expires_at

    @classmethod
    def create_room(
        cls,
        title: str,
        created_by: Optional[int] = None,
        description: Optional[str] = None,
        driver_name: Optional[str] = None,
        driver_phone: Optional[str] = None,
        vehicle_plate: Optional[str] = None,
        client_name: Optional[str] = None,
        hours_valid: Optional[int] = 48,
        notes: Optional[str] = None,
        # 상차지
        loading_name: Optional[str] = None,
        loading_address: Optional[str] = None,
        loading_lat: Optional[float] = None,
        loading_lng: Optional[float] = None,
        # 하차지
        unloading_name: Optional[str] = None,
        unloading_address: Optional[str] = None,
        unloading_lat: Optional[float] = None,
        unloading_lng: Optional[float] = None,
    ) -> "LocationRoom":
        """새 방 생성"""
        expires_at = None
        if hours_valid:
            expires_at = datetime.now() + timedelta(hours=hours_valid)

        return cls(
            room_code=generate_room_code(),
            title=title,
            status=RoomStatus.WAITING,
            description=description,
            driver_name=driver_name,
            driver_phone=driver_phone,
            vehicle_plate=vehicle_plate,
            client_name=client_name,
            driver_token=generate_driver_token(),
            client_token=generate_client_token(),
            expires_at=expires_at,
            created_by=created_by,
            notes=notes,
            loading_name=loading_name,
            loading_address=loading_address,
            loading_lat=loading_lat,
            loading_lng=loading_lng,
            unloading_name=unloading_name,
            unloading_address=unloading_address,
            unloading_lat=unloading_lat,
            unloading_lng=unloading_lng,
            _in_loading_zone=False,
            _in_unloading_zone=False,
        )


class RoomLocation(Base, IDMixin):
    """방 위치 이력"""

    __tablename__ = "room_locations"

    room_id: Mapped[int] = mapped_column(
        ForeignKey("location_rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="방 ID"
    )

    latitude: Mapped[float] = mapped_column(Float, nullable=False, comment="위도")
    longitude: Mapped[float] = mapped_column(Float, nullable=False, comment="경도")
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="GPS 정확도(m)")
    speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="속도(km/h)")
    heading: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="방향(도)")
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="역지오코딩 주소")

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="기록 시각"
    )

    # Relationships
    room: Mapped["LocationRoom"] = relationship("LocationRoom", back_populates="locations")


class RoomDocument(Base, IDMixin, TimestampMixin):
    """방 문서 (사진 업로드)"""

    __tablename__ = "room_documents"

    room_id: Mapped[int] = mapped_column(
        ForeignKey("location_rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="방 ID"
    )

    # 문서 분류
    document_type: Mapped[RoomDocumentType] = mapped_column(
        SQLEnum(RoomDocumentType, native_enum=False, length=30),
        nullable=False,
        comment="문서 유형"
    )

    stage: Mapped[RoomDocumentStage] = mapped_column(
        SQLEnum(RoomDocumentStage, native_enum=False, length=10),
        nullable=False,
        comment="단계 (출발/도착)"
    )

    # 파일 정보
    file_url: Mapped[str] = mapped_column(String(500), nullable=False, comment="파일 URL")
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="서버 파일 경로")
    file_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="원본 파일명")
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="파일 크기(bytes)")
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="MIME 타입")

    # 업로드 위치
    uploaded_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="업로드 위도")
    uploaded_lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="업로드 경도")

    # 메모
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="메모")

    # Relationships
    room: Mapped["LocationRoom"] = relationship("LocationRoom", back_populates="documents")

    def __repr__(self):
        return f"<RoomDocument room={self.room_id} {self.document_type} {self.stage}>"
