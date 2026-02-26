from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger

from app.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationType,
    NotificationChannel,
    NotificationStatus
)
from app.schemas.notification import (
    NotificationSendRequest,
    TemplateNotificationRequest
)
from app.services.sms_service import sms_service
from app.services.fcm_service import FCMService


class NotificationService:
    """통합 알림 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def send_notification(
        self,
        request: NotificationSendRequest
    ) -> Notification:
        """
        알림 발송
        
        Args:
            request: 알림 발송 요청
        
        Returns:
            생성된 알림 객체
        """
        # 알림 레코드 생성
        notification = Notification(
            notification_type=request.notification_type,
            channel=request.channel,
            status=NotificationStatus.PENDING,
            recipient_name=request.recipient_name,
            recipient_phone=request.recipient_phone,
            recipient_email=request.recipient_email,
            recipient_device_token=request.recipient_device_token,
            title=request.title,
            message=request.message,
            template_code=request.template_code,
            metadata=request.metadata,
            order_id=request.order_id,
            dispatch_id=request.dispatch_id,
            vehicle_id=request.vehicle_id,
            driver_id=request.driver_id
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        logger.info(f"📧 Created notification: ID={notification.id}, Type={notification.notification_type}, Channel={notification.channel}")
        
        # 채널별 발송
        if request.channel == NotificationChannel.SMS:
            await self._send_sms(notification)
        elif request.channel == NotificationChannel.KAKAO:
            await self._send_kakao(notification)
        elif request.channel == NotificationChannel.PUSH:
            await self._send_push(notification)
        elif request.channel == NotificationChannel.EMAIL:
            await self._send_email(notification)
        
        return notification
    
    async def send_from_template(
        self,
        request: TemplateNotificationRequest
    ) -> Notification:
        """
        템플릿 기반 알림 발송
        
        Args:
            request: 템플릿 알림 요청
        
        Returns:
            생성된 알림 객체
        """
        # 템플릿 조회
        template = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.template_code == request.template_code,
            NotificationTemplate.channel == request.channel,
            NotificationTemplate.is_active == True
        ).first()
        
        if not template:
            raise ValueError(f"템플릿을 찾을 수 없습니다: {request.template_code}")
        
        # 변수 치환
        title = self._replace_variables(template.title_template, request.variables)
        message = self._replace_variables(template.message_template, request.variables)
        
        # 알림 발송 요청 생성
        send_request = NotificationSendRequest(
            notification_type=template.notification_type,
            channel=request.channel,
            recipient_name=request.recipient_name,
            recipient_phone=request.recipient_phone,
            recipient_email=request.recipient_email,
            recipient_device_token=request.recipient_device_token,
            title=title,
            message=message,
            template_code=request.template_code,
            metadata=request.variables,
            order_id=request.order_id,
            dispatch_id=request.dispatch_id,
            vehicle_id=request.vehicle_id,
            driver_id=request.driver_id
        )
        
        return await self.send_notification(send_request)
    
    async def send_bulk_notifications(
        self,
        notifications: List[NotificationSendRequest]
    ) -> List[Notification]:
        """일괄 알림 발송"""
        results = []
        
        for notif_request in notifications:
            try:
                notification = await self.send_notification(notif_request)
                results.append(notification)
            except Exception as e:
                logger.error(f"❌ Bulk notification failed: {str(e)}")
                # 실패해도 계속 진행
                continue
        
        logger.info(f"✅ Bulk notifications sent: {len(results)}/{len(notifications)}")
        return results
    
    async def _send_sms(self, notification: Notification):
        """SMS 발송"""
        if not notification.recipient_phone:
            notification.status = NotificationStatus.FAILED
            notification.error_message = "수신자 전화번호가 없습니다"
            self.db.commit()
            return
        
        try:
            # Twilio SMS 발송
            result = sms_service.send_sms(
                to_number=notification.recipient_phone,
                message=notification.message,
                metadata=notification.metadata
            )
            
            if result["success"]:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
                notification.external_id = result.get("message_sid")
                notification.external_response = result
                logger.info(f"✅ SMS sent: Notification ID={notification.id}, SID={result.get('message_sid')}")
            else:
                notification.status = NotificationStatus.FAILED
                notification.error_message = result.get("error")
                notification.external_response = result
                logger.error(f"❌ SMS failed: Notification ID={notification.id}, Error={result.get('error')}")
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ SMS send error: {str(e)}")
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            self.db.commit()
    
    async def _send_kakao(self, notification: Notification):
        """카카오톡 발송 (구현 예정)"""
        logger.warning("⚠️ KakaoTalk notification not implemented yet")
        notification.status = NotificationStatus.FAILED
        notification.error_message = "카카오톡 발송 기능 준비 중"
        self.db.commit()
    
    async def _send_push(self, notification: Notification):
        """푸시 알림 발송"""
        if not notification.recipient_device_token:
            notification.status = NotificationStatus.FAILED
            notification.error_message = "기기 토큰이 없습니다"
            self.db.commit()
            return
        
        try:
            # FCM이 초기화되지 않았으면 경고
            if not FCMService._initialized:
                logger.warning("⚠️ FCM service not initialized, push notification skipped")
                notification.status = NotificationStatus.FAILED
                notification.error_message = "FCM 서비스가 초기화되지 않았습니다"
                self.db.commit()
                return
            
            # FCM 푸시 발송 - FCMService.send_notification() 사용
            # Note: FCMService.send_notification은 user_id를 받지만,
            # 여기서는 device token을 직접 사용해야 하므로 임시로 스킵
            logger.warning(f"⚠️ Push notification skipped: Notification ID={notification.id} (device token based push not yet supported by FCMService)")
            notification.status = NotificationStatus.PENDING
            notification.error_message = "FCMService는 user_id 기반 발송만 지원합니다"
            self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ Push send error: {str(e)}")
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            self.db.commit()
    
    async def _send_email(self, notification: Notification):
        """이메일 발송 (구현 예정)"""
        logger.warning("⚠️ Email notification not implemented yet")
        notification.status = NotificationStatus.FAILED
        notification.error_message = "이메일 발송 기능 준비 중"
        self.db.commit()
    
    def _replace_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """
        템플릿 변수 치환
        
        Args:
            template: 템플릿 문자열 (예: "안녕하세요 {{name}}님")
            variables: 변수 딕셔너리 (예: {"name": "홍길동"})
        
        Returns:
            치환된 문자열
        """
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    def get_notification_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """알림 통계 조회"""
        query = self.db.query(Notification)
        
        if start_date:
            query = query.filter(Notification.created_at >= start_date)
        if end_date:
            query = query.filter(Notification.created_at <= end_date)
        
        notifications = query.all()
        
        total_sent = sum(1 for n in notifications if n.status == NotificationStatus.SENT)
        total_delivered = sum(1 for n in notifications if n.status == NotificationStatus.DELIVERED)
        total_failed = sum(1 for n in notifications if n.status == NotificationStatus.FAILED)
        total_pending = sum(1 for n in notifications if n.status == NotificationStatus.PENDING)
        
        by_channel = {}
        by_type = {}
        by_status = {}
        
        for n in notifications:
            by_channel[n.channel.value] = by_channel.get(n.channel.value, 0) + 1
            by_type[n.notification_type.value] = by_type.get(n.notification_type.value, 0) + 1
            by_status[n.status.value] = by_status.get(n.status.value, 0) + 1
        
        return {
            "total_sent": total_sent,
            "total_delivered": total_delivered,
            "total_failed": total_failed,
            "total_pending": total_pending,
            "by_channel": by_channel,
            "by_type": by_type,
            "by_status": by_status
        }
