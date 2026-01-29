"""
보안 미들웨어
Rate Limiting, CORS, 보안 헤더
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
import time
from loguru import logger

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate Limiting 미들웨어
    IP 주소 기반으로 요청 횟수 제한
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 300  # 5분마다 정리
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next):
        # 특정 경로는 Rate Limiting 제외
        exempt_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        if any(request.url.path.startswith(path) for path in exempt_paths):
            return await call_next(request)
        
        # 클라이언트 IP 가져오기
        client_ip = self._get_client_ip(request)
        
        # 현재 시간
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # IP별 요청 기록 정리 (오래된 요청 제거)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        # Rate Limit 확인
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # 요청 기록
        self.requests[client_ip].append(now)
        
        # 주기적으로 메모리 정리
        if time.time() - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_requests()
        
        response = await call_next(request)
        
        # Rate Limit 헤더 추가
        remaining = self.requests_per_minute - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(minutes=1)).timestamp()))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 추출"""
        # X-Forwarded-For 헤더 확인 (프록시 뒤에 있을 경우)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # X-Real-IP 헤더 확인
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 직접 연결된 클라이언트 IP
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self):
        """오래된 요청 기록 정리"""
        minute_ago = datetime.now() - timedelta(minutes=1)
        
        # 오래된 IP 기록 제거
        ips_to_remove = []
        for ip, requests in self.requests.items():
            # 최근 1분 내 요청만 유지
            recent_requests = [req for req in requests if req > minute_ago]
            if recent_requests:
                self.requests[ip] = recent_requests
            else:
                ips_to_remove.append(ip)
        
        # 빈 IP 기록 제거
        for ip in ips_to_remove:
            del self.requests[ip]
        
        self.last_cleanup = time.time()
        logger.debug(f"Cleaned up rate limit records. Active IPs: {len(self.requests)}")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    보안 헤더 미들웨어
    HTTPS, XSS, Clickjacking 등 방어
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # HTTPS 강제 (프로덕션 환경)
        if settings.APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # XSS 방지
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
        )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    요청 로깅 미들웨어
    모든 API 요청을 로깅
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 요청 정보 로깅
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # 요청 처리
        try:
            response = await call_next(request)
            
            # 처리 시간 계산
            process_time = time.time() - start_time
            
            # 응답 정보 로깅
            logger.info(
                f"Response: {response.status_code} "
                f"in {process_time:.3f}s"
            )
            
            # 처리 시간 헤더 추가
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"failed in {process_time:.3f}s: {str(e)}"
            )
            raise


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    입력 검증 미들웨어
    SQL Injection, XSS 공격 패턴 감지
    """
    
    # 위험한 패턴
    DANGEROUS_PATTERNS = [
        # SQL Injection
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        
        # XSS
        r"(<script[^>]*>.*?<\/script>)",
        r"(<iframe[^>]*>)",
        r"(javascript:)",
        r"(on\w+\s*=)",
    ]
    
    async def dispatch(self, request: Request, call_next):
        # POST, PUT, PATCH 요청만 검증
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # 요청 본문 읽기
                body = await request.body()
                body_str = body.decode("utf-8")
                
                # 위험한 패턴 검사
                import re
                for pattern in self.DANGEROUS_PATTERNS:
                    if re.search(pattern, body_str, re.IGNORECASE):
                        logger.warning(
                            f"Suspicious input detected from {request.client.host if request.client else 'unknown'}: "
                            f"Pattern: {pattern[:50]}..."
                        )
                        return JSONResponse(
                            status_code=400,
                            content={"detail": "Invalid input detected"}
                        )
                
                # 원래 요청 본문으로 복원
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request._receive = receive
            
            except Exception as e:
                logger.error(f"Input validation error: {e}")
        
        response = await call_next(request)
        return response


def setup_security_middleware(app):
    """
    보안 미들웨어 설정
    
    Args:
        app: FastAPI 애플리케이션
    """
    # Rate Limiting (분당 60 요청)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    
    # 보안 헤더
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 요청 로깅
    app.add_middleware(RequestLoggingMiddleware)
    
    # 입력 검증 - DISABLED (causes ASGI protocol errors)
    # if settings.APP_ENV == "production":
    #     app.add_middleware(InputValidationMiddleware)
    
    logger.info("✅ Security middleware configured")
