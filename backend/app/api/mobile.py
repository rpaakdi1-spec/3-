"""
모바일 앱 전용 API
Phase 4 Week 9-10: Mobile App Development
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.dispatch import Dispatch
from app.models.vehicle import Vehicle
from app.models.order import Order
from app.schemas.dispatch import DispatchResponse
from app.schemas.vehicle import VehicleResponse

router = APIRouter()


@router.get("/summary")
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
        Dispatch.scheduled_time >= today,
        Dispatch.scheduled_time < today + timedelta(days=1)
    ).all()
    
    summary = {
        "total": len(dispatches),
        "pending": sum(1 for d in dispatches if d.status == "PENDING"),
        "in_progress": sum(1 for d in dispatches if d.status == "IN_PROGRESS"),
        "completed": sum(1 for d in dispatches if d.status == "COMPLETED"),
    }
    
    return summary


@router.get("/dispatches", response_model=List[DispatchResponse])
async def get_mobile_dispatches(
    status: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    모바일용 배차 목록 조회
    """
    query = db.query(Dispatch).filter(
        Dispatch.driver_id == current_user.id
    )
    
    if status:
        query = query.filter(Dispatch.status == status)
    
    dispatches = query.order_by(
        Dispatch.scheduled_time.desc()
    ).limit(limit).all()
    
    return dispatches


@router.get("/dispatches/{dispatch_id}")
async def get_dispatch_detail(
    dispatch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배차 상세 정보
    """
    dispatch = db.query(Dispatch).filter(
        Dispatch.id == dispatch_id,
        Dispatch.driver_id == current_user.id
    ).first()
    
    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    
    # 주문 정보 포함
    order = db.query(Order).filter(Order.id == dispatch.order_id).first()
    
    return {
        "id": dispatch.id,
        "order_id": dispatch.order_id,
        "vehicle_id": dispatch.vehicle_id,
        "status": dispatch.status,
        "pickup_address": order.pickup_address if order else "",
        "pickup_contact": order.client_contact if order else "",
        "delivery_address": order.delivery_address if order else "",
        "delivery_contact": order.client_contact if order else "",
        "scheduled_time": dispatch.scheduled_time,
        "notes": order.notes if order else "",
    }


@router.put("/dispatches/{dispatch_id}/status")
async def update_dispatch_status(
    dispatch_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배차 상태 업데이트
    """
    dispatch = db.query(Dispatch).filter(
        Dispatch.id == dispatch_id,
        Dispatch.driver_id == current_user.id
    ).first()
    
    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    
    # 상태 검증
    valid_statuses = ["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    dispatch.status = status
    
    if status == "IN_PROGRESS":
        dispatch.actual_start_time = datetime.now()
    elif status == "COMPLETED":
        dispatch.actual_end_time = datetime.now()
    
    db.commit()
    db.refresh(dispatch)
    
    return {"message": "Status updated successfully", "dispatch": dispatch}


@router.get("/vehicle", response_model=VehicleResponse)
async def get_assigned_vehicle(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    할당된 차량 정보
    """
    # 드라이버에게 할당된 차량 조회
    dispatch = db.query(Dispatch).filter(
        Dispatch.driver_id == current_user.id,
        Dispatch.status.in_(["PENDING", "IN_PROGRESS"])
    ).order_by(Dispatch.scheduled_time.desc()).first()
    
    if not dispatch:
        raise HTTPException(status_code=404, detail="No assigned vehicle")
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == dispatch.vehicle_id
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return vehicle


@router.post("/delivery-proof")
async def upload_delivery_proof(
    dispatch_id: int,
    photo: UploadFile = File(...),
    signature: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배송 증빙 자료 업로드
    """
    dispatch = db.query(Dispatch).filter(
        Dispatch.id == dispatch_id,
        Dispatch.driver_id == current_user.id
    ).first()
    
    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    
    # 파일 저장 (실제 구현에서는 S3 등에 업로드)
    photo_path = f"uploads/delivery_proofs/{dispatch_id}_{datetime.now().timestamp()}.jpg"
    
    # 배차 정보 업데이트
    dispatch.delivery_proof_photo = photo_path
    
    if signature:
        signature_path = f"uploads/signatures/{dispatch_id}_{datetime.now().timestamp()}.png"
        dispatch.delivery_proof_signature = signature_path
    
    dispatch.proof_uploaded_at = datetime.now()
    
    db.commit()
    
    return {
        "message": "Delivery proof uploaded successfully",
        "photo_url": photo_path,
        "signature_url": dispatch.delivery_proof_signature if signature else None
    }


@router.post("/register-device")
async def register_device(
    fcm_token: str,
    device_type: str,  # "android" or "ios"
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    푸시 알림용 디바이스 등록
    """
    # 디바이스 정보 저장 (실제 구현에서는 devices 테이블에 저장)
    # 여기서는 user 테이블에 fcm_token 추가
    current_user.fcm_token = fcm_token
    current_user.device_type = device_type
    current_user.device_id = device_id
    
    db.commit()
    
    return {
        "message": "Device registered successfully",
        "fcm_token": fcm_token
    }


@router.get("/sync")
async def sync_data(
    last_sync: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    오프라인 데이터 동기화
    """
    sync_time = datetime.fromisoformat(last_sync) if last_sync else datetime.now() - timedelta(days=7)
    
    # 최근 변경된 데이터 조회
    dispatches = db.query(Dispatch).filter(
        Dispatch.driver_id == current_user.id,
        Dispatch.updated_at >= sync_time
    ).all()
    
    return {
        "sync_time": datetime.now().isoformat(),
        "dispatches": dispatches,
        "has_more": False
    }


@router.post("/location")
async def update_location(
    latitude: float,
    longitude: float,
    accuracy: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    드라이버 위치 업데이트
    """
    # 위치 정보 저장 (실제 구현에서는 location_tracking 테이블에 저장)
    # 여기서는 user 테이블에 최신 위치만 저장
    current_user.last_latitude = latitude
    current_user.last_longitude = longitude
    current_user.location_updated_at = datetime.now()
    
    db.commit()
    
    return {
        "message": "Location updated successfully",
        "latitude": latitude,
        "longitude": longitude
    }


@router.get("/notifications")
async def get_notifications(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    알림 목록 조회
    """
    # 실제 구현에서는 notifications 테이블에서 조회
    notifications = [
        {
            "id": 1,
            "type": "NEW_DISPATCH",
            "title": "새 배차 알림",
            "message": "새로운 배차가 배정되었습니다.",
            "created_at": datetime.now().isoformat(),
            "read": False
        }
    ]
    
    return notifications


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    알림 읽음 처리
    """
    # 실제 구현에서는 notifications 테이블 업데이트
    return {"message": "Notification marked as read"}
