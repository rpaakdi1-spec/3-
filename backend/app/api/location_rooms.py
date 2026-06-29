"""
위치공유 방(Room) API

배차와 독립적으로 방을 생성하여 기사 GPS 위치 공유:
- 관리자: 방 생성 / 목록 조회 / 문서 확인
- 기사: 방 코드 입장 / GPS 전송 / 사진 업로드(출발·도착)
- 고객사: 전용 링크로 실시간 위치 지도 조회
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import math
import os
import hashlib

from app.core.database import get_db
from app.models.location_room import (
    LocationRoom, RoomLocation, RoomDocument,
    RoomStatus, RoomDocumentType, RoomDocumentStage
)
from app.api.auth import get_current_user
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.uvis_gps import VehicleGPSLog

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
ROOM_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "room_documents")
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


# ===================== Pydantic Schemas =====================

class RoomCreateRequest(BaseModel):
    """방 생성 요청"""
    title: str
    description: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    vehicle_plate: Optional[str] = None
    client_name: Optional[str] = None
    hours_valid: Optional[int] = 48
    notes: Optional[str] = None
    # 상차지
    loading_name: Optional[str] = None
    loading_address: Optional[str] = None
    loading_lat: Optional[float] = None
    loading_lng: Optional[float] = None
    # 하차지
    unloading_name: Optional[str] = None
    unloading_address: Optional[str] = None
    unloading_lat: Optional[float] = None
    unloading_lng: Optional[float] = None


class RoomCreateResponse(BaseModel):
    """방 생성 응답"""
    id: int
    room_code: str
    title: str
    status: str
    driver_token: str
    client_token: str
    driver_url: str      # 기사용 URL
    client_url: str      # 고객사용 URL
    expires_at: Optional[str]
    created_at: str


class RoomListItem(BaseModel):
    """방 목록 아이템"""
    id: int
    room_code: str
    title: str
    status: str
    driver_name: Optional[str]
    driver_phone: Optional[str]
    vehicle_plate: Optional[str]
    client_name: Optional[str]
    last_latitude: Optional[float]
    last_longitude: Optional[float]
    last_location_at: Optional[str]
    driver_joined_at: Optional[str]
    document_count: int
    client_view_count: int
    expires_at: Optional[str]
    created_at: str
    driver_url: str
    client_url: str


class RoomDetailResponse(BaseModel):
    """방 상세 정보"""
    id: int
    room_code: str
    title: str
    description: Optional[str]
    status: str
    driver_name: Optional[str]
    driver_phone: Optional[str]
    vehicle_plate: Optional[str]
    client_name: Optional[str]
    last_latitude: Optional[float]
    last_longitude: Optional[float]
    last_location_at: Optional[str]
    driver_joined_at: Optional[str]
    driver_last_seen: Optional[str]
    completed_at: Optional[str]
    client_view_count: int
    expires_at: Optional[str]
    created_at: str
    notes: Optional[str]
    documents: List[dict]
    location_history: List[dict]
    driver_url: str
    client_url: str


class LocationUpdate(BaseModel):
    """GPS 위치 업데이트"""
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None


class DriverJoinResponse(BaseModel):
    """기사 입장 응답"""
    room_id: int
    room_code: str
    title: str
    description: Optional[str]
    client_name: Optional[str]
    status: str
    driver_name: Optional[str]
    vehicle_plate: Optional[str]
    documents: List[dict]


# ===================== Helper =====================

def _build_driver_url(request: Request, token: str) -> str:
    base = str(request.base_url).rstrip("/")
    return f"{base}/room/driver/{token}"


def _build_client_url(request: Request, token: str) -> str:
    base = str(request.base_url).rstrip("/")
    return f"{base}/room/client/{token}"


def _fmt(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


def _status(room) -> str:
    """room.status가 None이거나 Enum이 아닌 경우 안전하게 문자열 반환"""
    if room.status is None:
        return "대기중"
    if hasattr(room.status, 'value'):
        return room.status.value   # ← 직접 .value 반환 (재귀 아님)
    return str(room.status)


# ===================== 관리자 API =====================

@router.post(
    "/rooms",
    response_model=RoomCreateResponse,
    summary="방 생성 (관리자)",
    tags=["Location Rooms"]
)
async def create_room(
    req: RoomCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """관리자가 위치공유 방을 생성합니다."""
    room = LocationRoom.create_room(
        title=req.title,
        created_by=current_user.id,
        description=req.description,
        driver_name=req.driver_name,
        driver_phone=req.driver_phone,
        vehicle_plate=req.vehicle_plate,
        client_name=req.client_name,
        hours_valid=req.hours_valid,
        notes=req.notes,
        loading_name=req.loading_name,
        loading_address=req.loading_address,
        loading_lat=req.loading_lat,
        loading_lng=req.loading_lng,
        unloading_name=req.unloading_name,
        unloading_address=req.unloading_address,
        unloading_lat=req.unloading_lat,
        unloading_lng=req.unloading_lng,
    )
    db.add(room)
    db.commit()
    db.refresh(room)

    # status가 None인 경우 DB에서 읽어온 값 사용
    return RoomCreateResponse(
        id=room.id,
        room_code=room.room_code,
        title=room.title,
        status=_status(room),
        driver_token=room.driver_token,
        client_token=room.client_token,
        driver_url=_build_driver_url(request, room.driver_token),
        client_url=_build_client_url(request, room.client_token),
        expires_at=_fmt(room.expires_at),
        created_at=_fmt(room.created_at)
    )


@router.get(
    "/rooms",
    summary="방 목록 조회 (관리자)",
    tags=["Location Rooms"]
)
async def list_rooms(
    request: Request,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """방 목록을 조회합니다."""
    query = db.query(LocationRoom)

    if status_filter:
        try:
            query = query.filter(LocationRoom.status == RoomStatus(status_filter))
        except ValueError:
            pass

    total = query.count()
    rooms = query.order_by(desc(LocationRoom.created_at)).offset((page - 1) * limit).limit(limit).all()

    items = []
    for room in rooms:
        items.append({
            "id": room.id,
            "room_code": room.room_code,
            "title": room.title,
            "status": _status(room),
            "driver_name": room.driver_name,
            "driver_phone": room.driver_phone,
            "vehicle_plate": room.vehicle_plate,
            "client_name": room.client_name,
            "last_latitude": room.last_latitude,
            "last_longitude": room.last_longitude,
            "last_location_at": _fmt(room.last_location_at),
            "driver_joined_at": _fmt(room.driver_joined_at),
            "document_count": len(room.documents),
            "client_view_count": room.client_view_count,
            "expires_at": _fmt(room.expires_at),
            "created_at": _fmt(room.created_at),
            "driver_url": _build_driver_url(request, room.driver_token),
            "client_url": _build_client_url(request, room.client_token),
        })

    return {"total": total, "page": page, "limit": limit, "items": items}


@router.get(
    "/rooms/{room_id}",
    summary="방 상세 조회 (관리자)",
    tags=["Location Rooms"]
)
async def get_room_detail(
    room_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """방 상세 정보를 조회합니다."""
    room = db.query(LocationRoom).filter(LocationRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")

    # 위치 이력 (최근 100건)
    locations = db.query(RoomLocation).filter(
        RoomLocation.room_id == room.id
    ).order_by(desc(RoomLocation.recorded_at)).limit(100).all()

    location_history = [{
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "accuracy": loc.accuracy,
        "speed": loc.speed,
        "recorded_at": _fmt(loc.recorded_at)
    } for loc in reversed(locations)]

    documents = [{
        "id": doc.id,
        "document_type": doc.document_type.value,
        "stage": doc.stage.value,
        "file_url": doc.file_url,
        "file_name": doc.file_name,
        "file_size": doc.file_size,
        "uploaded_lat": doc.uploaded_lat,
        "uploaded_lon": doc.uploaded_lon,
        "notes": doc.notes,
        "created_at": _fmt(doc.created_at)
    } for doc in room.documents]

    return {
        "id": room.id,
        "room_code": room.room_code,
        "title": room.title,
        "description": room.description,
        "status": _status(room),
        "driver_name": room.driver_name,
        "driver_phone": room.driver_phone,
        "vehicle_plate": room.vehicle_plate,
        "client_name": room.client_name,
        "last_latitude": room.last_latitude,
        "last_longitude": room.last_longitude,
        "last_location_at": _fmt(room.last_location_at),
        "driver_joined_at": _fmt(room.driver_joined_at),
        "driver_last_seen": _fmt(room.driver_last_seen),
        "completed_at": _fmt(room.completed_at),
        "client_view_count": room.client_view_count,
        "expires_at": _fmt(room.expires_at),
        "created_at": _fmt(room.created_at),
        "notes": room.notes,
        # 상차지
        "loading_name": room.loading_name,
        "loading_address": room.loading_address,
        "loading_lat": room.loading_lat,
        "loading_lng": room.loading_lng,
        # 하차지
        "unloading_name": room.unloading_name,
        "unloading_address": room.unloading_address,
        "unloading_lat": room.unloading_lat,
        "unloading_lng": room.unloading_lng,
        # 운행 타임라인
        "arrived_at_loading": _fmt(room.arrived_at_loading),
        "departed_loading": _fmt(room.departed_loading),
        "arrived_at_unloading": _fmt(room.arrived_at_unloading),
        "departed_unloading": _fmt(room.departed_unloading),
        "documents": documents,
        "location_history": location_history,
        "driver_url": _build_driver_url(request, room.driver_token),
        "client_url": _build_client_url(request, room.client_token),
    }


@router.patch(
    "/rooms/{room_id}/status",
    summary="방 상태 변경 (관리자)",
    tags=["Location Rooms"]
)
async def update_room_status(
    room_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """방 상태를 변경합니다 (완료/취소 등)."""
    room = db.query(LocationRoom).filter(LocationRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")

    try:
        room.status = RoomStatus(new_status)
        if room.status == RoomStatus.COMPLETED:
            room.completed_at = datetime.now()
        db.commit()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 상태: {new_status}")

    return {"status": "success", "new_status": _status(room)}


@router.delete(
    "/rooms/{room_id}",
    summary="방 삭제 (관리자)",
    tags=["Location Rooms"]
)
async def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """방을 삭제합니다."""
    room = db.query(LocationRoom).filter(LocationRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")

    db.delete(room)
    db.commit()
    return {"status": "success", "message": "방이 삭제되었습니다."}


# ===================== 기사용 API (토큰 기반, 인증 없음) =====================

@router.get(
    "/room/driver/{driver_token}",
    summary="기사용 방 정보 조회",
    tags=["Location Rooms - Driver"]
)
async def driver_get_room_info(
    driver_token: str,
    db: Session = Depends(get_db)
):
    """기사가 토큰으로 방 정보를 조회하고 입장합니다."""
    room = db.query(LocationRoom).filter(
        LocationRoom.driver_token == driver_token
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다. 링크를 확인해주세요.")

    if room.is_expired and room.status not in [RoomStatus.COMPLETED, RoomStatus.CANCELLED]:
        raise HTTPException(status_code=410, detail="방이 만료되었습니다.")

    if room.status == RoomStatus.CANCELLED:
        raise HTTPException(status_code=410, detail="취소된 방입니다.")

    # 첫 입장 처리
    if room.driver_joined_at is None:
        room.driver_joined_at = datetime.now()
        if room.status == RoomStatus.WAITING:
            room.status = RoomStatus.ACTIVE
        db.commit()

    # 업로드된 문서 목록
    documents = [{
        "id": doc.id,
        "document_type": doc.document_type.value,
        "stage": doc.stage.value,
        "file_url": doc.file_url,
        "file_name": doc.file_name,
        "notes": doc.notes,
        "created_at": _fmt(doc.created_at)
    } for doc in room.documents]

    return {
        "room_id": room.id,
        "room_code": room.room_code,
        "title": room.title,
        "description": room.description,
        "client_name": room.client_name,
        "status": _status(room),
        "driver_name": room.driver_name,
        "vehicle_plate": room.vehicle_plate,
        "documents": documents,
        "is_completed": room.status == RoomStatus.COMPLETED,
        "expires_at": _fmt(room.expires_at)
    }


@router.post(
    "/room/driver/{driver_token}/location",
    summary="기사 GPS 위치 전송",
    tags=["Location Rooms - Driver"]
)
async def driver_update_location(
    driver_token: str,
    location: LocationUpdate,
    db: Session = Depends(get_db)
):
    """기사가 GPS 위치를 전송합니다."""
    room = db.query(LocationRoom).filter(
        LocationRoom.driver_token == driver_token
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")

    if room.status not in [RoomStatus.ACTIVE, RoomStatus.WAITING]:
        raise HTTPException(status_code=400, detail=f"위치를 전송할 수 없는 상태입니다: {_status(room)}")

    # 위치 기록
    loc = RoomLocation(
        room_id=room.id,
        latitude=location.latitude,
        longitude=location.longitude,
        accuracy=location.accuracy,
        speed=location.speed,
        heading=location.heading,
        recorded_at=datetime.now()
    )
    db.add(loc)

    # 방 최근 위치 캐시 업데이트
    room.last_latitude = location.latitude
    room.last_longitude = location.longitude
    room.last_location_at = datetime.now()
    room.driver_last_seen = datetime.now()

    if room.status == RoomStatus.WAITING:
        room.status = RoomStatus.ACTIVE
        if not room.driver_joined_at:
            room.driver_joined_at = datetime.now()

    # ── Geofence 체크 (상차지 / 하차지) ─────────────────────────
    GEOFENCE_RADIUS_M = 300  # 반경 300m

    lat, lng = location.latitude, location.longitude
    now = datetime.now()

    # 상차지 체크
    if room.loading_lat and room.loading_lng:
        dist_loading = LocationRoom.haversine_m(lat, lng, room.loading_lat, room.loading_lng)
        in_zone = dist_loading <= GEOFENCE_RADIUS_M
        was_in_zone = room._in_loading_zone

        if in_zone and not was_in_zone:
            # 상차지 진입
            room._in_loading_zone = True
            if not room.arrived_at_loading:
                room.arrived_at_loading = now
        elif not in_zone and was_in_zone:
            # 상차지 이탈 → 출차
            room._in_loading_zone = False
            if room.arrived_at_loading and not room.departed_loading:
                room.departed_loading = now

    # 하차지 체크
    if room.unloading_lat and room.unloading_lng:
        dist_unloading = LocationRoom.haversine_m(lat, lng, room.unloading_lat, room.unloading_lng)
        in_zone = dist_unloading <= GEOFENCE_RADIUS_M
        was_in_zone = room._in_unloading_zone

        if in_zone and not was_in_zone:
            # 하차지 진입
            room._in_unloading_zone = True
            if not room.arrived_at_unloading:
                room.arrived_at_unloading = now
        elif not in_zone and was_in_zone:
            # 하차지 이탈 → 하차 완료
            room._in_unloading_zone = False
            if room.arrived_at_unloading and not room.departed_unloading:
                room.departed_unloading = now

    db.commit()

    return {
        "status": "success",
        "latitude": location.latitude,
        "longitude": location.longitude,
        "recorded_at": loc.recorded_at.isoformat()
    }


@router.post(
    "/room/driver/{driver_token}/documents",
    summary="기사 서류 사진 업로드 (출발/도착)",
    tags=["Location Rooms - Driver"]
)
async def driver_upload_document(
    driver_token: str,
    file: UploadFile = File(...),
    document_type: str = Form(..., description="거래명세표 | 온도기록지 | 기타"),
    stage: str = Form(..., description="출발 | 도착"),
    notes: Optional[str] = Form(None),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """기사가 출발/도착 시 서류 사진을 업로드합니다."""
    room = db.query(LocationRoom).filter(
        LocationRoom.driver_token == driver_token
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")

    if room.status == RoomStatus.CANCELLED:
        raise HTTPException(status_code=410, detail="취소된 방입니다.")

    # 문서 타입 검증
    try:
        doc_type = RoomDocumentType(document_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 문서 유형: {document_type}. 가능한 값: 거래명세표, 온도기록지, 기타")

    try:
        doc_stage = RoomDocumentStage(stage)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 단계: {stage}. 가능한 값: 출발, 도착")

    # 파일 읽기
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"파일이 너무 큽니다. 최대 {MAX_FILE_SIZE // 1024 // 1024}MB")

    # 허용된 파일 타입 확인
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/heic", "image/heif", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"허용되지 않는 파일 형식입니다. 사진(JPG/PNG) 또는 PDF만 가능합니다.")

    # 저장 디렉터리
    os.makedirs(ROOM_UPLOAD_DIR, exist_ok=True)

    # 파일명 생성
    file_hash = hashlib.sha256(file_content).hexdigest()[:12]
    ext = os.path.splitext(file.filename or "photo.jpg")[1] or ".jpg"
    saved_filename = f"room{room.id}_{stage}_{document_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_hash}{ext}"
    file_path = os.path.join(ROOM_UPLOAD_DIR, saved_filename)

    with open(file_path, "wb") as f:
        f.write(file_content)

    file_url = f"/uploads/room_documents/{saved_filename}"

    # DB 저장
    doc = RoomDocument(
        room_id=room.id,
        document_type=doc_type,
        stage=doc_stage,
        file_url=file_url,
        file_path=file_path,
        file_name=file.filename or saved_filename,
        file_size=len(file_content),
        mime_type=file.content_type,
        uploaded_lat=lat,
        uploaded_lon=lon,
        notes=notes
    )
    db.add(doc)

    # 기사 마지막 활동 업데이트
    room.driver_last_seen = datetime.now()
    db.commit()
    db.refresh(doc)

    return {
        "status": "success",
        "document_id": doc.id,
        "file_url": file_url,
        "document_type": doc_type.value,
        "stage": doc_stage.value,
        "uploaded_at": _fmt(doc.created_at)
    }


@router.post(
    "/room/driver/{driver_token}/complete",
    summary="기사 운행 완료 처리",
    tags=["Location Rooms - Driver"]
)
async def driver_complete(
    driver_token: str,
    db: Session = Depends(get_db)
):
    """기사가 운행 완료를 처리합니다."""
    room = db.query(LocationRoom).filter(
        LocationRoom.driver_token == driver_token
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")

    room.status = RoomStatus.COMPLETED
    room.completed_at = datetime.now()
    db.commit()

    return {"status": "success", "message": "운행이 완료되었습니다."}


# ===================== 고객사용 API (토큰 기반, 인증 없음) =====================

@router.get(
    "/room/client/{client_token}",
    summary="고객사용 실시간 위치 조회",
    tags=["Location Rooms - Client"]
)
async def client_get_location(
    client_token: str,
    db: Session = Depends(get_db)
):
    """고객사가 실시간 차량 위치를 조회합니다."""
    room = db.query(LocationRoom).filter(
        LocationRoom.client_token == client_token
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="유효하지 않은 링크입니다.")

    # 조회 수 카운트
    room.client_view_count += 1
    db.commit()

    # 위치 이력 (최근 50건)
    locations = db.query(RoomLocation).filter(
        RoomLocation.room_id == room.id
    ).order_by(RoomLocation.recorded_at).limit(200).all()  # 경로 표시용

    # 공개 문서만 반환
    documents = [{
        "id": doc.id,
        "document_type": doc.document_type.value,
        "stage": doc.stage.value,
        "file_url": doc.file_url,
        "file_name": doc.file_name,
        "mime_type": doc.mime_type,
        "created_at": _fmt(doc.created_at)
    } for doc in room.documents]

    location_history = [{
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "recorded_at": _fmt(loc.recorded_at)
    } for loc in locations]

    return {
        "room_code": room.room_code,
        "title": room.title,
        "description": room.description,
        "status": _status(room),
        "driver_name": room.driver_name,
        "vehicle_plate": room.vehicle_plate,
        "current_location": {
            "latitude": room.last_latitude,
            "longitude": room.last_longitude,
            "updated_at": _fmt(room.last_location_at)
        } if room.last_latitude else None,
        "location_history": location_history,
        "documents": documents,
        "driver_joined_at": _fmt(room.driver_joined_at),
        "completed_at": _fmt(room.completed_at),
        "is_completed": room.status == RoomStatus.COMPLETED,
        "expires_at": _fmt(room.expires_at)
    }


# ===================== 방 코드로 입장 (기사 대안 진입) =====================

@router.get(
    "/room/code/{room_code}",
    summary="방 코드로 기사 URL 조회",
    tags=["Location Rooms - Driver"]
)
async def get_room_by_code(
    room_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """방 코드로 기사용 URL을 반환합니다."""
    room = db.query(LocationRoom).filter(
        LocationRoom.room_code == room_code.upper()
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다. 방 코드를 확인해주세요.")

    if room.is_expired:
        raise HTTPException(status_code=410, detail="만료된 방입니다.")

    if room.status == RoomStatus.CANCELLED:
        raise HTTPException(status_code=410, detail="취소된 방입니다.")

    return {
        "room_id": room.id,
        "room_code": room.room_code,
        "title": room.title,
        "status": _status(room),
        "driver_token": room.driver_token,
        "driver_url": _build_driver_url(request, room.driver_token)
    }


# ===================== GPS 이력 조회 (UVIS DB 연동) =====================

@router.get(
    "/location-rooms/{room_id}/gps-history",
    summary="위치공유방 차량 GPS 이력 조회 (날짜별)",
    tags=["Location Rooms"]
)
async def get_room_gps_history(
    room_id: int,
    date: str = Query(..., description="조회 날짜 (YYYYMMDD, 예: 20260320)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    위치공유방에 등록된 차량번호로 UVIS GPS 이력을 날짜별로 조회합니다.
    - vehicle_plate → vehicles.plate_number 매칭 → vehicle_gps_logs 조회
    - 3일치 이내 데이터만 보존 (자동삭제 스케줄러 연동)
    """
    # 방 조회
    room = db.query(LocationRoom).filter(LocationRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")

    if not room.vehicle_plate:
        return {
            "room_id": room_id,
            "vehicle_plate": None,
            "vehicle_id": None,
            "date": date,
            "total": 0,
            "items": [],
            "message": "방에 차량번호가 등록되지 않았습니다."
        }

    # 차량번호로 vehicle 조회 (공백/하이픈 제거 후 비교)
    plate = room.vehicle_plate.replace(" ", "").replace("-", "")
    vehicle = db.query(Vehicle).filter(
        Vehicle.plate_number.ilike(f"%{plate}%")
    ).first()

    # vehicle_id가 없어도 cm_number(차량번호)로 직접 조회
    query = db.query(VehicleGPSLog).filter(
        VehicleGPSLog.bi_date == date
    )

    if vehicle:
        query = query.filter(VehicleGPSLog.vehicle_id == vehicle.id)
    else:
        # vehicle 등록 없이 UVIS cm_number로 직접 매칭
        query = query.filter(
            VehicleGPSLog.cm_number.ilike(f"%{plate}%")
        )

    logs = query.order_by(VehicleGPSLog.bi_time).all()

    items = []
    for log in logs:
        if log.latitude and log.longitude:
            items.append({
                "time": log.bi_time,            # HHMMSS
                "latitude": log.latitude,
                "longitude": log.longitude,
                "speed_kmh": log.speed_kmh,
                "is_engine_on": log.is_engine_on,
                "cm_number": log.cm_number,
            })

    return {
        "room_id": room_id,
        "vehicle_plate": room.vehicle_plate,
        "vehicle_id": vehicle.id if vehicle else None,
        "date": date,
        "total": len(items),
        "items": items,
        "message": None if items else "해당 날짜의 GPS 데이터가 없습니다. (데이터는 3일치만 보관됩니다)"
    }


@router.get(
    "/location-rooms/{room_id}/gps-available-dates",
    summary="GPS 이력이 있는 날짜 목록",
    tags=["Location Rooms"]
)
async def get_gps_available_dates(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    위치공유방 차량의 GPS 이력이 존재하는 날짜 목록을 반환합니다. (최근 3일)
    """
    from datetime import timedelta
    from sqlalchemy import distinct

    room = db.query(LocationRoom).filter(LocationRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")

    if not room.vehicle_plate:
        return {"dates": [], "vehicle_plate": None}

    plate = room.vehicle_plate.replace(" ", "").replace("-", "")
    vehicle = db.query(Vehicle).filter(
        Vehicle.plate_number.ilike(f"%{plate}%")
    ).first()

    # 최근 3일 날짜 범위
    today = datetime.utcnow().date()
    date_list = [(today - timedelta(days=i)).strftime("%Y%m%d") for i in range(3)]

    query = db.query(distinct(VehicleGPSLog.bi_date)).filter(
        VehicleGPSLog.bi_date.in_(date_list)
    )
    if vehicle:
        query = query.filter(VehicleGPSLog.vehicle_id == vehicle.id)
    else:
        query = query.filter(VehicleGPSLog.cm_number.ilike(f"%{plate}%"))

    available_dates = [row[0] for row in query.all()]
    available_dates.sort(reverse=True)

    return {
        "vehicle_plate": room.vehicle_plate,
        "vehicle_id": vehicle.id if vehicle else None,
        "dates": available_dates    # ["20260320", "20260319", ...]
    }


# ===================== 실시간모니터링 차량 목록 (방 생성 시 차량 선택용) =====================

@router.get(
    "/rooms/vehicles/monitoring-list",
    summary="실시간모니터링 차량 목록 조회 (방 생성용)",
    tags=["Location Rooms"]
)
async def get_monitoring_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    실시간모니터링에 등록된 활성 차량 목록을 반환합니다.
    방 생성 시 차량 선택 드롭다운에 사용합니다.
    최근 GPS 수신 정보도 함께 반환합니다.
    """
    from sqlalchemy import func
    from app.models.vehicle import VehicleStatus

    vehicles = db.query(Vehicle).filter(
        Vehicle.status == VehicleStatus.ACTIVE
    ).order_by(Vehicle.plate_number).all()

    # 각 차량의 최근 GPS 로그 조회 (오늘 날짜)
    today = datetime.utcnow().strftime("%Y%m%d")
    result = []
    for v in vehicles:
        latest_gps = db.query(VehicleGPSLog).filter(
            VehicleGPSLog.vehicle_id == v.id,
            VehicleGPSLog.bi_date == today
        ).order_by(desc(VehicleGPSLog.bi_time)).first()

        result.append({
            "id": v.id,
            "plate_number": v.plate_number,
            "vehicle_type": v.vehicle_type.value if hasattr(v.vehicle_type, 'value') else str(v.vehicle_type),
            "driver_name": v.driver_name,
            "last_gps_time": latest_gps.bi_time if latest_gps else None,
            "last_lat": latest_gps.latitude if latest_gps else None,
            "last_lng": latest_gps.longitude if latest_gps else None,
            "last_speed": latest_gps.speed_kmh if latest_gps else None,
            "is_engine_on": latest_gps.is_engine_on if latest_gps else None,
        })

    return {"total": len(result), "items": result}


# ===================== 운행 타임라인 수동 기록 (관리자 수동 체크용) =====================

class TimelineManualPatch(BaseModel):
    field: str   # arrived_at_loading | departed_loading | arrived_at_unloading | departed_unloading
    time: Optional[str] = None  # ISO datetime string, None이면 현재시각


@router.patch(
    "/rooms/{room_id}/timeline",
    summary="운행 타임라인 수동 기록 (관리자)",
    tags=["Location Rooms"]
)
async def patch_room_timeline(
    room_id: int,
    body: TimelineManualPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """관리자가 운행 타임라인 시각을 수동으로 기록/수정합니다."""
    room = db.query(LocationRoom).filter(LocationRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")

    allowed_fields = {
        "arrived_at_loading", "departed_loading",
        "arrived_at_unloading", "departed_unloading"
    }
    if body.field not in allowed_fields:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 필드: {body.field}")

    ts = datetime.now() if body.time is None else datetime.fromisoformat(body.time)
    setattr(room, body.field, ts)
    db.commit()

    return {
        "status": "success",
        "field": body.field,
        "value": ts.isoformat()
    }
