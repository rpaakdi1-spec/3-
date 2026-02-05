import os
import json
from typing import Optional, Dict, Any, List
from loguru import logger

# Firebase Admin을 optional import로 처리
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("⚠️ Firebase Admin SDK not installed. Push notifications will be disabled.")


class FCMService:
    """Firebase Cloud Messaging 푸시 알림 서비스"""
    
    def __init__(self):
        self.enabled = False
        
        if not FIREBASE_AVAILABLE:
            logger.warning("⚠️ Firebase Admin SDK not available. Push notifications disabled.")
            return
        
        try:
            # Firebase 서비스 계정 키 파일 경로
            service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
            
            if service_account_path and os.path.exists(service_account_path):
                # Firebase Admin SDK 초기화
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                self.enabled = True
                logger.info("✅ Firebase Cloud Messaging initialized")
            else:
                logger.warning("⚠️ Firebase service account not found. Push notifications disabled.")
                
        except ValueError as e:
            # 이미 초기화된 경우
            if "The default Firebase app already exists" in str(e):
                self.enabled = True
                logger.info("✅ Firebase app already initialized")
            else:
                logger.error(f"❌ Firebase initialization error: {str(e)}")
        except Exception as e:
            logger.error(f"❌ FCM initialization error: {str(e)}")
    
    def send_push(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        푸시 알림 발송
        
        Args:
            token: 기기 토큰 (FCM registration token)
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터 (key-value pairs, 모두 문자열)
            image_url: 이미지 URL (optional)
        
        Returns:
            발송 결과
        """
        if not self.enabled:
            logger.error("❌ FCM service is not enabled")
            return {
                "success": False,
                "error": "FCM service not configured",
                "message_id": None
            }
        
        try:
            # 알림 메시지 구성
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url
            )
            
            # 웹 푸시 설정
            web_push_config = messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    title=title,
                    body=body,
                    icon="/logo192.png",  # 앱 아이콘
                    badge="/badge.png",
                    image=image_url,
                    vibrate=[200, 100, 200],  # 진동 패턴
                    requireInteraction=True,  # 사용자가 닫을 때까지 유지
                ),
                fcm_options=messaging.WebpushFCMOptions(
                    link="/"  # 클릭 시 이동할 URL
                )
            )
            
            # FCM 메시지 생성
            message = messaging.Message(
                token=token,
                notification=notification,
                data=data or {},
                webpush=web_push_config
            )
            
            # 메시지 발송
            response = messaging.send(message)
            
            logger.info(f"✅ Push notification sent: ID={response}")
            
            return {
                "success": True,
                "message_id": response,
                "token": token,
                "error": None
            }
            
        except messaging.UnregisteredError:
            logger.error(f"❌ Invalid FCM token: {token[:20]}...")
            return {
                "success": False,
                "message_id": None,
                "error": "Invalid or expired token"
            }
        
        except messaging.SenderIdMismatchError:
            logger.error("❌ Sender ID mismatch")
            return {
                "success": False,
                "message_id": None,
                "error": "Sender ID mismatch"
            }
        
        except Exception as e:
            logger.error(f"❌ Push notification error: {str(e)}")
            return {
                "success": False,
                "message_id": None,
                "error": str(e)
            }
    
    def send_multicast(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        여러 기기에 푸시 알림 일괄 발송
        
        Args:
            tokens: 기기 토큰 목록 (최대 500개)
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터
        
        Returns:
            발송 결과
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "FCM service not configured",
                "success_count": 0,
                "failure_count": len(tokens)
            }
        
        try:
            # 멀티캐스트 메시지 생성
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )
            
            # 메시지 발송
            response = messaging.send_multicast(message)
            
            logger.info(f"✅ Multicast sent: Success={response.success_count}, Failed={response.failure_count}")
            
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": [
                    {
                        "success": r.success,
                        "message_id": r.message_id if r.success else None,
                        "error": str(r.exception) if not r.success else None
                    }
                    for r in response.responses
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Multicast error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "success_count": 0,
                "failure_count": len(tokens)
            }
    
    def send_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        토픽 구독자에게 푸시 알림 발송
        
        Args:
            topic: 토픽 이름 (예: "urgent_orders")
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터
        
        Returns:
            발송 결과
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "FCM service not configured"
            }
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                topic=topic
            )
            
            response = messaging.send(message)
            
            logger.info(f"✅ Topic message sent: Topic={topic}, ID={response}")
            
            return {
                "success": True,
                "message_id": response,
                "topic": topic,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"❌ Topic message error: {str(e)}")
            return {
                "success": False,
                "message_id": None,
                "error": str(e)
            }
    
    def subscribe_to_topic(
        self,
        tokens: List[str],
        topic: str
    ) -> Dict[str, Any]:
        """
        기기를 토픽에 구독
        
        Args:
            tokens: 기기 토큰 목록
            topic: 토픽 이름
        
        Returns:
            구독 결과
        """
        if not self.enabled:
            return {"success": False, "error": "FCM service not configured"}
        
        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            
            logger.info(f"✅ Subscribed {response.success_count} devices to topic '{topic}'")
            
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }
            
        except Exception as e:
            logger.error(f"❌ Topic subscription error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def unsubscribe_from_topic(
        self,
        tokens: List[str],
        topic: str
    ) -> Dict[str, Any]:
        """
        기기를 토픽에서 구독 해제
        
        Args:
            tokens: 기기 토큰 목록
            topic: 토픽 이름
        
        Returns:
            구독 해제 결과
        """
        if not self.enabled:
            return {"success": False, "error": "FCM service not configured"}
        
        try:
            response = messaging.unsubscribe_from_topic(tokens, topic)
            
            logger.info(f"✅ Unsubscribed {response.success_count} devices from topic '{topic}'")
            
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }
            
        except Exception as e:
            logger.error(f"❌ Topic unsubscription error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# 싱글톤 인스턴스
fcm_service = FCMService()
