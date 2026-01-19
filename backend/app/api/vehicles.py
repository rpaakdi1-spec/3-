from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path

from app.core.database import get_db
from app.models.vehicle import Vehicle, VehicleStatus
from app.schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleResponse, VehicleListResponse
)
from app.services.excel_upload_service import ExcelUploadService
from app.services.excel_template_service import ExcelTemplateService
from loguru import logger

router = APIRouter()


@router.get("/", response_model=VehicleListResponse)
def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vehicle_type: Optional[str] = None,
    status: Optional[VehicleStatus] = None,
    is_active: bool = True,
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
    template_path = ExcelTemplateService.create_vehicle_template()
    
    if not Path(template_path).exists():
        raise HTTPException(status_code=404, detail="템플릿 파일을 찾을 수 없습니다")
    
    return FileResponse(
        path=template_path,
        filename="vehicles_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
