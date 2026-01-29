from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
import shutil
import os
from pathlib import Path
from datetime import datetime

from ..core.database import get_db
from ..models.notice import Notice
from ..schemas.notice import NoticeCreate, NoticeUpdate, NoticeResponse, NoticeListResponse

router = APIRouter(tags=["Notices"])

# 이미지 업로드 디렉토리 설정
import os
UPLOAD_BASE = os.getenv("UPLOAD_BASE_DIR", "./uploads")
UPLOAD_DIR = Path(UPLOAD_BASE) / "notices"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/", response_model=NoticeListResponse)
def get_notices(
    skip: int = 0,
    limit: int = 100,
    is_important: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """공지사항 목록 조회"""
    query = db.query(Notice).filter(Notice.is_active == True)
    
    if is_important is not None:
        query = query.filter(Notice.is_important == is_important)
    
    total = query.count()
    items = query.order_by(desc(Notice.created_at)).offset(skip).limit(limit).all()
    
    return NoticeListResponse(total=total, items=items)

@router.get("/{notice_id}", response_model=NoticeResponse)
def get_notice(notice_id: int, db: Session = Depends(get_db)):
    """공지사항 상세 조회 (조회수 증가)"""
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
    
    # 조회수 증가
    notice.views += 1
    db.commit()
    db.refresh(notice)
    
    return notice

@router.post("/", response_model=NoticeResponse)
def create_notice(notice: NoticeCreate, db: Session = Depends(get_db)):
    """공지사항 생성"""
    db_notice = Notice(**notice.model_dump())
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return db_notice

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
    image_url = f"/uploads/notices/{filename}"
    return {"image_url": image_url}

@router.put("/{notice_id}", response_model=NoticeResponse)
def update_notice(
    notice_id: int,
    notice_update: NoticeUpdate,
    db: Session = Depends(get_db)
):
    """공지사항 수정"""
    db_notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not db_notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
    
    # 수정된 필드만 업데이트
    update_data = notice_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_notice, field, value)
    
    db.commit()
    db.refresh(db_notice)
    return db_notice

@router.delete("/{notice_id}")
def delete_notice(notice_id: int, db: Session = Depends(get_db)):
    """공지사항 삭제 (논리 삭제)"""
    db_notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not db_notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
    
    # 논리 삭제
    db_notice.is_active = False
    db.commit()
    
    return {"message": "공지사항이 삭제되었습니다"}
