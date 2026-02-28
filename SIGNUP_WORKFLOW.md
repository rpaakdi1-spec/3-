# 회원가입 승인 워크플로우 기능

## 개요

인사카드 시스템과 연동된 회원가입 및 관리자 승인 워크플로우를 구현했습니다.

## 주요 기능

### 1. 회원가입 (Public Signup)

- **공개 회원가입 페이지** (`/signup`)
  - 로그인 화면에서 "회원가입" 링크로 접근
  - 인사카드에 등록된 직원 정보로 검증
  - 필수 입력 항목:
    - 사용자명 (3자 이상)
    - 직원번호 (인사카드에서 확인)
    - 이름 (인사카드 이름과 일치 필요)
    - 전화번호 (인사카드 번호와 일치 필요)
    - 이메일
    - 비밀번호 (6자 이상)
    - 권한 선택 (운전사원/차량관리부/운영부)

- **인사카드 연동 검증**
  - 직원번호로 Employee 테이블 검색
  - 입력한 이름과 전화번호가 일치해야 함
  - 일치하지 않으면 가입 불가

### 2. 승인 대기 상태

- 회원가입 후 `approval_status = 'pending'` 상태로 생성
- `is_active = false`로 설정되어 로그인 불가
- 관리자 승인 후 활성화

### 3. 관리자 승인/거부

- **권한**
  - 총괄관리자 (MASTER) 또는 운영부 (ADMIN)만 승인/거부 가능

- **승인 대기 목록**
  - 설정 → 회원관리 페이지 상단에 표시
  - 사용자명, 이름, 이메일, 전화번호, 권한, 직원번호, 신청일 표시
  - 승인/거부 버튼 제공

- **승인 처리**
  - `approval_status = 'approved'`
  - `is_active = true` (로그인 가능)
  - `approved_by`, `approved_at` 기록

- **거부 처리**
  - `approval_status = 'rejected'`
  - `is_active = false` (로그인 불가)
  - 거부 사유 입력 가능 (선택사항)

### 4. 역할 구분

새로운 UserRole enum:

| Role | 한국어 | 설명 |
|------|--------|------|
| MASTER | 총괄관리자 | 최상위 권한, 모든 기능 사용 가능 |
| ADMIN | 운영부 | 운영 관리, 사용자 승인 가능 |
| VEHICLE_MANAGER | 차량관리부 | 차량 및 배차 관리 |
| DRIVER | 운전사원 | 운전 업무 관련 기능 |
| VIEWER | 조회자 | 읽기 전용 권한 |

## 데이터베이스 스키마

### users 테이블 추가 컬럼

```sql
ALTER TABLE users ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending' NOT NULL;
ALTER TABLE users ADD COLUMN approved_by INTEGER;
ALTER TABLE users ADD COLUMN approved_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
ALTER TABLE users ADD COLUMN employee_id INTEGER;
ALTER TABLE users ADD FOREIGN KEY (employee_id) REFERENCES employees(id);
```

## API Endpoints

### 공개 API

#### POST /api/v1/auth/signup
회원가입 (인증 불필요)

**Request Body:**
```json
{
  "username": "testuser1",
  "password": "test123456",
  "email": "testuser1@company.com",
  "full_name": "김테스트",
  "phone": "010-1234-5678",
  "employee_code": "D001",
  "role": "DRIVER"
}
```

**Response (201):**
```json
{
  "id": 5,
  "username": "testuser1",
  "email": "testuser1@company.com",
  "full_name": "김테스트",
  "phone": "010-1234-5678",
  "role": "DRIVER",
  "is_active": false,
  "approval_status": "pending",
  "employee_id": 1,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error (404):**
```json
{
  "detail": "해당 직원번호를 찾을 수 없습니다. 인사카드에 등록된 직원번호를 입력해주세요."
}
```

**Error (400):**
```json
{
  "detail": "등록된 전화번호와 일치하지 않습니다"
}
```

### 인증 필요 API (MASTER/ADMIN only)

#### GET /api/v1/auth/users/pending
승인 대기 중인 사용자 목록 조회

**Query Parameters:**
- `skip`: int (default: 0)
- `limit`: int (default: 100)

**Response:**
```json
{
  "total": 2,
  "items": [
    {
      "id": 5,
      "username": "testuser1",
      "email": "testuser1@company.com",
      "full_name": "김테스트",
      "phone": "010-1234-5678",
      "role": "DRIVER",
      "is_active": false,
      "approval_status": "pending",
      "employee": {
        "employee_code": "D001",
        "name": "김테스트",
        "phone": "010-1234-5678"
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### POST /api/v1/auth/users/{user_id}/approve
사용자 승인

**Response (200):**
```json
{
  "message": "사용자가 승인되었습니다",
  "user": { /* UserResponse */ }
}
```

#### POST /api/v1/auth/users/{user_id}/reject
사용자 가입 거부

**Request Body (optional):**
```json
{
  "rejection_reason": "직원 정보 불일치"
}
```

**Response (200):**
```json
{
  "message": "사용자 가입이 거부되었습니다: 직원 정보 불일치",
  "user": { /* UserResponse */ }
}
```

## 프론트엔드 컴포넌트

### 1. SignupPage (`/frontend/src/pages/SignupPage.tsx`)

- 회원가입 폼
- 인사카드 정보 입력 및 검증
- 유효성 검사
- 에러 메시지 표시

### 2. LoginPage 업데이트

- "회원가입" 링크 추가

### 3. UserManagementTab 확장

- 승인 대기 목록 섹션 추가
- 승인/거부 버튼
- 직원 정보 표시

## 배포 방법

### 서버에서 실행

```bash
cd /root/uvis
curl -L -o deploy_signup_workflow.sh "https://raw.githubusercontent.com/rpaakdi1-spec/3-/main/deploy_signup_workflow.sh"
chmod +x deploy_signup_workflow.sh
./deploy_signup_workflow.sh
```

### 스크립트 내용

1. GitHub에서 최신 코드 pull
2. 테스트 직원 데이터 확인 및 생성
3. 데이터베이스 마이그레이션 실행
4. 기존 사용자를 승인 상태로 업데이트
5. admin 사용자를 MASTER 역할로 업그레이드
6. Backend Docker 컨테이너 재빌드
7. UserManagementTab에 승인 기능 추가
8. Frontend Docker 컨테이너 재빌드
9. 배포 검증

## 테스트 시나리오

### 1. 회원가입 테스트

1. 브라우저에서 http://139.150.11.99/ 접속
2. "회원가입" 버튼 클릭
3. 다음 정보 입력:
   - 사용자명: `testuser1`
   - 직원번호: `D001`
   - 이름: `김테스트`
   - 전화번호: `010-1234-5678`
   - 이메일: `testuser1@company.com`
   - 비밀번호: `test123456`
   - 권한: `운전사원`
4. "회원가입" 버튼 클릭
5. "관리자 승인 후 로그인할 수 있습니다" 메시지 확인
6. 자동으로 로그인 페이지로 리다이렉트

### 2. 로그인 시도 (승인 전)

1. 가입한 계정으로 로그인 시도
2. "비활성화된 사용자입니다" 에러 확인

### 3. 관리자 승인

1. 관리자 계정으로 로그인 (`admin` / `admin123`)
2. "설정" → "회원관리" 이동
3. 상단에 "승인 대기 중인 사용자" 섹션 확인
4. 신청 내용 확인:
   - 사용자명, 이름, 이메일
   - 직원번호 (D001)
   - 신청일
5. "승인" 버튼 클릭
6. "사용자가 승인되었습니다" 토스트 메시지 확인
7. 승인 대기 목록에서 사라짐
8. 하단 전체 사용자 목록에 표시 (활성 상태)

### 4. 승인 후 로그인 테스트

1. 로그아웃
2. 승인된 계정으로 로그인 (`testuser1` / `test123456`)
3. 대시보드 접근 성공

### 5. 거부 테스트

1. 새로운 계정으로 회원가입
2. 관리자로 로그인
3. 승인 대기 목록에서 "거부" 버튼 클릭
4. 거부 사유 입력 (선택사항)
5. 확인
6. 해당 사용자는 거부 상태로 기록

## 보안 고려사항

### 1. 인사카드 연동 검증

- 직원번호, 이름, 전화번호 3가지 정보 일치 필요
- 무단 가입 방지

### 2. 승인 권한 제한

- MASTER, ADMIN 역할만 승인/거부 가능
- 일반 사용자는 승인 대기 목록 조회 불가

### 3. 계정 활성화 제어

- 승인 전: `is_active = false`, 로그인 불가
- 승인 후: `is_active = true`, 로그인 가능
- 거부 시: 영구적으로 비활성 상태

### 4. 감사 로그

- `approved_by`: 승인/거부한 관리자 ID 기록
- `approved_at`: 승인/거부 일시 기록

## 향후 개선 사항

1. **이메일 알림**
   - 가입 신청 시 관리자에게 알림
   - 승인/거부 시 신청자에게 이메일 발송

2. **대량 승인**
   - 여러 사용자를 한 번에 승인/거부

3. **승인 히스토리**
   - 승인/거부 내역 로그 테이블
   - 거부 사유 상세 기록

4. **자동 승인 규칙**
   - 특정 조건 충족 시 자동 승인
   - 예: 특정 부서, 직급

5. **2단계 승인**
   - 운영부 1차 승인
   - 총괄관리자 최종 승인

## 문제 해결

### Migration 실패

```bash
docker exec uvis-backend alembic upgrade head
```

### 컬럼 중복 오류

Migration 스크립트는 컬럼 존재 여부를 확인 후 추가하므로 안전합니다.

### 테스트 직원 데이터 없음

```bash
docker exec uvis-backend python3 << 'EOF'
from app.core.database import SessionLocal
from app.models.employee import Employee, EmployeeRole, EmploymentType
from datetime import date

db = SessionLocal()
employee = Employee(
    employee_code="D001",
    name="김테스트",
    phone="010-1234-5678",
    role=EmployeeRole.DRIVER,
    employment_type=EmploymentType.FULL_TIME,
    hire_date=date.today()
)
db.add(employee)
db.commit()
db.close()
EOF
```

## 참고 문서

- Backend Changes: 
  - `backend/app/api/auth.py`
  - `backend/app/models/user.py`
  - `backend/app/schemas/auth.py`

- Frontend Changes:
  - `frontend/src/pages/SignupPage.tsx`
  - `frontend/src/pages/LoginPage.tsx`
  - `frontend/src/components/settings/UserManagementTab.tsx`
  - `frontend/src/App.tsx`

- Scripts:
  - `deploy_signup_workflow.sh`
  - `add_pending_approvals.sh`
  - `create_migration_approval.sh`
