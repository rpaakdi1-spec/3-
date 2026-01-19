"""
Vehicle Tracking API
실시간 차량 추적 및 온도 모니터링 API
"""
from datetime import datetime, timedelta, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from loguru import logger

from ..database import get_db
from ..models import Vehicle, VehicleLocation, TemperatureAlert, Dispatch, DispatchStatus
from ..schemas.vehicle_location import (
    VehicleLocationResponse,
    VehicleLocationCreate,
    TemperatureAlertResponse,
    VehicleTrackingInfo,
    TrackingDashboardResponse,
)
from ..services.uvis_tracking_service import UVISTrackingService


router = APIRouter(
    prefix="/tracking",
    tags=["tracking"],
)


@router.post("/sync-vehicle/{vehicle_id}", response_model=VehicleLocationResponse)
async def sync_vehicle_tracking(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 차량의 UVIS 데이터 동기화
    
    - **vehicle_id**: 차량 ID
    """
    # 차량 조회
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    
    if not vehicle.uvis_enabled or not vehicle.uvis_device_id:
        raise HTTPException(status_code=400, detail="UVIS가 활성화되지 않은 차량입니다")
    
    # UVIS 서비스
    uvis_service = UVISTrackingService()
    
    # 위치 및 온도 데이터 조회
    status_data = await uvis_service.get_vehicle_full_status(vehicle.uvis_device_id)
    if not status_data:
        raise HTTPException(status_code=503, detail="UVIS API에서 데이터를 가져올 수 없습니다")
    
    # 현재 진행 중인 배차 찾기
    today = date.today()
    dispatch = db.query(Dispatch).filter(
        and_(
            Dispatch.vehicle_id == vehicle_id,
            Dispatch.dispatch_date == today,
            Dispatch.status.in_([DispatchStatus.CONFIRMED, DispatchStatus.IN_PROGRESS])
        )
    ).first()
    
    dispatch_id = dispatch.id if dispatch else None
    
    # 위치 데이터 저장
    location = uvis_service.save_vehicle_location(
        db=db,
        vehicle_id=vehicle_id,
        location_data=status_data,
        dispatch_id=dispatch_id
    )
    
    # 온도 알림 체크
    if status_data.get("temperature") is not None:
        uvis_service.check_temperature_alert(
            db=db,
            vehicle_id=vehicle_id,
            temperature=status_data["temperature"],
            vehicle_type=vehicle.vehicle_type.value,
            dispatch_id=dispatch_id,
            location_id=location.id
        )
    
    # 응답 구성
    location_response = VehicleLocationResponse.model_validate(location)
    location_response.vehicle_code = vehicle.code
    location_response.vehicle_plate_number = vehicle.plate_number
    
    return location_response


@router.post("/sync-all")
async def sync_all_vehicles(
    db: Session = Depends(get_db)
):
    """
    모든 UVIS 연동 차량의 데이터 동기화 (배치)
    """
    # UVIS가 활성화된 모든 차량 조회
    vehicles = db.query(Vehicle).filter(
        and_(
            Vehicle.uvis_enabled == True,
            Vehicle.uvis_device_id.isnot(None),
            Vehicle.is_active == True
        )
    ).all()
    
    if not vehicles:
        return {"message": "UVIS 연동 차량이 없습니다", "synced_count": 0}
    
    uvis_service = UVISTrackingService()
    
    # 배치 조회
    device_ids = [v.uvis_device_id for v in vehicles]
    status_data_dict = await uvis_service.batch_get_vehicles_status(device_ids)
    
    synced_count = 0
    today = date.today()
    
    for vehicle in vehicles:
        try:
            status_data = status_data_dict.get(vehicle.uvis_device_id)
            if not status_data:
                logger.warning(f"UVIS 데이터 없음: vehicle_id={vehicle.id}, device_id={vehicle.uvis_device_id}")
                continue
            
            # 현재 진행 중인 배차 찾기
            dispatch = db.query(Dispatch).filter(
                and_(
                    Dispatch.vehicle_id == vehicle.id,
                    Dispatch.dispatch_date == today,
                    Dispatch.status.in_([DispatchStatus.CONFIRMED, DispatchStatus.IN_PROGRESS])
                )
            ).first()
            
            dispatch_id = dispatch.id if dispatch else None
            
            # 위치 데이터 저장
            location = uvis_service.save_vehicle_location(
                db=db,
                vehicle_id=vehicle.id,
                location_data=status_data,
                dispatch_id=dispatch_id
            )
            
            # 온도 알림 체크
            if status_data.get("temperature") is not None:
                uvis_service.check_temperature_alert(
                    db=db,
                    vehicle_id=vehicle.id,
                    temperature=status_data["temperature"],
                    vehicle_type=vehicle.vehicle_type.value,
                    dispatch_id=dispatch_id,
                    location_id=location.id
                )
            
            synced_count += 1
            
        except Exception as e:
            logger.error(f"차량 동기화 실패: vehicle_id={vehicle.id}, error={str(e)}")
            continue
    
    return {
        "message": f"{synced_count}대 차량 동기화 완료",
        "total_vehicles": len(vehicles),
        "synced_count": synced_count
    }


@router.get("/dashboard", response_model=TrackingDashboardResponse)
async def get_tracking_dashboard(
    dispatch_date: Optional[date] = Query(None, description="배차 날짜 (기본: 오늘)"),
    db: Session = Depends(get_db)
):
    """
    실시간 추적 대시보드 데이터 조회
    
    - **dispatch_date**: 배차 날짜 (선택, 기본값: 오늘)
    """
    if not dispatch_date:
        dispatch_date = date.today()
    
    # 전체 차량 수
    total_vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).count()
    
    # 오늘 배차된 차량 (운행 중)
    active_dispatches = db.query(Dispatch).filter(
        and_(
            Dispatch.dispatch_date == dispatch_date,
            Dispatch.status.in_([DispatchStatus.CONFIRMED, DispatchStatus.IN_PROGRESS])
        )
    ).all()
    
    active_vehicle_ids = [d.vehicle_id for d in active_dispatches]
    active_vehicles_count = len(active_vehicle_ids)
    idle_vehicles_count = total_vehicles - active_vehicles_count
    
    # 차량별 추적 정보
    vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).all()
    
    vehicle_tracking_list = []
    
    for vehicle in vehicles:
        # 최신 위치
        latest_location = db.query(VehicleLocation).filter(
            VehicleLocation.vehicle_id == vehicle.id
        ).order_by(VehicleLocation.recorded_at.desc()).first()
        
        # 오늘 배차
        dispatch = db.query(Dispatch).filter(
            and_(
                Dispatch.vehicle_id == vehicle.id,
                Dispatch.dispatch_date == dispatch_date,
                Dispatch.status.in_([DispatchStatus.CONFIRMED, DispatchStatus.IN_PROGRESS])
            )
        ).first()
        
        # 오늘 주행 거리
        today_start = datetime.combine(dispatch_date, datetime.min.time())
        today_end = datetime.combine(dispatch_date, datetime.max.time())
        
        total_distance = db.query(func.sum(VehicleLocation.speed)).filter(
            and_(
                VehicleLocation.vehicle_id == vehicle.id,
                VehicleLocation.recorded_at >= today_start,
                VehicleLocation.recorded_at <= today_end
            )
        ).scalar() or 0.0
        
        # 평균 속도
        avg_speed = db.query(func.avg(VehicleLocation.speed)).filter(
            and_(
                VehicleLocation.vehicle_id == vehicle.id,
                VehicleLocation.recorded_at >= today_start,
                VehicleLocation.recorded_at <= today_end,
                VehicleLocation.speed.isnot(None)
            )
        ).scalar() or 0.0
        
        # 활성 알림
        active_alerts = db.query(TemperatureAlert).filter(
            and_(
                TemperatureAlert.vehicle_id == vehicle.id,
                TemperatureAlert.is_resolved == False
            )
        ).order_by(TemperatureAlert.detected_at.desc()).limit(5).all()
        
        # 응답 구성
        location_response = None
        if latest_location:
            location_response = VehicleLocationResponse.model_validate(latest_location)
            location_response.vehicle_code = vehicle.code
            location_response.vehicle_plate_number = vehicle.plate_number
        
        alert_responses = []
        for alert in active_alerts:
            alert_response = TemperatureAlertResponse.model_validate(alert)
            alert_response.vehicle_code = vehicle.code
            alert_response.vehicle_plate_number = vehicle.plate_number
            alert_responses.append(alert_response)
        
        tracking_info = VehicleTrackingInfo(
            vehicle_id=vehicle.id,
            vehicle_code=vehicle.code,
            plate_number=vehicle.plate_number,
            vehicle_type=vehicle.vehicle_type.value,
            current_location=location_response,
            dispatch_id=dispatch.id if dispatch else None,
            dispatch_number=dispatch.dispatch_number if dispatch else None,
            dispatch_status=dispatch.status.value if dispatch else None,
            total_distance_today_km=round(total_distance / 1000, 2),
            average_speed_kmh=round(avg_speed, 1) if avg_speed else 0.0,
            last_update=latest_location.recorded_at if latest_location else None,
            active_alerts_count=len(active_alerts),
            recent_alerts=alert_responses
        )
        
        vehicle_tracking_list.append(tracking_info)
    
    # 전체 알림 통계
    total_alerts = db.query(TemperatureAlert).filter(
        TemperatureAlert.is_resolved == False
    ).count()
    
    critical_alerts = db.query(TemperatureAlert).filter(
        and_(
            TemperatureAlert.is_resolved == False,
            TemperatureAlert.severity == "CRITICAL"
        )
    ).count()
    
    warning_alerts = db.query(TemperatureAlert).filter(
        and_(
            TemperatureAlert.is_resolved == False,
            TemperatureAlert.severity == "WARNING"
        )
    ).count()
    
    return TrackingDashboardResponse(
        total_vehicles=total_vehicles,
        active_vehicles=active_vehicles_count,
        idle_vehicles=idle_vehicles_count,
        vehicles=vehicle_tracking_list,
        total_alerts=total_alerts,
        critical_alerts=critical_alerts,
        warning_alerts=warning_alerts
    )


@router.get("/vehicles/{vehicle_id}/locations", response_model=List[VehicleLocationResponse])
async def get_vehicle_location_history(
    vehicle_id: int,
    start_date: Optional[datetime] = Query(None, description="시작 시간"),
    end_date: Optional[datetime] = Query(None, description="종료 시간"),
    limit: int = Query(100, ge=1, le=1000, description="최대 결과 수"),
    db: Session = Depends(get_db)
):
    """
    특정 차량의 위치 이력 조회
    
    - **vehicle_id**: 차량 ID
    - **start_date**: 시작 시간 (선택)
    - **end_date**: 종료 시간 (선택)
    - **limit**: 최대 결과 수 (기본: 100, 최대: 1000)
    """
    # 차량 조회
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    
    # 기본값 설정
    if not start_date:
        start_date = datetime.utcnow() - timedelta(hours=24)
    if not end_date:
        end_date = datetime.utcnow()
    
    # 위치 이력 조회
    locations = db.query(VehicleLocation).filter(
        and_(
            VehicleLocation.vehicle_id == vehicle_id,
            VehicleLocation.recorded_at >= start_date,
            VehicleLocation.recorded_at <= end_date
        )
    ).order_by(VehicleLocation.recorded_at.desc()).limit(limit).all()
    
    # 응답 구성
    location_responses = []
    for location in locations:
        location_response = VehicleLocationResponse.model_validate(location)
        location_response.vehicle_code = vehicle.code
        location_response.vehicle_plate_number = vehicle.plate_number
        location_responses.append(location_response)
    
    return location_responses


@router.get("/alerts", response_model=List[TemperatureAlertResponse])
async def get_temperature_alerts(
    vehicle_id: Optional[int] = Query(None, description="차량 ID"),
    is_resolved: Optional[bool] = Query(None, description="해결 여부"),
    severity: Optional[str] = Query(None, description="심각도 (WARNING, CRITICAL)"),
    start_date: Optional[datetime] = Query(None, description="시작 시간"),
    end_date: Optional[datetime] = Query(None, description="종료 시간"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    온도 알림 목록 조회
    
    - **vehicle_id**: 차량 ID (선택)
    - **is_resolved**: 해결 여부 (선택)
    - **severity**: 심각도 (선택)
    - **start_date**: 시작 시간 (선택)
    - **end_date**: 종료 시간 (선택)
    - **skip**: 건너뛸 레코드 수
    - **limit**: 최대 결과 수
    """
    query = db.query(TemperatureAlert)
    
    # 필터 적용
    if vehicle_id is not None:
        query = query.filter(TemperatureAlert.vehicle_id == vehicle_id)
    
    if is_resolved is not None:
        query = query.filter(TemperatureAlert.is_resolved == is_resolved)
    
    if severity:
        query = query.filter(TemperatureAlert.severity == severity)
    
    if start_date:
        query = query.filter(TemperatureAlert.detected_at >= start_date)
    
    if end_date:
        query = query.filter(TemperatureAlert.detected_at <= end_date)
    
    # 정렬 및 페이징
    alerts = query.order_by(TemperatureAlert.detected_at.desc()).offset(skip).limit(limit).all()
    
    # 응답 구성
    alert_responses = []
    for alert in alerts:
        vehicle = db.query(Vehicle).filter(Vehicle.id == alert.vehicle_id).first()
        alert_response = TemperatureAlertResponse.model_validate(alert)
        if vehicle:
            alert_response.vehicle_code = vehicle.code
            alert_response.vehicle_plate_number = vehicle.plate_number
        alert_responses.append(alert_response)
    
    return alert_responses


@router.put("/alerts/{alert_id}/resolve")
async def resolve_temperature_alert(
    alert_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    온도 알림 해결 처리
    
    - **alert_id**: 알림 ID
    - **notes**: 해결 메모 (선택)
    """
    alert = db.query(TemperatureAlert).filter(TemperatureAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다")
    
    if alert.is_resolved:
        raise HTTPException(status_code=400, detail="이미 해결된 알림입니다")
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    if notes:
        alert.notes = notes
    
    db.commit()
    db.refresh(alert)
    
    return {"message": "알림이 해결 처리되었습니다", "alert_id": alert_id}
