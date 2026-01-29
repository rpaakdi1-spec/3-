"""
UVIS GPS 관제 시스템 API 라우터
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.services.uvis_gps_service import UvisGPSService
from app.schemas.uvis_gps import (
    UvisAccessKeyResponse,
    VehicleGPSLogResponse,
    VehicleGPSListResponse,
    VehicleTemperatureLogResponse,
    VehicleTemperatureListResponse,
    VehicleRealtimeStatus,
    VehicleRealtimeListResponse,
    UvisApiLogResponse,
    UvisApiLogListResponse,
    SyncGPSRequest,
    SyncTemperatureRequest,
    SyncResponse,
)
from app.models.uvis_gps import (
    UvisAccessKey,
    VehicleGPSLog,
    VehicleTemperatureLog,
    UvisApiLog
)
from app.models.vehicle import Vehicle

router = APIRouter(prefix="/uvis-gps", tags=["UVIS GPS 관제"])


# ==================== 인증키 관리 ====================

@router.get("/access-key/current", response_model=Optional[UvisAccessKeyResponse])
async def get_current_access_key(db: Session = Depends(get_db)):
    """
    현재 유효한 실시간 인증키 조회
    """
    service = UvisGPSService(db)
    access_key_str = await service.get_valid_access_key()
    
    if not access_key_str:
        return None
    
    # DB에서 키 정보 조회
    key_info = db.query(UvisAccessKey).filter(
        UvisAccessKey.access_key == access_key_str,
        UvisAccessKey.is_active == True
    ).first()
    
    return key_info


@router.post("/access-key/issue", response_model=UvisAccessKeyResponse)
async def issue_new_access_key(db: Session = Depends(get_db)):
    """
    새로운 실시간 인증키 발급
    """
    service = UvisGPSService(db)
    access_key_str = await service.issue_access_key()
    
    if not access_key_str:
        raise HTTPException(status_code=500, detail="인증키 발급 실패")
    
    # DB에서 키 정보 조회
    key_info = db.query(UvisAccessKey).filter(
        UvisAccessKey.access_key == access_key_str
    ).first()
    
    return key_info


# ==================== GPS 데이터 동기화 ====================

@router.post("/sync/gps", response_model=SyncResponse)
async def sync_gps_data(
    request: SyncGPSRequest,
    db: Session = Depends(get_db)
):
    """
    UVIS로부터 실시간 GPS 데이터 동기화
    """
    service = UvisGPSService(db)
    
    # 새 인증키 강제 발급
    access_key_issued = False
    if request.force_new_key:
        await service.issue_access_key()
        access_key_issued = True
    
    # GPS 데이터 가져오기
    data = await service.get_vehicle_gps_data()
    
    return SyncResponse(
        success=len(data) > 0,
        message=f"GPS 데이터 {len(data)}건 동기화 완료",
        data_count=len(data),
        access_key_issued=access_key_issued
    )


@router.post("/sync/temperature", response_model=SyncResponse)
async def sync_temperature_data(
    request: SyncTemperatureRequest,
    db: Session = Depends(get_db)
):
    """
    UVIS로부터 실시간 온도 데이터 동기화
    """
    service = UvisGPSService(db)
    
    # 새 인증키 강제 발급
    access_key_issued = False
    if request.force_new_key:
        await service.issue_access_key()
        access_key_issued = True
    
    # 온도 데이터 가져오기
    data = await service.get_vehicle_temperature_data()
    
    return SyncResponse(
        success=len(data) > 0,
        message=f"온도 데이터 {len(data)}건 동기화 완료",
        data_count=len(data),
        access_key_issued=access_key_issued
    )


@router.post("/sync/all", response_model=dict)
async def sync_all_data(
    force_new_key: bool = False,
    db: Session = Depends(get_db)
):
    """
    GPS + 온도 데이터 모두 동기화
    """
    service = UvisGPSService(db)
    
    # 새 인증키 강제 발급
    access_key_issued = False
    if force_new_key:
        await service.issue_access_key()
        access_key_issued = True
    
    # GPS 데이터 가져오기
    gps_data = await service.get_vehicle_gps_data()
    
    # 온도 데이터 가져오기
    temp_data = await service.get_vehicle_temperature_data()
    
    return {
        "success": True,
        "message": f"전체 동기화 완료 (GPS: {len(gps_data)}건, 온도: {len(temp_data)}건)",
        "gps_count": len(gps_data),
        "temperature_count": len(temp_data),
        "access_key_issued": access_key_issued
    }


# ==================== GPS 로그 조회 ====================

@router.get("/gps-logs", response_model=VehicleGPSListResponse)
def get_gps_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    vehicle_id: Optional[int] = None,
    tid_id: Optional[str] = None,
    date_from: Optional[str] = Query(None, description="시작 날짜 (YYYYMMDD)"),
    date_to: Optional[str] = Query(None, description="종료 날짜 (YYYYMMDD)"),
    db: Session = Depends(get_db)
):
    """
    GPS 로그 목록 조회
    """
    query = db.query(VehicleGPSLog)
    
    # 필터링
    if vehicle_id:
        query = query.filter(VehicleGPSLog.vehicle_id == vehicle_id)
    
    if tid_id:
        query = query.filter(VehicleGPSLog.tid_id == tid_id)
    
    if date_from:
        query = query.filter(VehicleGPSLog.bi_date >= date_from)
    
    if date_to:
        query = query.filter(VehicleGPSLog.bi_date <= date_to)
    
    # 총 개수
    total = query.count()
    
    # 페이지네이션
    items = query.order_by(desc(VehicleGPSLog.created_at)).offset(skip).limit(limit).all()
    
    return VehicleGPSListResponse(total=total, items=items)


@router.get("/gps-logs/{gps_log_id}", response_model=VehicleGPSLogResponse)
def get_gps_log(gps_log_id: int, db: Session = Depends(get_db)):
    """
    GPS 로그 상세 조회
    """
    log = db.query(VehicleGPSLog).filter(VehicleGPSLog.id == gps_log_id).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="GPS 로그를 찾을 수 없습니다")
    
    return log


# ==================== 온도 로그 조회 ====================

@router.get("/temperature-logs", response_model=VehicleTemperatureListResponse)
def get_temperature_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    vehicle_id: Optional[int] = None,
    tid_id: Optional[str] = None,
    date_from: Optional[str] = Query(None, description="시작 날짜 (YYYYMMDD)"),
    date_to: Optional[str] = Query(None, description="종료 날짜 (YYYYMMDD)"),
    db: Session = Depends(get_db)
):
    """
    온도 로그 목록 조회
    """
    query = db.query(VehicleTemperatureLog)
    
    # 필터링
    if vehicle_id:
        query = query.filter(VehicleTemperatureLog.vehicle_id == vehicle_id)
    
    if tid_id:
        query = query.filter(VehicleTemperatureLog.tid_id == tid_id)
    
    if date_from:
        query = query.filter(VehicleTemperatureLog.tpl_date >= date_from)
    
    if date_to:
        query = query.filter(VehicleTemperatureLog.tpl_date <= date_to)
    
    # 총 개수
    total = query.count()
    
    # 페이지네이션
    items = query.order_by(desc(VehicleTemperatureLog.created_at)).offset(skip).limit(limit).all()
    
    return VehicleTemperatureListResponse(total=total, items=items)


@router.get("/temperature-logs/{temp_log_id}", response_model=VehicleTemperatureLogResponse)
def get_temperature_log(temp_log_id: int, db: Session = Depends(get_db)):
    """
    온도 로그 상세 조회
    """
    log = db.query(VehicleTemperatureLog).filter(VehicleTemperatureLog.id == temp_log_id).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="온도 로그를 찾을 수 없습니다")
    
    return log


# ==================== 실시간 모니터링 ====================

@router.get("/realtime/vehicles", response_model=VehicleRealtimeListResponse)
def get_realtime_vehicle_status(
    vehicle_ids: Optional[str] = Query(None, description="차량 ID 목록 (쉼표 구분)"),
    db: Session = Depends(get_db)
):
    """
    차량 실시간 상태 조회 (GPS + 온도 통합)
    """
    # 차량 목록
    vehicle_query = db.query(Vehicle).filter(Vehicle.is_active == True)
    
    if vehicle_ids:
        id_list = [int(vid.strip()) for vid in vehicle_ids.split(",")]
        vehicle_query = vehicle_query.filter(Vehicle.id.in_(id_list))
    
    vehicles = vehicle_query.all()
    
    # 각 차량의 최신 GPS + 온도 정보 가져오기
    result_items = []
    
    for vehicle in vehicles:
        # 최신 GPS
        latest_gps = db.query(VehicleGPSLog).filter(
            VehicleGPSLog.vehicle_id == vehicle.id
        ).order_by(desc(VehicleGPSLog.created_at)).first()
        
        # 최신 온도
        latest_temp = db.query(VehicleTemperatureLog).filter(
            VehicleTemperatureLog.vehicle_id == vehicle.id
        ).order_by(desc(VehicleTemperatureLog.created_at)).first()
        
        # GPS 일시
        gps_datetime = None
        if latest_gps:
            try:
                gps_datetime = f"{latest_gps.bi_date[:4]}-{latest_gps.bi_date[4:6]}-{latest_gps.bi_date[6:8]} {latest_gps.bi_time[:2]}:{latest_gps.bi_time[2:4]}:{latest_gps.bi_time[4:6]}"
            except:
                pass
        
        # 온도 일시
        temp_datetime = None
        if latest_temp:
            try:
                temp_datetime = f"{latest_temp.tpl_date[:4]}-{latest_temp.tpl_date[4:6]}-{latest_temp.tpl_date[6:8]} {latest_temp.tpl_time[:2]}:{latest_temp.tpl_time[2:4]}:{latest_temp.tpl_time[4:6]}"
            except:
                pass
        
        # 최종 업데이트 시간 (GPS와 온도 중 더 최근 것, KST 변환)
        last_updated = None
        if latest_gps and latest_temp:
            last_updated_utc = max(latest_gps.created_at, latest_temp.created_at)
            # UTC → KST 변환 (+9시간)
            last_updated = last_updated_utc + timedelta(hours=9)
        elif latest_gps:
            # UTC → KST 변환 (+9시간)
            last_updated = latest_gps.created_at + timedelta(hours=9)
        elif latest_temp:
            # UTC → KST 변환 (+9시간)
            last_updated = latest_temp.created_at + timedelta(hours=9)
        
        status = VehicleRealtimeStatus(
            vehicle_id=vehicle.id,
            vehicle_plate_number=vehicle.plate_number,
            tid_id=vehicle.uvis_device_id or "",
            gps_datetime=gps_datetime,
            latitude=latest_gps.latitude if latest_gps else None,
            longitude=latest_gps.longitude if latest_gps else None,
            is_engine_on=latest_gps.is_engine_on if latest_gps else None,
            speed_kmh=latest_gps.speed_kmh if latest_gps else None,
            temperature_datetime=temp_datetime,
            temperature_a=latest_temp.temperature_a if latest_temp else None,
            temperature_b=latest_temp.temperature_b if latest_temp else None,
            last_updated=last_updated
        )
        
        # Debug logging
        if latest_gps:
            print(f"🚗 {vehicle.plate_number}: is_engine_on={latest_gps.is_engine_on} (type={type(latest_gps.is_engine_on).__name__}), bi_turn_onoff='{latest_gps.bi_turn_onoff}', speed={latest_gps.speed_kmh}")
        
        result_items.append(status)
    
    return VehicleRealtimeListResponse(
        total=len(result_items),
        items=result_items
    )


@router.get("/realtime/vehicles/{vehicle_id}", response_model=VehicleRealtimeStatus)
def get_realtime_vehicle_status_by_id(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 차량의 실시간 상태 조회
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    
    # 최신 GPS
    latest_gps = db.query(VehicleGPSLog).filter(
        VehicleGPSLog.vehicle_id == vehicle_id
    ).order_by(desc(VehicleGPSLog.created_at)).first()
    
    # 최신 온도
    latest_temp = db.query(VehicleTemperatureLog).filter(
        VehicleTemperatureLog.vehicle_id == vehicle_id
    ).order_by(desc(VehicleTemperatureLog.created_at)).first()
    
    # GPS 일시
    gps_datetime = None
    if latest_gps:
        try:
            gps_datetime = f"{latest_gps.bi_date[:4]}-{latest_gps.bi_date[4:6]}-{latest_gps.bi_date[6:8]} {latest_gps.bi_time[:2]}:{latest_gps.bi_time[2:4]}:{latest_gps.bi_time[4:6]}"
        except:
            pass
    
    # 온도 일시
    temp_datetime = None
    if latest_temp:
        try:
            temp_datetime = f"{latest_temp.tpl_date[:4]}-{latest_temp.tpl_date[4:6]}-{latest_temp.tpl_date[6:8]} {latest_temp.tpl_time[:2]}:{latest_temp.tpl_time[2:4]}:{latest_temp.tpl_time[4:6]}"
        except:
            pass
    
    # 최종 업데이트 시간 (GPS와 온도 중 더 최근 것, KST 변환)
    last_updated = None
    if latest_gps and latest_temp:
        last_updated_utc = max(latest_gps.created_at, latest_temp.created_at)
        # UTC → KST 변환 (+9시간)
        last_updated = last_updated_utc + timedelta(hours=9)
    elif latest_gps:
        # UTC → KST 변환 (+9시간)
        last_updated = latest_gps.created_at + timedelta(hours=9)
    elif latest_temp:
        # UTC → KST 변환 (+9시간)
        last_updated = latest_temp.created_at + timedelta(hours=9)
    
    return VehicleRealtimeStatus(
        vehicle_id=vehicle.id,
        vehicle_plate_number=vehicle.plate_number,
        tid_id=vehicle.uvis_device_id or "",
        gps_datetime=gps_datetime,
        latitude=latest_gps.latitude if latest_gps else None,
        longitude=latest_gps.longitude if latest_gps else None,
        is_engine_on=latest_gps.is_engine_on if latest_gps else None,
        speed_kmh=latest_gps.speed_kmh if latest_gps else None,
        temperature_datetime=temp_datetime,
        temperature_a=latest_temp.temperature_a if latest_temp else None,
        temperature_b=latest_temp.temperature_b if latest_temp else None,
        last_updated=last_updated
    )


# ==================== API 로그 조회 ====================

@router.get("/api-logs", response_model=UvisApiLogListResponse)
def get_api_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    api_type: Optional[str] = Query(None, description="API 유형 (auth/gps/temperature)"),
    db: Session = Depends(get_db)
):
    """
    UVIS API 호출 로그 조회
    """
    query = db.query(UvisApiLog)
    
    if api_type:
        query = query.filter(UvisApiLog.api_type == api_type)
    
    total = query.count()
    items = query.order_by(desc(UvisApiLog.created_at)).offset(skip).limit(limit).all()
    
    return UvisApiLogListResponse(total=total, items=items)
