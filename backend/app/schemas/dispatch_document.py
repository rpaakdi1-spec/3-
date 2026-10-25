"""
배차 서류 및 추적 스키마
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """서류 유형"""
    TRANSACTION_STATEMENT = "거래명세표"
    TEMPERATURE_RECORD = "온도기록지"
    SIGNATURE = "서명"
    DELIVERY_PROOF = "배송증빙"
    OTHER = "기타"


class DocumentStage(str, Enum):
    """서류 단계"""
    DEPARTURE = "출발"
    ARRIVAL = "도착"
    IN_TRANSIT = "운송중"


# ===== 서류 업로드 =====

class DocumentUploadRequest(BaseModel):
    """서류 업로드 요청"""
    dispatch_id: int = Field(..., description="배차 ID")
    route_id: Optional[int] = Field(None, description="배차 경로 ID")
    order_id: Optional[int] = Field(None, description="주문 ID")
    document_type: DocumentType = Field(..., description="서류 유형")
    stage: DocumentStage = Field(..., description="서류 단계")
    notes: Optional[str] = Field(None, max_length=500, description="메모")
    location: Optional[str] = Field(None, description="업로드 위치")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="위도")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="경도")
    is_public: bool = Field(True, description="고객 공개 여부")


class DocumentResponse(BaseModel):
    """서류 응답"""
    id: int
    dispatch_id: int
    route_id: Optional[int]
    order_id: Optional[int]
    document_type: DocumentType
    stage: DocumentStage
    file_url: str
    file_name: str
    file_size: int
    mime_type: str
    uploaded_by: int
    uploaded_at_location: Optional[str]
    uploaded_lat: Optional[float]
    uploaded_lon: Optional[float]
    notes: Optional[str]
    is_verified: bool
    verified_by: Optional[int]
    verified_at: Optional[str]
    is_public: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== 추적 번호 =====

class TrackingCreateRequest(BaseModel):
    """추적 번호 생성 요청"""
    dispatch_id: int = Field(..., description="배차 ID")
    customer_name: Optional[str] = Field(None, max_length=200, description="고객사명")
    customer_email: Optional[str] = Field(None, max_length=255, description="고객 이메일")
    customer_phone: Optional[str] = Field(None, max_length=20, description="고객 전화번호")
    notify_on_departure: bool = Field(True, description="출발 시 알림")
    notify_on_arrival: bool = Field(True, description="도착 시 알림")
    notify_on_document_upload: bool = Field(True, description="서류 업로드 시 알림")
    expires_days: Optional[int] = Field(7, ge=1, le=365, description="유효 기간 (일)")


class TrackingResponse(BaseModel):
    """추적 정보 응답"""
    id: int
    dispatch_id: int
    tracking_number: str
    is_active: bool
    expires_at: Optional[str]
    customer_name: Optional[str]
    customer_email: Optional[str]
    customer_phone: Optional[str]
    notify_on_departure: bool
    notify_on_arrival: bool
    notify_on_document_upload: bool
    view_count: int
    last_viewed_at: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== 공개 추적 (고객용) =====

class PublicLocationPoint(BaseModel):
    """위치 포인트"""
    latitude: float
    longitude: float
    timestamp: datetime
    speed: Optional[float] = None
    heading: Optional[float] = None


class PublicRouteStop(BaseModel):
    """경로 정류장"""
    sequence: int
    location_name: str
    address: str
    latitude: float
    longitude: float
    route_type: str
    estimated_arrival_time: Optional[str]
    actual_arrival_time: Optional[str] = None
    estimated_departure_time: Optional[str]
    actual_departure_time: Optional[str] = None
    is_completed: bool = False


class PublicDocument(BaseModel):
    """공개 서류"""
    id: int
    document_type: DocumentType
    stage: DocumentStage
    file_url: str
    file_name: str
    file_size: int
    mime_type: str
    uploaded_at: datetime
    notes: Optional[str]


class PublicTrackingDetail(BaseModel):
    """공개 추적 상세 정보"""
    tracking_number: str
    dispatch_number: str
    dispatch_date: str
    status: str
    
    # 차량 정보 (민감 정보 제외)
    vehicle_number: str
    vehicle_type: Optional[str]
    
    # 기사 정보 (이름만)
    driver_name: Optional[str]
    
    # 현재 위치
    current_location: Optional[PublicLocationPoint]
    
    # 경로 정보
    routes: List[PublicRouteStop]
    
    # 진행률
    progress_percentage: float = Field(0, ge=0, le=100, description="진행률 (%)")
    
    # 예상 도착 시간
    estimated_arrival: Optional[str]
    
    # 서류
    documents: List[PublicDocument] = []
    
    # 통계
    total_distance_km: Optional[float]
    completed_distance_km: Optional[float] = 0
    total_pallets: int = 0
    
    # 알림 설정
    customer_name: Optional[str]
    customer_email: Optional[str]
    
    # 메타
    last_updated: datetime
    view_count: int


# ===== 서류 검증 =====

class DocumentVerifyRequest(BaseModel):
    """서류 검증 요청"""
    is_verified: bool = Field(..., description="검증 여부")
    notes: Optional[str] = Field(None, max_length=500, description="검증 메모")


# ===== 일괄 서류 조회 =====

class DocumentListQuery(BaseModel):
    """서류 목록 조회"""
    dispatch_id: Optional[int] = None
    route_id: Optional[int] = None
    order_id: Optional[int] = None
    document_type: Optional[DocumentType] = None
    stage: Optional[DocumentStage] = None
    is_verified: Optional[bool] = None
    is_public: Optional[bool] = None
    
    limit: int = Field(100, ge=1, le=500)
    offset: int = Field(0, ge=0)


class DocumentListResponse(BaseModel):
    """서류 목록 응답"""
    total: int
    items: List[DocumentResponse]
