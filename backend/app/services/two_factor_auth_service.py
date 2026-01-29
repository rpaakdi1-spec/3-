"""
Two-Factor Authentication Service
"""

import pyotp
import qrcode
import io
import base64
import secrets
import json
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from loguru import logger

from app.models.security import TwoFactorAuth, TwoFactorLog
from app.models.user import User


class TwoFactorAuthService:
    """2FA 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_secret(self) -> str:
        """2FA 시크릿 키 생성"""
        return pyotp.random_base32()
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """백업 코드 생성"""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    def enable_2fa(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[str, List[str], str]:
        """
        2FA 활성화
        
        Returns:
            (secret_key, backup_codes, qr_code_base64)
        """
        # 시크릿 키 생성
        secret = self.generate_secret()
        
        # 백업 코드 생성
        backup_codes = self.generate_backup_codes()
        
        # 기존 2FA 설정 확인
        existing_2fa = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user.id
        ).first()
        
        if existing_2fa:
            # 업데이트
            existing_2fa.secret_key = secret
            existing_2fa.backup_codes = json.dumps(backup_codes)
            existing_2fa.is_enabled = True
            existing_2fa.last_used_at = datetime.utcnow()
        else:
            # 새로 생성
            two_factor_auth = TwoFactorAuth(
                user_id=user.id,
                secret_key=secret,
                backup_codes=json.dumps(backup_codes),
                is_enabled=True
            )
            self.db.add(two_factor_auth)
        
        # 로그 저장
        log = TwoFactorLog(
            user_id=user.id,
            action="enabled",
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )
        self.db.add(log)
        
        self.db.commit()
        
        # QR 코드 생성
        qr_code_base64 = self._generate_qr_code(user, secret)
        
        logger.info(f"2FA enabled for user {user.id}")
        
        return secret, backup_codes, qr_code_base64
    
    def disable_2fa(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """2FA 비활성화"""
        two_factor_auth = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user.id
        ).first()
        
        if not two_factor_auth:
            return False
        
        two_factor_auth.is_enabled = False
        
        # 로그 저장
        log = TwoFactorLog(
            user_id=user.id,
            action="disabled",
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )
        self.db.add(log)
        
        self.db.commit()
        
        logger.info(f"2FA disabled for user {user.id}")
        
        return True
    
    def verify_totp(
        self,
        user: User,
        code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        TOTP 코드 검증
        
        Args:
            user: 사용자
            code: 6자리 TOTP 코드
            
        Returns:
            검증 성공 여부
        """
        two_factor_auth = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user.id,
            TwoFactorAuth.is_enabled == True
        ).first()
        
        if not two_factor_auth:
            return False
        
        # TOTP 객체 생성
        totp = pyotp.TOTP(two_factor_auth.secret_key)
        
        # 코드 검증 (30초 윈도우)
        is_valid = totp.verify(code, valid_window=1)
        
        # 로그 저장
        log = TwoFactorLog(
            user_id=user.id,
            action="verified",
            ip_address=ip_address,
            user_agent=user_agent,
            success=is_valid
        )
        self.db.add(log)
        
        if is_valid:
            two_factor_auth.last_used_at = datetime.utcnow()
        
        self.db.commit()
        
        if is_valid:
            logger.info(f"2FA verification successful for user {user.id}")
        else:
            logger.warning(f"2FA verification failed for user {user.id}")
        
        return is_valid
    
    def verify_backup_code(
        self,
        user: User,
        backup_code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        백업 코드 검증 (일회용)
        
        Args:
            user: 사용자
            backup_code: 백업 코드
            
        Returns:
            검증 성공 여부
        """
        two_factor_auth = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user.id,
            TwoFactorAuth.is_enabled == True
        ).first()
        
        if not two_factor_auth or not two_factor_auth.backup_codes:
            return False
        
        # 백업 코드 리스트 파싱
        backup_codes = json.loads(two_factor_auth.backup_codes)
        
        # 백업 코드 검증
        backup_code_upper = backup_code.upper()
        
        if backup_code_upper in backup_codes:
            # 백업 코드 제거 (일회용)
            backup_codes.remove(backup_code_upper)
            two_factor_auth.backup_codes = json.dumps(backup_codes)
            two_factor_auth.last_used_at = datetime.utcnow()
            
            # 로그 저장
            log = TwoFactorLog(
                user_id=user.id,
                action="backup_code_used",
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )
            self.db.add(log)
            
            self.db.commit()
            
            logger.info(f"Backup code used for user {user.id}")
            return True
        else:
            # 로그 저장
            log = TwoFactorLog(
                user_id=user.id,
                action="backup_code_failed",
                ip_address=ip_address,
                user_agent=user_agent,
                success=False
            )
            self.db.add(log)
            self.db.commit()
            
            logger.warning(f"Invalid backup code for user {user.id}")
            return False
    
    def is_2fa_enabled(self, user: User) -> bool:
        """2FA 활성화 여부 확인"""
        two_factor_auth = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user.id,
            TwoFactorAuth.is_enabled == True
        ).first()
        
        return two_factor_auth is not None
    
    def get_backup_codes_count(self, user: User) -> int:
        """남은 백업 코드 개수"""
        two_factor_auth = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user.id
        ).first()
        
        if not two_factor_auth or not two_factor_auth.backup_codes:
            return 0
        
        backup_codes = json.loads(two_factor_auth.backup_codes)
        return len(backup_codes)
    
    def _generate_qr_code(self, user: User, secret: str) -> str:
        """
        QR 코드 생성 (Base64 인코딩)
        
        Returns:
            Base64 인코딩된 QR 코드 이미지
        """
        # TOTP URI 생성
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email or user.username,
            issuer_name="Cold Chain Dispatch"
        )
        
        # QR 코드 생성
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 이미지를 Base64로 인코딩
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
