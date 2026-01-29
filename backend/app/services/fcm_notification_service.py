"""
FCM 푸시 알림 서비스
- Firebase Cloud Messaging 통합
- 모바일 앱 푸시 알림 발송
- 토큰 관리 및 알림 이력
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger
import httpx
import json

from app.core.config import settings


class FCMNotificationService:
    """FCM 푸시 알림 서비스"""
    
    def __init__(self):
        # FCM Server Key (Firebase Console에서 발급)
        self.server_key = settings.FCM_SERVER_KEY if hasattr(settings, 'FCM_SERVER_KEY') else None
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        
        if not self.server_key:
            logger.warning("FCM_SERVER_KEY not configured. Push notifications will not be sent.")
    
    async def send_push_notification(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = "high"
    ) -> Dict[str, Any]:
        """
        FCM 푸시 알림 전송
        
        Args:
            tokens: FCM 토큰 리스트
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터
            priority: 우선순위 (high/normal)
            
        Returns:
            전송 결과
        """
        if not self.server_key:
            return {
                "status": "error",
                "message": "FCM not configured"
            }
        
        if not tokens:
            return {
                "status": "error",
                "message": "No tokens provided"
            }
        
        success_count = 0
        failure_count = 0
        failed_tokens = []
        
        headers = {
            "Authorization": f"key={self.server_key}",
            "Content-Type": "application/json"
        }
        
        # 각 토큰에 개별 전송
        async with httpx.AsyncClient(timeout=30.0) as client:
            for token in tokens:
                try:
                    payload = {
                        "to": token,
                        "priority": priority,
                        "notification": {
                            "title": title,
                            "body": body,
                            "sound": "default",
                            "badge": "1"
                        }
                    }
                    
                    # 추가 데이터가 있으면 포함
                    if data:
                        payload["data"] = data
                    
                    response = await client.post(
                        self.fcm_url,
                        headers=headers,
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get("success") == 1:
                            success_count += 1
                            logger.info(f"Push notification sent successfully to {token[:20]}...")
                        else:
                            failure_count += 1
                            failed_tokens.append(token)
                            logger.error(f"Push notification failed for {token[:20]}...: {result.get('results')}")
                    else:
                        failure_count += 1
                        failed_tokens.append(token)
                        logger.error(f"FCM API error: HTTP {response.status_code}")
                
                except Exception as e:
                    failure_count += 1
                    failed_tokens.append(token)
                    logger.error(f"Error sending push notification: {e}")
        
        return {
            "status": "success",
            "total": len(tokens),
            "success": success_count,
            "failure": failure_count,
            "failed_tokens": failed_tokens
        }
    
    async def send_dispatch_assigned_notification(
        self,
        tokens: List[str],
        dispatch_id: int,
        vehicle_name: str,
        order_count: int
    ):
        """배차 할당 알림"""
        return await self.send_push_notification(
            tokens=tokens,
            title="새 배차 할당",
            body=f"{vehicle_name} 차량에 {order_count}건의 주문이 할당되었습니다.",
            data={
                "type": "dispatch_assigned",
                "dispatch_id": str(dispatch_id),
                "screen": "DispatchDetail"
            }
        )
    
    async def send_order_completed_notification(
        self,
        tokens: List[str],
        order_id: int,
        client_name: str
    ):
        """주문 완료 알림"""
        return await self.send_push_notification(
            tokens=tokens,
            title="주문 완료",
            body=f"{client_name} 주문이 완료되었습니다.",
            data={
                "type": "order_completed",
                "order_id": str(order_id),
                "screen": "OrderDetail"
            }
        )
    
    async def send_temperature_alert_notification(
        self,
        tokens: List[str],
        vehicle_name: str,
        temperature: float,
        threshold: str
    ):
        """온도 이탈 알림"""
        return await self.send_push_notification(
            tokens=tokens,
            title="⚠️ 온도 이탈 알림",
            body=f"{vehicle_name} 차량의 온도가 {temperature:.1f}°C로 허용 범위({threshold})를 벗어났습니다.",
            data={
                "type": "temperature_alert",
                "vehicle_name": vehicle_name,
                "temperature": str(temperature),
                "screen": "VehicleMonitoring"
            },
            priority="high"
        )
    
    async def send_maintenance_alert_notification(
        self,
        tokens: List[str],
        vehicle_name: str,
        alert_message: str
    ):
        """유지보수 알림"""
        return await self.send_push_notification(
            tokens=tokens,
            title="🔧 유지보수 알림",
            body=f"{vehicle_name}: {alert_message}",
            data={
                "type": "maintenance_alert",
                "vehicle_name": vehicle_name,
                "screen": "VehicleDetail"
            }
        )
    
    async def send_broadcast_notification(
        self,
        tokens: List[str],
        title: str,
        message: str
    ):
        """전체 공지 알림"""
        return await self.send_push_notification(
            tokens=tokens,
            title=title,
            body=message,
            data={
                "type": "broadcast",
                "screen": "Notifications"
            }
        )


# 싱글톤 인스턴스
_fcm_service_instance = None


def get_fcm_service() -> FCMNotificationService:
    """FCM 서비스 인스턴스 가져오기"""
    global _fcm_service_instance
    
    if _fcm_service_instance is None:
        _fcm_service_instance = FCMNotificationService()
    
    return _fcm_service_instance
