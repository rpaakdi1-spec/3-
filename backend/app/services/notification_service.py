"""
Notification Service for Delivery Tracking System
Sends SMS and Email notifications for dispatch events
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.dispatch import Dispatch
from app.models.dispatch_document import DispatchTracking
from app.models.client import Client
import os
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications about dispatch events"""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def send_departure_notification(
        self,
        dispatch_id: int,
        tracking_number: str
    ) -> bool:
        """Send notification when dispatch departs"""
        try:
            dispatch = self.db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
            if not dispatch:
                logger.error(f"Dispatch {dispatch_id} not found")
                return False
            
            # Get client contact info
            # Note: This assumes there's a relationship to get client info
            # Adjust based on your actual model relationships
            
            tracking_url = f"{os.getenv('FRONTEND_URL', 'http://localhost')}/track/{tracking_number}"
            
            message = f"""
🚚 배송이 시작되었습니다

배차번호: {dispatch.dispatch_number}
차량: {dispatch.vehicle_plate if hasattr(dispatch, 'vehicle_plate') else 'N/A'}
출발시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}

실시간 위치 추적:
{tracking_url}

문의사항이 있으시면 연락주세요.
"""
            
            # TODO: Implement actual SMS/Email sending
            # For now, just log
            logger.info(f"[NOTIFICATION] Departure notification for dispatch {dispatch_id}")
            logger.info(f"Message: {message}")
            
            # If Twilio is configured, send SMS
            # if os.getenv('TWILIO_ACCOUNT_SID'):
            #     self._send_sms(client_phone, message)
            
            # If SMTP is configured, send email
            # if os.getenv('SMTP_HOST'):
            #     self._send_email(client_email, "배송 시작 알림", message)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send departure notification: {e}")
            return False
    
    async def send_arrival_notification(
        self,
        dispatch_id: int
    ) -> bool:
        """Send notification when dispatch arrives"""
        try:
            dispatch = self.db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
            if not dispatch:
                logger.error(f"Dispatch {dispatch_id} not found")
                return False
            
            message = f"""
✅ 배송이 완료되었습니다

배차번호: {dispatch.dispatch_number}
차량: {dispatch.vehicle_plate if hasattr(dispatch, 'vehicle_plate') else 'N/A'}
도착시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}

업로드된 서류는 추적 페이지에서 다운로드하실 수 있습니다.

감사합니다.
"""
            
            logger.info(f"[NOTIFICATION] Arrival notification for dispatch {dispatch_id}")
            logger.info(f"Message: {message}")
            
            # TODO: Implement actual SMS/Email sending
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send arrival notification: {e}")
            return False
    
    async def send_document_upload_notification(
        self,
        dispatch_id: int,
        document_type: str,
        stage: str
    ) -> bool:
        """Send notification when document is uploaded"""
        try:
            dispatch = self.db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
            if not dispatch:
                logger.error(f"Dispatch {dispatch_id} not found")
                return False
            
            doc_type_labels = {
                'transaction_statement': '거래명세표',
                'temperature_record': '온도기록지',
                'signature': '서명'
            }
            
            stage_labels = {
                'departure': '출발',
                'arrival': '도착'
            }
            
            document_name = doc_type_labels.get(document_type, document_type)
            stage_name = stage_labels.get(stage, stage)
            
            message = f"""
📄 서류가 업로드되었습니다

배차번호: {dispatch.dispatch_number}
서류: {stage_name} 시 {document_name}
업로드시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}

추적 페이지에서 다운로드하실 수 있습니다.
"""
            
            logger.info(f"[NOTIFICATION] Document upload notification for dispatch {dispatch_id}")
            logger.info(f"Message: {message}")
            
            # TODO: Implement actual SMS/Email sending
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send document upload notification: {e}")
            return False
    
    def _send_sms(self, phone: str, message: str) -> bool:
        """Send SMS using Twilio"""
        # TODO: Implement Twilio SMS
        try:
            # from twilio.rest import Client
            # account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            # auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            # from_phone = os.getenv('TWILIO_PHONE_NUMBER')
            # 
            # client = Client(account_sid, auth_token)
            # message = client.messages.create(
            #     body=message,
            #     from_=from_phone,
            #     to=phone
            # )
            logger.info(f"SMS would be sent to {phone}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
    
    def _send_email(self, email: str, subject: str, message: str) -> bool:
        """Send email using SMTP"""
        # TODO: Implement SMTP email
        try:
            # import smtplib
            # from email.mime.text import MIMEText
            # from email.mime.multipart import MIMEMultipart
            # 
            # smtp_host = os.getenv('SMTP_HOST')
            # smtp_port = int(os.getenv('SMTP_PORT', 587))
            # smtp_user = os.getenv('SMTP_USER')
            # smtp_pass = os.getenv('SMTP_PASS')
            # 
            # msg = MIMEMultipart()
            # msg['From'] = smtp_user
            # msg['To'] = email
            # msg['Subject'] = subject
            # msg.attach(MIMEText(message, 'plain'))
            # 
            # server = smtplib.SMTP(smtp_host, smtp_port)
            # server.starttls()
            # server.login(smtp_user, smtp_pass)
            # server.send_message(msg)
            # server.quit()
            logger.info(f"Email would be sent to {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


async def send_dispatch_notification(
    db: Session,
    dispatch_id: int,
    event_type: str,
    **kwargs
) -> bool:
    """
    Convenience function to send notifications
    
    Args:
        db: Database session
        dispatch_id: ID of the dispatch
        event_type: Type of event ('departure', 'arrival', 'document_uploaded')
        **kwargs: Additional parameters (e.g., document_type, stage, tracking_number)
    
    Returns:
        bool: True if notification sent successfully
    """
    service = NotificationService(db)
    
    if event_type == 'departure':
        tracking_number = kwargs.get('tracking_number', '')
        return await service.send_departure_notification(dispatch_id, tracking_number)
    
    elif event_type == 'arrival':
        return await service.send_arrival_notification(dispatch_id)
    
    elif event_type == 'document_uploaded':
        document_type = kwargs.get('document_type', '')
        stage = kwargs.get('stage', '')
        return await service.send_document_upload_notification(
            dispatch_id, document_type, stage
        )
    
    else:
        logger.error(f"Unknown event type: {event_type}")
        return False
