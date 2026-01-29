"""
Sentry 에러 트래킹 서비스
실시간 에러 모니터링, 알림, 스택 트레이스
"""
import os
from typing import Optional, Dict, Any
from loguru import logger

from app.core.config import settings


class SentryService:
    """Sentry 에러 트래킹 서비스"""
    
    def __init__(self):
        self.enabled = False
        self.sentry_sdk = None
        self.setup_sentry()
    
    def setup_sentry(self):
        """Sentry 설정"""
        # Sentry DSN 확인
        sentry_dsn = os.getenv("SENTRY_DSN")
        
        if not sentry_dsn or sentry_dsn == "":
            logger.info("ℹ️  Sentry DSN not configured. Error tracking disabled.")
            return
        
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            from sentry_sdk.integrations.redis import RedisIntegration
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            # Sentry 초기화
            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=settings.APP_ENV,
                release=f"cold-chain-dispatch@1.0.0",
                
                # 통합 설정
                integrations=[
                    FastApiIntegration(transaction_style="endpoint"),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                    LoggingIntegration(
                        level=None,  # Breadcrumbs에 모든 로그 캡처
                        event_level="ERROR"  # ERROR 이상만 Sentry로 전송
                    )
                ],
                
                # 성능 추적
                traces_sample_rate=0.1,  # 10%의 트랜잭션 추적
                
                # 에러 샘플링
                sample_rate=1.0,  # 모든 에러 전송
                
                # 추가 옵션
                send_default_pii=False,  # 개인정보 전송 비활성화
                attach_stacktrace=True,  # 스택 트레이스 첨부
                max_breadcrumbs=50,  # 최대 breadcrumb 수
            )
            
            self.sentry_sdk = sentry_sdk
            self.enabled = True
            logger.success(f"✅ Sentry initialized for environment: {settings.APP_ENV}")
        
        except ImportError:
            logger.warning("⚠️  Sentry SDK not installed. Run: pip install sentry-sdk")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Sentry: {e}")
    
    def capture_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: str = "error",
        tags: Optional[Dict[str, str]] = None
    ):
        """
        예외 캡처 및 Sentry로 전송
        
        Args:
            exception: 예외 객체
            context: 추가 컨텍스트
            level: 심각도 (debug, info, warning, error, fatal)
            tags: 태그
        """
        if not self.enabled:
            return
        
        try:
            with self.sentry_sdk.push_scope() as scope:
                # 레벨 설정
                scope.level = level
                
                # 태그 추가
                if tags:
                    for key, value in tags.items():
                        scope.set_tag(key, value)
                
                # 컨텍스트 추가
                if context:
                    scope.set_context("additional_info", context)
                
                # 예외 캡처
                self.sentry_sdk.capture_exception(exception)
                logger.debug(f"Exception captured by Sentry: {type(exception).__name__}")
        
        except Exception as e:
            logger.error(f"Failed to capture exception in Sentry: {e}")
    
    def capture_message(
        self,
        message: str,
        level: str = "info",
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        메시지 캡처 및 Sentry로 전송
        
        Args:
            message: 메시지
            level: 심각도
            context: 추가 컨텍스트
            tags: 태그
        """
        if not self.enabled:
            return
        
        try:
            with self.sentry_sdk.push_scope() as scope:
                # 레벨 설정
                scope.level = level
                
                # 태그 추가
                if tags:
                    for key, value in tags.items():
                        scope.set_tag(key, value)
                
                # 컨텍스트 추가
                if context:
                    scope.set_context("additional_info", context)
                
                # 메시지 캡처
                self.sentry_sdk.capture_message(message, level=level)
                logger.debug(f"Message captured by Sentry: {message[:50]}...")
        
        except Exception as e:
            logger.error(f"Failed to capture message in Sentry: {e}")
    
    def set_user(
        self,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """
        사용자 컨텍스트 설정
        
        Args:
            user_id: 사용자 ID
            email: 이메일
            username: 사용자명
            ip_address: IP 주소
        """
        if not self.enabled:
            return
        
        try:
            self.sentry_sdk.set_user({
                "id": user_id,
                "email": email,
                "username": username,
                "ip_address": ip_address
            })
        except Exception as e:
            logger.error(f"Failed to set user context in Sentry: {e}")
    
    def add_breadcrumb(
        self,
        category: str,
        message: str,
        level: str = "info",
        data: Optional[Dict] = None
    ):
        """
        Breadcrumb 추가 (에러 발생 전 이벤트 추적)
        
        Args:
            category: 카테고리 (http, db, cache, auth 등)
            message: 메시지
            level: 레벨
            data: 추가 데이터
        """
        if not self.enabled:
            return
        
        try:
            self.sentry_sdk.add_breadcrumb(
                category=category,
                message=message,
                level=level,
                data=data or {}
            )
        except Exception as e:
            logger.error(f"Failed to add breadcrumb in Sentry: {e}")
    
    def start_transaction(
        self,
        name: str,
        op: str = "http.server"
    ):
        """
        트랜잭션 시작 (성능 추적)
        
        Args:
            name: 트랜잭션 이름
            op: 작업 타입
            
        Returns:
            트랜잭션 객체
        """
        if not self.enabled:
            return None
        
        try:
            return self.sentry_sdk.start_transaction(name=name, op=op)
        except Exception as e:
            logger.error(f"Failed to start transaction in Sentry: {e}")
            return None
    
    def set_tag(self, key: str, value: str):
        """
        전역 태그 설정
        
        Args:
            key: 태그 키
            value: 태그 값
        """
        if not self.enabled:
            return
        
        try:
            self.sentry_sdk.set_tag(key, value)
        except Exception as e:
            logger.error(f"Failed to set tag in Sentry: {e}")
    
    def set_context(self, name: str, context: Dict[str, Any]):
        """
        전역 컨텍스트 설정
        
        Args:
            name: 컨텍스트 이름
            context: 컨텍스트 데이터
        """
        if not self.enabled:
            return
        
        try:
            self.sentry_sdk.set_context(name, context)
        except Exception as e:
            logger.error(f"Failed to set context in Sentry: {e}")


# 전역 Sentry 서비스 인스턴스
sentry_service = SentryService()


def get_sentry() -> SentryService:
    """전역 Sentry 서비스 반환"""
    return sentry_service
