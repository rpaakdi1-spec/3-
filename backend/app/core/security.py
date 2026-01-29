"""
보안 유틸리티
입력 검증, 출력 이스케이프, CSRF 토큰
"""
import html
import secrets
import hashlib
from typing import Any, Optional
from datetime import datetime, timedelta
import re
from loguru import logger


class SecurityUtils:
    """보안 유틸리티 클래스"""
    
    # XSS 위험 패턴
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>',
        r'javascript:',
        r'on\w+\s*=',
        r'<embed[^>]*>',
        r'<object[^>]*>',
    ]
    
    # SQL Injection 패턴
    SQL_PATTERNS = [
        r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b',
        r'(--|;|/\*|\*/)',
        r'\bOR\b.*=',
        r'\bAND\b.*=',
        r'\bUNION\b.*\bSELECT\b',
    ]
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        입력 값 정제 (XSS 방지)
        
        Args:
            text: 입력 텍스트
            
        Returns:
            정제된 텍스트
        """
        if not text:
            return text
        
        # HTML 이스케이프
        sanitized = html.escape(text)
        
        # 위험한 패턴 제거
        for pattern in SecurityUtils.XSS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @staticmethod
    def validate_sql_input(text: str) -> bool:
        """
        SQL Injection 검증
        
        Args:
            text: 검증할 텍스트
            
        Returns:
            안전하면 True, 위험하면 False
        """
        if not text:
            return True
        
        # SQL Injection 패턴 검사
        for pattern in SecurityUtils.SQL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {text[:50]}...")
                return False
        
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        이메일 주소 검증
        
        Args:
            email: 이메일 주소
            
        Returns:
            유효하면 True
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        전화번호 검증 (한국)
        
        Args:
            phone: 전화번호
            
        Returns:
            유효하면 True
        """
        # 010-1234-5678 또는 01012345678
        pattern = r'^(01[016789])[-]?(\d{3,4})[-]?(\d{4})$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_business_number(business_number: str) -> bool:
        """
        사업자 번호 검증
        
        Args:
            business_number: 사업자 번호 (123-45-67890)
            
        Returns:
            유효하면 True
        """
        # 123-45-67890 형식
        pattern = r'^\d{3}-\d{2}-\d{5}$'
        return bool(re.match(pattern, business_number))
    
    @staticmethod
    def generate_csrf_token() -> str:
        """
        CSRF 토큰 생성
        
        Returns:
            32자 랜덤 토큰
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple:
        """
        비밀번호 해싱 (SHA-256 + salt)
        
        Args:
            password: 평문 비밀번호
            salt: 솔트 (없으면 자동 생성)
            
        Returns:
            (해시, 솔트) 튜플
        """
        if not salt:
            salt = secrets.token_hex(32)
        
        # SHA-256 해싱
        hash_obj = hashlib.sha256((password + salt).encode())
        password_hash = hash_obj.hexdigest()
        
        return password_hash, salt
    
    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """
        비밀번호 검증
        
        Args:
            password: 입력된 비밀번호
            password_hash: 저장된 해시
            salt: 솔트
            
        Returns:
            일치하면 True
        """
        computed_hash, _ = SecurityUtils.hash_password(password, salt)
        return computed_hash == password_hash
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, list]:
        """
        비밀번호 강도 검증
        
        Args:
            password: 비밀번호
            
        Returns:
            (유효 여부, 오류 메시지 리스트)
        """
        errors = []
        
        # 최소 길이
        if len(password) < 8:
            errors.append("비밀번호는 최소 8자 이상이어야 합니다")
        
        # 최대 길이
        if len(password) > 128:
            errors.append("비밀번호는 최대 128자까지 가능합니다")
        
        # 대문자 포함
        if not re.search(r'[A-Z]', password):
            errors.append("대문자를 최소 1개 포함해야 합니다")
        
        # 소문자 포함
        if not re.search(r'[a-z]', password):
            errors.append("소문자를 최소 1개 포함해야 합니다")
        
        # 숫자 포함
        if not re.search(r'\d', password):
            errors.append("숫자를 최소 1개 포함해야 합니다")
        
        # 특수문자 포함
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("특수문자를 최소 1개 포함해야 합니다")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
        """
        민감한 데이터 마스킹
        
        Args:
            data: 원본 데이터
            visible_chars: 보이는 문자 수
            
        Returns:
            마스킹된 데이터
        """
        if not data or len(data) <= visible_chars:
            return "*" * len(data)
        
        visible_part = data[-visible_chars:]
        masked_part = "*" * (len(data) - visible_chars)
        
        return masked_part + visible_part
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        보안 토큰 생성
        
        Args:
            length: 토큰 길이
            
        Returns:
            랜덤 토큰
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def is_safe_redirect_url(url: str, allowed_hosts: list = None) -> bool:
        """
        안전한 리다이렉트 URL 검증 (Open Redirect 방지)
        
        Args:
            url: 리다이렉트 URL
            allowed_hosts: 허용된 호스트 리스트
            
        Returns:
            안전하면 True
        """
        if not url:
            return False
        
        # 상대 경로는 허용
        if url.startswith('/') and not url.startswith('//'):
            return True
        
        # 절대 URL인 경우 호스트 검증
        if allowed_hosts:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc in allowed_hosts
        
        return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        파일명 정제 (Path Traversal 방지)
        
        Args:
            filename: 원본 파일명
            
        Returns:
            정제된 파일명
        """
        if not filename:
            return ""
        
        # 위험한 문자 제거
        safe_filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        # .. 제거 (디렉토리 탐색 방지)
        safe_filename = safe_filename.replace('..', '')
        
        # 앞뒤 공백 제거
        safe_filename = safe_filename.strip()
        
        return safe_filename
    
    @staticmethod
    def log_security_event(
        event_type: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        details: Optional[dict] = None
    ):
        """
        보안 이벤트 로깅
        
        Args:
            event_type: 이벤트 유형
            user_id: 사용자 ID
            ip_address: IP 주소
            details: 상세 정보
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details
        }
        
        logger.warning(f"Security Event: {log_data}")


# 전역 인스턴스
security_utils = SecurityUtils()
