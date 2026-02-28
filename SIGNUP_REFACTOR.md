# 회원가입 워크플로우 수정 완료 ✅

## 변경사항 요약

기존 잘못된 구현:
- ❌ 회원가입 → 기존 인사카드에서 검증 → 승인

올바른 구현:
- ✅ 회원가입(인사카드 전체 양식) → 승인 → 인사카드 생성

---

## 백엔드 변경사항

### 1. 새 모델: PendingEmployee

**위치**: `backend/app/models/pending_employee.py`

회원가입 시 입력한 인사카드 정보를 임시 저장하는 테이블입니다.

**필드**:
- 기본 정보: employee_code, name, name_en, phone, email, address, emergency_contact
- 조직 정보: role, employment_type, department, position
- 근무 정보: hire_date, work_start_time, work_end_time, max_work_hours
- 운전면허: license_type, license_number, license_issue_date
- 화물운송자격증: has_cargo_license, cargo_license_number, issue/expiry dates
- 지게차: can_drive_forklift, has_forklift_certificate, certificate number/dates

### 2. SignupRequest 스키마 확장

**위치**: `backend/app/schemas/auth.py`

인사카드 전체 정보를 받을 수 있도록 확장:
```python
class SignupRequest(BaseModel):
    # 계정 정보
    username, password, email, role
    
    # 기본 인적사항 (19개 필드)
    employee_code, name, name_en, phone, address...
    
    # 조직/근무/자격증 정보
    employee_role, employment_type, department...
```

### 3. POST /api/v1/auth/signup 수정

**변경 전**: 기존 Employee 테이블에서 검증
**변경 후**: PendingEmployee 테이블에 저장

- 사용자명/이메일 중복 체크
- 사원번호 중복 체크 (Employee + PendingEmployee)
- User 생성 (approval_status='pending', is_active=False)
- PendingEmployee 생성 (모든 인사카드 정보 저장)

### 4. POST /api/v1/auth/users/{id}/approve 수정

**추가 기능**: Employee 레코드 자동 생성

1. PendingEmployee 데이터 조회
2. Employee 테이블에 레코드 생성
3. User.employee_id에 새 Employee ID 연결
4. User 승인 처리 (is_active=True, approval_status='approved')
5. PendingEmployee 데이터 삭제

### 5. POST /api/v1/auth/users/{id}/reject 수정

- PendingEmployee 데이터 삭제 추가

---

## 데이터베이스 마이그레이션

### 필수 마이그레이션

```sql
CREATE TABLE pending_employees (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
    
    -- 기본 식별 정보
    employee_code VARCHAR(50) NOT NULL,
    
    -- 개인 정보
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    address TEXT,
    emergency_contact VARCHAR(20),
    
    -- 조직 정보
    role VARCHAR(20) NOT NULL,
    employment_type VARCHAR(20) NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    
    -- 근무 정보
    hire_date DATE NOT NULL,
    work_start_time VARCHAR(5) DEFAULT '08:00',
    work_end_time VARCHAR(5) DEFAULT '18:00',
    max_work_hours INTEGER DEFAULT 10,
    
    -- 운전면허
    license_type VARCHAR(20),
    license_number VARCHAR(50),
    license_issue_date DATE,
    
    -- 화물운송자격증
    has_cargo_license BOOLEAN DEFAULT FALSE,
    cargo_license_number VARCHAR(50),
    cargo_license_issue_date DATE,
    cargo_license_expiry_date DATE,
    
    -- 지게차
    can_drive_forklift BOOLEAN DEFAULT FALSE,
    has_forklift_certificate BOOLEAN DEFAULT FALSE,
    forklift_certificate_number VARCHAR(50),
    forklift_certificate_issue_date DATE,
    forklift_certificate_expiry_date DATE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_pending_employees_user_id ON pending_employees(user_id);
CREATE INDEX idx_pending_employees_code ON pending_employees(employee_code);
```

---

## 프론트엔드 변경사항 (TODO)

### SignupPage 업데이트 필요

현재 SignupPage는 기본 정보만 입력받습니다. 다음 필드를 추가해야 합니다:

**필수 추가 필드**:
1. 기본 정보
   - name_en (영문명)
   - address (주소)
   - emergency_contact (비상연락처)

2. 조직 정보
   - employee_role (직급: MASTER/ADMIN/MANAGER/DRIVER)
   - employment_type (고용형태: FULL_TIME/CONTRACT/PART_TIME/DAILY)
   - department (부서)
   - position (직책)

3. 근무 정보
   - hire_date (입사일) *
   - work_start_time (근무 시작)
   - work_end_time (근무 종료)
   - max_work_hours (최대 근무시간)

4. 운전면허
   - license_type (면허 종류)
   - license_number (면허 번호)
   - license_issue_date (발급일)

5. 화물운송자격증
   - has_cargo_license (보유 여부) *
   - cargo_license_number (번호)
   - cargo_license_issue_date (발급일)
   - cargo_license_expiry_date (만료일)

6. 지게차 자격
   - can_drive_forklift (운전 가능) *
   - has_forklift_certificate (자격증 보유) *
   - forklift_certificate_number (번호)
   - forklift_certificate_issue_date (발급일)
   - forklift_certificate_expiry_date (만료일)

**UI 개선 제안**:
- 섹션별로 Accordion 또는 Step Wizard 사용
- 필수/선택 필드 명확히 표시
- 날짜 입력은 DatePicker 사용
- 자격증 보유 여부에 따라 관련 필드 show/hide

---

## 승인 페이지 업데이트 (TODO)

UserManagementTab의 승인 대기 목록에서 PendingEmployee 정보를 표시해야 합니다.

**표시할 정보**:
- 사원번호
- 이름 / 영문명
- 전화번호 / 비상연락처
- 부서 / 직책
- 입사일
- 자격증 보유 현황

**구현 방법**:
1. GET /auth/users/pending 응답에 pending_employee_data 포함 (backend)
2. UserResponse 스키마에 pending_employee 필드 추가 (optional)
3. 프론트엔드에서 pending_employee_data를 표시

---

## 테스트 시나리오

### 1. 회원가입 테스트

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newdriver1",
    "password": "test123456",
    "email": "driver1@company.com",
    "role": "DRIVER",
    "employee_code": "D999",
    "name": "테스트운전사",
    "phone": "010-9999-9999",
    "employee_role": "DRIVER",
    "employment_type": "FULL_TIME",
    "hire_date": "2024-01-15",
    "has_cargo_license": true,
    "can_drive_forklift": false,
    "has_forklift_certificate": false
  }'
```

예상 응답:
```json
{
  "id": 10,
  "username": "newdriver1",
  "email": "driver1@company.com",
  "full_name": "테스트운전사",
  "phone": "010-9999-9999",
  "role": "DRIVER",
  "is_active": false,
  "approval_status": "pending",
  "employee_id": null
}
```

### 2. 승인 테스트

```bash
# 관리자 로그인
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# 승인 대기 목록 확인
curl http://localhost:8000/api/v1/auth/users/pending \
  -H "Authorization: Bearer $TOKEN"

# 승인 처리
curl -X POST http://localhost:8000/api/v1/auth/users/10/approve \
  -H "Authorization: Bearer $TOKEN"
```

예상 결과:
- User.is_active = True
- User.approval_status = 'approved'
- User.employee_id = (새로 생성된 Employee ID)
- Employee 테이블에 새 레코드 생성
- PendingEmployee 레코드 삭제

### 3. 거부 테스트

```bash
curl -X POST http://localhost:8000/api/v1/auth/users/10/reject \
  -H "Authorization: Bearer $TOKEN" \
  -d 'rejection_reason=중복 사원번호'
```

예상 결과:
- User.approval_status = 'rejected'
- PendingEmployee 레코드 삭제

---

## 배포 순서

1. ✅ **백엔드 업데이트** (완료)
   - PendingEmployee 모델
   - SignupRequest 스키마
   - signup/approve/reject 엔드포인트 수정

2. ⏳ **데이터베이스 마이그레이션**
   - pending_employees 테이블 생성
   - Alembic migration 실행

3. ⏳ **프론트엔드 업데이트**
   - SignupPage 인사카드 전체 양식 추가
   - UserManagementTab pending_employee 정보 표시

4. ⏳ **테스트**
   - 회원가입 → 승인 → Employee 생성 확인
   - 회원가입 → 거부 → 데이터 삭제 확인

---

## 주의사항

1. **BREAKING CHANGE**: 기존 회원가입 로직이 완전히 변경되었습니다
2. **마이그레이션 필수**: pending_employees 테이블을 생성해야 합니다
3. **프론트엔드 업데이트 필요**: SignupPage가 많은 필드를 추가해야 합니다
4. **기존 pending users**: 기존에 승인 대기 중인 사용자가 있다면 PendingEmployee 데이터가 없어 승인 불가 → 수동 처리 필요

---

## 다음 단계

1. 프론트엔드 SignupPage 완전 재작성 (인사카드 양식)
2. UserManagementTab에 PendingEmployee 정보 표시
3. 배포 스크립트 작성
4. 엔드투엔드 테스트

---

**커밋 해시**: dc03082
**변경 파일**: 
- `backend/app/models/pending_employee.py` (신규)
- `backend/app/schemas/auth.py`
- `backend/app/api/auth.py`
- `backend/app/models/__init__.py`
