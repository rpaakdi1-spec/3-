"""
구조화된 로깅 서비스
JSON 포맷 로깅, 로그 레벨 관리, 컨텍스트 추가
"""
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from loguru import logger
import traceback
import sys

from app.core.config import settings


class StructuredLogger:
    """구조화된 로거 클래스"""
    
    def __init__(self, service_name: str = "cold-chain-dispatch"):
        self.service_name = service_name
        self.setup_logger()
    
    def setup_logger(self):
        """로거 설정"""
        # 기존 핸들러 제거
        logger.remove()
        
        # 로그 디렉토리 생성
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 콘솔 출력 (컬러, 개발 환경)
        if settings.APP_ENV == "development":
            logger.add(
                sys.stdout,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                       "<level>{level: <8}</level> | "
                       "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                       "<level>{message}</level>",
                level="DEBUG",
                colorize=True
            )
        else:
            # 프로덕션: 간단한 포맷
            logger.add(
                sys.stdout,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
                level="INFO"
            )
        
        # JSON 포맷 파일 로깅 (구조화)
        logger.add(
            log_dir / "app.json",
            format="{message}",
            level="INFO",
            rotation="500 MB",
            retention="30 days",
            compression="zip",
            serialize=True,  # JSON 직렬화
            backtrace=True,
            diagnose=True
        )
        
        # 일반 텍스트 파일 로깅
        logger.add(
            log_dir / "app.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="INFO",
            rotation="500 MB",
            retention="30 days",
            compression="zip"
        )
        
        # 에러 전용 로그
        logger.add(
            log_dir / "error.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation="100 MB",
            retention="60 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        logger.info(f"✅ Logger configured for {self.service_name}")
    
    def log_with_context(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ):
        """
        컨텍스트와 함께 로그 기록
        
        Args:
            level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: 로그 메시지
            context: 추가 컨텍스트 정보
            exception: 예외 객체
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "level": level,
            "message": message,
            "context": context or {}
        }
        
        # 예외 정보 추가
        if exception:
            log_data["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback": traceback.format_exc()
            }
        
        # 환경 정보 추가
        log_data["environment"] = settings.APP_ENV
        
        # 로그 레벨에 따라 기록
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(json.dumps(log_data, ensure_ascii=False))
    
    def debug(self, message: str, **context):
        """디버그 로그"""
        self.log_with_context("DEBUG", message, context)
    
    def info(self, message: str, **context):
        """정보 로그"""
        self.log_with_context("INFO", message, context)
    
    def warning(self, message: str, **context):
        """경고 로그"""
        self.log_with_context("WARNING", message, context)
    
    def error(self, message: str, exception: Optional[Exception] = None, **context):
        """에러 로그"""
        self.log_with_context("ERROR", message, context, exception)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **context):
        """심각한 에러 로그"""
        self.log_with_context("CRITICAL", message, context, exception)
    
    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """
        API 요청 로그
        
        Args:
            method: HTTP 메서드
            path: 요청 경로
            status_code: 응답 상태 코드
            duration: 처리 시간 (초)
            user_id: 사용자 ID
            ip_address: 클라이언트 IP
        """
        self.info(
            f"API Request: {method} {path}",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration * 1000, 2),
            user_id=user_id,
            ip_address=ip_address
        )
    
    def log_database_query(
        self,
        query_type: str,
        table: str,
        duration: float,
        rows_affected: Optional[int] = None
    ):
        """
        데이터베이스 쿼리 로그
        
        Args:
            query_type: 쿼리 타입 (SELECT, INSERT, UPDATE, DELETE)
            table: 테이블 이름
            duration: 실행 시간 (초)
            rows_affected: 영향받은 행 수
        """
        self.debug(
            f"DB Query: {query_type} {table}",
            query_type=query_type,
            table=table,
            duration_ms=round(duration * 1000, 2),
            rows_affected=rows_affected
        )
    
    def log_business_event(
        self,
        event_type: str,
        entity_type: str,
        entity_id: int,
        action: str,
        user_id: Optional[int] = None,
        details: Optional[Dict] = None
    ):
        """
        비즈니스 이벤트 로그
        
        Args:
            event_type: 이벤트 타입 (order_created, dispatch_completed 등)
            entity_type: 엔티티 타입 (order, dispatch, vehicle 등)
            entity_id: 엔티티 ID
            action: 액션 (create, update, delete)
            user_id: 사용자 ID
            details: 상세 정보
        """
        self.info(
            f"Business Event: {event_type}",
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            details=details or {}
        )
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        ip_address: Optional[str] = None,
        user_id: Optional[int] = None,
        details: Optional[Dict] = None
    ):
        """
        보안 이벤트 로그
        
        Args:
            event_type: 이벤트 타입 (failed_login, rate_limit_exceeded 등)
            severity: 심각도 (low, medium, high, critical)
            ip_address: IP 주소
            user_id: 사용자 ID
            details: 상세 정보
        """
        self.warning(
            f"Security Event: {event_type}",
            event_type=event_type,
            severity=severity,
            ip_address=ip_address,
            user_id=user_id,
            details=details or {}
        )
    
    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        tags: Optional[Dict] = None
    ):
        """
        성능 메트릭 로그
        
        Args:
            metric_name: 메트릭 이름
            value: 값
            unit: 단위
            tags: 태그
        """
        self.debug(
            f"Performance Metric: {metric_name}",
            metric_name=metric_name,
            value=value,
            unit=unit,
            tags=tags or {}
        )


# 전역 로거 인스턴스
structured_logger = StructuredLogger()


def get_logger() -> StructuredLogger:
    """전역 로거 반환"""
    return structured_logger
