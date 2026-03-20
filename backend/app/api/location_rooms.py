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
import os
import hashlib

from app.core.database import get_db
from app.models.location_room import (
    LocationRoom, RoomLocation, RoomDocument,
    RoomStatus, RoomDocumentType, RoomDocumentStage
)
from app.api.auth import get_current_user
from app.models.user import User

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
        notes=req.notes
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
