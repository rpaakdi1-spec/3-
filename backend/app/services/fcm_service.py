"""
Firebase Cloud Messaging (FCM) 푸시 알림 서비스
"""

import os
import json
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

from firebase_admin import credentials, messaging
import firebase_admin

from sqlalchemy.orm import Session

from app.models import FCMToken, PushNotificationLog, User

logger = logging.getLogger(__name__)


class FCMService:
    """Firebase Cloud Messaging 서비스"""
    
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Firebase Admin SDK 초기화"""
        if cls._initialized:
            return
        
        try:
            # 환경변수에서 Firebase 설정 파일 경로 가져오기
            firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            
            if not firebase_cred_path:
                logger.warning("FIREBASE_CREDENTIALS_PATH 환경변수가 설정되지 않았습니다.")
                return
            
            if not os.path.exists(firebase_cred_path):
                logger.warning(f"Firebase 인증 파일을 찾을 수 없습니다: {firebase_cred_path}")
                return
            
            # Firebase Admin 초기화
            cred = credentials.Certificate(firebase_cred_path)
            firebase_admin.initialize_app(cred)
            
            cls._initialized = True
            logger.info("✅ Firebase Admin SDK 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ Firebase Admin SDK 초기화 실패: {e}")
    
    @staticmethod
    def register_token(
        db: Session,
        user_id: int,
        token: str,
        device_type: Optional[str] = None,
        device_id: Optional[str] = None,
        app_version: Optional[str] = None
    ) -> FCMToken:
        """
        FCM 토큰 등록 또는 업데이트
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            token: FCM 토큰
            device_type: 디바이스 타입 ('ios', 'android', 'web')
            device_id: 디바이스 고유 ID
            app_version: 앱 버전
            
        Returns:
            FCMToken 객체
        """
        try:
            # 기존 토큰 확인
            existing_token = db.query(FCMToken).filter(
                FCMToken.token == token
            ).first()
            
            if existing_token:
                # 토큰 업데이트
                existing_token.user_id = user_id
                existing_token.device_type = device_type or existing_token.device_type
                existing_token.device_id = device_id or existing_token.device_id
                existing_token.app_version = app_version or existing_token.app_version
                existing_token.is_active = True
                existing_token.last_used_at = datetime.utcnow()
                existing_token.updated_at = datetime.utcnow()
                
                db.commit()
                db.refresh(existing_token)
                
                logger.info(f"✅ FCM 토큰 업데이트: user_id={user_id}, device_type={device_type}")
                return existing_token
            
            # 새 토큰 생성
            new_token = FCMToken(
                user_id=user_id,
                token=token,
                device_type=device_type,
                device_id=device_id,
                app_version=app_version,
                is_active=True
            )
            
            db.add(new_token)
            db.commit()
            db.refresh(new_token)
            
            logger.info(f"✅ FCM 토큰 등록 완료: user_id={user_id}, device_type={device_type}")
            return new_token
            
        except Exception as e:
            logger.error(f"❌ FCM 토큰 등록 실패: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def deactivate_token(db: Session, token: str) -> bool:
        """
        FCM 토큰 비활성화
        
        Args:
            db: 데이터베이스 세션
            token: FCM 토큰
            
        Returns:
            성공 여부
        """
        try:
            fcm_token = db.query(FCMToken).filter(
                FCMToken.token == token
            ).first()
            
            if fcm_token:
                fcm_token.is_active = False
                fcm_token.updated_at = datetime.utcnow()
                db.commit()
                
                logger.info(f"✅ FCM 토큰 비활성화 완료: token={token[:20]}...")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ FCM 토큰 비활성화 실패: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def get_user_tokens(db: Session, user_id: int) -> List[str]:
        """
        사용자의 활성 FCM 토큰 목록 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            FCM 토큰 리스트
        """
        try:
            tokens = db.query(FCMToken).filter(
                FCMToken.user_id == user_id,
                FCMToken.is_active == True
            ).all()
            
            return [token.token for token in tokens]
            
        except Exception as e:
            logger.error(f"❌ 사용자 토큰 조회 실패: {e}")
            return []
    
    @staticmethod
    def send_notification(
        db: Session,
        user_id: int,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        notification_type: Optional[str] = None
    ) -> bool:
        """
        푸시 알림 발송
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터 (딕셔너리)
            notification_type: 알림 타입
            
        Returns:
            발송 성공 여부
        """
        if not FCMService._initialized:
            FCMService.initialize()
        
        if not FCMService._initialized:
            logger.warning("FCM이 초기화되지 않았습니다. 알림을 발송할 수 없습니다.")
            return False
        
        try:
            # 사용자의 활성 토큰 조회
            tokens = FCMService.get_user_tokens(db, user_id)
            
            if not tokens:
                logger.warning(f"사용자 {user_id}의 활성 FCM 토큰이 없습니다.")
                return False
            
            # 데이터를 문자열로 변환 (FCM은 문자열만 지원)
            data_dict = {}
            if data:
                for key, value in data.items():
                    data_dict[key] = str(value)
            
            # 알림 메시지 생성
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data_dict,
                tokens=tokens,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                ),
                webpush=messaging.WebpushConfig(
                    notification=messaging.WebpushNotification(
                        icon='/logo192.png',
                        badge='/badge.png'
                    )
                )
            )
            
            # 알림 발송
            response = messaging.send_multicast(message)
            
            # 로그 저장
            for idx, token in enumerate(tokens):
                if idx < len(response.responses):
                    send_response = response.responses[idx]
                    status = "sent" if send_response.success else "failed"
                    error_msg = None if send_response.success else str(send_response.exception)
                    
                    # 실패한 토큰 비활성화
                    if not send_response.success:
                        FCMService.deactivate_token(db, token)
                else:
                    status = "failed"
                    error_msg = "No response from FCM"
                
                # 로그 저장
                log = PushNotificationLog(
                    user_id=user_id,
                    token=token,
                    title=title,
                    body=body,
                    data_json=json.dumps(data_dict) if data_dict else None,
                    notification_type=notification_type,
                    status=status,
                    error_message=error_msg
                )
                db.add(log)
            
            db.commit()
            
            logger.info(
                f"✅ FCM 알림 발송 완료: user_id={user_id}, "
                f"성공={response.success_count}, 실패={response.failure_count}"
            )
            
            return response.success_count > 0
            
        except Exception as e:
            logger.error(f"❌ FCM 알림 발송 실패: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def send_to_multiple_users(
        db: Session,
        user_ids: List[int],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        notification_type: Optional[str] = None
    ) -> Dict[str, int]:
        """
        여러 사용자에게 푸시 알림 발송
        
        Args:
            db: 데이터베이스 세션
            user_ids: 사용자 ID 리스트
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터
            notification_type: 알림 타입
            
        Returns:
            {'success': 성공 수, 'failed': 실패 수}
        """
        success_count = 0
        failed_count = 0
        
        for user_id in user_ids:
            result = FCMService.send_notification(
                db, user_id, title, body, data, notification_type
            )
            
            if result:
                success_count += 1
            else:
                failed_count += 1
        
        logger.info(
            f"✅ 다중 사용자 알림 발송 완료: "
            f"대상={len(user_ids)}, 성공={success_count}, 실패={failed_count}"
        )
        
        return {"success": success_count, "failed": failed_count}
    
    @staticmethod
    def send_order_notification(
        db: Session,
        user_id: int,
        order_id: int,
        order_name: str,
        notification_type: str = "order_created"
    ) -> bool:
        """
        주문 관련 알림 발송
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            order_id: 주문 ID
            order_name: 주문명
            notification_type: 알림 타입
            
        Returns:
            발송 성공 여부
        """
        notification_messages = {
            "order_created": ("새 주문 등록", f"'{order_name}' 주문이 등록되었습니다."),
            "order_updated": ("주문 변경", f"'{order_name}' 주문이 수정되었습니다."),
            "order_cancelled": ("주문 취소", f"'{order_name}' 주문이 취소되었습니다."),
            "dispatch_assigned": ("배차 완료", f"'{order_name}' 주문이 배차되었습니다."),
        }
        
        title, body = notification_messages.get(
            notification_type,
            ("주문 알림", f"주문 '{order_name}'에 대한 업데이트가 있습니다.")
        )
        
        data = {
            "type": "order",
            "order_id": order_id,
            "action": notification_type
        }
        
        return FCMService.send_notification(
            db, user_id, title, body, data, notification_type
        )
    
    @staticmethod
    def send_vehicle_alert(
        db: Session,
        user_id: int,
        vehicle_plate: str,
        alert_type: str,
        alert_message: str
    ) -> bool:
        """
        차량 알림 발송 (UVIS 연동)
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            vehicle_plate: 차량 번호
            alert_type: 알림 타입
            alert_message: 알림 메시지
            
        Returns:
            발송 성공 여부
        """
        alert_titles = {
            "speed_warning": "⚠️ 과속 경고",
            "speed_critical": "🚨 과속 위험",
            "temperature_warning": "🌡️ 온도 주의",
            "temperature_critical": "🌡️ 온도 위험",
            "engine_warning": "🔧 엔진 경고",
            "gps_disconnected": "📍 GPS 연결 끊김",
        }
        
        title = alert_titles.get(alert_type, "🚛 차량 알림")
        body = f"[{vehicle_plate}] {alert_message}"
        
        data = {
            "type": "vehicle_alert",
            "vehicle_plate": vehicle_plate,
            "alert_type": alert_type
        }
        
        return FCMService.send_notification(
            db, user_id, title, body, data, "vehicle_alert"
        )


# 서비스 초기화 (앱 시작 시 한 번만 실행)
FCMService.initialize()
