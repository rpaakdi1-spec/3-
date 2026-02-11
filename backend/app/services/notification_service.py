"""
Phase 16: Notification Service
드라이버 알림 및 Push 알림 서비스
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.driver_app import (
    DriverNotification,
    PushToken,
    NotificationType
)


class NotificationService:
    """알림 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def send_notification(
        self,
        driver_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        dispatch_id: Optional[int] = None,
        action_required: bool = False,
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DriverNotification:
        """
        드라이버에게 알림 발송
        
        Args:
            driver_id: 드라이버 ID
            notification_type: 알림 타입
            title: 알림 제목
            message: 알림 내용
            dispatch_id: 배차 ID (선택)
            action_required: 액션 필요 여부
            action_url: 액션 URL
            metadata: 추가 메타데이터
        
        Returns:
            생성된 알림 객체
        """
        # 드라이버의 Push 토큰 조회
        push_token = self.db.query(PushToken).filter(
            and_(
                PushToken.driver_id == driver_id,
                PushToken.is_active == True
            )
        ).first()
        
        # 알림 생성
        notification = DriverNotification(
            driver_id=driver_id,
            dispatch_id=dispatch_id,
            notification_type=notification_type,
            title=title,
            message=message,
            push_token=push_token.token if push_token else None,
            action_required=action_required,
            action_url=action_url,
            metadata=metadata or {}
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # TODO: 실제 FCM Push 알림 발송
        # await self._send_fcm_push(notification)
        
        return notification
    
    async def send_dispatch_assigned_notification(
        self,
        driver_id: int,
        dispatch_id: int,
        order_info: Dict[str, Any]
    ) -> DriverNotification:
        """배차 배정 알림"""
        title = "🚚 새로운 배차가 배정되었습니다"
        message = f"주문 #{order_info.get('order_number')} - {order_info.get('customer_name')}"
        
        return await self.send_notification(
            driver_id=driver_id,
            notification_type=NotificationType.DISPATCH_ASSIGNED,
            title=title,
            message=message,
            dispatch_id=dispatch_id,
            action_required=True,
            action_url=f"/dispatch/{dispatch_id}",
            metadata={"order_info": order_info}
        )
    
    async def send_route_optimized_notification(
        self,
        driver_id: int,
        dispatch_id: int,
        optimization_info: Dict[str, Any]
    ) -> DriverNotification:
        """경로 최적화 알림"""
        title = "🗺️ 경로가 최적화되었습니다"
        message = f"예상 시간: {optimization_info.get('estimated_time')}분 단축"
        
        return await self.send_notification(
            driver_id=driver_id,
            notification_type=NotificationType.ROUTE_OPTIMIZED,
            title=title,
            message=message,
            dispatch_id=dispatch_id,
            action_required=False,
            metadata={"optimization_info": optimization_info}
        )
    
    async def send_chat_message_notification(
        self,
        driver_id: int,
        sender_name: str,
        message: str,
        room_id: int
    ) -> DriverNotification:
        """채팅 메시지 알림"""
        title = f"💬 {sender_name}님의 메시지"
        
        return await self.send_notification(
            driver_id=driver_id,
            notification_type=NotificationType.CHAT_MESSAGE,
            title=title,
            message=message[:100],  # 메시지 미리보기
            action_required=False,
            action_url=f"/chat/{room_id}",
            metadata={"sender_name": sender_name, "room_id": room_id}
        )
    
    def get_driver_notifications(
        self,
        driver_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[DriverNotification]:
        """
        드라이버 알림 목록 조회
        
        Args:
            driver_id: 드라이버 ID
            unread_only: 읽지 않은 알림만 조회
            limit: 조회 개수
        
        Returns:
            알림 목록
        """
        query = self.db.query(DriverNotification).filter(
            DriverNotification.driver_id == driver_id
        )
        
        if unread_only:
            query = query.filter(DriverNotification.is_read == False)
        
        notifications = query.order_by(
            desc(DriverNotification.created_at)
        ).limit(limit).all()
        
        return notifications
    
    def mark_as_read(
        self,
        notification_id: int,
        driver_id: int
    ) -> Optional[DriverNotification]:
        """
        알림을 읽음으로 표시
        
        Args:
            notification_id: 알림 ID
            driver_id: 드라이버 ID
        
        Returns:
            업데이트된 알림 객체
        """
        notification = self.db.query(DriverNotification).filter(
            and_(
                DriverNotification.id == notification_id,
                DriverNotification.driver_id == driver_id
            )
        ).first()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(notification)
        
        return notification
    
    def mark_action_taken(
        self,
        notification_id: int,
        driver_id: int
    ) -> Optional[DriverNotification]:
        """
        알림 액션 수행 표시
        
        Args:
            notification_id: 알림 ID
            driver_id: 드라이버 ID
        
        Returns:
            업데이트된 알림 객체
        """
        notification = self.db.query(DriverNotification).filter(
            and_(
                DriverNotification.id == notification_id,
                DriverNotification.driver_id == driver_id
            )
        ).first()
        
        if notification:
            notification.action_taken = True
            notification.action_taken_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(notification)
        
        return notification
    
    def get_unread_count(self, driver_id: int) -> int:
        """
        읽지 않은 알림 개수
        
        Args:
            driver_id: 드라이버 ID
        
        Returns:
            읽지 않은 알림 개수
        """
        count = self.db.query(DriverNotification).filter(
            and_(
                DriverNotification.driver_id == driver_id,
                DriverNotification.is_read == False
            )
        ).count()
        
        return count
    
    # Push Token 관리
    
    def register_push_token(
        self,
        driver_id: int,
        token: str,
        device_type: Optional[str] = None,
        device_id: Optional[str] = None
    ) -> PushToken:
        """
        Push 토큰 등록
        
        Args:
            driver_id: 드라이버 ID
            token: FCM 토큰
            device_type: 디바이스 타입
            device_id: 디바이스 ID
        
        Returns:
            등록된 토큰 객체
        """
        # 기존 토큰 비활성화
        self.db.query(PushToken).filter(
            PushToken.driver_id == driver_id
        ).update({"is_active": False})
        
        # 새 토큰 등록
        push_token = PushToken(
            driver_id=driver_id,
            token=token,
            device_type=device_type,
            device_id=device_id,
            is_active=True
        )
        
        self.db.add(push_token)
        self.db.commit()
        self.db.refresh(push_token)
        
        return push_token
    
    def update_push_token_usage(self, token: str):
        """Push 토큰 사용 시각 업데이트"""
        push_token = self.db.query(PushToken).filter(
            PushToken.token == token
        ).first()
        
        if push_token:
            push_token.last_used_at = datetime.utcnow()
            self.db.commit()
    
    async def _send_fcm_push(self, notification: DriverNotification):
        """
        FCM Push 알림 발송 (구현 필요)
        
        TODO: Firebase Cloud Messaging 연동
        """
        # FCM 발송 로직
        # ...
        
        # 발송 완료 표시
        notification.push_sent = True
        notification.push_sent_at = datetime.utcnow()
        self.db.commit()
