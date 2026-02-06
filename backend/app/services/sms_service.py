import os
from typing import Optional, Dict, Any
from loguru import logger

# Twilio를 optional import로 처리
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("⚠️ Twilio package not installed. SMS service will be disabled.")


class SMSService:
    """SMS 발송 서비스 (Twilio)"""
    
    def __init__(self):
        self.client = None
        self.enabled = False
        
        if not TWILIO_AVAILABLE:
            logger.warning("⚠️ Twilio package not available. SMS service disabled.")
            return
        
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER")
        
        # Twilio 클라이언트 초기화
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self.enabled = True
                logger.info("✅ Twilio SMS Service initialized")
            except Exception as e:
                logger.error(f"❌ Twilio initialization error: {e}")
                self.enabled = False
        else:
            logger.warning("⚠️ Twilio credentials not found. SMS service disabled.")
    
    def send_sms(
        self,
        to_number: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        SMS 발송
        
        Args:
            to_number: 수신자 전화번호 (예: +821012345678)
            message: 메시지 내용
            metadata: 추가 메타데이터
        
        Returns:
            발송 결과
        """
        if not self.enabled:
            logger.error("❌ SMS service is not enabled")
            return {
                "success": False,
                "error": "SMS service not configured",
                "message_sid": None
            }
        
        try:
            # 전화번호 포맷 검증 및 변환
            formatted_number = self._format_phone_number(to_number)
            
            # SMS 발송
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=formatted_number
            )
            
            logger.info(f"✅ SMS sent successfully: SID={message_obj.sid}, To={formatted_number}")
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "to": formatted_number,
                "from": self.from_number,
                "date_sent": message_obj.date_sent,
                "error": None
            }
            
        except Exception as e:
            # TwilioRestException 처리 (if available)
            if TWILIO_AVAILABLE and hasattr(e, 'msg'):
                logger.error(f"❌ Twilio SMS error: {e.msg} (Code: {e.code})")
                return {
                    "success": False,
                    "message_sid": None,
                    "error": f"Twilio error: {e.msg}",
                    "error_code": e.code
                }
            else:
                logger.error(f"❌ SMS send error: {str(e)}")
                return {
                    "success": False,
                    "message_sid": None,
                    "error": str(e)
                }
        

    
    def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """
        SMS 발송 상태 조회
        
        Args:
            message_sid: 메시지 SID
        
        Returns:
            메시지 상태
        """
        if not self.enabled:
            return {"success": False, "error": "SMS service not enabled"}
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                "success": True,
                "sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "date_sent": message.date_sent,
                "date_updated": message.date_updated,
                "error_code": message.error_code,
                "error_message": message.error_message
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch message status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_phone_number(self, phone: str) -> str:
        """
        전화번호를 국제 형식으로 변환
        
        Args:
            phone: 전화번호 (예: 010-1234-5678 또는 01012345678)
        
        Returns:
            국제 형식 전화번호 (예: +821012345678)
        """
        # 하이픈, 공백 제거
        phone = phone.replace("-", "").replace(" ", "")
        
        # 한국 번호 처리
        if phone.startswith("010") or phone.startswith("011") or phone.startswith("016"):
            # 0으로 시작하면 +82로 변환
            return f"+82{phone[1:]}"
        elif phone.startswith("+82"):
            # 이미 국제 형식
            return phone
        else:
            # 기타 국가 번호는 그대로
            return phone
    
    def send_order_confirmed_sms(
        self,
        to_number: str,
        order_number: str,
        customer_name: str,
        pickup_address: str,
        delivery_address: str,
        pickup_date: str
    ) -> Dict[str, Any]:
        """주문 확정 SMS 발송"""
        message = (
            f"[냉동냉장배차] 주문이 확정되었습니다.\n"
            f"주문번호: {order_number}\n"
            f"고객명: {customer_name}\n"
            f"상차지: {pickup_address}\n"
            f"하차지: {delivery_address}\n"
            f"상차일: {pickup_date}\n"
            f"감사합니다."
        )
        
        return self.send_sms(to_number, message)
    
    def send_dispatch_completed_sms(
        self,
        to_number: str,
        dispatch_number: str,
        driver_name: str,
        vehicle_plate: str,
        order_count: int
    ) -> Dict[str, Any]:
        """배차 완료 SMS 발송"""
        message = (
            f"[냉동냉장배차] 배차가 완료되었습니다.\n"
            f"배차번호: {dispatch_number}\n"
            f"기사명: {driver_name}\n"
            f"차량: {vehicle_plate}\n"
            f"주문 건수: {order_count}건\n"
            f"안전 운행 부탁드립니다."
        )
        
        return self.send_sms(to_number, message)
    
    def send_urgent_dispatch_sms(
        self,
        to_number: str,
        order_number: str,
        pickup_address: str,
        urgency_reason: str
    ) -> Dict[str, Any]:
        """긴급 배차 SMS 발송"""
        message = (
            f"🚨 [긴급배차] 긴급 주문이 접수되었습니다.\n"
            f"주문번호: {order_number}\n"
            f"상차지: {pickup_address}\n"
            f"긴급사유: {urgency_reason}\n"
            f"즉시 확인 부탁드립니다."
        )
        
        return self.send_sms(to_number, message)


# 싱글톤 인스턴스
sms_service = SMSService()
