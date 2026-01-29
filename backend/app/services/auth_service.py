"""
JWT Authentication Service
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from loguru import logger

from app.core.config import settings
from app.models.user import User, UserRole


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """JWT 인증 서비스"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """비밀번호 해싱"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """액세스 토큰 생성"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """토큰 디코딩"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError as e:
            logger.error(f"Token decode error: {e}")
            return None
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """사용자 인증 (username 또는 email)"""
        # username 또는 email로 검색
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return None
        
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"User authenticated: {username}")
        return user
    
    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.VIEWER,
        is_superuser: bool = False
    ) -> User:
        """사용자 생성"""
        hashed_password = AuthService.get_password_hash(password)
        
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_superuser=is_superuser,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User created: {username} (role: {role})")
        return user
    
    @staticmethod
    def has_permission(user: User, required_role: UserRole) -> bool:
        """권한 확인"""
        # Superuser는 모든 권한
        if user.is_superuser:
            return True
        
        # 역할 계층: ADMIN > DISPATCHER > DRIVER > VIEWER
        role_hierarchy = {
            UserRole.ADMIN: 4,
            UserRole.DISPATCHER: 3,
            UserRole.DRIVER: 2,
            UserRole.VIEWER: 1
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
