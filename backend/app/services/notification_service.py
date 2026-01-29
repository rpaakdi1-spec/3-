"""
알림 서비스

다양한 채널을 통한 알림 전송:
1. 이메일 (SMTP)
2. SMS (알리고 등)
3. Slack
4. 웹훅
"""

import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from app.core.config import settings


class NotificationChannel:
    """알림 채널 타입"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"


class NotificationLevel:
    """알림 레벨"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class NotificationService:
    """알림 서비스"""
    
    def __init__(self):
        # SMTP 설정
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_user = getattr(settings, 'SMTP_USER', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.smtp_from = getattr(settings, 'SMTP_FROM', self.smtp_user)
        
        # Slack 설정
        self.slack_webhook_url = getattr(settings, 'SLACK_WEBHOOK_URL', '')
        
        # SMS 설정 (알리고)
        self.sms_api_key = getattr(settings, 'ALIGO_API_KEY', '')
        self.sms_user_id = getattr(settings, 'ALIGO_USER_ID', '')
        self.sms_sender = getattr(settings, 'ALIGO_SENDER', '')
    
    def send_alert(
        self,
        title: str,
        message: str,
        level: str = NotificationLevel.INFO,
        channels: List[str] = None,
        recipients: Dict[str, List[str]] = None
    ) -> Dict[str, bool]:
        """
        알림 전송
        
        Args:
            title: 알림 제목
            message: 알림 내용
            level: 알림 레벨 (info/warning/critical)
            channels: 전송 채널 목록
            recipients: 수신자 정보 {"email": [...], "sms": [...], "slack": [...]}
            
        Returns:
            Dict: 채널별 전송 결과
        """
        if channels is None:
            channels = [NotificationChannel.EMAIL]
        
        if recipients is None:
            recipients = {}
        
        results = {}
        
        # 이메일 전송
        if NotificationChannel.EMAIL in channels:
            email_recipients = recipients.get("email", [])
            if email_recipients:
                results["email"] = self.send_email(
                    to_emails=email_recipients,
                    subject=f"[{level.upper()}] {title}",
                    body=message
                )
            else:
                results["email"] = False
                logger.warning("No email recipients specified")
        
        # SMS 전송
        if NotificationChannel.SMS in channels:
            sms_recipients = recipients.get("sms", [])
            if sms_recipients:
                results["sms"] = self.send_sms_bulk(
                    phone_numbers=sms_recipients,
                    message=f"[{level.upper()}] {title}\n{message}"
                )
            else:
                results["sms"] = False
                logger.warning("No SMS recipients specified")
        
        # Slack 전송
        if NotificationChannel.SLACK in channels:
            results["slack"] = self.send_slack(
                title=title,
                message=message,
                level=level
            )
        
        return results
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """
        이메일 전송
        
        Args:
            to_emails: 수신자 이메일 목록
            subject: 제목
            body: 본문
            html: HTML 형식 여부
            
        Returns:
            bool: 전송 성공 여부
        """
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
            return False
        
        try:
            message = MIMEMultipart()
            message["From"] = self.smtp_from
            message["To"] = ", ".join(to_emails)
            message["Subject"] = subject
            message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            
            # 본문 추가
            content_type = "html" if html else "plain"
            message.attach(MIMEText(body, content_type, "utf-8"))
            
            # SMTP 서버 연결 및 전송
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {len(to_emails)} recipient(s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        SMS 전송 (단일)
        
        Args:
            phone_number: 수신자 전화번호
            message: 메시지 내용
            
        Returns:
            bool: 전송 성공 여부
        """
        if not self.sms_api_key or not self.sms_user_id:
            logger.warning("SMS API credentials not configured")
            return False
        
        try:
            url = "https://apis.aligo.in/send/"
            data = {
                "key": self.sms_api_key,
                "user_id": self.sms_user_id,
                "sender": self.sms_sender,
                "receiver": phone_number,
                "msg": message,
                "msg_type": "SMS"
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("result_code") == "1":
                logger.info(f"SMS sent successfully to {phone_number}")
                return True
            else:
                logger.error(f"SMS send failed: {result.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
    
    def send_sms_bulk(self, phone_numbers: List[str], message: str) -> bool:
        """
        SMS 대량 전송
        
        Args:
            phone_numbers: 수신자 전화번호 목록
            message: 메시지 내용
            
        Returns:
            bool: 전송 성공 여부
        """
        success_count = 0
        for phone in phone_numbers:
            if self.send_sms(phone, message):
                success_count += 1
        
        return success_count > 0
    
    def send_slack(
        self,
        title: str,
        message: str,
        level: str = NotificationLevel.INFO
    ) -> bool:
        """
        Slack 메시지 전송
        
        Args:
            title: 제목
            message: 내용
            level: 알림 레벨
            
        Returns:
            bool: 전송 성공 여부
        """
        if not self.slack_webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False
        
        try:
            # 레벨별 색상
            color_map = {
                NotificationLevel.INFO: "#36a64f",      # 녹색
                NotificationLevel.WARNING: "#ff9800",   # 주황
                NotificationLevel.CRITICAL: "#f44336"   # 빨강
            }
            
            # 레벨별 이모지
            emoji_map = {
                NotificationLevel.INFO: ":information_source:",
                NotificationLevel.WARNING: ":warning:",
                NotificationLevel.CRITICAL: ":rotating_light:"
            }
            
            payload = {
                "username": "Cold Chain Monitor",
                "icon_emoji": emoji_map.get(level, ":robot_face:"),
                "attachments": [
                    {
                        "color": color_map.get(level, "#36a64f"),
                        "title": title,
                        "text": message,
                        "footer": "Cold Chain Dispatch System",
                        "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            response = requests.post(
                self.slack_webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("Slack message sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            return False
    
    def send_webhook(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        웹훅 전송
        
        Args:
            url: 웹훅 URL
            payload: 전송할 데이터
            headers: HTTP 헤더
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            if headers is None:
                headers = {"Content-Type": "application/json"}
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Webhook sent successfully to {url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
            return False
    
    def send_system_alert(
        self,
        alert: Dict[str, Any],
        admin_emails: List[str] = None,
        admin_phones: List[str] = None
    ) -> Dict[str, bool]:
        """
        시스템 알림 전송
        
        모니터링 서비스에서 감지된 알림을 관리자에게 전송
        
        Args:
            alert: 알림 정보
            admin_emails: 관리자 이메일 목록
            admin_phones: 관리자 전화번호 목록
            
        Returns:
            Dict: 채널별 전송 결과
        """
        title = alert.get("title", "시스템 알림")
        message = alert.get("message", "")
        level = alert.get("level", NotificationLevel.INFO)
        
        # 전송 채널 결정 (레벨에 따라)
        channels = []
        recipients = {}
        
        if level == NotificationLevel.CRITICAL:
            # Critical: 모든 채널 사용
            channels = [NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.SLACK]
            if admin_emails:
                recipients["email"] = admin_emails
            if admin_phones:
                recipients["sms"] = admin_phones
                
        elif level == NotificationLevel.WARNING:
            # Warning: 이메일 + Slack
            channels = [NotificationChannel.EMAIL, NotificationChannel.SLACK]
            if admin_emails:
                recipients["email"] = admin_emails
                
        else:
            # Info: Slack만
            channels = [NotificationChannel.SLACK]
        
        # 메시지 포맷팅
        formatted_message = f"""
{message}

Category: {alert.get('category', 'system')}
Timestamp: {alert.get('timestamp', datetime.now().isoformat())}

---
Cold Chain Dispatch System
        """.strip()
        
        return self.send_alert(
            title=title,
            message=formatted_message,
            level=level,
            channels=channels,
            recipients=recipients
        )
    
    def send_email_template(
        self,
        to_emails: List[str],
        template_name: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        템플릿 기반 이메일 전송
        
        Args:
            to_emails: 수신자 목록
            template_name: 템플릿 이름
            context: 템플릿 컨텍스트
            
        Returns:
            bool: 전송 성공 여부
        """
        # 템플릿 정의
        templates = {
            "system_health": {
                "subject": "[Cold Chain] 시스템 상태 보고",
                "body": """
<html>
<body>
    <h2>시스템 상태 보고</h2>
    <p>시스템 상태: <strong>{status}</strong></p>
    
    <h3>데이터베이스</h3>
    <ul>
        <li>상태: {db_status}</li>
        <li>응답 시간: {db_response_time}ms</li>
    </ul>
    
    <h3>시스템 리소스</h3>
    <ul>
        <li>CPU: {cpu_percent}%</li>
        <li>메모리: {memory_percent}%</li>
        <li>디스크: {disk_percent}%</li>
    </ul>
    
    <p>보고 시각: {timestamp}</p>
</body>
</html>
                """
            },
            "alert_summary": {
                "subject": "[Cold Chain] 알림 요약",
                "body": """
<html>
<body>
    <h2>알림 요약</h2>
    <p>총 {alert_count}개의 알림이 발생했습니다.</p>
    
    <h3>심각도별 분류</h3>
    <ul>
        <li>Critical: {critical_count}건</li>
        <li>Warning: {warning_count}건</li>
        <li>Info: {info_count}건</li>
    </ul>
    
    <h3>최근 알림</h3>
    <ul>
        {recent_alerts}
    </ul>
    
    <p>보고 시각: {timestamp}</p>
</body>
</html>
                """
            }
        }
        
        if template_name not in templates:
            logger.error(f"Template '{template_name}' not found")
            return False
        
        template = templates[template_name]
        
        try:
            subject = template["subject"].format(**context)
            body = template["body"].format(**context)
            
            return self.send_email(
                to_emails=to_emails,
                subject=subject,
                body=body,
                html=True
            )
            
        except Exception as e:
            logger.error(f"Failed to send template email: {e}")
            return False
