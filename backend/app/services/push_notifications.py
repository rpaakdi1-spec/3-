"""
Push Notification Server - Phase 9.2
Firebase Cloud Messaging integration for mobile push notifications
"""
from typing import Dict, List, Optional
from firebase_admin import credentials, messaging, initialize_app
import logging

logger = logging.getLogger(__name__)


class PushNotificationService:
    """
    Handles sending push notifications to mobile devices
    Uses Firebase Cloud Messaging (FCM)
    """
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Firebase Admin SDK
        
        Args:
            credentials_path: Path to Firebase service account JSON
        """
        self.initialized = False
        
        if credentials_path:
            try:
                cred = credentials.Certificate(credentials_path)
                initialize_app(cred)
                self.initialized = True
                logger.info("Push notification service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize FCM: {e}")
    
    def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ) -> bool:
        """
        Send push notification to a single device
        
        Args:
            token: Device FCM token
            title: Notification title
            body: Notification body
            data: Optional custom data payload
            
        Returns:
            Success status
        """
        if not self.initialized:
            logger.warning("Push notification service not initialized")
            return False
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
            )
            
            response = messaging.send(message)
            logger.info(f"Push notification sent: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False
    
    def send_multicast(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """
        Send push notification to multiple devices
        
        Args:
            tokens: List of device FCM tokens
            title: Notification title
            body: Notification body
            data: Optional custom data payload
            
        Returns:
            Dictionary with success/failure counts
        """
        if not self.initialized:
            logger.warning("Push notification service not initialized")
            return {'success': 0, 'failure': len(tokens)}
        
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=tokens,
            )
            
            response = messaging.send_multicast(message)
            logger.info(f"Multicast sent: {response.success_count} success, {response.failure_count} failed")
            
            return {
                'success': response.success_count,
                'failure': response.failure_count,
            }
            
        except Exception as e:
            logger.error(f"Failed to send multicast: {e}")
            return {'success': 0, 'failure': len(tokens)}
    
    def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ) -> bool:
        """
        Send push notification to a topic
        
        Args:
            topic: FCM topic name
            title: Notification title
            body: Notification body
            data: Optional custom data payload
            
        Returns:
            Success status
        """
        if not self.initialized:
            logger.warning("Push notification service not initialized")
            return False
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                topic=topic,
            )
            
            response = messaging.send(message)
            logger.info(f"Topic notification sent: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send topic notification: {e}")
            return False
    
    def subscribe_to_topic(self, tokens: List[str], topic: str) -> bool:
        """
        Subscribe devices to a topic
        
        Args:
            tokens: List of device FCM tokens
            topic: Topic name
            
        Returns:
            Success status
        """
        if not self.initialized:
            logger.warning("Push notification service not initialized")
            return False
        
        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            logger.info(f"Subscribed {response.success_count} devices to topic {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to topic: {e}")
            return False
    
    def unsubscribe_from_topic(self, tokens: List[str], topic: str) -> bool:
        """
        Unsubscribe devices from a topic
        
        Args:
            tokens: List of device FCM tokens
            topic: Topic name
            
        Returns:
            Success status
        """
        if not self.initialized:
            logger.warning("Push notification service not initialized")
            return False
        
        try:
            response = messaging.unsubscribe_from_topic(tokens, topic)
            logger.info(f"Unsubscribed {response.success_count} devices from topic {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to unsubscribe from topic: {e}")
            return False


# Global push notification service
push_service = PushNotificationService()


# Notification templates
class NotificationTemplates:
    """Pre-defined notification templates"""
    
    @staticmethod
    def order_created(order_id: int) -> Dict:
        return {
            'title': '새 주문',
            'body': f'주문 #{order_id}이(가) 생성되었습니다',
            'data': {'type': 'order_created', 'order_id': str(order_id)},
        }
    
    @staticmethod
    def order_assigned(order_id: int, driver_name: str) -> Dict:
        return {
            'title': '주문 배정',
            'body': f'주문 #{order_id}이(가) {driver_name}에게 배정되었습니다',
            'data': {'type': 'order_assigned', 'order_id': str(order_id)},
        }
    
    @staticmethod
    def delivery_started(order_id: int) -> Dict:
        return {
            'title': '배송 시작',
            'body': f'주문 #{order_id}의 배송이 시작되었습니다',
            'data': {'type': 'delivery_started', 'order_id': str(order_id)},
        }
    
    @staticmethod
    def delivery_completed(order_id: int) -> Dict:
        return {
            'title': '배송 완료',
            'body': f'주문 #{order_id}이(가) 완료되었습니다',
            'data': {'type': 'delivery_completed', 'order_id': str(order_id)},
        }
    
    @staticmethod
    def temperature_alert(vehicle_number: str, temperature: float) -> Dict:
        return {
            'title': '온도 경고',
            'body': f'차량 {vehicle_number}의 온도가 {temperature}°C입니다',
            'data': {
                'type': 'temperature_alert',
                'vehicle': vehicle_number,
                'temperature': str(temperature),
            },
        }
