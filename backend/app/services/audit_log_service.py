"""
Audit Logging Service
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger
import json

from app.models.security import AuditLog, SecurityAlert
from app.models.user import User


class AuditLogService:
    """감사 로그 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        action: str,
        user: Optional[User] = None,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success"
    ):
        """
        액션 로그 기록
        
        Args:
            action: 액션 타입 (login, logout, create_order, delete_dispatch, etc.)
            user: 사용자 객체
            user_id: 사용자 ID (user가 없을 때)
            resource_type: 리소스 타입 (order, dispatch, user, etc.)
            resource_id: 리소스 ID
            details: 추가 세부 정보 (JSON)
            ip_address: IP 주소
            user_agent: User Agent
            status: 상태 (success, failed, blocked)
        """
        try:
            audit_log = AuditLog(
                user_id=user.id if user else user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=json.dumps(details) if details else None,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status
            )
            
            self.db.add(audit_log)
            self.db.commit()
            
            logger.info(
                f"Audit log: {action} by user {user.id if user else user_id} "
                f"on {resource_type}:{resource_id} - {status}"
            )
        
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            self.db.rollback()
    
    def log_login(
        self,
        user: User,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """로그인 로그"""
        self.log_action(
            action="login",
            user=user,
            status="success" if success else "failed",
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_logout(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """로그아웃 로그"""
        self.log_action(
            action="logout",
            user=user,
            status="success",
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_create(
        self,
        user: User,
        resource_type: str,
        resource_id: int,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """생성 로그"""
        self.log_action(
            action=f"create_{resource_type}",
            user=user,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            status="success"
        )
    
    def log_update(
        self,
        user: User,
        resource_type: str,
        resource_id: int,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """수정 로그"""
        self.log_action(
            action=f"update_{resource_type}",
            user=user,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            status="success"
        )
    
    def log_delete(
        self,
        user: User,
        resource_type: str,
        resource_id: int,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """삭제 로그"""
        self.log_action(
            action=f"delete_{resource_type}",
            user=user,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            status="success"
        )
    
    def get_user_audit_logs(
        self,
        user_id: int,
        limit: int = 100,
        action: Optional[str] = None
    ):
        """사용자의 감사 로그 조회"""
        query = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        )
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    def get_resource_audit_logs(
        self,
        resource_type: str,
        resource_id: int,
        limit: int = 100
    ):
        """리소스의 감사 로그 조회"""
        return self.db.query(AuditLog).filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()


class SecurityAlertService:
    """보안 알림 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.brute_force_threshold = 5  # 5번 실패 시 알림
        self.time_window_minutes = 15  # 15분 내
    
    def create_alert(
        self,
        alert_type: str,
        severity: str,
        description: str,
        user: Optional[User] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """보안 알림 생성"""
        try:
            alert = SecurityAlert(
                user_id=user.id if user else user_id,
                alert_type=alert_type,
                severity=severity,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(alert)
            self.db.commit()
            
            logger.warning(
                f"Security alert [{severity}]: {alert_type} - {description}"
            )
            
            return alert
        
        except Exception as e:
            logger.error(f"Failed to create security alert: {e}")
            self.db.rollback()
            return None
    
    def check_brute_force(
        self,
        user_id: int,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Brute force 공격 감지
        
        Returns:
            True if brute force detected
        """
        from datetime import timedelta
        
        # 최근 15분 내 실패한 로그인 시도 확인
        time_threshold = datetime.utcnow() - timedelta(minutes=self.time_window_minutes)
        
        failed_attempts = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == "login",
            AuditLog.status == "failed",
            AuditLog.created_at >= time_threshold
        ).count()
        
        if failed_attempts >= self.brute_force_threshold:
            # 보안 알림 생성
            self.create_alert(
                alert_type="brute_force",
                severity="high",
                description=f"Brute force attack detected: {failed_attempts} failed login attempts in {self.time_window_minutes} minutes",
                user_id=user_id,
                ip_address=ip_address
            )
            
            return True
        
        return False
    
    def check_suspicious_login(
        self,
        user: User,
        ip_address: str,
        user_agent: str
    ) -> bool:
        """
        의심스러운 로그인 감지 (새로운 IP/디바이스)
        
        Returns:
            True if suspicious login detected
        """
        from datetime import timedelta
        
        # 최근 30일 내 로그인 이력 확인
        time_threshold = datetime.utcnow() - timedelta(days=30)
        
        previous_logins = self.db.query(AuditLog).filter(
            AuditLog.user_id == user.id,
            AuditLog.action == "login",
            AuditLog.status == "success",
            AuditLog.created_at >= time_threshold
        ).all()
        
        # 이전 로그인과 IP/User Agent 비교
        known_ips = set(log.ip_address for log in previous_logins if log.ip_address)
        
        if ip_address not in known_ips and len(known_ips) > 0:
            # 새로운 IP에서 로그인 시도
            self.create_alert(
                alert_type="suspicious_login",
                severity="medium",
                description=f"Login from new IP address: {ip_address}",
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return True
        
        return False
    
    def resolve_alert(
        self,
        alert_id: int,
        resolver: User
    ) -> bool:
        """보안 알림 해결"""
        alert = self.db.query(SecurityAlert).filter(
            SecurityAlert.id == alert_id
        ).first()
        
        if not alert:
            return False
        
        alert.is_resolved = True
        alert.resolved_by = resolver.id
        alert.resolved_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Security alert {alert_id} resolved by user {resolver.id}")
        
        return True
    
    def get_unresolved_alerts(
        self,
        severity: Optional[str] = None,
        limit: int = 100
    ):
        """미해결 보안 알림 조회"""
        query = self.db.query(SecurityAlert).filter(
            SecurityAlert.is_resolved == False
        )
        
        if severity:
            query = query.filter(SecurityAlert.severity == severity)
        
        return query.order_by(SecurityAlert.created_at.desc()).limit(limit).all()
