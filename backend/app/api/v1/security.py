"""
Security API Endpoints (2FA, Audit Log)
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from loguru import logger

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.two_factor_auth_service import TwoFactorAuthService
from app.services.audit_log_service import AuditLogService, SecurityAlertService


router = APIRouter()


# Request/Response Models
class Enable2FARequest(BaseModel):
    pass


class Verify2FARequest(BaseModel):
    code: str  # 6-digit TOTP code or backup code


class VerifyBackupCodeRequest(BaseModel):
    backup_code: str


# 2FA Endpoints
@router.post("/2fa/enable")
async def enable_2fa(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    2FA 활성화
    
    Returns QR code and backup codes
    """
    try:
        two_factor_service = TwoFactorAuthService(db)
        
        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        secret, backup_codes, qr_code_base64 = two_factor_service.enable_2fa(
            user=current_user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Audit log
        audit_service = AuditLogService(db)
        audit_service.log_action(
            action="enable_2fa",
            user=current_user,
            ip_address=ip_address,
            status="success"
        )
        
        return {
            "status": "success",
            "message": "2FA enabled successfully",
            "data": {
                "qr_code": qr_code_base64,
                "backup_codes": backup_codes,
                "secret": secret  # For manual entry
            }
        }
    
    except Exception as e:
        logger.error(f"Error enabling 2FA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/2fa/disable")
async def disable_2fa(
    request: Request,
    verify_request: Verify2FARequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    2FA 비활성화 (TOTP 코드로 검증 필요)
    """
    try:
        two_factor_service = TwoFactorAuthService(db)
        
        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Verify TOTP code
        is_valid = two_factor_service.verify_totp(
            user=current_user,
            code=verify_request.code,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid 2FA code")
        
        # Disable 2FA
        two_factor_service.disable_2fa(
            user=current_user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Audit log
        audit_service = AuditLogService(db)
        audit_service.log_action(
            action="disable_2fa",
            user=current_user,
            ip_address=ip_address,
            status="success"
        )
        
        return {
            "status": "success",
            "message": "2FA disabled successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling 2FA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/2fa/verify")
async def verify_2fa(
    request: Request,
    verify_request: Verify2FARequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """TOTP 코드 검증"""
    try:
        two_factor_service = TwoFactorAuthService(db)
        
        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        is_valid = two_factor_service.verify_totp(
            user=current_user,
            code=verify_request.code,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid 2FA code")
        
        return {
            "status": "success",
            "message": "2FA verification successful"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying 2FA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/2fa/status")
async def get_2fa_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """2FA 상태 조회"""
    try:
        two_factor_service = TwoFactorAuthService(db)
        
        is_enabled = two_factor_service.is_2fa_enabled(current_user)
        backup_codes_count = two_factor_service.get_backup_codes_count(current_user)
        
        return {
            "status": "success",
            "data": {
                "is_enabled": is_enabled,
                "backup_codes_remaining": backup_codes_count
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting 2FA status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Audit Log Endpoints
@router.get("/audit-logs/me")
async def get_my_audit_logs(
    limit: int = 100,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """내 감사 로그 조회"""
    try:
        audit_service = AuditLogService(db)
        logs = audit_service.get_user_audit_logs(
            user_id=current_user.id,
            limit=limit,
            action=action
        )
        
        return {
            "status": "success",
            "data": [
                {
                    "id": log.id,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "status": log.status,
                    "ip_address": log.ip_address,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit-logs/user/{user_id}")
async def get_user_audit_logs(
    user_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자 감사 로그 조회 (관리자 only)"""
    # Only admins can view other users' logs
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        audit_service = AuditLogService(db)
        logs = audit_service.get_user_audit_logs(
            user_id=user_id,
            limit=limit
        )
        
        return {
            "status": "success",
            "data": [
                {
                    "id": log.id,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "status": log.status,
                    "ip_address": log.ip_address,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting user audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Security Alert Endpoints
@router.get("/security-alerts")
async def get_security_alerts(
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """보안 알림 조회 (관리자 only)"""
    # Only admins can view security alerts
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        alert_service = SecurityAlertService(db)
        alerts = alert_service.get_unresolved_alerts(
            severity=severity,
            limit=limit
        )
        
        return {
            "status": "success",
            "data": [
                {
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "description": alert.description,
                    "user_id": alert.user_id,
                    "ip_address": alert.ip_address,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in alerts
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting security alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/security-alerts/{alert_id}/resolve")
async def resolve_security_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """보안 알림 해결 (관리자 only)"""
    # Only admins can resolve security alerts
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        alert_service = SecurityAlertService(db)
        success = alert_service.resolve_alert(
            alert_id=alert_id,
            resolver=current_user
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "status": "success",
            "message": "Security alert resolved"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving security alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))
