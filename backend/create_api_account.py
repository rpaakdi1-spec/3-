#!/usr/bin/env python3
"""
외부 앱 전용 API 계정 생성 스크립트
서버에서 실행: docker compose exec backend python3 /app/create_api_account.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from datetime import datetime, timedelta

# ============================================================
# ✏️ 여기를 수정하세요 (외부 앱 전용 계정 정보)
# ============================================================
API_ACCOUNT = {
    "username":  "cargo_api",           # 로그인 ID
    "password":  "CargoApp!2026",       # 비밀번호 (강력한 비밀번호 권장)
    "full_name": "화물운송앱 API계정",   # 계정 이름
    "email":     "cargo-api@rhkdtls.cloud",  # 이메일
    "role":      UserRole.VIEWER,       # VIEWER = 업로드만 가능, 읽기 전용
}
# ============================================================


def create_api_account():
    db: Session = SessionLocal()
    try:
        # 중복 체크
        existing = db.query(User).filter(
            (User.username == API_ACCOUNT["username"]) |
            (User.email    == API_ACCOUNT["email"])
        ).first()

        if existing:
            print(f"\n⚠️  이미 존재하는 계정입니다: {existing.username}")
            print(f"   계정 ID     : {existing.id}")
            print(f"   역할        : {existing.role}")
            print(f"   활성 상태   : {existing.is_active}")
            print(f"   승인 상태   : {existing.approval_status}")
            return existing

        # 계정 생성
        user = User(
            username        = API_ACCOUNT["username"],
            email           = API_ACCOUNT["email"],
            hashed_password = AuthService.get_password_hash(API_ACCOUNT["password"]),
            full_name       = API_ACCOUNT["full_name"],
            role            = API_ACCOUNT["role"],
            is_active       = True,
            is_superuser    = False,
            approval_status = "approved",   # 승인 완료 상태로 바로 생성
            approved_at     = datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"\n✅ API 계정 생성 완료!")
        print(f"   계정 ID     : {user.id}")
        print(f"   사용자명    : {user.username}")
        print(f"   이메일      : {user.email}")
        print(f"   역할        : {user.role}")
        print(f"   승인 상태   : {user.approval_status}")
        return user

    except Exception as e:
        db.rollback()
        print(f"\n❌ 계정 생성 실패: {e}")
        raise
    finally:
        db.close()


def generate_token(username: str, password: str):
    """계정 생성 후 즉시 토큰 발급 테스트"""
    db: Session = SessionLocal()
    try:
        user = AuthService.authenticate_user(db, username, password)
        if not user:
            print("\n❌ 토큰 발급 실패: 인증 오류")
            return None

        token = AuthService.create_access_token(
            data={"sub": user.username, "role": user.role.value},
            expires_delta=timedelta(minutes=1440)  # 24시간
        )
        return token
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 55)
    print("  외부 앱 전용 API 계정 생성")
    print("=" * 55)

    user = create_api_account()

    if user:
        print("\n🔑 토큰 발급 테스트 중...")
        token = generate_token(API_ACCOUNT["username"], API_ACCOUNT["password"])

        if token:
            print(f"\n✅ 토큰 발급 성공! (24시간 유효)")
            print("\n" + "=" * 55)
            print("  다른 앱 개발팀에 전달할 정보")
            print("=" * 55)
            print(f"\n📌 로그인 URL (토큰 발급)")
            print(f"   POST https://www.rhkdtls.cloud/api/v1/auth/login")
            print(f"\n📌 계정 정보")
            print(f"   username : {API_ACCOUNT['username']}")
            print(f"   password : {API_ACCOUNT['password']}")
            print(f"\n📌 이미지 업로드 URL")
            print(f"   POST https://www.rhkdtls.cloud/api/v1/files/upload-image")
            print(f"\n📌 요청 예시 (curl)")
            print(f"""
  # 1단계: 로그인 → 토큰 발급
  curl -X POST https://www.rhkdtls.cloud/api/v1/auth/login \\
    -H "Content-Type: application/x-www-form-urlencoded" \\
    -d "username={API_ACCOUNT['username']}&password={API_ACCOUNT['password']}"

  # 응답 예시:
  # {{"access_token": "eyJ...", "token_type": "bearer"}}

  # 2단계: 이미지 업로드
  curl -X POST https://www.rhkdtls.cloud/api/v1/files/upload-image \\
    -H "Authorization: Bearer {{access_token}}" \\
    -F "file=@/path/to/image.jpg" \\
    -F "folder=cargo-images"

  # 응답 예시:
  # {{"success": true, "url": "https://...", "key": "cargo-images/..."}}
""")
            print("=" * 55)
        else:
            print("\n❌ 토큰 발급 실패 - 계정을 확인해주세요")
