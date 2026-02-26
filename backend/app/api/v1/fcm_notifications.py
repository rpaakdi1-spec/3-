"""
FCM 푸시 알림 API 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from loguru import logger

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.fcm_token import FCMToken, PushNotificationLog
from app.services.fcm_service import FCMService


router = APIRouter()


# Request/Response Models
class FCMTokenRegisterRequest(BaseModel):
    token: str
    device_type: Optional[str] = "web"  # 'ios', 'android', 'web'
    device_id: Optional[str] = None
    app_version: Optional[str] = None


class PushNotificationRequest(BaseModel):
    user_ids: List[int]
    title: str
    body: str
    notification_type: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class TestNotificationRequest(BaseModel):
    title: Optional[str] = "🔔 테스트 알림"
    body: Optional[str] = "FCM 푸시 알림이 정상 작동합니다."


# FCM 토큰 등록
@router.post("/register-token")
async def register_fcm_token(
    request: FCMTokenRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    FCM 토큰 등록
    
    모바일 앱 또는 웹 브라우저에서 FCM 토큰을 서버에 등록합니다.
    """
    try:
        fcm_token = FCMService.register_token(
            db=db,
            user_id=current_user.id,
            token=request.token,
            device_type=request.device_type,
            device_id=request.device_id,
            app_version=request.app_version
        )
        
        return {
            "status": "success",
            "message": "Token registered successfully",
            "token_id": fcm_token.id,
            "device_type": fcm_token.device_type
        }
    
    except Exception as e:
        logger.error(f"Error registering FCM token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# FCM 토큰 비활성화
@router.delete("/unregister-token/{token}")
async def unregister_fcm_token(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """FCM 토큰 비활성화 (로그아웃 시)"""
    try:
        success = FCMService.deactivate_token(db, token)
        
        if not success:
            raise HTTPException(status_code=404, detail="Token not found")
        
        return {
            "status": "success",
            "message": "Token unregistered successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unregistering FCM token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 사용자별 알림 전송
@router.post("/send-notification")
async def send_push_notification(
    request: PushNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    푸시 알림 전송
    
    특정 사용자들에게 푸시 알림을 전송합니다. (관리자 전용)
    """
    # 관리자만 실행 가능
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        result = FCMService.send_to_multiple_users(
            db=db,
            user_ids=request.user_ids,
            title=request.title,
            body=request.body,
            data=request.data,
            notification_type=request.notification_type
        )
        
        return {
            "status": "success",
            "message": "Notifications sent",
            "result": result
        }
    
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 알림 이력 조회
@router.get("/notification-logs")
async def get_notification_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    푸시 알림 이력 조회
    
    현재 사용자의 알림 이력을 조회합니다.
    """
    try:
        logs = db.query(PushNotificationLog).filter(
            PushNotificationLog.user_id == current_user.id
        ).order_by(PushNotificationLog.sent_at.desc()).limit(limit).all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": log.id,
                    "title": log.title,
                    "body": log.body,
                    "notification_type": log.notification_type,
                    "status": log.status,
                    "sent_at": log.sent_at.isoformat()
                }
                for log in logs
            ]
        }
    
    except Exception as e:
        logger.error(f"Error fetching notification logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 테스트 알림 전송
@router.post("/test")
async def send_test_notification(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    테스트 푸시 알림 전송
    
    자신에게 테스트 푸시 알림을 전송합니다.
    FCM 토큰이 제대로 등록되었는지 확인할 수 있습니다.
    """
    try:
        success = FCMService.send_notification(
            db=db,
            user_id=current_user.id,
            title="🔔 테스트 알림",
            body=f"안녕하세요, {current_user.name}님! FCM 푸시 알림이 정상 작동합니다.",
            data={"type": "test", "timestamp": str(current_user.created_at)},
            notification_type="test"
        )
        
        if success:
            return {
                "status": "success",
                "message": "테스트 알림이 발송되었습니다. 디바이스에서 확인해주세요."
            }
        else:
            return {
                "status": "warning",
                "message": "FCM 토큰이 등록되지 않았거나, 알림 발송에 실패했습니다."
            }
    
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 내 FCM 토큰 목록 조회
@router.get("/my-tokens")
async def get_my_fcm_tokens(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 FCM 토큰 목록 조회
    
    현재 사용자의 등록된 FCM 토큰 목록을 반환합니다.
    """
    try:
        tokens = db.query(FCMToken).filter(
            FCMToken.user_id == current_user.id,
            FCMToken.is_active == True
        ).all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": token.id,
                    "device_type": token.device_type,
                    "device_id": token.device_id,
                    "app_version": token.app_version,
                    "last_used_at": token.last_used_at.isoformat(),
                    "created_at": token.created_at.isoformat()
                }
                for token in tokens
            ]
        }
    
    except Exception as e:
        logger.error(f"Error fetching my tokens: {e}")
        raise HTTPException(status_code=500, detail=str(e))
