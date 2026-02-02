from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path

from app.core.database import get_db
from app.models.vehicle import Vehicle, VehicleStatus, VehicleType
from app.schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleResponse, VehicleListResponse, VehicleWithGPSResponse
)
from app.services.excel_upload_service import ExcelUploadService
from app.services.excel_template_service import ExcelTemplateService
from app.services.uvis_gps_service import UvisGPSService
from app.services.naver_map_service import NaverMapService
from loguru import logger

router = APIRouter()


@router.get("/", response_model=VehicleListResponse)
async def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vehicle_type: Optional[str] = None,
    status: Optional[VehicleStatus] = None,
    is_active: bool = True,
    include_gps: bool = Query(False, description="Include real-time GPS data"),
    db: Session = Depends(get_db)
):
    """차량 목록 조회"""
    query = db.query(Vehicle)
    
    if vehicle_type:
        query = query.filter(Vehicle.vehicle_type == vehicle_type)
    
    if status:
        query = query.filter(Vehicle.status == status)
    
    query = query.filter(Vehicle.is_active == is_active)
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    # Include GPS data if requested
    if include_gps:
        from app.models.uvis_gps import VehicleGPSLog, VehicleTemperatureLog
        from sqlalchemy import desc
        from app.schemas.vehicle import VehicleGPSData
        
        enhanced_items = []
        for vehicle in items:
            # Convert vehicle to dict properly
            vehicle_data = {
                'id': vehicle.id,
                'code': vehicle.code,
                'plate_number': vehicle.plate_number,
                'vehicle_type': vehicle.vehicle_type,
                'max_pallets': vehicle.max_pallets,
                'max_weight_kg': vehicle.max_weight_kg,
                'max_volume_cbm': vehicle.max_volume_cbm,
                'tonnage': vehicle.tonnage,
                'length_m': vehicle.length_m,
                'width_m': vehicle.width_m,
                'height_m': vehicle.height_m,
                'driver_name': vehicle.driver_name,
                'driver_phone': vehicle.driver_phone,
                'min_temp_celsius': vehicle.min_temp_celsius,
                'max_temp_celsius': vehicle.max_temp_celsius,
                'fuel_efficiency_km_per_liter': vehicle.fuel_efficiency_km_per_liter,
                'fuel_cost_per_liter': vehicle.fuel_cost_per_liter,
                'status': vehicle.status,
                'uvis_device_id': vehicle.uvis_device_id,
                'uvis_enabled': vehicle.uvis_enabled,
                'has_forklift': vehicle.has_forklift,
                'garage_address': vehicle.garage_address,
                'garage_latitude': vehicle.garage_latitude,
                'garage_longitude': vehicle.garage_longitude,
                'notes': vehicle.notes,
                'is_active': vehicle.is_active,
                'created_at': vehicle.created_at,
                'updated_at': vehicle.updated_at,
                'gps_data': None
            }
            
            if vehicle.uvis_enabled and vehicle.uvis_device_id:
                # Get latest GPS data
                latest_gps = db.query(VehicleGPSLog).filter(
                    VehicleGPSLog.vehicle_id == vehicle.id
                ).order_by(desc(VehicleGPSLog.created_at)).first()
                
                # Get latest temperature data
                latest_temp = db.query(VehicleTemperatureLog).filter(
                    VehicleTemperatureLog.vehicle_id == vehicle.id
                ).order_by(desc(VehicleTemperatureLog.created_at)).first()
                
                if latest_gps or latest_temp:
                    from datetime import timedelta
                    
                    # GPS datetime
                    gps_datetime = None
                    if latest_gps and latest_gps.bi_date and latest_gps.bi_time:
                        try:
                            gps_datetime = f"{latest_gps.bi_date[:4]}-{latest_gps.bi_date[4:6]}-{latest_gps.bi_date[6:8]} {latest_gps.bi_time[:2]}:{latest_gps.bi_time[2:4]}:{latest_gps.bi_time[4:6]}"
                        except:
                            pass
                    
                    # Last updated (KST)
                    last_updated = None
                    if latest_gps and latest_temp:
                        last_updated_utc = max(latest_gps.created_at, latest_temp.created_at)
                        last_updated = last_updated_utc + timedelta(hours=9)
                    elif latest_gps:
                        last_updated = latest_gps.created_at + timedelta(hours=9)
                    elif latest_temp:
                        last_updated = latest_temp.created_at + timedelta(hours=9)
                    
                    # Reverse geocoding: Convert GPS coordinates to address
                    current_address = None
                    if latest_gps and latest_gps.latitude and latest_gps.longitude:
                        try:
                            naver_map_service = NaverMapService()
                            # Use await in async function
                            current_address = await naver_map_service.reverse_geocode(
                                latest_gps.latitude,
                                latest_gps.longitude
                            )
                        except Exception as e:
                            logger.warning(f"Failed to reverse geocode for vehicle {vehicle.id}: {e}")
                    
                    vehicle_data['gps_data'] = VehicleGPSData(
                        latitude=latest_gps.latitude if latest_gps else None,
                        longitude=latest_gps.longitude if latest_gps else None,
                        current_address=current_address,
                        is_engine_on=latest_gps.is_engine_on if latest_gps else None,
                        speed_kmh=latest_gps.speed_kmh if latest_gps else None,
                        temperature_a=latest_temp.temperature_a if latest_temp else None,
                        temperature_b=latest_temp.temperature_b if latest_temp else None,
                        battery_voltage=None,  # TODO: Add battery voltage to UVIS data
                        last_updated=last_updated,
                        gps_datetime=gps_datetime
                    )
            
            enhanced_items.append(vehicle_data)
        
        # Return as dict with proper structure
        return {"total": total, "items": enhanced_items}
    
    return VehicleListResponse(total=total, items=items)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """차량 상세 조회"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    return vehicle


@router.post("/", response_model=VehicleResponse, status_code=201)
def create_vehicle(vehicle_data: VehicleCreate, db: Session = Depends(get_db)):
    """차량 생성"""
    # Check if code already exists
    existing = db.query(Vehicle).filter(Vehicle.code == vehicle_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 차량 코드입니다")
    
    # Check if plate number already exists
    existing_plate = db.query(Vehicle).filter(Vehicle.plate_number == vehicle_data.plate_number).first()
    if existing_plate:
        raise HTTPException(status_code=400, detail="이미 존재하는 차량번호입니다")
    
    vehicle = Vehicle(**vehicle_data.model_dump(), status=VehicleStatus.AVAILABLE)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    
    logger.info(f"Created vehicle: {vehicle.code}")
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db)
):
    """차량 수정"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    
    # Update fields
    update_data = vehicle_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)
    
    db.commit()
    db.refresh(vehicle)
    
    logger.info(f"Updated vehicle: {vehicle.code}")
    return vehicle


@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """차량 삭제 (소프트 삭제)"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    
    vehicle.is_active = False
    db.commit()
    
    logger.info(f"Deleted (soft) vehicle: {vehicle.code}")
    return {"message": "차량이 삭제되었습니다"}


@router.post("/upload")
async def upload_vehicles_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """엑셀 파일로 차량 일괄 업로드"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="엑셀 파일만 업로드 가능합니다")
    
    try:
        content = await file.read()
        result = ExcelUploadService.upload_vehicles(db, content)
        
        logger.info(f"Uploaded vehicles: {result['created']} created, {result['failed']} failed")
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading vehicles: {e}")
        raise HTTPException(status_code=500, detail="업로드 중 오류가 발생했습니다")



@router.get("/template/download")
def download_vehicle_template():
    """차량 Excel 템플릿 다운로드"""
    template_path = ExcelTemplateService.create_vehicles_template()
    
    if not Path(template_path).exists():
        raise HTTPException(status_code=404, detail="템플릿 파일을 찾을 수 없습니다")
    
    return FileResponse(
        path=template_path,
        filename="vehicles_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.post("/sync/uvis")
async def sync_uvis_vehicles(db: Session = Depends(get_db)):
    """UVIS GPS에서 차량 정보 동기화"""
    try:
        uvis_service = UvisGPSService(db)
        
        # GPS 데이터 조회
        gps_data = await uvis_service.get_vehicle_gps_data()
        
        if not gps_data:
            return {
                "success": False,
                "message": "UVIS GPS 데이터를 가져올 수 없습니다",
                "synced": 0,
                "created": 0,
                "updated": 0
            }
        
        synced_count = 0
        created_count = 0
        updated_count = 0
        
        for item in gps_data:
            try:
                tid_id = item.get("TID_ID")
                cm_number = item.get("CM_NUMBER")
                
                if not tid_id or not cm_number:
                    continue
                
                # 기존 차량 찾기
                vehicle = db.query(Vehicle).filter(
                    Vehicle.uvis_device_id == tid_id
                ).first()
                
                if vehicle:
                    # 기존 차량 업데이트 - 차량번호만 덮어쓰기
                    vehicle.plate_number = cm_number
                    updated_count += 1
                else:
                    # 새 차량 생성
                    # 차량번호로 코드 생성
                    code = f"V{cm_number.replace('-', '').replace(' ', '')}"
                    
                    # 코드 중복 체크
                    existing_code = db.query(Vehicle).filter(Vehicle.code == code).first()
                    if existing_code:
                        code = f"{code}_{tid_id[:4]}"
                    
                    vehicle = Vehicle(
                        code=code,
                        plate_number=cm_number,
                        vehicle_type=VehicleType.FROZEN,  # 기본값: 냉동
                        uvis_device_id=tid_id,
                        uvis_enabled=True,
                        max_pallets=20,  # 기본값
                        max_weight_kg=5000.0,  # 기본값
                        tonnage=5.0,  # 기본값
                        status=VehicleStatus.AVAILABLE,
                        is_active=True
                    )
                    db.add(vehicle)
                    created_count += 1
                
                synced_count += 1
                
            except Exception as e:
                logger.error(f"차량 동기화 실패 (TID: {item.get('TID_ID')}): {e}")
                continue
        
        db.commit()
        
        logger.info(f"UVIS 차량 동기화 완료: {synced_count}건 처리 ({created_count}건 생성, {updated_count}건 업데이트)")
        
        return {
            "success": True,
            "message": f"UVIS 차량 {synced_count}건 동기화 완료",
            "synced": synced_count,
            "created": created_count,
            "updated": updated_count
        }
        
    except Exception as e:
        logger.error(f"UVIS 차량 동기화 오류: {e}")
        raise HTTPException(status_code=500, detail=f"UVIS 차량 동기화 중 오류 발생: {str(e)}")
