"""
IoT 센서 통합 - 알림 전송기
2026-02-05

다양한 채널로 알림을 전송합니다.
"""
from typing import Optional
from loguru import logger
import asyncio
import aiohttp
from datetime import datetime

from config import settings
from models import AlertBase, AlertLevel


class AlertNotifier:
    """알림 전송기"""
    
    def __init__(self):
        self.telegram_enabled = bool(settings.ALERT_TELEGRAM_BOT_TOKEN)
        self.email_enabled = settings.ALERT_EMAIL_ENABLED
        self.sms_enabled = settings.ALERT_SMS_ENABLED
        
    async def send_alert(self, alert: AlertBase):
        """
        알림 전송 (모든 채널)
        
        Args:
            alert: 알림 객체
        """
        logger.info(f"알림 전송: {alert.level.value} | {alert.message}")
        
        # 동시 전송
        tasks = []
        
        if self.telegram_enabled:
            tasks.append(self.send_telegram(alert))
            
        if self.email_enabled:
            tasks.append(self.send_email(alert))
            
        if self.sms_enabled and alert.level in [AlertLevel.CRITICAL, AlertLevel.WARNING]:
            tasks.append(self.send_sms(alert))
            
        # WebSocket은 별도 처리 (실시간 대시보드)
        tasks.append(self.send_websocket(alert))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def send_telegram(self, alert: AlertBase):
        """
        Telegram 메시지 전송
        
        Args:
            alert: 알림 객체
        """
        if not self.telegram_enabled:
            return
            
        try:
            bot_token = settings.ALERT_TELEGRAM_BOT_TOKEN
            chat_id = settings.ALERT_TELEGRAM_CHAT_ID
            
            # 이모티콘 매핑
            emoji_map = {
                AlertLevel.INFO: "ℹ️",
                AlertLevel.WARNING: "⚠️",
                AlertLevel.CRITICAL: "🚨"
            }
            emoji = emoji_map.get(alert.level, "📢")
            
            # 메시지 작성
            message = (
                f"{emoji} **{alert.level.value.upper()} 알림**\n\n"
                f"📍 센서: `{alert.sensor_id}`\n"
            )
            
            if alert.vehicle_id:
                message += f"🚚 차량: `{alert.vehicle_id}`\n"
                
            message += (
                f"💬 내용: {alert.message}\n"
                f"🕐 시간: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            # Telegram API 호출
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"✅ Telegram 알림 전송 성공: {alert.sensor_id}")
                    else:
                        logger.error(f"❌ Telegram 알림 전송 실패: {response.status}")
                        
        except Exception as e:
            logger.error(f"Telegram 알림 오류: {e}")
            
    async def send_email(self, alert: AlertBase):
        """
        이메일 전송
        
        Args:
            alert: 알림 객체
        """
        # TODO: 이메일 전송 구현 (SMTP)
        logger.info(f"📧 이메일 알림 전송 (미구현): {alert.sensor_id}")
        
    async def send_sms(self, alert: AlertBase):
        """
        SMS 전송
        
        Args:
            alert: 알림 객체
        """
        # TODO: SMS 전송 구현 (Twilio, AWS SNS 등)
        logger.info(f"📱 SMS 알림 전송 (미구현): {alert.sensor_id}")
        
    async def send_websocket(self, alert: AlertBase):
        """
        WebSocket 브로드캐스트
        
        Args:
            alert: 알림 객체
        """
        # TODO: WebSocket 서버로 브로드캐스트
        logger.debug(f"🔌 WebSocket 알림 전송: {alert.sensor_id}")
        
        # Redis Pub/Sub 또는 WebSocket 매니저 사용
        # 예: await websocket_manager.broadcast(alert.dict())


# ============================================================================
# 전역 인스턴스
# ============================================================================

notifier = AlertNotifier()
