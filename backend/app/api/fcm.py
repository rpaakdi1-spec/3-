"""
FCM 푸시 알림 API 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.database import get_db
from app.auth import get_current_user
from app.models import User, FCMToken, PushNotificationLog
from app.services.fcm_service import FCMService

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fcm", tags=["FCM Push Notifications"])


# ===== Schemas =====

class FCMTokenRegister(BaseModel):
    """FCM 토큰 등록 요청"""
    token: str
    device_type: Optional[str] = "web"  # 'ios', 'android', 'web'
    device_id: Optional[str] = None
    app_version: Optional[str] = None


class FCMTokenResponse(BaseModel):
    """FCM 토큰 응답"""
    id: int
    user_id: int
    token: str
    device_type: Optional[str]
    is_active: bool
    last_used_at: str
    created_at: str
    
    class Config:
        from_attributes = True


class PushNotificationRequest(BaseModel):
    """푸시 알림 발송 요청"""
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    notification_type: Optional[str] = None


class PushNotificationResponse(BaseModel):
    """푸시 알림 응답"""
    success: bool
    message: str


class NotificationLogResponse(BaseModel):
    """알림 로그 응답"""
    id: int
    user_id: Optional[int]
    title: str
    body: str
    notification_type: Optional[str]
    status: str
    sent_at: str
    
    class Config:
        from_attributes = True


# ===== API Endpoints =====

@router.post("/register", response_model=FCMTokenResponse)
async def register_fcm_token(
    token_data: FCMTokenRegister,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    FCM 토큰 등록 또는 업데이트
    
    - 사용자의 디바이스 FCM 토큰을 등록합니다.
    - 이미 등록된 토큰은 업데이트됩니다.
    """
    try:
        fcm_token = FCMService.register_token(
            db=db,
            user_id=current_user.id,
            token=token_data.token,
            device_type=token_data.device_type,
            device_id=token_data.device_id,
            app_version=token_data.app_version
        )
        
        return FCMTokenResponse(
            id=fcm_token.id,
            user_id=fcm_token.user_id,
            token=fcm_token.token,
            device_type=fcm_token.device_type,
            is_active=fcm_token.is_active,
            last_used_at=fcm_token.last_used_at.isoformat(),
            created_at=fcm_token.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ FCM 토큰 등록 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/unregister")
async def unregister_fcm_token(
    token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    FCM 토큰 비활성화 (로그아웃 시 호출)
    
    - 디바이스 FCM 토큰을 비활성화합니다.
    - 더 이상 푸시 알림을 받지 않습니다.
    """
    try:
        success = FCMService.deactivate_token(db, token)
        
        if success:
            return {"message": "FCM 토큰이 비활성화되었습니다."}
        else:
            raise HTTPException(status_code=404, detail="토큰을 찾을 수 없습니다.")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ FCM 토큰 비활성화 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tokens", response_model=List[FCMTokenResponse])
async def get_my_fcm_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 FCM 토큰 목록 조회
    
    - 현재 사용자의 등록된 FCM 토큰 목록을 반환합니다.
    """
    try:
        tokens = db.query(FCMToken).filter(
            FCMToken.user_id == current_user.id,
            FCMToken.is_active == True
        ).all()
        
        return [
            FCMTokenResponse(
                id=token.id,
                user_id=token.user_id,
                token=token.token,
                device_type=token.device_type,
                is_active=token.is_active,
                last_used_at=token.last_used_at.isoformat(),
                created_at=token.created_at.isoformat()
            )
            for token in tokens
        ]
        
    except Exception as e:
        logger.error(f"❌ FCM 토큰 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send", response_model=PushNotificationResponse)
async def send_push_notification(
    notification: PushNotificationRequest,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    푸시 알림 발송 (관리자 전용)
    
    - 특정 사용자에게 푸시 알림을 발송합니다.
    - 관리자 권한이 필요합니다.
    """
    # 관리자 권한 확인
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    
    try:
        success = FCMService.send_notification(
            db=db,
            user_id=user_id,
            title=notification.title,
            body=notification.body,
            data=notification.data,
            notification_type=notification.notification_type
        )
        
        if success:
            return PushNotificationResponse(
                success=True,
                message="푸시 알림이 발송되었습니다."
            )
        else:
            return PushNotificationResponse(
                success=False,
                message="푸시 알림 발송에 실패했습니다."
            )
            
    except Exception as e:
        logger.error(f"❌ 푸시 알림 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-multiple", response_model=Dict[str, int])
async def send_push_to_multiple_users(
    notification: PushNotificationRequest,
    user_ids: List[int] = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    여러 사용자에게 푸시 알림 발송 (관리자 전용)
    
    - 여러 사용자에게 동시에 푸시 알림을 발송합니다.
    - 관리자 권한이 필요합니다.
    """
    # 관리자 권한 확인
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    
    try:
        result = FCMService.send_to_multiple_users(
            db=db,
            user_ids=user_ids,
            title=notification.title,
            body=notification.body,
            data=notification.data,
            notification_type=notification.notification_type
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 다중 사용자 알림 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs", response_model=List[NotificationLogResponse])
async def get_notification_logs(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 푸시 알림 로그 조회
    
    - 현재 사용자에게 발송된 푸시 알림 로그를 반환합니다.
    """
    try:
        logs = db.query(PushNotificationLog).filter(
            PushNotificationLog.user_id == current_user.id
        ).order_by(
            PushNotificationLog.sent_at.desc()
        ).limit(limit).all()
        
        return [
            NotificationLogResponse(
                id=log.id,
                user_id=log.user_id,
                title=log.title,
                body=log.body,
                notification_type=log.notification_type,
                status=log.status,
                sent_at=log.sent_at.isoformat()
            )
            for log in logs
        ]
        
    except Exception as e:
        logger.error(f"❌ 알림 로그 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def send_test_notification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    테스트 푸시 알림 발송
    
    - 자신에게 테스트 푸시 알림을 발송합니다.
    - FCM 토큰이 제대로 등록되었는지 확인할 수 있습니다.
    """
    try:
        success = FCMService.send_notification(
            db=db,
            user_id=current_user.id,
            title="🔔 테스트 알림",
            body=f"안녕하세요, {current_user.name}님! FCM 푸시 알림이 정상 작동합니다.",
            data={"type": "test"},
            notification_type="test"
        )
        
        if success:
            return {
                "success": True,
                "message": "테스트 알림이 발송되었습니다. 디바이스에서 확인해주세요."
            }
        else:
            return {
                "success": False,
                "message": "FCM 토큰이 등록되지 않았거나, 알림 발송에 실패했습니다."
            }
            
    except Exception as e:
        logger.error(f"❌ 테스트 알림 발송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
