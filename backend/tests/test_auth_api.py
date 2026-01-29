"""
인증 API 테스트
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAuthAPI:
    """인증 API 테스트 클래스"""
    
    def test_register_user(self, client: TestClient):
        """사용자 등록 테스트"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
    
    def test_register_duplicate_username(self, client: TestClient, test_user):
        """중복 사용자명 등록 실패 테스트"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "another@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400
    
    def test_login_success(self, client: TestClient, test_user):
        """로그인 성공 테스트"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client: TestClient, test_user):
        """잘못된 비밀번호 로그인 실패 테스트"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client: TestClient):
        """존재하지 않는 사용자 로그인 실패 테스트"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient, auth_headers):
        """현재 사용자 정보 조회 테스트"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """인증 없이 사용자 정보 조회 실패 테스트"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """잘못된 토큰으로 사용자 정보 조회 실패 테스트"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401


@pytest.mark.database
class TestAuthDatabase:
    """인증 데이터베이스 테스트"""
    
    def test_password_hashing(self, db: Session):
        """비밀번호 해싱 테스트"""
        from app.models.user import User
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        password = "testpassword123"
        hashed = pwd_context.hash(password)
        
        assert hashed != password
        assert pwd_context.verify(password, hashed)
    
    def test_user_creation(self, db: Session):
        """사용자 생성 테스트"""
        from app.models.user import User
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        user = User(
            username="testuser2",
            email="test2@example.com",
            hashed_password=pwd_context.hash("password123"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser2"
        assert user.email == "test2@example.com"
        assert user.is_active is True
