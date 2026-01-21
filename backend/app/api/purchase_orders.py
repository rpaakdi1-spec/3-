from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
import shutil
import os
from pathlib import Path
from datetime import datetime, date

from ..database import get_db
from ..models.purchase_order import PurchaseOrder
from ..schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse, PurchaseOrderListResponse

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])

# 이미지 업로드 디렉토리 설정
UPLOAD_DIR = Path("/home/user/webapp/backend/uploads/purchase_orders")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/", response_model=PurchaseOrderListResponse)
def get_purchase_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """발주서 목록 조회"""
    query = db.query(PurchaseOrder).filter(PurchaseOrder.is_active == True)
    
    if status:
        query = query.filter(PurchaseOrder.status == status)
    
    total = query.count()
    items = query.order_by(desc(PurchaseOrder.created_at)).offset(skip).limit(limit).all()
    
    return PurchaseOrderListResponse(total=total, items=items)

@router.get("/{po_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    """발주서 상세 조회"""
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="발주서를 찾을 수 없습니다")
    
    return po

@router.post("/", response_model=PurchaseOrderResponse)
def create_purchase_order(po: PurchaseOrderCreate, db: Session = Depends(get_db)):
    """발주서 생성"""
    # 발주서 번호 중복 체크
    existing = db.query(PurchaseOrder).filter(PurchaseOrder.po_number == po.po_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 발주서 번호입니다")
    
    db_po = PurchaseOrder(**po.model_dump())
    db.add(db_po)
    db.commit()
    db.refresh(db_po)
    return db_po

@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    """이미지 업로드"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다")
    
    # 파일명 생성 (타임스탬프 + 원본 파일명)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    
    # 파일 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # URL 반환 (상대 경로)
    image_url = f"/uploads/purchase_orders/{filename}"
    return {"image_url": image_url}

@router.put("/{po_id}", response_model=PurchaseOrderResponse)
def update_purchase_order(
    po_id: int,
    po_update: PurchaseOrderUpdate,
    db: Session = Depends(get_db)
):
    """발주서 수정"""
    db_po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not db_po:
        raise HTTPException(status_code=404, detail="발주서를 찾을 수 없습니다")
    
    # 수정된 필드만 업데이트
    update_data = po_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_po, field, value)
    
    db.commit()
    db.refresh(db_po)
    return db_po

@router.delete("/{po_id}")
def delete_purchase_order(po_id: int, db: Session = Depends(get_db)):
    """발주서 삭제 (논리 삭제)"""
    db_po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not db_po:
        raise HTTPException(status_code=404, detail="발주서를 찾을 수 없습니다")
    
    # 논리 삭제
    db_po.is_active = False
    db.commit()
    
    return {"message": "발주서가 삭제되었습니다"}
