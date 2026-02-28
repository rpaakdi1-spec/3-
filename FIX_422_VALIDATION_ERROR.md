# 422 Validation Error 해결 가이드

## 문제 상황
- 회원가입 시 POST `/api/v1/auth/signup` 요청이 422 Unprocessable Entity 에러 발생
- 프론트엔드에서 email 필드를 제거했지만, 백엔드 `UserBase` 스키마에서는 여전히 필수로 요구

## 해결 방법
`backend/app/schemas/auth.py`의 `UserBase` 클래스에서 `email` 필드를 Optional로 변경:

```python
# Before
email: EmailStr

# After  
email: Optional[EmailStr] = None
```

## 서버 배포 단계

### 1. 최신 코드 가져오기
```bash
cd /root/uvis
git pull origin main
```

### 2. 백엔드 재빌드 및 재시작
```bash
# 백엔드 중지
docker-compose down backend

# 이미지 재빌드 (캐시 없이)
docker-compose build --no-cache backend

# 백엔드 시작
docker-compose up -d backend

# 10초 대기
sleep 10
```

### 3. 상태 확인
```bash
# 컨테이너 상태
docker-compose ps

# 백엔드 로그 (최근 50줄)
docker-compose logs backend | tail -50

# 헬스체크
curl http://139.150.11.99:8000/health
```

**기대 출력:**
```json
{"status":"healthy","app_name":"Cold Chain Dispatch System","environment":"production"}
```

### 4. 회원가입 테스트

1. **프론트엔드 접속**: http://139.150.11.99/
2. **회원가입 페이지 이동**
3. **Step 1 - 계정 정보 입력**:
   - 사용자명: `testuser123`
   - 비밀번호: `test123456`
   - 비밀번호 확인: `test123456`
   - 권한: `DRIVER`
   - ✅ email 필드 없음 (제거됨)

4. **Step 2 - 기본 인적사항**:
   - 이름: `홍길동`
   - 영문명: `Hong Gildong` (선택)
   - 전화번호: `01012345678` → 자동으로 `010-1234-5678` 포맷팅
   - 비상연락처: `01098765432` → 자동으로 `010-9876-5432` 포맷팅
   - 주소: (선택)
   - ✅ 사원번호 필드 없음 (자동 생성: `PENDING_20260228_001`)

5. **Step 3 - 조직/근무 정보**:
   - 직급: `DRIVER`
   - 고용 형태: `FULL_TIME`
   - 부서: (선택)
   - 직책: (선택)
   - 입사일: (기본값: 오늘 날짜)
   - ✅ 근무시간 필드 없음 (제거됨)

6. **Step 4 - 자격증 정보**:
   - 운전면허: (선택)
   - 화물운송자격증: (선택)
   - 지게차 자격: (선택)

7. **가입 완료**:
   - "회원가입이 완료되었습니다..." 토스트 메시지 표시
   - 2초 후 로그인 페이지로 자동 이동

### 5. 승인 테스트

1. **관리자 로그인**: `admin` / `admin123`
2. **설정 → 사용자 관리 → Pending Users** 탭
3. **대기 중인 사용자 확인**:
   - 사용자명: `testuser123`
   - 이름: `홍길동`
   - 자동 생성된 사원번호: `PENDING_20260228_001`
   - 전화번호: `010-1234-5678` (하이픈 포함)
4. **승인 처리**: "Approve" 버튼 클릭
5. **최종 사원번호 부여**: 예) `D001`, `E001` 등
6. **성공 메시지**: "User approved successfully" 토스트

### 6. 데이터베이스 확인 (선택)
```bash
# pending_employees 테이블 확인
docker-compose exec db psql -U uvis_user -d uvis_db -c "
SELECT 
  id, employee_code, name, phone, email, 
  created_at 
FROM pending_employees 
ORDER BY id DESC 
LIMIT 5;
"

# employees 테이블 확인 (승인 후)
docker-compose exec db psql -U uvis_user -d uvis_db -c "
SELECT 
  id, employee_code, name, phone, email, 
  created_at 
FROM employees 
ORDER BY id DESC 
LIMIT 5;
"
```

## 변경 사항 요약

### 백엔드 (`backend/app/schemas/auth.py`)
- ✅ `UserBase.email`: `EmailStr` → `Optional[EmailStr] = None`
- ✅ `SignupRequest.email`: 이미 Optional로 설정됨
- ✅ `SignupRequest.phone`: 12-13자 (하이픈 포함 형식)

### 프론트엔드 (`frontend/src/pages/SignupPage.tsx`)
- ✅ Email 필드 제거
- ✅ 사원번호(employee_code) 필드 제거
- ✅ 전화번호 자동 포맷팅 (`formatPhoneNumber()` 함수)
- ✅ 비상연락처 자동 포맷팅
- ✅ 근무시간 필드 제거 (work_start_time, work_end_time, max_work_hours)

### 백엔드 로직 (`backend/app/api/auth.py`)
- ✅ email이 없으면 `{username}@pending.local` 자동 생성
- ✅ employee_code 자동 생성: `PENDING_YYYYMMDD_XXX` (예: `PENDING_20260228_001`)
- ✅ 전화번호 형식 검증: `###-####-####` (12-13자)

## 커밋 정보
- **Commit**: `8ee6887`
- **Message**: "fix: make email optional in UserBase schema to fix 422 validation error"
- **Date**: 2026-02-28
- **Files Changed**: 
  - `backend/app/schemas/auth.py`
  - `rebuild_backend.sh` (신규 스크립트)

## 트러블슈팅

### 문제 1: 422 에러가 여전히 발생
**원인**: Docker 이미지 캐시 문제
**해결**:
```bash
cd /root/uvis
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

### 문제 2: 전화번호 형식 에러
**원인**: 하이픈 없이 입력
**해결**: 프론트엔드에서 자동 포맷팅되므로 숫자만 입력하면 됨 (예: `01012345678` → `010-1234-5678`)

### 문제 3: email 필드가 여전히 표시됨
**원인**: 프론트엔드 빌드가 안 됨
**해결**:
```bash
docker-compose down frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### 문제 4: 백엔드가 시작되지 않음
**확인 사항**:
```bash
# 로그 확인
docker-compose logs backend | tail -100

# DB 연결 확인
docker-compose exec db pg_isready -U uvis_user

# 포트 확인
netstat -tlnp | grep 8000
```

## 다음 단계
1. ✅ 회원가입 422 에러 해결 완료
2. ✅ Email 선택 사항으로 변경
3. ✅ 사원번호 자동 생성
4. ✅ 전화번호 자동 포맷팅
5. ⏳ 실제 사용자 회원가입 및 승인 테스트
6. ⏳ 엔드투엔드 워크플로우 검증
