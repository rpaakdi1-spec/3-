"""
Phase 7: Enhanced Mobile App API
모바일 앱 강화 API - 인증, 푸시, GPS, 사진 업로드
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import hashlib
from loguru import logger

from app.core.database import get_db
from app.services.auth_service import create_access_token
from app.api.deps import get_current_user
from app.models.user import User
from app.models.dispatch import Dispatch
from app.models.vehicle import Vehicle
from app.models.order import Order
from app.models.fcm_token import FCMToken, PushNotificationLog
from app.models.vehicle_location import VehicleLocation, TemperatureAlert
from app.schemas.mobile import (
    MobileLoginRequest,
    MobileLoginResponse,
    RefreshTokenRequest,
    DeviceRegistration,
    DeviceInfo,
    SendPushNotificationRequest,
    NotificationResponse,
    LocationUpdate,
    BatchLocationUpdate,
    LocationResponse,
    PhotoUploadRequest,
    PhotoResponse,
    DispatchSummary,
    MobileDispatchDetail,
    MobileStatistics,
    SyncRequest,
    SyncResponse,
    NotificationPriority,
)
from app.services.fcm_service import fcm_service

router = APIRouter(prefix="/mobile/v2", tags=["Mobile API v2"])


# ==================== Authentication ====================

@router.post("/auth/login", response_model=MobileLoginResponse)
async def mobile_login(
    request: MobileLoginRequest,
    db: Session = Depends(get_db)
):
    """
    모바일 로그인 (디바이스 등록 포함)
    """
    # 사용자 인증
    from app.services.auth_service import AuthService
    
    user = AuthService.authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="사용자명 또는 비밀번호가 올바르지 않습니다")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="비활성화된 계정입니다")
    
    # Access token 생성
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Refresh token 생성 (30일)
    refresh_token = secrets.token_urlsafe(32)
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    
    # Refresh token을 사용자 정보에 저장 (실제로는 별도 테이블에 저장)
    # 여기서는 간단히 처리
    
    # FCM 토큰 등록
    if request.fcm_token:
        existing_token = db.query(FCMToken).filter(
            FCMToken.token == request.fcm_token
        ).first()
        
        if existing_token:
            # 기존 토큰 업데이트
            existing_token.user_id = user.id
            existing_token.device_type = request.device_type.value
            existing_token.device_id = request.device_id
            existing_token.app_version = request.app_version
            existing_token.is_active = True
            existing_token.last_used_at = datetime.utcnow()
        else:
            # 새 토큰 생성
            new_token = FCMToken(
                user_id=user.id,
                token=request.fcm_token,
                device_type=request.device_type.value,
                device_id=request.device_id,
                app_version=request.app_version,
                is_active=True
            )
            db.add(new_token)
    
    # 마지막 로그인 시간 업데이트
    user.last_login = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"✅ Mobile login: user={user.username}, device={request.device_type.value}")
    
    return MobileLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        user_id=user.id,
        username=user.username,
        role=user.role.value,
        full_name=user.full_name
    )


@router.post("/auth/refresh")
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Access token 갱신
    """
    # Refresh token 검증 (실제로는 DB에서 확인)
    # 여기서는 간단히 새 토큰 발급
    
    # 실제 구현에서는:
    # 1. Refresh token이 DB에 있는지 확인
    # 2. 만료되지 않았는지 확인
    # 3. 사용자 정보 가져오기
    # 4. 새 access token 발급
    
    raise HTTPException(status_code=501, detail="Refresh token not implemented yet")


@router.post("/auth/logout")
async def mobile_logout(
    fcm_token: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    모바일 로그아웃 (FCM 토큰 비활성화)
    """
    if fcm_token:
        token = db.query(FCMToken).filter(
            FCMToken.user_id == current_user.id,
            FCMToken.token == fcm_token
        ).first()
        
        if token:
            token.is_active = False
            db.commit()
    
    return {"message": "로그아웃 되었습니다"}


# ==================== Device Management ====================

@router.post("/devices/register", response_model=DeviceInfo)
async def register_device(
    request: DeviceRegistration,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    디바이스 등록 (FCM 토큰)
    """
    # 기존 토큰 확인
    existing = db.query(FCMToken).filter(
        FCMToken.token == request.fcm_token
    ).first()
    
    if existing:
        # 기존 토큰 업데이트
        existing.user_id = current_user.id
        existing.device_type = request.device_type.value
        existing.device_id = request.device_id
        existing.app_version = request.app_version
        existing.is_active = True
        existing.last_used_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    
    # 새 토큰 생성
    new_token = FCMToken(
        user_id=current_user.id,
        token=request.fcm_token,
        device_type=request.device_type.value,
        device_id=request.device_id,
        app_version=request.app_version,
        is_active=True
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    
    logger.info(f"✅ Device registered: user={current_user.username}, device={request.device_type.value}")
    
    return new_token


@router.get("/devices", response_model=List[DeviceInfo])
async def list_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 디바이스 목록 조회
    """
    devices = db.query(FCMToken).filter(
        FCMToken.user_id == current_user.id,
        FCMToken.is_active == True
    ).order_by(FCMToken.last_used_at.desc()).all()
    
    return devices


@router.delete("/devices/{device_id}")
async def remove_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    디바이스 제거
    """
    device = db.query(FCMToken).filter(
        FCMToken.id == device_id,
        FCMToken.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device.is_active = False
    db.commit()
    
    return {"message": "Device removed successfully"}


# ==================== Push Notifications ====================

@router.post("/notifications/send")
async def send_push_notification(
    request: SendPushNotificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    푸시 알림 발송 (관리자 전용)
    """
    # 권한 확인
    if current_user.role not in ["ADMIN", "DISPATCHER"]:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    # 수신자 토큰 조회
    query = db.query(FCMToken).filter(FCMToken.is_active == True)
    
    if request.user_ids:
        query = query.filter(FCMToken.user_id.in_(request.user_ids))
    
    tokens = query.all()
    
    if not tokens:
        raise HTTPException(status_code=404, detail="No active devices found")
    
    # 백그라운드에서 알림 발송
    def send_notifications():
        for token in tokens:
            try:
                result = fcm_service.send_push(
                    token=token.token,
                    title=request.title,
                    body=request.body,
                    data=request.data or {},
                    image_url=request.image_url
                )
                
                # 로그 저장
                log = PushNotificationLog(
                    user_id=token.user_id,
                    token=token.token,
                    title=request.title,
                    body=request.body,
                    data_json=str(request.data) if request.data else None,
                    notification_type=request.notification_type.value,
                    status="sent" if result["success"] else "failed",
                    error_message=result.get("error")
                )
                db.add(log)
            except Exception as e:
                logger.error(f"Failed to send notification: {str(e)}")
        
        db.commit()
    
    background_tasks.add_task(send_notifications)
    
    return {
        "message": "Notifications are being sent",
        "recipient_count": len(tokens)
    }


# ==================== GPS Location Tracking ====================

@router.post("/location", response_model=LocationResponse)
async def update_location(
    location: LocationUpdate,
    vehicle_id: Optional[int] = None,
    dispatch_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    단일 위치 업데이트
    """
    # 차량 ID 확인
    if not vehicle_id:
        # 현재 배차에서 차량 ID 가져오기
        dispatch = db.query(Dispatch).filter(
            Dispatch.driver_id == current_user.id,
            Dispatch.status.in_(["PENDING", "IN_PROGRESS"])
        ).order_by(Dispatch.scheduled_time.desc()).first()
        
        if dispatch:
            vehicle_id = dispatch.vehicle_id
            dispatch_id = dispatch.id
    
    if not vehicle_id:
        raise HTTPException(status_code=400, detail="Vehicle ID is required")
    
    # 위치 저장
    new_location = VehicleLocation(
        vehicle_id=vehicle_id,
        dispatch_id=dispatch_id,
        latitude=location.latitude,
        longitude=location.longitude,
        accuracy=location.accuracy,
        altitude=location.altitude,
        speed=location.speed,
        heading=location.heading,
        recorded_at=location.timestamp
    )
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    
    return new_location


@router.post("/location/batch", response_model=List[LocationResponse])
async def batch_update_locations(
    batch: BatchLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배치 위치 업데이트 (여러 위치 한 번에)
    오프라인에서 수집한 위치를 한 번에 업로드
    """
    vehicle_id = batch.vehicle_id
    dispatch_id = batch.dispatch_id
    
    # 차량 ID 확인
    if not vehicle_id:
        dispatch = db.query(Dispatch).filter(
            Dispatch.driver_id == current_user.id,
            Dispatch.status.in_(["PENDING", "IN_PROGRESS"])
        ).order_by(Dispatch.scheduled_time.desc()).first()
        
        if dispatch:
            vehicle_id = dispatch.vehicle_id
            dispatch_id = dispatch.id
    
    if not vehicle_id:
        raise HTTPException(status_code=400, detail="Vehicle ID is required")
    
    # 배치 위치 저장
    new_locations = []
    for location in batch.locations:
        new_loc = VehicleLocation(
            vehicle_id=vehicle_id,
            dispatch_id=dispatch_id,
            latitude=location.latitude,
            longitude=location.longitude,
            accuracy=location.accuracy,
            altitude=location.altitude,
            speed=location.speed,
            heading=location.heading,
            recorded_at=location.timestamp
        )
        db.add(new_loc)
        new_locations.append(new_loc)
    
    db.commit()
    
    # Refresh all locations
    for loc in new_locations:
        db.refresh(loc)
    
    logger.info(f"✅ Batch location update: {len(new_locations)} locations saved")
    
    return new_locations


@router.get("/location/history", response_model=List[LocationResponse])
async def get_location_history(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 위치 이력 조회
    """
    # 현재 배차 정보 가져오기
    dispatch = db.query(Dispatch).filter(
        Dispatch.driver_id == current_user.id,
        Dispatch.status.in_(["PENDING", "IN_PROGRESS"])
    ).order_by(Dispatch.scheduled_time.desc()).first()
    
    if not dispatch:
        return []
    
    # 위치 이력 조회
    query = db.query(VehicleLocation).filter(
        VehicleLocation.vehicle_id == dispatch.vehicle_id
    )
    
    if start_time:
        query = query.filter(VehicleLocation.recorded_at >= start_time)
    if end_time:
        query = query.filter(VehicleLocation.recorded_at <= end_time)
    
    locations = query.order_by(
        VehicleLocation.recorded_at.desc()
    ).limit(limit).all()
    
    return locations


# ==================== Photo Upload ====================

@router.post("/photos/upload", response_model=PhotoResponse)
async def upload_photo(
    file: UploadFile = File(...),
    photo_type: str = Form(...),
    dispatch_id: Optional[int] = Form(None),
    vehicle_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    사진 업로드 (배송 증명, 차량 점검 등)
    
    TODO: 실제 구현 시 S3/MinIO에 업로드
    """
    # 파일 검증
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Image file required")
    
    # 파일 크기 제한 (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    # 임시로 로컬에 저장 (실제로는 S3/MinIO)
    filename = f"{datetime.utcnow().timestamp()}_{file.filename}"
    file_path = f"uploads/mobile_photos/{photo_type}/{filename}"
    
    # TODO: 실제 파일 저장 로직
    # - S3/MinIO에 업로드
    # - 썸네일 생성
    # - 이미지 압축
    
    # 메타데이터 저장 (실제로는 photos 테이블에 저장)
    photo_data = {
        "id": 1,  # TODO: DB에서 생성
        "photo_type": photo_type,
        "url": file_path,
        "thumbnail_url": f"{file_path}_thumb.jpg",
        "file_size": len(contents),
        "mime_type": file.content_type,
        "width": None,  # TODO: 이미지 메타데이터 추출
        "height": None,
        "latitude": latitude,
        "longitude": longitude,
        "uploaded_at": datetime.utcnow()
    }
    
    logger.info(f"✅ Photo uploaded: type={photo_type}, user={current_user.username}")
    
    return PhotoResponse(**photo_data)


# ==================== Dispatch & Statistics ====================

@router.get("/summary", response_model=DispatchSummary)
async def get_dispatch_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    오늘의 배차 요약
    """
    today = datetime.now().date()
    
    dispatches = db.query(Dispatch).filter(
        Dispatch.driver_id == current_user.id,
        func.date(Dispatch.scheduled_time) == today
    ).all()
    
    summary = DispatchSummary(
        total=len(dispatches),
        pending=sum(1 for d in dispatches if d.status == "PENDING"),
        in_progress=sum(1 for d in dispatches if d.status == "IN_PROGRESS"),
        completed=sum(1 for d in dispatches if d.status == "COMPLETED"),
        cancelled=sum(1 for d in dispatches if d.status == "CANCELLED"),
        today_earnings=sum(d.estimated_cost or 0 for d in dispatches if d.status == "COMPLETED")
    )
    
    return summary


@router.get("/statistics", response_model=MobileStatistics)
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    드라이버 통계 (오늘, 이번 주, 전체)
    """
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    # 오늘 통계
    today_dispatches = db.query(Dispatch).filter(
        Dispatch.driver_id == current_user.id,
        func.date(Dispatch.scheduled_time) == today
    ).all()
    
    # 이번 주 통계
    week_dispatches = db.query(Dispatch).filter(
        Dispatch.driver_id == current_user.id,
        Dispatch.scheduled_time >= week_start
    ).all()
    
    # 전체 통계
    total_dispatches = db.query(func.count(Dispatch.id)).filter(
        Dispatch.driver_id == current_user.id,
        Dispatch.status == "COMPLETED"
    ).scalar() or 0
    
    total_distance = db.query(func.sum(Dispatch.distance_km)).filter(
        Dispatch.driver_id == current_user.id,
        Dispatch.status == "COMPLETED"
    ).scalar() or 0.0
    
    statistics = MobileStatistics(
        today_dispatches=len(today_dispatches),
        today_completed=sum(1 for d in today_dispatches if d.status == "COMPLETED"),
        today_distance_km=sum(d.distance_km or 0 for d in today_dispatches if d.status == "COMPLETED"),
        today_earnings=sum(d.estimated_cost or 0 for d in today_dispatches if d.status == "COMPLETED"),
        
        week_dispatches=len(week_dispatches),
        week_completed=sum(1 for d in week_dispatches if d.status == "COMPLETED"),
        week_distance_km=sum(d.distance_km or 0 for d in week_dispatches if d.status == "COMPLETED"),
        week_earnings=sum(d.estimated_cost or 0 for d in week_dispatches if d.status == "COMPLETED"),
        
        total_dispatches=total_dispatches,
        total_distance_km=total_distance,
        rating=None,  # TODO: 평점 시스템 구현
        rating_count=0
    )
    
    return statistics


# ==================== Offline Sync ====================

@router.post("/sync", response_model=SyncResponse)
async def sync_data(
    request: SyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    오프라인 데이터 동기화
    """
    last_sync = request.last_sync or (datetime.utcnow() - timedelta(days=7))
    
    response = SyncResponse(
        sync_time=datetime.utcnow(),
        has_more=False
    )
    
    # 배차 동기화
    if "dispatches" in request.sync_types:
        dispatches = db.query(Dispatch).filter(
            Dispatch.driver_id == current_user.id,
            Dispatch.updated_at >= last_sync
        ).order_by(Dispatch.updated_at.desc()).limit(50).all()
        
        # TODO: MobileDispatchDetail로 변환
        # response.dispatches = [convert_to_mobile_dispatch(d) for d in dispatches]
    
    # 알림 동기화
    if "notifications" in request.sync_types:
        # TODO: 알림 조회 및 추가
        pass
    
    return response


# ==================== Health Check ====================

@router.get("/health")
async def mobile_api_health():
    """
    모바일 API 상태 확인
    """
    return {
        "status": "healthy",
        "service": "Mobile API v2",
        "timestamp": datetime.utcnow().isoformat(),
        "fcm_enabled": fcm_service.enabled
    }
