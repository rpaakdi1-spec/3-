from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path

from app.core.database import get_db
from app.models.client import Client
from app.schemas.client import (
    ClientCreate, ClientUpdate, ClientResponse, ClientListResponse,
    GeocodeRequest, GeocodeResponse
)
from app.services.excel_upload_service import ExcelUploadService
from app.services.excel_template_service import ExcelTemplateService
from app.services.naver_map_service import NaverMapService
from loguru import logger

router = APIRouter()


@router.get("/", response_model=ClientListResponse)
def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    client_type: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """거래처 목록 조회"""
    query = db.query(Client)
    
    if client_type:
        query = query.filter(Client.client_type == client_type)
    
    query = query.filter(Client.is_active == is_active)
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return ClientListResponse(total=total, items=items)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """거래처 상세 조회"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="거래처를 찾을 수 없습니다")
    return client


@router.post("/", response_model=ClientResponse, status_code=201)
def create_client(client_data: ClientCreate, db: Session = Depends(get_db)):
    """거래처 생성"""
    # Check if code already exists
    existing = db.query(Client).filter(Client.code == client_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 거래처 코드입니다")
    
    client = Client(**client_data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    
    logger.info(f"Created client: {client.code}")
    return client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db)
):
    """거래처 수정"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="거래처를 찾을 수 없습니다")
    
    # Update fields
    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    
    logger.info(f"Updated client: {client.code}")
    return client


@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """거래처 삭제 (소프트 삭제)"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="거래처를 찾을 수 없습니다")
    
    client.is_active = False
    db.commit()
    
    logger.info(f"Deleted (soft) client: {client.code}")
    return {"message": "거래처가 삭제되었습니다"}


@router.post("/upload")
async def upload_clients_excel(
    file: UploadFile = File(...),
    auto_geocode: bool = Query(True, description="자동 지오코딩 실행"),
    db: Session = Depends(get_db)
):
    """엑셀 파일로 거래처 일괄 업로드"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="엑셀 파일만 업로드 가능합니다")
    
    try:
        content = await file.read()
        result = await ExcelUploadService.upload_clients(db, content, auto_geocode)
        
        logger.info(f"Uploaded clients: {result['created']} created, {result['failed']} failed")
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading clients: {e}")
        raise HTTPException(status_code=500, detail="업로드 중 오류가 발생했습니다")


@router.post("/geocode/auto", response_model=GeocodeResponse)
async def auto_geocode_missing_clients(
    db: Session = Depends(get_db)
):
    """위도/경도가 없는 거래처 자동 지오코딩"""
    # 위도/경도가 null이고 주소가 있는 거래처 조회
    clients = db.query(Client).filter(
        Client.is_active == True,
        Client.address.isnot(None),
        Client.address != "",
        Client.latitude.is_(None)
    ).all()
    
    if not clients:
        logger.info("지오코딩이 필요한 거래처가 없습니다")
        return GeocodeResponse(
            success_count=0,
            failed_count=0,
            results=[],
            message="지오코딩이 필요한 거래처가 없습니다"
        )
    
    logger.info(f"자동 지오코딩 시작: {len(clients)}개 거래처")
    
    naver_service = NaverMapService()
    success_count = 0
    failed_count = 0
    results = []
    
    for client in clients:
        lat, lon, error = await naver_service.geocode_address(client.address)
        
        if lat and lon:
            client.latitude = lat
            client.longitude = lon
            client.geocoded = True
            client.geocode_error = None
            
            results.append({
                "client_id": client.id,
                "client_code": client.code,
                "client_name": client.name,
                "address": client.address,
                "success": True,
                "latitude": lat,
                "longitude": lon
            })
            success_count += 1
            logger.info(f"✅ 지오코딩 성공: {client.code} - {client.name}")
        else:
            client.geocode_error = error
            
            results.append({
                "client_id": client.id,
                "client_code": client.code,
                "client_name": client.name,
                "address": client.address,
                "success": False,
                "error": error
            })
            failed_count += 1
            logger.warning(f"❌ 지오코딩 실패: {client.code} - {client.name}: {error}")
    
    db.commit()
    
    logger.info(f"자동 지오코딩 완료: {success_count}개 성공, {failed_count}개 실패")
    
    return GeocodeResponse(
        success_count=success_count,
        failed_count=failed_count,
        results=results,
        message=f"{success_count}개 거래처 지오코딩 완료"
    )


@router.post("/geocode", response_model=GeocodeResponse)
async def geocode_clients(
    request: GeocodeRequest,
    db: Session = Depends(get_db)
):
    """거래처 주소 지오코딩 (선택한 거래처)"""
    naver_service = NaverMapService()
    
    success_count = 0
    failed_count = 0
    results = []
    
    for client_id in request.client_ids:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            results.append({
                "client_id": client_id,
                "success": False,
                "error": "거래처를 찾을 수 없음"
            })
            failed_count += 1
            continue
        
        if not client.address:
            results.append({
                "client_id": client_id,
                "client_code": client.code,
                "success": False,
                "error": "주소가 없음"
            })
            failed_count += 1
            continue
        
        lat, lon, error = await naver_service.geocode_address(client.address)
        
        if lat and lon:
            client.latitude = lat
            client.longitude = lon
            client.geocoded = True
            client.geocode_error = None
            
            results.append({
                "client_id": client_id,
                "client_code": client.code,
                "success": True,
                "latitude": lat,
                "longitude": lon
            })
            success_count += 1
        else:
            client.geocode_error = error
            
            results.append({
                "client_id": client_id,
                "client_code": client.code,
                "success": False,
                "error": error
            })
            failed_count += 1
    
    db.commit()
    
    logger.info(f"Geocoded clients: {success_count} success, {failed_count} failed")
    
    return GeocodeResponse(
        success_count=success_count,
        failed_count=failed_count,
        results=results
    )


@router.get("/template/download")
def download_client_template():
    """거래처 Excel 템플릿 다운로드"""
    template_path = ExcelTemplateService.create_clients_template()
    
    if not Path(template_path).exists():
        raise HTTPException(status_code=404, detail="템플릿 파일을 찾을 수 없습니다")
    
    return FileResponse(
        path=template_path,
        filename="clients_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
