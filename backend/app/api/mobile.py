"""
모바일 앱 전용 API
Phase 4 Week 9-10: Mobile App Development
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, date
import io

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.dispatch import Dispatch
from app.models.vehicle import Vehicle
from app.models.order import Order
from app.models.driver import Driver
from app.models.driver_daily_mileage import DriverDailyMileage
from app.schemas.dispatch import DispatchResponse
from app.schemas.vehicle import VehicleResponse
from app.services.driver_mileage_excel_service import DriverMileageExcelService
from app.services.driver_mileage_pdf_service import DriverMileagePDFService

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


# ========== 운전자 주행거리 API (모바일 전용) ==========

@router.get("/driver-mileage/my-summary")
async def get_my_mileage_summary(
    start_date: Optional[date] = Query(None, description="시작 날짜 (기본: 7일전)"),
    end_date: Optional[date] = Query(None, description="종료 날짜 (기본: 오늘)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 주행거리 요약 (모바일용)
    운전자 본인의 주행거리 통계를 조회합니다.
    """
    # 기본 날짜 설정
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=7)
    
    # 운전자 정보 조회
    driver = db.query(Driver).filter(
        Driver.user_id == current_user.id
    ).first()
    
    if not driver:
        return {
            "success": False,
            "message": "운전자 정보를 찾을 수 없습니다",
            "driver_id": None,
            "driver_name": current_user.username,
            "period": f"{start_date} ~ {end_date}",
            "total_distance_km": 0,
            "total_driving_hours": 0,
            "driving_days": 0,
            "avg_distance_per_day": 0,
            "avg_speed_kmh": 0,
            "daily_records": []
        }
    
    # 주행거리 데이터 조회
    records = db.query(DriverDailyMileage).filter(
        DriverDailyMileage.driver_id == driver.id,
        DriverDailyMileage.date >= start_date,
        DriverDailyMileage.date <= end_date
    ).order_by(DriverDailyMileage.date.desc()).all()
    
    # 통계 계산
    total_distance = sum(r.total_distance_km or 0 for r in records)
    total_driving_minutes = sum(r.total_driving_minutes or 0 for r in records)
    driving_days = len(records)
    
    avg_distance = total_distance / driving_days if driving_days > 0 else 0
    avg_speed = sum(r.avg_speed_kmh or 0 for r in records) / driving_days if driving_days > 0 else 0
    
    return {
        "success": True,
        "driver_id": driver.id,
        "driver_name": driver.name or current_user.username,
        "driver_code": driver.code,
        "period": f"{start_date} ~ {end_date}",
        "total_distance_km": round(total_distance, 2),
        "total_driving_hours": round(total_driving_minutes / 60, 1),
        "driving_days": driving_days,
        "avg_distance_per_day": round(avg_distance, 2),
        "avg_speed_kmh": round(avg_speed, 1),
        "daily_records": [
            {
                "date": str(r.date),
                "distance_km": round(r.total_distance_km or 0, 2),
                "driving_minutes": r.total_driving_minutes or 0,
                "driving_hours": round((r.total_driving_minutes or 0) / 60, 1),
                "engine_on_minutes": r.engine_on_minutes or 0,
                "idle_minutes": r.idle_minutes or 0,
                "avg_speed": round(r.avg_speed_kmh or 0, 1),
                "max_speed": round(r.max_speed_kmh or 0, 1),
                "start_time": r.start_time.isoformat() if r.start_time else None,
                "end_time": r.end_time.isoformat() if r.end_time else None,
                "vehicle_count": r.vehicle_count or 0
            }
            for r in records
        ]
    }


@router.get("/driver-mileage/my-daily")
async def get_my_daily_mileage(
    target_date: Optional[date] = Query(None, description="조회 날짜 (기본: 어제)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 일별 주행거리 (모바일용)
    특정 날짜의 운전자 본인 주행거리를 조회합니다.
    """
    # 기본 날짜 설정 (어제)
    if not target_date:
        target_date = date.today() - timedelta(days=1)
    
    # 운전자 정보 조회
    driver = db.query(Driver).filter(
        Driver.user_id == current_user.id
    ).first()
    
    if not driver:
        return {
            "success": False,
            "message": "운전자 정보를 찾을 수 없습니다",
            "date": str(target_date),
            "data": None
        }
    
    # 주행거리 데이터 조회
    record = db.query(DriverDailyMileage).filter(
        DriverDailyMileage.driver_id == driver.id,
        DriverDailyMileage.date == target_date
    ).first()
    
    if not record:
        return {
            "success": True,
            "message": "해당 날짜에 주행 기록이 없습니다",
            "date": str(target_date),
            "data": None
        }
    
    return {
        "success": True,
        "date": str(target_date),
        "data": {
            "driver_id": driver.id,
            "driver_name": driver.name or current_user.username,
            "driver_code": driver.code,
            "distance_km": round(record.total_distance_km or 0, 2),
            "driving_minutes": record.total_driving_minutes or 0,
            "driving_hours": round((record.total_driving_minutes or 0) / 60, 1),
            "engine_on_minutes": record.engine_on_minutes or 0,
            "idle_minutes": record.idle_minutes or 0,
            "avg_speed": round(record.avg_speed_kmh or 0, 1),
            "max_speed": round(record.max_speed_kmh or 0, 1),
            "start_time": record.start_time.isoformat() if record.start_time else None,
            "end_time": record.end_time.isoformat() if record.end_time else None,
            "vehicle_count": record.vehicle_count or 0,
            "vehicle_ids": record.vehicle_ids,
            "calculation_method": record.calculation_method
        }
    }


@router.get("/driver-mileage/my-ranking")
async def get_my_ranking(
    start_date: Optional[date] = Query(None, description="시작 날짜 (기본: 30일전)"),
    end_date: Optional[date] = Query(None, description="종료 날짜 (기본: 오늘)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 순위 조회 (모바일용)
    전체 운전자 중 내 주행거리 순위를 확인합니다.
    """
    # 기본 날짜 설정
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # 운전자 정보 조회
    driver = db.query(Driver).filter(
        Driver.user_id == current_user.id
    ).first()
    
    if not driver:
        return {
            "success": False,
            "message": "운전자 정보를 찾을 수 없습니다",
            "my_rank": None,
            "total_drivers": 0
        }
    
    # 전체 운전자 주행거리 집계
    from sqlalchemy import func
    
    rankings = db.query(
        DriverDailyMileage.driver_id,
        func.sum(DriverDailyMileage.total_distance_km).label('total_distance')
    ).filter(
        DriverDailyMileage.date >= start_date,
        DriverDailyMileage.date <= end_date
    ).group_by(
        DriverDailyMileage.driver_id
    ).order_by(
        func.sum(DriverDailyMileage.total_distance_km).desc()
    ).all()
    
    # 내 순위 찾기
    my_rank = None
    my_distance = 0
    for idx, (driver_id, distance) in enumerate(rankings, 1):
        if driver_id == driver.id:
            my_rank = idx
            my_distance = distance or 0
            break
    
    return {
        "success": True,
        "period": f"{start_date} ~ {end_date}",
        "my_rank": my_rank,
        "total_drivers": len(rankings),
        "my_distance_km": round(my_distance, 2) if my_distance else 0,
        "top_driver_distance_km": round(rankings[0][1], 2) if rankings else 0
    }


@router.get("/driver-mileage/export/my-excel")
async def download_my_excel(
    start_date: Optional[date] = Query(None, description="시작 날짜 (기본: 30일전)"),
    end_date: Optional[date] = Query(None, description="종료 날짜 (기본: 오늘)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 주행거리 Excel 다운로드 (모바일용)
    """
    # 기본 날짜 설정
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # 운전자 정보 조회
    driver = db.query(Driver).filter(
        Driver.user_id == current_user.id
    ).first()
    
    if not driver:
        raise HTTPException(status_code=404, detail="운전자 정보를 찾을 수 없습니다")
    
    # 주행거리 데이터 조회
    records = db.query(DriverDailyMileage).filter(
        DriverDailyMileage.driver_id == driver.id,
        DriverDailyMileage.date >= start_date,
        DriverDailyMileage.date <= end_date
    ).order_by(DriverDailyMileage.date.asc()).all()
    
    # Excel 생성
    excel_service = DriverMileageExcelService(db)
    excel_bytes = excel_service.generate_custom_report(
        records=records,
        title=f"{driver.name or current_user.username} 주행거리 리포트",
        period=f"{start_date} ~ {end_date}"
    )
    
    # 파일명 생성
    filename = f"my_mileage_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/driver-mileage/export/my-pdf")
async def download_my_pdf(
    start_date: Optional[date] = Query(None, description="시작 날짜 (기본: 30일전)"),
    end_date: Optional[date] = Query(None, description="종료 날짜 (기본: 오늘)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 주행거리 PDF 다운로드 (모바일용)
    """
    # 기본 날짜 설정
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # 운전자 정보 조회
    driver = db.query(Driver).filter(
        Driver.user_id == current_user.id
    ).first()
    
    if not driver:
        raise HTTPException(status_code=404, detail="운전자 정보를 찾을 수 없습니다")
    
    # 주행거리 데이터 조회
    records = db.query(DriverDailyMileage).filter(
        DriverDailyMileage.driver_id == driver.id,
        DriverDailyMileage.date >= start_date,
        DriverDailyMileage.date <= end_date
    ).order_by(DriverDailyMileage.date.asc()).all()
    
    # PDF 생성
    pdf_service = DriverMileagePDFService(db)
    pdf_bytes = pdf_service.generate_custom_report(
        records=records,
        driver_name=driver.name or current_user.username,
        period=f"{start_date} ~ {end_date}"
    )
    
    # 파일명 생성
    filename = f"my_mileage_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
