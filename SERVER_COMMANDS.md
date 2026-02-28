# 서버 직접 실행 명령어 모음

## 1️⃣ Admin 계정 복원 (가장 중요!)

```bash
cd /root/uvis

docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()

# 기존 admin 확인
admin = db.query(User).filter(User.username == 'admin').first()

if admin:
    print('✅ Admin 계정이 이미 존재합니다.')
    print(f'   ID: {admin.id}, Email: {admin.email}, Active: {admin.is_active}')
else:
    print('⚠️ Admin 계정을 생성합니다...')
    admin = User(
        username='admin',
        email='admin@uvis.com',
        hashed_password=get_password_hash('admin123'),
        full_name='System Administrator',
        phone='010-0000-0000',
        role=UserRole.ADMIN,
        is_active=True,
        is_superuser=True,
        approval_status='approved'
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f'✅ Admin 계정 생성 완료!')
    print(f'   ID: {admin.id}')
    print(f'   Username: {admin.username}')
    print(f'   Email: {admin.email}')

db.close()
"
```

## 2️⃣ Admin 로그인 테스트

```bash
curl -X POST http://139.150.11.99/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## 3️⃣ 백엔드 스키마 확인 (email 필드가 Optional인지)

```bash
docker compose exec backend cat /app/backend/app/schemas/auth.py | grep -A 5 "class UserBase"
```

## 4️⃣ 회원가입 API 직접 테스트

```bash
curl -v -X POST http://139.150.11.99/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser01",
    "password": "test123456",
    "role": "DRIVER",
    "name": "홍길동",
    "phone": "010-1234-5678",
    "employee_role": "DRIVER",
    "employment_type": "FULL_TIME",
    "hire_date": "2026-02-28",
    "has_cargo_license": false,
    "can_drive_forklift": false,
    "has_forklift_certificate": false
  }'
```

## 5️⃣ 백엔드 로그 확인 (422 에러 상세)

```bash
docker compose logs backend --tail=100 | grep -A 20 "422\|validation\|error"
```

## 6️⃣ 데이터베이스 상태 확인

```bash
# Users 테이블 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "SELECT id, username, email, role, is_active, approval_status FROM users;"

# Pending employees 테이블 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "SELECT COUNT(*) FROM pending_employees;"

# 테이블 목록
docker compose exec db psql -U uvis_user -d uvis_db -c "\dt"
```

## 7️⃣ 백엔드 완전 재빌드 (필요 시)

```bash
cd /root/uvis
docker compose down backend
docker compose build --no-cache backend
docker compose up -d backend
sleep 15
docker compose logs backend --tail=50
curl http://139.150.11.99/api/v1/health
```

---

## 실행 순서

1. **먼저 Admin 계정 복원** (위 1번 명령어)
2. **Admin 로그인 테스트** (위 2번 명령어)
3. **백엔드 스키마 확인** (위 3번 명령어)
4. **회원가입 API 테스트** (위 4번 명령어)
5. **에러 로그 확인** (위 5번 명령어)

---

## 예상 결과

### 1번 명령어 성공 시:
```
⚠️ Admin 계정을 생성합니다...
✅ Admin 계정 생성 완료!
   ID: 1
   Username: admin
   Email: admin@uvis.com
```

### 2번 명령어 성공 시:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@uvis.com",
    ...
  }
}
```

### 3번 명령어 기대 출력:
```python
class UserBase(BaseModel):
    """사용자 기본 스키마"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None  # ← 이것이 있어야 함!
```

### 4번 명령어 성공 시:
```json
{
  "id": 2,
  "username": "testuser01",
  "email": "testuser01@pending.local",
  ...
}
```

---

**위 명령어들을 순서대로 실행하고 결과를 알려주세요!**
