"""
배차 템플릿 API
Dispatch Template Management API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.dispatch_template import DispatchFormTemplate
from pydantic import BaseModel, Field

router = APIRouter()


# ========== Pydantic 스키마 ==========

class DispatchItem(BaseModel):
    """배차 항목"""
    time: str = Field(default="", description="배차 시간 (예: 13:00)")
    vehicle_type: str = Field(..., description="차량 타입 (예: 11톤)")
    tonnage: Optional[float] = Field(None, description="톤수 (선택)")
    product_type: Optional[str] = Field(None, description="제품 타입 (선택)")
    temperature: str = Field(default="냉장", description="온도 (냉동/냉장)")
    pallet_count: int = Field(..., description="팔레트 수")
    notes: str = Field(default="", description="비고")


class TemplateData(BaseModel):
    """템플릿 데이터"""
    dispatches: List[DispatchItem] = Field(..., description="배차 목록")
    default_pickup: str = Field(default="", description="기본 상차지")
    default_delivery: str = Field(default="", description="기본 하차지")
    default_notes: str = Field(default="", description="기본 비고")


class DispatchFormTemplateCreate(BaseModel):
    """템플릿 생성"""
    name: str = Field(..., min_length=1, max_length=200, description="템플릿 이름")
    client_name: str = Field(..., min_length=1, max_length=200, description="거래처명")
    category: Optional[str] = Field(None, max_length=100, description="카테고리")
    description: Optional[str] = Field(None, description="설명")
    template_data: TemplateData = Field(..., description="템플릿 데이터")
    is_favorite: bool = Field(default=False, description="즐겨찾기 여부")


class DispatchFormTemplateUpdate(BaseModel):
    """템플릿 수정"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    client_name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    template_data: Optional[TemplateData] = None
    is_active: Optional[bool] = None
    is_favorite: Optional[bool] = None


class DispatchFormTemplateResponse(BaseModel):
    """템플릿 응답"""
    id: int
    name: str
    client_name: str
    category: Optional[str]
    description: Optional[str]
    template_data: dict
    usage_count: int
    is_active: bool
    is_favorite: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]

    class Config:
        from_attributes = True


# ========== API 엔드포인트 ==========

@router.post("/templates", response_model=DispatchFormTemplateResponse)
async def create_template(
    template: DispatchFormTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배차 템플릿 생성
    
    거래처별 자주 사용하는 배차 폼을 템플릿으로 저장합니다.
    """
    # 중복 체크
    existing = db.query(DispatchFormTemplate).filter(
        DispatchFormTemplate.client_name == template.client_name,
        DispatchFormTemplate.name == template.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"템플릿 '{template.name}'이(가) 이미 존재합니다."
        )
    
    # 템플릿 생성
    db_template = DispatchFormTemplate(
        name=template.name,
        client_name=template.client_name,
        category=template.category,
        description=template.description,
        template_data=template.template_data.model_dump(),
        is_favorite=template.is_favorite,
        created_by=current_user.id
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template


@router.get("/templates", response_model=List[DispatchFormTemplateResponse])
async def get_templates(
    client_name: Optional[str] = Query(None, description="거래처명으로 필터링"),
    category: Optional[str] = Query(None, description="카테고리로 필터링"),
    is_favorite: Optional[bool] = Query(None, description="즐겨찾기만 조회"),
    search: Optional[str] = Query(None, description="검색어 (이름, 거래처명)"),
    limit: int = Query(50, ge=1, le=200, description="최대 결과 수"),
    db: Session = Depends(get_db)
):
    """
    배차 템플릿 목록 조회
    
    거래처명, 카테고리, 검색어로 필터링하여 템플릿을 조회합니다.
    """
    query = db.query(DispatchFormTemplate).filter(
        DispatchFormTemplate.is_active == True
    )
    
    # 필터링
    if client_name:
        query = query.filter(DispatchFormTemplate.client_name == client_name)
    
    if category:
        query = query.filter(DispatchFormTemplate.category == category)
    
    if is_favorite is not None:
        query = query.filter(DispatchFormTemplate.is_favorite == is_favorite)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                DispatchFormTemplate.name.ilike(search_pattern),
                DispatchFormTemplate.client_name.ilike(search_pattern),
                DispatchFormTemplate.description.ilike(search_pattern)
            )
        )
    
    # 정렬: 즐겨찾기 > 사용 횟수 > 최근 사용
    templates = query.order_by(
        DispatchFormTemplate.is_favorite.desc(),
        DispatchFormTemplate.usage_count.desc(),
        DispatchFormTemplate.last_used_at.desc().nullslast(),
        DispatchFormTemplate.updated_at.desc()
    ).limit(limit).all()
    
    return templates


@router.get("/templates/all", response_model=List[DispatchFormTemplateResponse])
async def get_all_templates(
    limit: int = Query(200, ge=1, le=500, description="최대 결과 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배차 템플릿 전체 목록 조회 (관리자용)

    is_active 여부에 상관없이 모든 템플릿을 반환합니다.
    템플릿 관리 페이지에서 비활성화된 템플릿도 확인/수정할 수 있도록 사용합니다.
    """
    templates = db.query(DispatchFormTemplate).order_by(
        DispatchFormTemplate.is_active.desc(),
        DispatchFormTemplate.is_favorite.desc(),
        DispatchFormTemplate.usage_count.desc(),
        DispatchFormTemplate.updated_at.desc()
    ).limit(limit).all()

    return templates


@router.get("/templates/search", response_model=List[dict])
async def search_templates(
    q: str = Query(..., min_length=1, description="검색어"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    템플릿 자동완성 검색
    
    실시간 자동완성을 위한 빠른 검색 API
    """
    search_pattern = f"%{q}%"
    
    templates = db.query(DispatchFormTemplate).filter(
        DispatchFormTemplate.is_active == True,
        or_(
            DispatchFormTemplate.name.ilike(search_pattern),
            DispatchFormTemplate.client_name.ilike(search_pattern)
        )
    ).order_by(
        DispatchFormTemplate.is_favorite.desc(),
        DispatchFormTemplate.usage_count.desc()
    ).limit(limit).all()
    
    # 간단한 응답 형식
    return [
        {
            "id": t.id,
            "name": t.name,
            "client_name": t.client_name,
            "category": t.category,
            "is_favorite": t.is_favorite,
            "usage_count": t.usage_count
        }
        for t in templates
    ]


@router.get("/templates/{template_id}", response_model=DispatchFormTemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """
    템플릿 상세 조회
    """
    template = db.query(DispatchFormTemplate).filter(
        DispatchFormTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다.")
    
    return template


@router.put("/templates/{template_id}", response_model=DispatchFormTemplateResponse)
async def update_template(
    template_id: int,
    update_data: DispatchFormTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    템플릿 수정
    """
    template = db.query(DispatchFormTemplate).filter(
        DispatchFormTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다.")
    
    # 업데이트 (Pydantic v2: model_dump() returns plain dicts for nested models)
    update_dict = update_data.model_dump(exclude_unset=True)

    # template_data is already a plain dict after model_dump() — assign directly
    # (do NOT call .dict() on it; that worked in Pydantic v1 but fails in v2)
    for key, value in update_dict.items():
        setattr(template, key, value)

    db.commit()
    db.refresh(template)

    return template


@router.post("/templates/{template_id}/use")
async def use_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """
    템플릿 사용 기록
    
    템플릿을 불러올 때 사용 횟수와 마지막 사용 시간을 업데이트합니다.
    """
    template = db.query(DispatchFormTemplate).filter(
        DispatchFormTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다.")
    
    # 사용 횟수 증가
    template.usage_count += 1
    template.last_used_at = datetime.now()
    
    db.commit()
    db.refresh(template)
    
    return {
        "success": True,
        "message": "템플릿 사용 기록 완료",
        "template": {
            "id": template.id,
            "name": template.name,
            "usage_count": template.usage_count,
            "template_data": template.template_data
        }
    }


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    permanent: bool = Query(False, description="영구 삭제 여부"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    템플릿 삭제
    
    permanent=False: 비활성화 (기본)
    permanent=True: 영구 삭제
    """
    template = db.query(DispatchFormTemplate).filter(
        DispatchFormTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다.")
    
    if permanent:
        db.delete(template)
        message = "템플릿이 영구 삭제되었습니다."
    else:
        template.is_active = False
        message = "템플릿이 비활성화되었습니다."
    
    db.commit()
    
    return {"success": True, "message": message}


@router.get("/templates/clients/list")
async def get_client_list(
    db: Session = Depends(get_db)
):
    """
    거래처 목록 조회
    
    템플릿에 등록된 거래처 목록을 반환합니다.
    """
    clients = db.query(
        DispatchFormTemplate.client_name,
        func.count(DispatchFormTemplate.id).label('template_count')
    ).filter(
        DispatchFormTemplate.is_active == True
    ).group_by(
        DispatchFormTemplate.client_name
    ).order_by(
        func.count(DispatchFormTemplate.id).desc()
    ).all()
    
    return [
        {
            "client_name": client.client_name,
            "template_count": client.template_count
        }
        for client in clients
    ]
