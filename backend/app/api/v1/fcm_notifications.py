"""
FCM 푸시 알림 API 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.fcm_token import FCMToken, PushNotificationLog
from app.services.fcm_notification_service import get_fcm_service


router = APIRouter()


# Request/Response Models
class FCMTokenRegisterRequest(BaseModel):
    token: str
    device_type: Optional[str] = None  # 'ios', 'android'
    device_id: Optional[str] = None
    app_version: Optional[str] = None


class PushNotificationRequest(BaseModel):
    user_ids: List[int]
    title: str
    body: str
    notification_type: Optional[str] = None
    data: Optional[dict] = None


# FCM 토큰 등록
@router.post("/register-token")
async def register_fcm_token(
    request: FCMTokenRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    FCM 토큰 등록
    
    모바일 앱에서 FCM 토큰을 서버에 등록합니다.
    """
    try:
        # 기존 토큰 확인
        existing_token = db.query(FCMToken).filter(
            FCMToken.token == request.token
        ).first()
        
        if existing_token:
            # 토큰이 이미 존재하면 업데이트
            existing_token.user_id = current_user.id
            existing_token.device_type = request.device_type
            existing_token.device_id = request.device_id
            existing_token.app_version = request.app_version
            existing_token.is_active = True
            
            db.commit()
            db.refresh(existing_token)
            
            return {
                "status": "success",
                "message": "Token updated",
                "token_id": existing_token.id
            }
        else:
            # 새 토큰 생성
            new_token = FCMToken(
                user_id=current_user.id,
                token=request.token,
                device_type=request.device_type,
                device_id=request.device_id,
                app_version=request.app_version,
                is_active=True
            )
            
            db.add(new_token)
            db.commit()
            db.refresh(new_token)
            
            return {
                "status": "success",
                "message": "Token registered",
                "token_id": new_token.id
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
        fcm_token = db.query(FCMToken).filter(
            FCMToken.token == token,
            FCMToken.user_id == current_user.id
        ).first()
        
        if not fcm_token:
            raise HTTPException(status_code=404, detail="Token not found")
        
        fcm_token.is_active = False
        db.commit()
        
        return {
            "status": "success",
            "message": "Token unregistered"
        }
    
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
    
    특정 사용자들에게 푸시 알림을 전송합니다.
    """
    # 관리자만 실행 가능
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        # 대상 사용자의 활성 토큰 조회
        fcm_tokens = db.query(FCMToken).filter(
            FCMToken.user_id.in_(request.user_ids),
            FCMToken.is_active == True
        ).all()
        
        if not fcm_tokens:
            return {
                "status": "error",
                "message": "No active tokens found for target users"
            }
        
        tokens = [t.token for t in fcm_tokens]
        
        # FCM 서비스로 알림 전송
        fcm_service = get_fcm_service()
        result = await fcm_service.send_push_notification(
            tokens=tokens,
            title=request.title,
            body=request.body,
            data=request.data
        )
        
        # 알림 로그 저장
        for user_id in request.user_ids:
            user_tokens = [t for t in fcm_tokens if t.user_id == user_id]
            
            for token_obj in user_tokens:
                log = PushNotificationLog(
                    user_id=user_id,
                    token=token_obj.token,
                    title=request.title,
                    body=request.body,
                    data_json=str(request.data) if request.data else None,
                    notification_type=request.notification_type,
                    status="sent" if token_obj.token not in result.get('failed_tokens', []) else "failed"
                )
                db.add(log)
        
        db.commit()
        
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
