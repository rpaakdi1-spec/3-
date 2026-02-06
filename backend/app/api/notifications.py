from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.schemas.notification import (
    NotificationSendRequest,
    TemplateNotificationRequest,
    BulkNotificationRequest,
    NotificationResponse,
    NotificationListResponse,
    NotificationStatsResponse,
    NotificationTemplateCreate,
    NotificationTemplateUpdate,
    NotificationTemplateResponse
)
from app.services.notification_service import NotificationService
from app.models.notification import Notification, NotificationTemplate, NotificationStatus
from loguru import logger

router = APIRouter()


@router.post("/send", response_model=NotificationResponse, summary="알림 발송")
async def send_notification(
    request: NotificationSendRequest,
    db: Session = Depends(get_db)
):
    """
    알림을 발송합니다.
    
    - **notification_type**: 알림 유형
    - **channel**: 발송 채널 (SMS/KAKAO/PUSH/EMAIL)
    - **recipient_name**: 수신자명
    - **title**: 제목
    - **message**: 메시지 내용
    """
    try:
        service = NotificationService(db)
        notification = await service.send_notification(request)
        return notification
    except Exception as e:
        logger.error(f"❌ Notification send error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-template", response_model=NotificationResponse, summary="템플릿 기반 알림 발송")
async def send_from_template(
    request: TemplateNotificationRequest,
    db: Session = Depends(get_db)
):
    """
    템플릿을 사용하여 알림을 발송합니다.
    
    - **template_code**: 템플릿 코드
    - **channel**: 발송 채널
    - **variables**: 템플릿 변수 ({{variable}} 형식)
    """
    try:
        service = NotificationService(db)
        notification = await service.send_from_template(request)
        return notification
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Template notification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-bulk", response_model=List[NotificationResponse], summary="일괄 알림 발송")
async def send_bulk_notifications(
    request: BulkNotificationRequest,
    db: Session = Depends(get_db)
):
    """
    여러 알림을 일괄 발송합니다.
    
    - **notifications**: 알림 목록 (최대 100개)
    """
    try:
        service = NotificationService(db)
        notifications = await service.send_bulk_notifications(request.notifications)
        return notifications
    except Exception as e:
        logger.error(f"❌ Bulk notification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=NotificationListResponse, summary="알림 목록 조회")
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    channel: Optional[str] = None,
    status: Optional[str] = None,
    notification_type: Optional[str] = None,
    recipient_phone: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    알림 목록을 조회합니다.
    
    - **skip**: 건너뛸 개수
    - **limit**: 조회할 개수
    - **channel**: 채널 필터
    - **status**: 상태 필터
    - **notification_type**: 알림 유형 필터
    """
    query = db.query(Notification)
    
    # 필터 적용
    if channel:
        query = query.filter(Notification.channel == channel)
    if status:
        query = query.filter(Notification.status == status)
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    if recipient_phone:
        query = query.filter(Notification.recipient_phone.like(f"%{recipient_phone}%"))
    if start_date:
        query = query.filter(Notification.created_at >= start_date)
    if end_date:
        query = query.filter(Notification.created_at <= end_date)
    
    total = query.count()
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    return NotificationListResponse(total=total, items=notifications)


@router.get("/{notification_id}", response_model=NotificationResponse, summary="알림 상세 조회")
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """특정 알림의 상세 정보를 조회합니다."""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다")
    
    return notification


@router.post("/{notification_id}/retry", response_model=NotificationResponse, summary="알림 재발송")
async def retry_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """실패한 알림을 재발송합니다."""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다")
    
    if notification.status != NotificationStatus.FAILED:
        raise HTTPException(status_code=400, detail="실패한 알림만 재발송할 수 있습니다")
    
    # 재발송
    notification.status = NotificationStatus.PENDING
    notification.retry_count += 1
    notification.error_message = None
    db.commit()
    
    # 발송 시도
    service = NotificationService(db)
    if notification.channel.value == "SMS":
        await service._send_sms(notification)
    
    db.refresh(notification)
    return notification


@router.get("/stats/summary", response_model=NotificationStatsResponse, summary="알림 통계")
def get_notification_stats(
    days: int = Query(7, ge=1, le=365, description="통계 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    알림 발송 통계를 조회합니다.
    
    - **days**: 최근 N일 통계
    """
    service = NotificationService(db)
    start_date = datetime.utcnow() - timedelta(days=days)
    stats = service.get_notification_stats(start_date=start_date)
    
    return NotificationStatsResponse(**stats)


# ===== 템플릿 관리 API =====

@router.post("/templates", response_model=NotificationTemplateResponse, summary="템플릿 생성")
def create_template(
    template: NotificationTemplateCreate,
    db: Session = Depends(get_db)
):
    """알림 템플릿을 생성합니다."""
    # 중복 확인
    existing = db.query(NotificationTemplate).filter(
        NotificationTemplate.template_code == template.template_code
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 템플릿 코드입니다")
    
    db_template = NotificationTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    logger.info(f"✅ Created notification template: {db_template.template_code}")
    return db_template


@router.get("/templates", response_model=List[NotificationTemplateResponse], summary="템플릿 목록")
def get_templates(
    channel: Optional[str] = None,
    notification_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """알림 템플릿 목록을 조회합니다."""
    query = db.query(NotificationTemplate)
    
    if channel:
        query = query.filter(NotificationTemplate.channel == channel)
    if notification_type:
        query = query.filter(NotificationTemplate.notification_type == notification_type)
    if is_active is not None:
        query = query.filter(NotificationTemplate.is_active == is_active)
    
    templates = query.order_by(NotificationTemplate.created_at.desc()).all()
    return templates


@router.get("/templates/{template_id}", response_model=NotificationTemplateResponse, summary="템플릿 상세")
def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """템플릿 상세 정보를 조회합니다."""
    template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    return template


@router.put("/templates/{template_id}", response_model=NotificationTemplateResponse, summary="템플릿 수정")
def update_template(
    template_id: int,
    template_update: NotificationTemplateUpdate,
    db: Session = Depends(get_db)
):
    """템플릿을 수정합니다."""
    template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    update_data = template_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)
    
    db.commit()
    db.refresh(template)
    
    logger.info(f"✅ Updated notification template: {template.template_code}")
    return template


@router.delete("/templates/{template_id}", summary="템플릿 삭제")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """템플릿을 삭제합니다."""
    template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    
    db.delete(template)
    db.commit()
    
    logger.info(f"✅ Deleted notification template: {template.template_code}")
    return {"message": "템플릿이 삭제되었습니다"}
