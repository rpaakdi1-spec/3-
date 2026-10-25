"""
게스트 배송 API

회원가입 없이 1회용 링크로 배송 작업 수행:
- 토큰 생성
- 게스트 인증
- GPS 위치 전송
- 서류 업로드
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.models.guest_delivery_token import GuestDeliveryToken, generate_guest_token
from app.models.dispatch import Dispatch, DispatchRoute
from app.models.dispatch_document import DispatchDocument, DocumentType, DocumentStage
from app.models.vehicle_location import VehicleLocation

router = APIRouter()


# ===== Request/Response Models =====

class GuestTokenCreateRequest(BaseModel):
    """게스트 토큰 생성 요청"""
    dispatch_id: int
    driver_phone: Optional[str] = None
    driver_name: Optional[str] = None
    hours_valid: int = 24


class GuestTokenResponse(BaseModel):
    """게스트 토큰 응답"""
    token: str
    dispatch_id: int
    expires_at: str
    guest_url: str
    qr_code_url: Optional[str] = None


class GuestDeliveryInfo(BaseModel):
    """게스트 배송 정보"""
    dispatch_number: str
    dispatch_date: str
    vehicle_plate: Optional[str] = None
    total_orders: int
    total_distance_km: Optional[float] = None
    planned_start_time: Optional[str] = None
    planned_end_time: Optional[str] = None
    routes: List[dict]
    status: str
    is_expired: bool


class GuestLocationUpdate(BaseModel):
    """게스트 위치 업데이트"""
    latitude: float
    longitude: float
    accuracy: Optional[float] = None


class GuestDocumentUploadResponse(BaseModel):
    """게스트 서류 업로드 응답"""
    document_id: int
    file_url: str
    document_type: str
    stage: str
    uploaded_at: str


# ===== Helper Functions =====

async def get_guest_token(token: str, db: Session) -> GuestDeliveryToken:
    """게스트 토큰 조회 및 검증"""
    guest_token = db.query(GuestDeliveryToken).filter(
        GuestDeliveryToken.token == token
    ).first()
    
    if not guest_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid token"
        )
    
    if guest_token.is_expired:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Token has expired"
        )
    
    return guest_token


# ===== API Endpoints =====

@router.post(
    "/guest/delivery/create-token",
    response_model=GuestTokenResponse,
    summary="게스트 토큰 생성",
    description="배차에 대한 게스트 접근 토큰 생성 (관리자용)"
)
async def create_guest_token(
    request: GuestTokenCreateRequest,
    db: Session = Depends(get_db)
):
    """
    게스트 배송 토큰 생성
    
    - 배차 ID로 1회용 링크 생성
    - 기사 정보 선택적 등록
    - 유효 기간 설정 (기본 24시간)
    """
    # 배차 존재 확인
    dispatch = db.query(Dispatch).filter(Dispatch.id == request.dispatch_id).first()
    if not dispatch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispatch {request.dispatch_id} not found"
        )
    
    # 토큰 생성
    guest_token = GuestDeliveryToken.create_token(
        dispatch_id=request.dispatch_id,
        hours_valid=request.hours_valid,
        driver_phone=request.driver_phone,
        driver_name=request.driver_name
    )
    
    db.add(guest_token)
    db.commit()
    db.refresh(guest_token)
    
    # 게스트 URL 생성
    guest_url = f"/guest/delivery/{guest_token.token}"
    
    return GuestTokenResponse(
        token=guest_token.token,
        dispatch_id=guest_token.dispatch_id,
        expires_at=guest_token.expires_at.isoformat(),
        guest_url=guest_url
    )


@router.get(
    "/guest/delivery/{token}",
    response_model=GuestDeliveryInfo,
    summary="게스트 배송 정보 조회",
    description="토큰으로 배송 정보 조회 (인증 불필요)"
)
async def get_guest_delivery_info(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    게스트 배송 정보 조회
    
    - 토큰으로 배차 정보 확인
    - 경로 정보 제공
    - 접속 기록
    """
    # 토큰 검증
    guest_token = await get_guest_token(token, db)
    
    # 접속 기록
    ip_address = request.client.host if request.client else None
    guest_token.mark_accessed(ip_address)
    db.commit()
    
    # 배차 정보 조회
    dispatch = db.query(Dispatch).filter(Dispatch.id == guest_token.dispatch_id).first()
    if not dispatch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch not found"
        )
    
    # 경로 정보
    routes = []
    for route in dispatch.routes:
        routes.append({
            "sequence": route.sequence,
            "type": route.route_type.value,
            "location_name": route.location_name,
            "address": route.address,
            "latitude": route.latitude,
            "longitude": route.longitude,
            "estimated_arrival_time": route.estimated_arrival_time,
            "notes": route.notes
        })
    
    return GuestDeliveryInfo(
        dispatch_number=dispatch.dispatch_number,
        dispatch_date=str(dispatch.dispatch_date),
        vehicle_plate=dispatch.vehicle.license_plate if dispatch.vehicle else None,
        total_orders=dispatch.total_orders,
        total_distance_km=dispatch.total_distance_km,
        planned_start_time=dispatch.planned_start_time,
        planned_end_time=dispatch.planned_end_time,
        routes=routes,
        status=dispatch.status.value,
        is_expired=guest_token.is_expired
    )


@router.post(
    "/guest/delivery/{token}/location",
    status_code=status.HTTP_201_CREATED,
    summary="게스트 GPS 위치 업데이트",
    description="토큰으로 GPS 위치 전송 (인증 불필요)"
)
async def update_guest_location(
    token: str,
    location: GuestLocationUpdate,
    db: Session = Depends(get_db)
):
    """
    게스트 GPS 위치 업데이트
    
    - 토큰으로 인증
    - 실시간 위치 저장
    - 배차의 차량 ID와 연동
    """
    # 토큰 검증
    guest_token = await get_guest_token(token, db)
    
    # 배차 정보 조회
    dispatch = db.query(Dispatch).filter(Dispatch.id == guest_token.dispatch_id).first()
    if not dispatch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch not found"
        )
    
    if not dispatch.vehicle_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dispatch has no vehicle assigned"
        )
    
    # 위치 정보 저장
    vehicle_location = VehicleLocation(
        vehicle_id=dispatch.vehicle_id,
        dispatch_id=dispatch.id,
        latitude=location.latitude,
        longitude=location.longitude,
        accuracy=location.accuracy,
        timestamp=datetime.now()
    )
    
    db.add(vehicle_location)
    db.commit()
    
    return {
        "status": "success",
        "message": "Location updated",
        "latitude": location.latitude,
        "longitude": location.longitude,
        "timestamp": vehicle_location.timestamp.isoformat()
    }


@router.post(
    "/guest/delivery/{token}/documents",
    response_model=GuestDocumentUploadResponse,
    summary="게스트 서류 업로드",
    description="토큰으로 출발/도착 서류 업로드 (인증 불필요)"
)
async def upload_guest_document(
    token: str,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    stage: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    게스트 서류 업로드
    
    - 거래명세표, 온도기록지 업로드
    - 출발/도착 단계 구분
    - 파일 저장 및 DB 기록
    """
    # 토큰 검증
    guest_token = await get_guest_token(token, db)
    
    # 파일 저장 로직 (기존 dispatch_documents.py와 동일)
    import os
    import hashlib
    from datetime import datetime
    
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads/dispatch_documents")
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # 디렉터리 확인
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # 파일 크기 확인
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 파일 해시 생성
    file_hash = hashlib.sha256(file_content).hexdigest()[:16]
    file_extension = os.path.splitext(file.filename)[1]
    saved_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_hash}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    # 파일 저장
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    file_url = f"/uploads/dispatch_documents/{saved_filename}"
    
    # DB 저장
    document = DispatchDocument(
        dispatch_id=guest_token.dispatch_id,
        document_type=DocumentType(document_type),
        stage=DocumentStage(stage),
        file_path=file_path,
        file_url=file_url,
        file_name=file.filename,
        file_size=len(file_content),
        mime_type=file.content_type,
        notes=notes
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return GuestDocumentUploadResponse(
        document_id=document.id,
        file_url=file_url,
        document_type=document_type,
        stage=stage,
        uploaded_at=document.created_at.isoformat()
    )


@router.get(
    "/guest/delivery/{token}/track",
    summary="게스트 배송 실시간 위치 추적 (관리자용)",
    description="토큰으로 게스트 기사의 실시간 GPS 위치 조회 (관리자 화면용)"
)
async def track_guest_delivery_location(
    token: str,
    db: Session = Depends(get_db)
):
    """
    게스트 기사 실시간 위치 추적 (관리자용)
    
    - 최근 GPS 위치 반환
    - 위치 이력 경로 반환 (최근 50건)
    - 배차 정보, 기사 정보 포함
    """
    # 토큰 조회 (만료 여부 상관없이 관리자는 조회 가능)
    guest_token = db.query(GuestDeliveryToken).filter(
        GuestDeliveryToken.token == token
    ).first()
    
    if not guest_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid token"
        )
    
    # 배차 정보 조회
    dispatch = db.query(Dispatch).filter(Dispatch.id == guest_token.dispatch_id).first()
    if not dispatch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch not found"
        )
    
    if not dispatch.vehicle_id:
        return {
            "token": token,
            "dispatch_id": guest_token.dispatch_id,
            "dispatch_number": dispatch.dispatch_number,
            "driver_name": guest_token.driver_name,
            "driver_phone": guest_token.driver_phone,
            "current_location": None,
            "location_history": [],
            "routes": [],
            "last_updated": None,
            "is_active": not guest_token.is_expired and not guest_token.is_used,
            "message": "차량이 배정되지 않았습니다"
        }
    
    # 최근 위치 조회
    latest_location = db.query(VehicleLocation).filter(
        VehicleLocation.vehicle_id == dispatch.vehicle_id,
        VehicleLocation.dispatch_id == dispatch.id
    ).order_by(VehicleLocation.timestamp.desc()).first()
    
    # 위치 이력 조회 (최근 50건)
    location_history = db.query(VehicleLocation).filter(
        VehicleLocation.vehicle_id == dispatch.vehicle_id,
        VehicleLocation.dispatch_id == dispatch.id
    ).order_by(VehicleLocation.timestamp.desc()).limit(50).all()
    
    current_location = None
    if latest_location:
        current_location = {
            "latitude": latest_location.latitude,
            "longitude": latest_location.longitude,
            "accuracy": latest_location.accuracy,
            "timestamp": latest_location.timestamp.isoformat() if latest_location.timestamp else None
        }
    
    history = []
    for loc in reversed(location_history):  # 오래된 것부터 정렬
        history.append({
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "accuracy": loc.accuracy,
            "timestamp": loc.timestamp.isoformat() if loc.timestamp else None
        })
    
    # 경로 정보
    routes = []
    for route in dispatch.routes:
        routes.append({
            "sequence": route.sequence,
            "type": route.route_type.value,
            "location_name": route.location_name,
            "address": route.address,
            "latitude": route.latitude,
            "longitude": route.longitude,
            "estimated_arrival_time": route.estimated_arrival_time,
            "notes": route.notes
        })
    
    return {
        "token": token,
        "dispatch_id": guest_token.dispatch_id,
        "dispatch_number": dispatch.dispatch_number,
        "dispatch_date": str(dispatch.dispatch_date),
        "driver_name": guest_token.driver_name,
        "driver_phone": guest_token.driver_phone,
        "vehicle_plate": dispatch.vehicle.license_plate if dispatch.vehicle else None,
        "current_location": current_location,
        "location_history": history,
        "routes": routes,
        "last_updated": current_location["timestamp"] if current_location else None,
        "is_active": not guest_token.is_expired and not guest_token.is_used,
        "access_count": guest_token.access_count,
        "first_accessed_at": guest_token.first_accessed_at.isoformat() if guest_token.first_accessed_at else None,
        "expires_at": guest_token.expires_at.isoformat()
    }


@router.post(
    "/guest/delivery/{token}/complete",
    summary="게스트 배송 완료",
    description="배송 완료 처리 및 토큰 사용 완료"
)
async def complete_guest_delivery(
    token: str,
    db: Session = Depends(get_db)
):
    """
    게스트 배송 완료
    
    - 배송 완료 처리
    - 토큰 사용 완료 마킹
    """
    # 토큰 검증
    guest_token = await get_guest_token(token, db)
    
    # 배차 상태 업데이트
    dispatch = db.query(Dispatch).filter(Dispatch.id == guest_token.dispatch_id).first()
    if dispatch:
        from app.models.dispatch import DispatchStatus
        dispatch.status = DispatchStatus.COMPLETED
    
    # 토큰 사용 완료
    guest_token.mark_used()
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Delivery completed",
        "dispatch_id": guest_token.dispatch_id
    }
