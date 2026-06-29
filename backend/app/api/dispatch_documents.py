"""
배차 서류 및 추적 API

기능:
- 서류 업로드 (거래명세표, 온도기록지)
- 추적 번호 생성
- 공개 추적 페이지
- 실시간 위치 조회
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
import hashlib
import secrets
from datetime import datetime, timedelta
import os

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.dispatch import Dispatch, DispatchRoute
from app.models.dispatch_document import (
    DispatchDocument,
    DispatchTracking,
    DocumentType,
    DocumentStage
)
from app.models.vehicle_location import VehicleLocation
from app.schemas.dispatch_document import (
    DocumentUploadRequest,
    DocumentResponse,
    DocumentListResponse,
    DocumentVerifyRequest,
    TrackingCreateRequest,
    TrackingResponse,
    PublicTrackingDetail,
    PublicLocationPoint,
    PublicRouteStop,
    PublicDocument
)
from app.services.notification_service import send_dispatch_notification

router = APIRouter()


# ===== 추적 통계 API =====

@router.get(
    "/tracking/statistics",
    summary="배송 추적 통계",
    description="실시간 배송 현황 통계를 반환합니다"
)
async def get_tracking_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """배송 추적 통계 - Redis 캐시 30초"""
    from datetime import date as date_cls
    from sqlalchemy import cast, Date, text

    CACHE_KEY = "dispatch:tracking:statistics"
    CACHE_TTL = 30

    # Redis 캐시 먼저 조회
    try:
        from app.services.cache_service import cache_service
        cached = cache_service.get(CACHE_KEY)
        if cached:
            return cached
    except Exception as e:
        pass

    # ── 진행 중인 배송 수 ──────────────────────────────
    try:
        in_progress_count = db.query(Dispatch).filter(
            or_(Dispatch.status == '확정', Dispatch.status == '진행중')
        ).count()
    except Exception:
        in_progress_count = 0

    # ── 오늘 완료된 배송 수 ───────────────────────────
    try:
        today = date_cls.today()
        completed_today_count = db.query(Dispatch).filter(
            Dispatch.status == '완료',
            cast(Dispatch.updated_at, Date) == today
        ).count()
    except Exception:
        completed_today_count = 0

    # ── 평균 배송 시간 (최근 30건, 안전 계산) ──────────
    avg_delivery_time_minutes = 0
    try:
        recent_done = db.query(
            Dispatch.dispatch_date,
            Dispatch.updated_at
        ).filter(
            Dispatch.status == '완료',
            Dispatch.dispatch_date.isnot(None),
            Dispatch.updated_at.isnot(None)
        ).order_by(Dispatch.updated_at.desc()).limit(30).all()

        total_min, cnt = 0, 0
        for row in recent_done:
            try:
                d = row.dispatch_date
                u = row.updated_at
                # dispatch_date is a Python date, updated_at is datetime
                start = datetime(d.year, d.month, d.day) if isinstance(d, date_cls) else datetime.fromisoformat(str(d))
                end = u if isinstance(u, datetime) else datetime.fromisoformat(str(u))
                mins = (end - start).total_seconds() / 60
                if 0 < mins < 10080:   # 0 ~ 7일 이내만 유효
                    total_min += mins
                    cnt += 1
            except Exception:
                pass
        if cnt:
            avg_delivery_time_minutes = int(total_min / cnt)
    except Exception:
        pass

    # ── 활성 추적 목록 (스칼라 쿼리, 관계 없이) ────────
    active_deliveries = []
    try:
        from app.models.vehicle import Vehicle

        rows = db.query(
            DispatchTracking.tracking_number,
            Dispatch.dispatch_number,
            Dispatch.vehicle_id,
            Dispatch.dispatch_date
        ).join(
            Dispatch, DispatchTracking.dispatch_id == Dispatch.id
        ).filter(
            DispatchTracking.is_active == True,
            or_(Dispatch.status == '확정', Dispatch.status == '진행중')
        ).limit(20).all()

        for row in rows:
            try:
                # 차량 번호판 직접 조회 (관계 traversal 없이)
                vehicle_plate = None
                if row.vehicle_id:
                    v = db.query(Vehicle.plate_number).filter(
                        Vehicle.id == row.vehicle_id
                    ).first()
                    if v:
                        vehicle_plate = v.plate_number

                # 최신 GPS 위치
                latest_location = None
                if row.vehicle_id:
                    loc = db.query(
                        VehicleLocation.latitude,
                        VehicleLocation.longitude
                    ).filter(
                        VehicleLocation.vehicle_id == row.vehicle_id
                    ).order_by(VehicleLocation.recorded_at.desc()).first()
                    if loc:
                        latest_location = {"lat": float(loc.latitude), "lon": float(loc.longitude)}

                # 진행률 (경과 시간 기준, 8h 표준)
                progress_percent = 50
                try:
                    d = row.dispatch_date
                    if d:
                        start = datetime(d.year, d.month, d.day) if isinstance(d, date_cls) else datetime.fromisoformat(str(d))
                        elapsed = (datetime.now() - start).total_seconds()
                        progress_percent = min(95, max(5, int(elapsed / (8 * 3600) * 100)))
                except Exception:
                    pass

                active_deliveries.append({
                    "tracking_number": row.tracking_number,
                    "dispatch_number": row.dispatch_number,
                    "current_location": latest_location,
                    "progress_percent": progress_percent,
                    "vehicle_plate": vehicle_plate
                })
            except Exception:
                continue
    except Exception:
        pass

    result = {
        "in_progress": in_progress_count,
        "completed_today": completed_today_count,
        "avg_delivery_time_minutes": avg_delivery_time_minutes,
        "active_deliveries": active_deliveries,
        "last_updated": datetime.now().isoformat()
    }

    # Redis 캐시 저장
    try:
        from app.services.cache_service import cache_service
        cache_service.set(CACHE_KEY, result, ttl=CACHE_TTL)
    except Exception:
        pass

    return result


# ===== 파일 업로드 헬퍼 =====

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads/dispatch_documents")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def save_upload_file(file: UploadFile, dispatch_id: int) -> dict:
    """파일 저장"""
    # 디렉토리 생성
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # 파일 크기 확인
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"파일 크기가 너무 큽니다. 최대 {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 파일명 생성 (해시 + 원본 확장자)
    file_hash = hashlib.sha256(content).hexdigest()[:16]
    ext = os.path.splitext(file.filename)[1]
    new_filename = f"{dispatch_id}_{file_hash}{ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    
    # 파일 저장
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "file_path": file_path,
        "file_url": f"/uploads/dispatch_documents/{new_filename}",
        "file_name": file.filename,
        "file_size": len(content),
        "mime_type": file.content_type or "application/octet-stream"
    }


# ===== 서류 업로드 API =====

@router.post(
    "/documents/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="배차 서류 업로드",
    description="기사님이 거래명세표, 온도기록지 등을 업로드합니다"
)
async def upload_document(
    file: UploadFile = File(..., description="업로드할 파일"),
    dispatch_id: int = Form(..., description="배차 ID"),
    document_type: DocumentType = Form(..., description="서류 유형"),
    stage: DocumentStage = Form(..., description="서류 단계 (출발/도착)"),
    route_id: Optional[int] = Form(None, description="배차 경로 ID"),
    order_id: Optional[int] = Form(None, description="주문 ID"),
    notes: Optional[str] = Form(None, description="메모"),
    location: Optional[str] = Form(None, description="업로드 위치"),
    latitude: Optional[float] = Form(None, description="위도"),
    longitude: Optional[float] = Form(None, description="경도"),
    is_public: bool = Form(True, description="고객 공개 여부"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배차 서류 업로드
    
    **지원 파일 형식:** JPG, PNG, PDF
    **최대 파일 크기:** 10MB
    
    **사용 시나리오:**
    1. 출발 시: 거래명세표, 온도기록지 촬영/업로드
    2. 도착 시: 거래명세표, 온도기록지, 서명 촬영/업로드
    """
    # 배차 존재 확인
    dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
    if not dispatch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="배차를 찾을 수 없습니다"
        )
    
    # 파일 저장
    file_info = await save_upload_file(file, dispatch_id)
    
    # DB 저장
    document = DispatchDocument(
        dispatch_id=dispatch_id,
        route_id=route_id,
        order_id=order_id,
        document_type=document_type,
        stage=stage,
        file_url=file_info["file_url"],
        file_name=file_info["file_name"],
        file_size=file_info["file_size"],
        mime_type=file_info["mime_type"],
        uploaded_by=current_user.id,
        uploaded_at_location=location,
        uploaded_lat=latitude,
        uploaded_lon=longitude,
        notes=notes,
        is_public=is_public
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Send notification
    try:
        await send_dispatch_notification(
            db=db,
            dispatch_id=dispatch_id,
            event_type='document_uploaded',
            document_type=document_type.value,
            stage=stage.value
        )
    except Exception as e:
        # Don't fail upload if notification fails
        print(f"Failed to send notification: {e}")
    
    return document


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    summary="서류 목록 조회",
    description="배차별, 경로별, 주문별 서류 목록 조회"
)
async def list_documents(
    dispatch_id: Optional[int] = None,
    route_id: Optional[int] = None,
    order_id: Optional[int] = None,
    document_type: Optional[DocumentType] = None,
    stage: Optional[DocumentStage] = None,
    is_verified: Optional[bool] = None,
    is_public: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """서류 목록 조회"""
    query = db.query(DispatchDocument)
    
    # 필터 적용
    if dispatch_id:
        query = query.filter(DispatchDocument.dispatch_id == dispatch_id)
    if route_id:
        query = query.filter(DispatchDocument.route_id == route_id)
    if order_id:
        query = query.filter(DispatchDocument.order_id == order_id)
    if document_type:
        query = query.filter(DispatchDocument.document_type == document_type)
    if stage:
        query = query.filter(DispatchDocument.stage == stage)
    if is_verified is not None:
        query = query.filter(DispatchDocument.is_verified == is_verified)
    if is_public is not None:
        query = query.filter(DispatchDocument.is_public == is_public)
    
    # 총 개수
    total = query.count()
    
    # 페이지네이션
    items = query.order_by(DispatchDocument.created_at.desc()).offset(offset).limit(limit).all()
    
    return DocumentListResponse(total=total, items=items)


@router.patch(
    "/documents/{document_id}/verify",
    response_model=DocumentResponse,
    summary="서류 검증",
    description="관리자가 업로드된 서류를 검증합니다"
)
async def verify_document(
    document_id: int,
    request: DocumentVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """서류 검증"""
    document = db.query(DispatchDocument).filter(DispatchDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="서류를 찾을 수 없습니다"
        )
    
    document.is_verified = request.is_verified
    document.verified_by = current_user.id
    document.verified_at = datetime.now().isoformat()
    if request.notes:
        document.notes = (document.notes or "") + f"\n[검증] {request.notes}"
    
    db.commit()
    db.refresh(document)
    
    return document


# ===== 추적 번호 API =====

def generate_tracking_number(dispatch_id: int) -> str:
    """추적 번호 생성: TRK-YYYYMMDD-{8자리 해시}"""
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = secrets.token_hex(4).upper()
    return f"TRK-{date_str}-{random_str}"


@router.post(
    "/tracking/generate",
    response_model=TrackingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="추적 번호 생성",
    description="배차에 대한 공개 추적 번호를 생성합니다"
)
async def create_tracking(
    request: TrackingCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    추적 번호 생성
    
    고객사에 공유할 수 있는 공개 추적 번호를 생성합니다.
    고객은 이 번호로 실시간 배송 위치와 서류를 확인할 수 있습니다.
    """
    # 배차 존재 확인
    dispatch = db.query(Dispatch).filter(Dispatch.id == request.dispatch_id).first()
    if not dispatch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="배차를 찾을 수 없습니다"
        )
    
    # 이미 존재하는지 확인
    existing = db.query(DispatchTracking).filter(
        DispatchTracking.dispatch_id == request.dispatch_id
    ).first()
    
    if existing:
        return existing
    
    # 추적 번호 생성
    tracking_number = generate_tracking_number(request.dispatch_id)
    
    # 만료 일시 계산
    expires_at = None
    if request.expires_days:
        expires_at = (datetime.now() + timedelta(days=request.expires_days)).isoformat()
    
    # DB 저장
    tracking = DispatchTracking(
        dispatch_id=request.dispatch_id,
        tracking_number=tracking_number,
        is_active=True,
        expires_at=expires_at,
        customer_name=request.customer_name,
        customer_email=request.customer_email,
        customer_phone=request.customer_phone,
        notify_on_departure=request.notify_on_departure,
        notify_on_arrival=request.notify_on_arrival,
        notify_on_document_upload=request.notify_on_document_upload,
        view_count=0
    )
    
    db.add(tracking)
    db.commit()
    db.refresh(tracking)
    
    # Send departure notification if enabled
    if request.notify_on_departure:
        try:
            await send_dispatch_notification(
                db=db,
                dispatch_id=request.dispatch_id,
                event_type='departure',
                tracking_number=tracking_number
            )
        except Exception as e:
            # Don't fail if notification fails
            print(f"Failed to send departure notification: {e}")
    
    return tracking


# ===== 공개 추적 API (인증 불필요) =====

@router.get(
    "/tracking/public/{tracking_number}",
    response_model=PublicTrackingDetail,
    summary="공개 배송 추적",
    description="추적 번호로 배송 정보를 조회합니다 (인증 불필요)",
    tags=["Public"]
)
async def get_public_tracking(
    tracking_number: str,
    db: Session = Depends(get_db)
):
    """
    공개 배송 추적
    
    **인증 불필요** - 추적 번호만으로 조회 가능
    
    **반환 정보:**
    - 실시간 차량 위치
    - 배송 경로 및 진행 상황
    - 업로드된 서류 (거래명세표, 온도기록지)
    - 예상 도착 시간
    """
    # 추적 정보 조회
    tracking = db.query(DispatchTracking).filter(
        DispatchTracking.tracking_number == tracking_number,
        DispatchTracking.is_active == True
    ).first()
    
    if not tracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="추적 정보를 찾을 수 없습니다"
        )
    
    # 만료 확인
    if tracking.expires_at:
        expires = datetime.fromisoformat(tracking.expires_at)
        if datetime.now() > expires:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="추적 정보가 만료되었습니다"
            )
    
    # 조회수 증가
    tracking.view_count += 1
    tracking.last_viewed_at = datetime.now().isoformat()
    db.commit()
    
    # 배차 정보 조회
    dispatch = db.query(Dispatch).filter(Dispatch.id == tracking.dispatch_id).first()
    if not dispatch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="배차 정보를 찾을 수 없습니다"
        )
    
    # 경로 정보
    routes = db.query(DispatchRoute).filter(
        DispatchRoute.dispatch_id == dispatch.id
    ).order_by(DispatchRoute.sequence).all()
    
    route_stops = [
        PublicRouteStop(
            sequence=route.sequence,
            location_name=route.location_name,
            address=route.address,
            latitude=route.latitude,
            longitude=route.longitude,
            route_type=route.route_type.value,
            estimated_arrival_time=route.estimated_arrival_time,
            estimated_departure_time=route.estimated_departure_time,
            is_completed=False  # TODO: 실제 완료 여부 추적
        )
        for route in routes
    ]
    
    # 현재 위치 (최신 GPS)
    current_location = None
    latest_gps = db.query(VehicleLocation).filter(
        VehicleLocation.dispatch_id == dispatch.id
    ).order_by(VehicleLocation.timestamp.desc()).first()
    
    if latest_gps:
        current_location = PublicLocationPoint(
            latitude=latest_gps.latitude,
            longitude=latest_gps.longitude,
            timestamp=latest_gps.timestamp,
            speed=latest_gps.speed,
            heading=latest_gps.heading
        )
    
    # 서류 조회 (공개된 것만)
    documents_db = db.query(DispatchDocument).filter(
        DispatchDocument.dispatch_id == dispatch.id,
        DispatchDocument.is_public == True
    ).order_by(DispatchDocument.created_at.desc()).all()
    
    documents = [
        PublicDocument(
            id=doc.id,
            document_type=doc.document_type,
            stage=doc.stage,
            file_url=doc.file_url,
            file_name=doc.file_name,
            file_size=doc.file_size,
            mime_type=doc.mime_type,
            uploaded_at=doc.created_at,
            notes=doc.notes
        )
        for doc in documents_db
    ]
    
    # 진행률 계산 (간단히: 완료된 경로 / 전체 경로)
    # TODO: 실제 GPS 기반 진행률 계산
    progress_percentage = 0.0
    if len(route_stops) > 0:
        # 임시로 현재 시간 기반
        progress_percentage = min(50.0, len(documents) * 10)  # 서류 업로드 개수로 대략 추정
    
    return PublicTrackingDetail(
        tracking_number=tracking_number,
        dispatch_number=dispatch.dispatch_number,
        dispatch_date=str(dispatch.dispatch_date),
        status=dispatch.status.value,
        vehicle_number=dispatch.vehicle.vehicle_number if dispatch.vehicle else "N/A",
        vehicle_type=dispatch.vehicle.vehicle_type if dispatch.vehicle else None,
        driver_name=dispatch.driver.name if dispatch.driver else None,
        current_location=current_location,
        routes=route_stops,
        progress_percentage=progress_percentage,
        estimated_arrival=dispatch.planned_end_time,
        documents=documents,
        total_distance_km=dispatch.total_distance_km,
        completed_distance_km=0,  # TODO: 실제 주행 거리
        total_pallets=dispatch.total_pallets,
        customer_name=tracking.customer_name,
        customer_email=tracking.customer_email,
        last_updated=datetime.now(),
        view_count=tracking.view_count
    )
