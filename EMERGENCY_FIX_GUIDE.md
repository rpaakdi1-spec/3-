# 🚨 긴급 문제 해결 가이드

## 문제 상황
1. ❌ POST `/api/v1/auth/signup` → 422 Unprocessable Entity
2. ❌ Admin 로그인 실패
3. ⚠️ 데이터베이스가 초기화되어 모든 사용자 데이터 삭제된 것으로 추정

## 🔍 진단 단계

### 1단계: 문제 확인
서버에서 다음 명령어 실행:

```bash
bash /tmp/check_backend_detailed.sh
```

이 스크립트는 다음을 확인합니다:
- 백엔드 로그에서 422 에러 상세 내용
- Admin 계정 존재 여부
- 전체 사용자 수
- Users 테이블 스키마

### 2단계: Admin 계정 복원
```bash
bash /tmp/restore_initial_data.sh
```

이 스크립트는:
- Admin 계정 존재 확인
- 없으면 자동 생성 (`admin` / `admin123`)
- 생성 후 로그인 테스트

### 3단계: 회원가입 API 테스트
```bash
bash /tmp/test_signup_api.sh
```

이 스크립트는:
- 헬스체크 확인
- 실제 회원가입 요청 전송
- 422 에러 상세 내용 확인
- 백엔드 로그 분석

---

## 🛠️ 수동 복구 방법

### Admin 계정 수동 생성
```bash
cd /root/uvis

docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()

# 기존 admin 삭제 (있다면)
db.query(User).filter(User.username == 'admin').delete()

# Admin 계정 생성
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
print(f'✅ Admin 계정 생성: ID={admin.id}')
db.close()
"
```

### Admin 로그인 테스트
```bash
curl -X POST http://139.150.11.99/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**기대 출력**: `{"access_token":"...", "token_type":"bearer", "user":{...}}`

---

## 🔍 422 에러 원인 분석

### 가능한 원인

#### 1. 백엔드가 이전 코드 실행 중
**확인**:
```bash
docker compose exec backend cat /app/backend/app/schemas/auth.py | grep -A 2 "class UserBase"
```

**기대**:
```python
class UserBase(BaseModel):
    """사용자 기본 스키마"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None  # ← 이것이 있어야 함
```

**문제**: `email: EmailStr` (Optional 없음)로 되어 있다면 이미지 재빌드 필요

**해결**:
```bash
cd /root/uvis
docker compose down backend
docker compose build --no-cache backend
docker compose up -d backend
sleep 10
docker compose logs backend --tail=30
```

#### 2. 프론트엔드가 잘못된 데이터 전송
**확인**: 브라우저 개발자 도구 (F12) → Network 탭 → signup 요청 → Payload 확인

**문제 사항**:
- `email` 필드가 포함되어 있는가?
- `phone` 형식이 맞는가? (12-13자, 하이픈 포함)
- 필수 필드가 누락되었는가?

#### 3. 데이터베이스 스키마 문제
**확인**:
```bash
docker compose exec db psql -U uvis_user -d uvis_db -c "\d pending_employees"
```

**문제**: 테이블이 없거나 컬럼이 누락된 경우

**해결** (테이블 재생성):
```bash
docker compose exec backend python -c "
from app.models.base import Base
from app.core.database import engine
import app.models

print('Creating tables...')
Base.metadata.create_all(bind=engine)
print('✅ Done')
"
```

---

## 📊 상세 진단 명령어

### 백엔드 로그 실시간 모니터링
```bash
docker compose logs -f backend
```

그리고 별도 터미널에서 회원가입 시도

### 데이터베이스 상태 확인
```bash
# 모든 테이블 목록
docker compose exec db psql -U uvis_user -d uvis_db -c "\dt"

# Users 테이블 데이터
docker compose exec db psql -U uvis_user -d uvis_db -c "SELECT * FROM users;"

# Pending employees 테이블 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "SELECT * FROM pending_employees;"

# Alembic 버전 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "SELECT * FROM alembic_version;"
```

### 백엔드 상태 확인
```bash
# 헬스체크
curl http://139.150.11.99/api/v1/health

# API 문서 확인
curl http://139.150.11.99/docs

# 스키마 확인
docker compose exec backend cat /app/backend/app/schemas/auth.py | head -50
```

---

## 🚀 완전 재시작 프로세스

데이터베이스를 완전히 초기화하고 처음부터 다시 시작:

```bash
cd /root/uvis

# 1. 모든 컨테이너 중지 및 볼륨 삭제
docker compose down -v

# 2. 데이터베이스 볼륨 확인 및 삭제
docker volume ls | grep uvis
docker volume rm uvis_postgres_data

# 3. 컨테이너 재시작 (DB 먼저)
docker compose up -d db redis
sleep 20

# 4. 데이터베이스 초기화 확인
docker compose exec db pg_isready -U uvis_user

# 5. 테이블 생성
docker compose exec backend python -c "
from app.models.base import Base
from app.core.database import engine
import app.models
Base.metadata.create_all(bind=engine)
print('✅ Tables created')
"

# 6. Alembic 스탬프
docker compose exec backend alembic stamp head

# 7. Admin 계정 생성
bash /tmp/restore_initial_data.sh

# 8. 나머지 서비스 시작
docker compose up -d backend frontend minio

# 9. 상태 확인
sleep 10
docker compose ps
curl http://139.150.11.99/api/v1/health
```

---

## 📝 체크리스트

### 진단
- [ ] `bash /tmp/check_backend_detailed.sh` 실행
- [ ] 422 에러 상세 내용 확인
- [ ] Admin 계정 존재 여부 확인
- [ ] Users 테이블 스키마 확인

### 복구
- [ ] `bash /tmp/restore_initial_data.sh` 실행
- [ ] Admin 계정 생성 확인
- [ ] Admin 로그인 테스트 성공

### 테스트
- [ ] `bash /tmp/test_signup_api.sh` 실행
- [ ] 422 에러 원인 파악
- [ ] 백엔드 로그 분석

### 해결
- [ ] 문제 원인 식별
- [ ] 적절한 해결 방법 적용
- [ ] 회원가입 성공 확인
- [ ] Admin 로그인 성공 확인

---

## 🆘 긴급 연락

위 방법으로 해결되지 않으면 다음 정보를 제공해 주세요:

1. `/tmp/check_backend_detailed.sh` 출력 결과
2. `/tmp/test_signup_api.sh` 출력 결과
3. 백엔드 전체 로그: `docker compose logs backend > backend.log`
4. 브라우저 개발자 도구 (F12) → Network 탭 → signup 요청의 Payload 스크린샷

---

## 다음 단계

**즉시 실행**:
```bash
# 서버에서 순서대로 실행
bash /tmp/check_backend_detailed.sh
bash /tmp/restore_initial_data.sh
bash /tmp/test_signup_api.sh
```

**결과를 공유해 주시면 정확한 해결 방법을 제시하겠습니다!**
