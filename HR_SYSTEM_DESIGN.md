# 화물운수업 인사관리 시스템 설계

**작성일**: 2026-02-27  
**목적**: 화물운수업에 맞는 체계적인 회원 등록 및 관리 시스템 구축

---

## 📋 시스템 개요

### 사용자 계층 구조
```
마스터 (MASTER)
  └─ 관리자 (ADMIN)
      └─ 운영사원 (MANAGER)
          └─ 운전직 (DRIVER)
```

### 주요 기능
1. **통합 인사 카드**: 모든 회원을 화물운수업 인사카드로 등록 및 관리
2. **운전자 풀 연동**: 운전직 사원 정보만 자동으로 운전자 풀에 표시
3. **권한 관리**: 직급별 권한 차등 부여
4. **자격증 관리**: 운전면허, 화물운송자격증, 지게차 자격증 관리

---

## 🗂️ 데이터베이스 설계

### 1. Employee (통합 인사 테이블) - 신규 생성

```python
class EmployeeRole(str, Enum):
    """직급"""
    MASTER = "MASTER"          # 마스터 (총괄)
    ADMIN = "ADMIN"            # 관리자
    MANAGER = "MANAGER"        # 운영사원
    DRIVER = "DRIVER"          # 운전직
    
class EmploymentType(str, Enum):
    """고용 형태"""
    FULL_TIME = "FULL_TIME"    # 정규직
    CONTRACT = "CONTRACT"       # 계약직
    PART_TIME = "PART_TIME"    # 시간제
    DAILY = "DAILY"            # 일용직

class Employee(Base, IDMixin, TimestampMixin):
    """통합 인사 카드"""
    __tablename__ = "employees"
    
    # === 기본 정보 ===
    employee_code: str          # 사번 (예: EMP-2024-001)
    name: str                   # 이름
    name_en: Optional[str]      # 영문명
    
    # === 연락처 ===
    phone: str                  # 전화번호
    emergency_contact: Optional[str]  # 비상연락처
    emergency_name: Optional[str]     # 비상연락처 이름
    emergency_relation: Optional[str] # 비상연락처 관계
    email: Optional[str]        # 이메일
    address: Optional[str]      # 주소
    
    # === 직급 및 근무 ===
    role: EmployeeRole          # 직급
    employment_type: EmploymentType  # 고용형태
    department: Optional[str]   # 부서
    position: Optional[str]     # 직책
    
    # === 입퇴사 정보 ===
    hire_date: date             # 입사일
    resignation_date: Optional[date]  # 퇴사일
    
    # === 근무 시간 ===
    work_start_time: str = "08:00"    # 근무시작시간
    work_end_time: str = "18:00"      # 근무종료시간
    max_work_hours: int = 10          # 최대근무시간
    
    # === 운전직 전용 정보 ===
    # 운전면허
    license_number: Optional[str]     # 운전면허번호
    license_type: Optional[str]       # 면허종류 (1종 대형, 1종 보통, 2종)
    license_issue_date: Optional[date]  # 면허발급일
    license_expiry_date: Optional[date] # 면허만료일
    
    # 화물운송자격증
    cargo_license_number: Optional[str]     # 화물운송자격증번호
    cargo_license_issue_date: Optional[date] # 발급일
    cargo_license_expiry_date: Optional[date] # 만료일
    has_cargo_license: bool = False         # 화물운송자격증 보유여부
    
    # 지게차 자격증
    forklift_license_number: Optional[str]     # 지게차자격증번호
    forklift_license_issue_date: Optional[date] # 발급일
    forklift_license_expiry_date: Optional[date] # 만료일
    has_forklift_license: bool = False         # 지게차자격증 보유여부
    
    # 지게차 운전 능력 (자격증 없어도 운전 가능 여부 파악용)
    can_operate_forklift: bool = False         # 지게차 운전 가능 여부
    forklift_experience_years: Optional[int]   # 지게차 운전 경력(년)
    
    # === 급여 정보 ===
    salary_type: Optional[str]  # 급여형태 (월급, 일급, 시급)
    base_salary: Optional[int]  # 기본급
    bank_name: Optional[str]    # 은행명
    account_number: Optional[str] # 계좌번호
    
    # === 기타 ===
    photo_url: Optional[str]    # 사진 URL
    notes: Optional[str]        # 비고
    is_active: bool = True      # 재직 여부
    
    # === User 연동 ===
    user_id: Optional[int]      # User 테이블 FK (로그인 계정)
    
    # === Relationships ===
    user: Mapped["User"] = relationship("User", back_populates="employee")
    dispatches: Mapped[List["Dispatch"]] = relationship("Dispatch", back_populates="driver_employee")
```

### 2. User 테이블 확장

```python
class UserRole(str, Enum):
    """사용자 권한"""
    MASTER = "MASTER"      # 마스터 (모든 권한)
    ADMIN = "ADMIN"        # 관리자 (운영 권한)
    MANAGER = "MANAGER"    # 운영사원 (제한된 권한)
    DRIVER = "DRIVER"      # 운전직 (배차 조회만)
    VIEWER = "VIEWER"      # 조회자 (읽기 전용)

class User(Base):
    """사용자 계정 (로그인용)"""
    __tablename__ = "users"
    
    # 기존 필드 유지
    id: int
    username: str
    email: str
    hashed_password: str
    full_name: str
    role: UserRole
    is_active: bool
    
    # 신규 필드
    employee_id: Optional[int]  # Employee 테이블 FK
    
    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="user")
```

### 3. Driver 테이블 (기존 유지 → 향후 통합)

현재는 기존 Driver 테이블 유지하고, 점진적으로 Employee로 마이그레이션

---

## 🔄 데이터 흐름

### 운전자 풀 데이터 흐름
```
Employee (role=DRIVER)
  ↓ (조회 시 필터링)
  ↓ 조건:
  ↓   - role = "DRIVER"
  ↓   - is_active = True
  ↓   - has_cargo_license = True (선택)
  ↓
Driver Pool (운전자 풀)
  ↓
Vehicle Assignment (차량 배정)
```

---

## 📊 API 엔드포인트 설계

### 1. Employee API

```python
# 인사 관리
POST   /api/v1/employees                  # 사원 등록
GET    /api/v1/employees                  # 사원 목록
GET    /api/v1/employees/{id}             # 사원 상세
PUT    /api/v1/employees/{id}             # 사원 수정
DELETE /api/v1/employees/{id}             # 사원 삭제

# 필터링
GET    /api/v1/employees?role=DRIVER      # 운전직만 조회
GET    /api/v1/employees?is_active=true   # 재직자만 조회
GET    /api/v1/employees?has_cargo_license=true  # 자격증 보유자

# 운전자 풀 전용
GET    /api/v1/employees/drivers          # 운전직 목록 (운전자 풀용)
GET    /api/v1/employees/drivers/available  # 배정 가능 운전직

# 자격증 관리
PUT    /api/v1/employees/{id}/license     # 면허 정보 수정
PUT    /api/v1/employees/{id}/cargo-license  # 화물자격증 수정
PUT    /api/v1/employees/{id}/forklift-license  # 지게차자격증 수정

# Excel 업로드/다운로드
POST   /api/v1/employees/upload           # Excel 일괄 등록
GET    /api/v1/employees/export           # Excel 내보내기
GET    /api/v1/employees/template         # Excel 템플릿 다운로드
```

### 2. 권한별 접근 제어

```python
# 마스터 (MASTER)
- 모든 API 접근 가능
- 사원 등록/수정/삭제
- 권한 부여

# 관리자 (ADMIN)
- 사원 조회/수정
- 배차 관리
- 보고서 생성

# 운영사원 (MANAGER)
- 사원 조회 (제한적)
- 배차 조회/생성
- 일일 운영

# 운전직 (DRIVER)
- 본인 정보 조회
- 배차 조회
- 상태 업데이트
```

---

## 🎨 프론트엔드 화면 설계

### 1. 인사 관리 페이지 (/employees)

**레이아웃**:
```
┌─────────────────────────────────────────────────────────────┐
│ 인사 관리                                   [+ 신규 등록]    │
├─────────────────────────────────────────────────────────────┤
│ 🔍 검색: [이름/사번/전화번호]  [검색]                        │
│                                                              │
│ 필터:                                                        │
│ 직급: [전체▼] 고용형태: [전체▼] 재직: [전체▼]              │
│ 면허: [전체▼] 화물자격증: [전체▼] 지게차운전: [전체▼]      │
│                                           [필터 초기화]      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌────────────────────────────────────────┐                  │
│ │ [사진]  EMP-2024-001                   │ [편집] [삭제]   │
│ │         김철수 (1종 대형)               │                  │
│ │         운전직 | 정규직                 │                  │
│ │         📞 010-1234-5678               │                  │
│ │         ✅ 화물자격증 | 🚜 지게차 가능 │                  │
│ └────────────────────────────────────────┘                  │
│                                                              │
│ ┌────────────────────────────────────────┐                  │
│ │ [사진]  EMP-2024-002                   │ [편집] [삭제]   │
│ │         이영희                          │                  │
│ │         관리자 | 정규직                  │                  │
│ │         📞 010-2345-6789               │                  │
│ └────────────────────────────────────────┘                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. 인사 카드 모달 (신규/편집)

**탭 구조**:
```
[기본정보] [근무정보] [자격증] [급여정보]

=== 기본정보 탭 ===
┌─────────────────────────────────────────┐
│ 사진 업로드: [파일선택]                  │
│                                         │
│ * 사번: [EMP-2024-001]                  │
│ * 이름: [김철수]                        │
│   영문명: [Kim Chul Soo]               │
│                                         │
│ * 전화번호: [010-1234-5678]            │
│   이메일: [kim@example.com]            │
│   주소: [서울시 강남구...]              │
│                                         │
│   비상연락처: [010-9876-5432]          │
│   비상연락처 이름: [김부모]             │
│   관계: [부]                            │
└─────────────────────────────────────────┘

=== 근무정보 탭 ===
┌─────────────────────────────────────────┐
│ * 직급: [운전직 ▼]                      │
│ * 고용형태: [정규직 ▼]                  │
│   부서: [물류팀]                        │
│   직책: [운전사]                        │
│                                         │
│ * 입사일: [2024-01-01]                  │
│   퇴사일: [         ]                   │
│                                         │
│   근무시작: [08:00]                     │
│   근무종료: [18:00]                     │
│   최대근무: [10] 시간                   │
└─────────────────────────────────────────┘

=== 자격증 탭 ===
┌─────────────────────────────────────────┐
│ 운전면허                                 │
│   면허번호: [서울12-345678-90]          │
│   면허종류: [1종 대형 ▼]               │
│   발급일: [2020-01-01]                  │
│   만료일: [2030-01-01]                  │
│                                         │
│ 화물운송자격증                           │
│   ☑ 보유                                │
│   자격증번호: [CARGO-12345]            │
│   발급일: [2021-01-01]                  │
│   만료일: [2026-01-01]                  │
│                                         │
│ 지게차운전기능사                         │
│   ☑ 자격증 보유                         │
│   자격증번호: [FORK-12345]             │
│   발급일: [2019-01-01]                  │
│   만료일: [만료없음]                     │
│                                         │
│ 지게차 운전 능력 (실태 파악용)           │
│   ☑ 운전 가능                           │
│   운전 경력: [5] 년                     │
│   ※ 자격증 미보유 시에도 실제 운전      │
│      가능 여부를 파악하여 배차에 활용    │
└─────────────────────────────────────────┘

=== 급여정보 탭 ===
┌─────────────────────────────────────────┐
│ 급여형태: [월급 ▼]                      │
│ 기본급: [3,000,000] 원                  │
│                                         │
│ 은행명: [국민은행]                       │
│ 계좌번호: [123-456-789012]             │
│                                         │
│ 비고:                                   │
│ [                                    ]  │
│ [                                    ]  │
└─────────────────────────────────────────┘

          [취소]  [저장]
```

### 3. 운전자 풀 연동

**VehicleDriverManagementPage 수정**:
```typescript
// 기존: Mock 데이터
const mockDrivers = [...]

// 변경: API에서 운전직 사원 조회
const fetchDrivers = async () => {
  const response = await employeesAPI.getDrivers({
    role: 'DRIVER',
    is_active: true
  });
  return response.data;
};
```

**표시 정보**:
- 이름
- 전화번호
- 면허 종류 (1종 대형/1종 보통/2종)
- 화물운송자격증 보유 여부 (✅ 배지)
- 지게차 운전 가능 여부 (🚜 배지) ⭐ 신규
  - 자격증 보유: "🎓 지게차 자격증"
  - 운전 가능 (자격증 무): "🚜 지게차 가능 (경력 5년)"
  - 불가능: 배지 없음
- 근무 시간 (08:00 ~ 18:00)

---

## 📁 구현 파일 구조

```
backend/
├── app/
│   ├── models/
│   │   ├── employee.py          # 신규 Employee 모델
│   │   ├── user.py               # User 모델 확장
│   │   └── driver.py             # 기존 유지 (향후 통합)
│   │
│   ├── api/v1/
│   │   ├── employees.py          # 신규 인사 관리 API
│   │   ├── auth.py               # 인증 (권한 체크 강화)
│   │   └── drivers.py            # 기존 유지
│   │
│   ├── services/
│   │   ├── employee_service.py   # 인사 관리 비즈니스 로직
│   │   └── excel_service.py      # Excel 업로드/다운로드
│   │
│   └── schemas/
│       └── employee.py           # Employee Pydantic 스키마

frontend/
├── src/
│   ├── pages/
│   │   ├── EmployeesPage.tsx     # 신규 인사 관리 페이지
│   │   └── VehicleDriverManagementPage.tsx  # 기존 (API 연동 수정)
│   │
│   ├── components/
│   │   └── employees/
│   │       ├── EmployeeCard.tsx  # 인사 카드 컴포넌트
│   │       ├── EmployeeModal.tsx # 인사 등록/수정 모달
│   │       └── LicenseInfo.tsx   # 자격증 정보 컴포넌트
│   │
│   └── services/
│       └── api.ts                # employeesAPI 추가
```

---

## 🚀 구현 단계

### Phase 1: 데이터베이스 (1일)
1. ✅ Employee 모델 생성
2. ✅ User 모델 확장
3. ✅ 마이그레이션 스크립트 작성

### Phase 2: Backend API (2일)
1. ✅ Employee CRUD API
2. ✅ 필터링 및 검색
3. ✅ 권한 체크 구현
4. ✅ Excel 업로드/다운로드

### Phase 3: Frontend (3일)
1. ✅ 인사 관리 페이지
2. ✅ 인사 카드 모달
3. ✅ 운전자 풀 API 연동
4. ✅ 필터 및 검색

### Phase 4: 테스트 및 배포 (1일)
1. ✅ 통합 테스트
2. ✅ 데이터 마이그레이션
3. ✅ 문서 작성
4. ✅ 배포

**총 예상 기간**: 7일

---

## 📊 데이터 마이그레이션 계획

### 기존 Driver → Employee

```python
# 마이그레이션 스크립트
def migrate_drivers_to_employees():
    """기존 Driver 데이터를 Employee로 마이그레이션"""
    drivers = db.query(Driver).all()
    
    for driver in drivers:
        employee = Employee(
            employee_code=f"EMP-DRIVER-{driver.code}",
            name=driver.name,
            phone=driver.phone,
            emergency_contact=driver.emergency_contact,
            role=EmployeeRole.DRIVER,
            employment_type=EmploymentType.FULL_TIME,
            hire_date=driver.created_at.date(),
            work_start_time=driver.work_start_time,
            work_end_time=driver.work_end_time,
            max_work_hours=driver.max_work_hours,
            license_number=driver.license_number,
            license_type=driver.license_type,
            notes=driver.notes,
            is_active=driver.is_active
        )
        db.add(employee)
    
    db.commit()
```

---

## 🎯 핵심 기능 요약

### 1. 통합 인사 관리
- 모든 직원을 하나의 시스템에서 관리
- 직급별 차등 권한
- 화물운수업 특화 필드

### 2. 운전자 풀 자동 연동
- 운전직 사원만 자동 필터링
- 자격증 정보 실시간 반영
- 배정 가능 여부 확인

### 3. 자격증 관리
```
운전면허
├─ 면허번호
├─ 면허종류 (1종 대형/1종 보통/2종)
├─ 발급일
└─ 만료일

화물운송자격증
├─ 보유 여부 ☑
├─ 자격증번호
├─ 발급일
└─ 만료일

지게차운전기능사
├─ 자격증 보유 여부 ☑
├─ 자격증번호
├─ 발급일
└─ 만료일

지게차 운전 능력 (실태 파악용) ⭐ 신규
├─ 운전 가능 여부 ☑
├─ 운전 경력 (년)
└─ ※ 자격증 미보유 시에도 실제 운전 가능 여부 파악
```

**특징**:
- `has_forklift_license`: 자격증 보유 여부 (공식 자격)
- `can_operate_forklift`: 실제 운전 가능 여부 (실태 파악용)
- 자격증이 없어도 운전 경험이 있는 경우 체크
- 배차 시 지게차 작업 필요 여부 판단에 활용

### 4. Excel 연동
- 일괄 등록
- 템플릿 다운로드
- 데이터 내보내기

---

이제 구현을 시작하겠습니다. 어떤 단계부터 진행할까요?

1. **Phase 1**: 데이터베이스 모델 생성
2. **Phase 2**: Backend API 구현
3. **Phase 3**: Frontend 페이지 구현
4. **전체 순차 구현**

어떤 것을 원하시나요?
