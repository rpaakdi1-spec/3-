# 회원관리 기능 구현 완료

**날짜**: 2026-02-28  
**기능**: 설정 페이지에 회원관리 탭 추가 및 인사카드 연동

---

## 📋 구현 내용

### 1. 설정 페이지에 '회원관리' 탭 추가
- **위치**: 설정 > 회원관리
- **아이콘**: Users (lucide-react)
- **순서**: 프로필 다음, 알림 설정 이전

### 2. UserManagementTab 컴포넌트 생성
**파일**: `frontend/src/components/settings/UserManagementTab.tsx`

**주요 기능**:
- ✅ 사용자 목록 조회 (검색 기능 포함)
- ✅ 신규 회원 등록 (모달 폼)
- ✅ 사용자 활성화/비활성화
- ✅ 사용자 삭제
- ✅ 직원 정보 동시 생성 옵션

### 3. 회원가입 양식 - 인사카드 필드 매핑

#### 계정 정보
```typescript
- username: string (필수)
- email: string (필수)
- password: string (필수)
- full_name: string
- role: 'driver' | 'manager' | 'admin'
```

#### 직원 기본 정보 (인사카드 연동)
```typescript
employee: {
  // 기본 식별
  employee_code: string (필수) // 예: D001, A001
  name: string (필수)
  phone: string (필수)
  email: string
  address: string
  emergency_contact: string
  
  // 조직 정보
  role: 'DRIVER' | 'MANAGER' | 'ADMIN' | 'MASTER'
  employment_type: 'FULL_TIME' | 'CONTRACT' | 'PART_TIME' | 'DAILY'
  department: string
  position: string
  hire_date: date (필수)
  
  // 운전면허
  license_type: '1종 대형' | '1종 보통' | '2종 보통'
  license_number: string
  license_issue_date: date
  
  // 자격증
  has_cargo_license: boolean
  cargo_license_number: string
  can_drive_forklift: boolean
  has_forklift_certificate: boolean
}
```

---

## 🎨 UI/UX 특징

### 사용자 목록 테이블
| 열 | 내용 |
|----|------|
| 사용자명 | username |
| 이메일 | email |
| 이름 | full_name |
| 직원정보 | employee_code, name, department |
| 권한 | role (배지 스타일) |
| 상태 | 활성/비활성 (버튼) |
| 작업 | 삭제 버튼 |

### 신규 회원 등록 모달
- **크기**: max-w-4xl (와이드 모달)
- **스크롤**: 최대 높이 90vh, 세로 스크롤
- **섹션 구분**: 
  1. 계정 정보
  2. 직원 정보 생성 옵션 (체크박스)
  3. 직원 기본 정보
  4. 조직 정보
  5. 운전면허 및 자격증

---

## 🔧 기술 구현

### API 호출
```typescript
// 사용자 목록 조회
GET /users

// 신규 회원 등록 (직원 정보 포함)
POST /users/register
{
  username, email, password, full_name, role,
  employee?: {
    employee_code, name, phone, ...
  }
}

// 사용자 상태 변경
PUT /users/{userId}/status
{ is_active: boolean }

// 사용자 삭제
DELETE /users/{userId}
```

### 상태 관리
```typescript
- users: UserAccount[]
- loading: boolean
- searchTerm: string
- showNewUserModal: boolean
- showPassword: boolean
- newUser: NewUserForm
```

---

## 📝 사용 시나리오

### 시나리오 1: 신규 운전자 등록
1. 설정 > 회원관리 클릭
2. "신규 회원 등록" 버튼 클릭
3. 계정 정보 입력:
   - 사용자명: driver01
   - 이메일: driver01@company.com
   - 비밀번호: ********
   - 권한: 운전자
4. "직원 정보도 함께 생성" 체크
5. 직원 정보 입력:
   - 사원번호: D001
   - 이름: 홍길동
   - 전화번호: 010-1234-5678
   - 직급: 운전직
   - 고용 형태: 정규직
   - 입사일: 2026-02-28
6. 운전면허 정보:
   - 면허 종류: 1종 대형
   - 면허 번호: 12-345678-90
7. 자격증:
   - ✅ 화물운송자격증 보유
   - ✅ 지게차 운전 가능
8. "등록" 버튼 클릭

**결과**:
- ✅ User 계정 생성 (로그인 가능)
- ✅ Employee 레코드 생성 (인사카드 자동 생성)
- ✅ 차량 배정 가능한 운전자로 등록

### 시나리오 2: 관리자 계정만 생성
1. "신규 회원 등록" 클릭
2. 계정 정보 입력:
   - 사용자명: manager01
   - 이메일: manager@company.com
   - 권한: 관리자
3. "직원 정보도 함께 생성" 체크 해제
4. "등록" 클릭

**결과**:
- ✅ User 계정만 생성 (employee_id = null)
- ✅ 시스템 관리용 계정

---

## 🔐 권한 제어

현재 구현된 기능은 모든 로그인 사용자가 접근 가능합니다.  
향후 ADMIN 권한만 접근하도록 제한할 수 있습니다:

```typescript
// SettingsPage.tsx에서
const { user } = useAuthStore();
const canManageUsers = user?.role === 'admin' || user?.role === 'master';

// users 탭 조건부 표시
{canManageUsers && { id: 'users', label: '회원관리', icon: Users }}
```

---

## 🧪 테스트 가이드

### 1. 사용자 목록 조회
```bash
# 브라우저 접속
http://139.150.11.99/settings

# 회원관리 탭 클릭
# 예상: 등록된 사용자 목록 표시
```

### 2. 검색 기능
```
검색어 입력 → 사용자명, 이메일, 이름으로 필터링
```

### 3. 신규 회원 등록 (직원 정보 포함)
```bash
# F12 → Network 탭
POST /users/register

# Request Body
{
  "username": "test_driver",
  "email": "test@example.com",
  "password": "test123456",
  "role": "driver",
  "createEmployee": true,
  "employee": {
    "employee_code": "D999",
    "name": "테스트 운전자",
    "phone": "010-9999-9999",
    "role": "DRIVER",
    "employment_type": "FULL_TIME",
    "hire_date": "2026-02-28"
  }
}

# 예상 응답: 201 Created
```

### 4. 사용자 상태 변경
```bash
# 활성 버튼 클릭
PUT /users/{userId}/status
{ "is_active": false }

# 예상: 버튼 색상 변경 (초록색 → 빨간색)
```

### 5. 사용자 삭제
```bash
# 삭제 버튼 클릭
DELETE /users/{userId}

# 확인 대화상자: "정말 이 사용자를 삭제하시겠습니까?"
# 예상: 사용자 목록에서 제거
```

---

## 📊 데이터베이스 스키마 연동

### users 테이블
```sql
- id: INTEGER (PK)
- username: VARCHAR(50) UNIQUE
- email: VARCHAR(100)
- hashed_password: VARCHAR(255)
- full_name: VARCHAR(100)
- role: ENUM('driver', 'manager', 'admin', 'master')
- is_active: BOOLEAN
- employee_id: INTEGER (FK → employees.id)
- created_at: TIMESTAMP
```

### employees 테이블 (기존)
```sql
- id: INTEGER (PK)
- employee_code: VARCHAR(50) UNIQUE
- name: VARCHAR(100)
- phone: VARCHAR(20)
- email: VARCHAR(100)
- role: ENUM('DRIVER', 'MANAGER', 'ADMIN', 'MASTER')
- employment_type: ENUM('FULL_TIME', 'CONTRACT', 'PART_TIME', 'DAILY')
- hire_date: DATE
- license_type: VARCHAR(20)
- has_cargo_license: BOOLEAN
- can_drive_forklift: BOOLEAN
- has_forklift_certificate: BOOLEAN
- ...
```

---

## 🔄 백엔드 API 요구사항

UserManagementTab이 정상 작동하려면 다음 API가 필요합니다:

### 1. 사용자 목록 조회 ✅
```python
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).options(joinedload(User.employee)).all()
    return users
```

### 2. 신규 회원 등록 (직원 포함) ⚠️ 확인 필요
```python
@router.post("/users/register")
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # 1. User 생성
    user = User(...)
    db.add(user)
    
    # 2. Employee 생성 (선택)
    if user_data.createEmployee:
        employee = Employee(...)
        db.add(employee)
        user.employee_id = employee.id
    
    db.commit()
    return user
```

### 3. 사용자 상태 변경 ⚠️ 확인 필요
```python
@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    status: dict,
    db: Session = Depends(get_db)
):
    user = db.query(User).get(user_id)
    user.is_active = status["is_active"]
    db.commit()
    return user
```

### 4. 사용자 삭제 ⚠️ 확인 필요
```python
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).get(user_id)
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
```

---

## 🚀 배포 가이드

### 프론트엔드 배포
```bash
cd /root/uvis
git pull origin main
docker-compose down frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
sleep 30
```

### 백엔드 API 확인
```bash
# auth.py에 필요한 엔드포인트가 있는지 확인
grep -n "register\|/users" backend/app/api/auth.py
```

### 브라우저 테스트
```
1. http://139.150.11.99/settings 접속
2. "회원관리" 탭 클릭
3. "신규 회원 등록" 버튼 확인
4. 모달 열고 폼 확인
```

---

## 📝 향후 개선 사항

### 1. 권한 제어 강화
- ADMIN만 회원관리 접근
- 일반 사용자는 프로필만 수정 가능

### 2. 사용자 편집 기능
- 기존 사용자 정보 수정
- 비밀번호 재설정 (관리자)

### 3. 일괄 작업
- 여러 사용자 선택 → 일괄 활성화/비활성화
- CSV 업로드로 대량 등록

### 4. 감사 로그
- 사용자 생성/수정/삭제 이력 기록
- 로그인 이력 추적

### 5. 직원-사용자 매핑
- 기존 직원에게 계정 연결
- 직원 없이 생성된 계정에 나중에 직원 연결

---

## 🔗 관련 파일

### 프론트엔드
- `frontend/src/pages/SettingsPage.tsx` - 설정 페이지 (탭 추가)
- `frontend/src/components/settings/UserManagementTab.tsx` - 회원관리 컴포넌트 (신규)

### 백엔드
- `backend/app/api/auth.py` - 사용자 인증 API
- `backend/app/models/user.py` - User 모델
- `backend/app/models/employee.py` - Employee 모델 (연동)
- `backend/app/schemas/auth.py` - User 스키마

### Git
- **커밋**: `39c5fe7`
- **메시지**: "feat: Add user management tab in settings with employee integration"

---

**최종 업데이트**: 2026-02-28  
**상태**: ✅ 프론트엔드 구현 완료, 백엔드 API 확인 필요  
**다음 단계**: 백엔드 API 엔드포인트 구현 및 통합 테스트
