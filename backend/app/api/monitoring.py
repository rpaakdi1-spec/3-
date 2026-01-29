"""
모니터링 API

시스템 상태 모니터링 및 알림 관리 엔드포인트:
- 시스템 헬스 체크
- 메트릭 조회
- 알림 조회
- 알림 전송
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.services.monitoring_service import MonitoringService
from app.services.notification_service import NotificationService, NotificationLevel
from pydantic import BaseModel, Field

router = APIRouter()


class AlertRequest(BaseModel):
    """알림 전송 요청"""
    title: str = Field(..., description="알림 제목")
    message: str = Field(..., description="알림 내용")
    level: str = Field(NotificationLevel.INFO, description="알림 레벨")
    channels: List[str] = Field(default=["slack"], description="전송 채널")
    email_recipients: Optional[List[str]] = Field(None, description="이메일 수신자")
    sms_recipients: Optional[List[str]] = Field(None, description="SMS 수신자")


@router.get(
    "/health",
    summary="시스템 헬스 체크",
    description="전체 시스템의 상태를 확인합니다"
)
async def get_system_health(
    db: Session = Depends(get_db)
):
    """
    시스템 헬스 체크
    
    - 데이터베이스 상태
    - 시스템 리소스 (CPU, 메모리, 디스크)
    - 애플리케이션 상태
    
    **상태 코드:**
    - healthy: 정상
    - degraded: 성능 저하
    - unhealthy: 비정상
    """
    health = MonitoringService.get_system_health(db)
    return health


@router.get(
    "/metrics",
    summary="시스템 메트릭 조회",
    description="시스템 성능 및 사용 메트릭을 조회합니다"
)
async def get_system_metrics(
    period_hours: int = Query(24, description="수집 기간 (시간)", ge=1, le=168),
    db: Session = Depends(get_db)
):
    """
    시스템 메트릭 조회
    
    - 주문 메트릭 (총 주문 수, 상태별 분포, 평균 처리 시간)
    - 배차 메트릭 (총 배차 수, 상태별 분포, 평균 거리)
    - 차량 메트릭 (차량 수, 활용률)
    - 시스템 메트릭 (CPU, 메모리, 디스크, 네트워크)
    
    **기간:**
    - 최소: 1시간
    - 최대: 168시간 (7일)
    - 기본: 24시간
    """
    metrics = MonitoringService.get_metrics(db, period_hours)
    return metrics


@router.get(
    "/alerts",
    summary="시스템 알림 조회",
    description="현재 활성화된 시스템 알림을 조회합니다"
)
async def get_system_alerts(
    db: Session = Depends(get_db)
):
    """
    시스템 알림 조회
    
    자동으로 감지된 이상 상황:
    
    **시스템 리소스:**
    - CPU 사용률 높음 (>70%, >90%)
    - 메모리 부족 (>70%, >90%)
    - 디스크 공간 부족 (>90%)
    
    **데이터베이스:**
    - 응답 시간 지연 (>500ms, >1000ms)
    - 연결 실패
    
    **비즈니스 로직:**
    - 배차 대기 주문 많음
    - 차량 활용률 낮음
    - 지연된 배차 발견
    
    **알림 레벨:**
    - info: 정보성 알림
    - warning: 주의 필요
    - critical: 즉시 조치 필요
    """
    alerts = MonitoringService.get_alerts(db)
    return {
        "total": len(alerts),
        "alerts": alerts
    }


@router.post(
    "/notify",
    summary="알림 전송",
    description="지정된 채널로 알림을 전송합니다"
)
async def send_notification(
    request: AlertRequest
):
    """
    알림 전송
    
    - 이메일 (SMTP)
    - SMS (알리고 API)
    - Slack (Webhook)
    
    **알림 레벨:**
    - info: Slack만
    - warning: 이메일 + Slack
    - critical: 모든 채널 (이메일 + SMS + Slack)
    
    **필요 설정 (환경 변수):**
    ```
    # 이메일
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USER=your_email@gmail.com
    SMTP_PASSWORD=your_app_password
    
    # SMS (알리고)
    ALIGO_API_KEY=your_api_key
    ALIGO_USER_ID=your_user_id
    ALIGO_SENDER=01012345678
    
    # Slack
    SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
    ```
    """
    notification_service = NotificationService()
    
    recipients = {}
    if request.email_recipients:
        recipients["email"] = request.email_recipients
    if request.sms_recipients:
        recipients["sms"] = request.sms_recipients
    
    results = notification_service.send_alert(
        title=request.title,
        message=request.message,
        level=request.level,
        channels=request.channels,
        recipients=recipients
    )
    
    return {
        "success": any(results.values()),
        "results": results,
        "message": "알림이 전송되었습니다" if any(results.values()) else "알림 전송 실패"
    }


@router.get(
    "/dashboard",
    summary="대시보드 요약",
    description="모니터링 대시보드용 요약 정보를 조회합니다"
)
async def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    """
    대시보드 요약
    
    - 시스템 헬스
    - 주요 메트릭 (24시간 기준)
    - 활성 알림
    
    프론트엔드 대시보드에서 한 번의 API 호출로 모든 정보를 가져올 수 있습니다.
    """
    # 헬스 체크
    health = MonitoringService.get_system_health(db)
    
    # 메트릭
    metrics = MonitoringService.get_metrics(db, 24)
    
    # 알림
    alerts = MonitoringService.get_alerts(db)
    
    # 알림 레벨별 집계
    alert_counts = {
        "critical": sum(1 for a in alerts if a["level"] == "critical"),
        "warning": sum(1 for a in alerts if a["level"] == "warning"),
        "info": sum(1 for a in alerts if a["level"] == "info")
    }
    
    return {
        "timestamp": health["timestamp"],
        "health": {
            "status": health["status"],
            "database": health["checks"]["database"]["status"],
            "resources": health["checks"]["system_resources"]["status"],
            "application": health["checks"]["application"]["status"]
        },
        "metrics": {
            "orders_24h": metrics["orders"]["total"],
            "active_dispatches": metrics["dispatches"]["by_status"].get("진행중", 0),
            "vehicle_utilization": metrics["vehicles"]["utilization_rate"],
            "cpu_percent": metrics["system"]["cpu"]["percent"],
            "memory_percent": metrics["system"]["memory"]["percent"],
            "disk_percent": metrics["system"]["disk"]["percent"]
        },
        "alerts": {
            "total": len(alerts),
            "by_level": alert_counts,
            "recent": alerts[:5]  # 최근 5개
        }
    }


@router.get(
    "/test/email",
    summary="이메일 테스트",
    description="이메일 전송을 테스트합니다"
)
async def test_email(
    to_email: str = Query(..., description="수신자 이메일")
):
    """
    이메일 전송 테스트
    
    SMTP 설정이 올바른지 확인합니다.
    """
    notification_service = NotificationService()
    
    success = notification_service.send_email(
        to_emails=[to_email],
        subject="[Test] Cold Chain 모니터링 시스템",
        body="""
안녕하세요!

이것은 Cold Chain Dispatch System의 이메일 테스트 메시지입니다.

이 이메일을 받으셨다면 SMTP 설정이 정상적으로 완료된 것입니다.

---
Cold Chain Dispatch System
        """.strip()
    )
    
    return {
        "success": success,
        "message": "이메일이 전송되었습니다" if success else "이메일 전송 실패 (SMTP 설정 확인 필요)"
    }


@router.get(
    "/test/slack",
    summary="Slack 테스트",
    description="Slack 메시지 전송을 테스트합니다"
)
async def test_slack():
    """
    Slack 메시지 전송 테스트
    
    Slack Webhook URL 설정이 올바른지 확인합니다.
    """
    notification_service = NotificationService()
    
    success = notification_service.send_slack(
        title="테스트 메시지",
        message="Cold Chain Dispatch System의 Slack 연동 테스트입니다.",
        level=NotificationLevel.INFO
    )
    
    return {
        "success": success,
        "message": "Slack 메시지가 전송되었습니다" if success else "Slack 전송 실패 (Webhook URL 설정 확인 필요)"
    }


@router.post(
    "/test/alert",
    summary="알림 테스트",
    description="시스템 알림을 테스트합니다"
)
async def test_alert(
    level: str = Query(NotificationLevel.WARNING, description="알림 레벨"),
    channel: str = Query("slack", description="전송 채널")
):
    """
    시스템 알림 테스트
    
    실제 알림과 동일한 형식으로 테스트 알림을 전송합니다.
    """
    notification_service = NotificationService()
    
    test_alert = {
        "level": level,
        "category": "test",
        "title": "테스트 알림",
        "message": f"이것은 {level} 레벨의 테스트 알림입니다.",
        "timestamp": "2026-01-27T22:00:00"
    }
    
    results = notification_service.send_system_alert(
        alert=test_alert,
        admin_emails=["admin@example.com"] if channel == "email" else None
    )
    
    return {
        "success": any(results.values()),
        "results": results,
        "message": "테스트 알림이 전송되었습니다"
    }
