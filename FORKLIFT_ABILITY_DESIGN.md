# 지게차 운전 능력 추가 - 설계 보완

**작성일**: 2026-02-27  
**목적**: 자격증 미보유 시에도 실제 지게차 운전 가능 여부 파악

---

## 🎯 요구사항

### 기존 문제점
- `has_forklift_license`: 지게차 자격증 보유 여부만 체크
- **문제**: 자격증은 없지만 실제로 지게차를 운전할 수 있는 경우를 파악 불가
- **영향**: 배차 시 지게차 작업이 필요한 경우 활용 불가

### 개선 방안
- 자격증 보유 여부와 **별도로** 실제 운전 가능 여부 추가
- 운전 경력(년)도 함께 관리하여 숙련도 파악

---

## 📊 데이터베이스 설계

### Employee 모델에 추가되는 필드

```python
class Employee(Base):
    # ... 기존 필드들 ...
    
    # === 지게차 자격증 (기존) ===
    forklift_license_number: Optional[str]      # 자격증번호
    forklift_license_issue_date: Optional[date] # 발급일
    forklift_license_expiry_date: Optional[date] # 만료일
    has_forklift_license: bool = False          # 자격증 보유 여부
    
    # === 지게차 운전 능력 (신규) ===
    can_operate_forklift: bool = False          # 지게차 운전 가능 여부
    forklift_experience_years: Optional[int]    # 지게차 운전 경력(년)
```

### 필드 설명

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `has_forklift_license` | bool | 공식 자격증 보유 여부 | True/False |
| `can_operate_forklift` | bool | 실제 운전 가능 여부 (자격증 무관) | True/False |
| `forklift_experience_years` | int | 운전 경력 (년) | 5, 10, 15 |

### 사용 시나리오

#### 시나리오 1: 자격증 보유 + 운전 가능
```python
has_forklift_license = True
can_operate_forklift = True
forklift_experience_years = 10

→ 표시: "🎓 지게차 자격증 (경력 10년)"
```

#### 시나리오 2: 자격증 없음 + 운전 가능 (경력 있음)
```python
has_forklift_license = False
can_operate_forklift = True
forklift_experience_years = 5

→ 표시: "🚜 지게차 가능 (경력 5년)"
```

#### 시나리오 3: 자격증 보유 + 운전 가능
```python
has_forklift_license = True
can_operate_forklift = True
forklift_experience_years = None

→ 표시: "🎓 지게차 자격증"
```

#### 시나리오 4: 자격증 없음 + 운전 불가
```python
has_forklift_license = False
can_operate_forklift = False
forklift_experience_years = None

→ 표시: (배지 없음)
```

---

## 🎨 UI 설계

### 1. 인사 카드 - 자격증 탭

```
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
│ ─────────────────────────────────────── │
│                                         │
│ 지게차운전기능사 (공식 자격증)           │
│   ☑ 자격증 보유                         │
│   자격증번호: [FORK-12345]             │
│   발급일: [2019-01-01]                  │
│   만료일: [만료없음]                     │
│                                         │
│ 지게차 운전 능력 (실태 파악용) ⭐        │
│   ☑ 운전 가능                           │
│   운전 경력: [5] 년                     │
│   ※ 자격증 미보유 시에도 실제 운전      │
│      가능 여부를 파악하여 배차에 활용    │
└─────────────────────────────────────────┘
```

### 2. 사원 카드 (목록 화면)

```
┌────────────────────────────────────────┐
│ [사진]  EMP-2024-001                   │
│         김철수 (1종 대형)               │
│         운전직 | 정규직                 │
│         📞 010-1234-5678               │
│         ✅ 화물 | 🎓 지게차 자격증      │ ← 자격증 보유
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ [사진]  EMP-2024-002                   │
│         이영수 (1종 보통)               │
│         운전직 | 계약직                 │
│         📞 010-2345-6789               │
│         ✅ 화물 | 🚜 지게차 가능 (5년) │ ← 자격증 없지만 운전 가능
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ [사진]  EMP-2024-003                   │
│         박민수 (1종 대형)               │
│         운전직 | 정규직                 │
│         📞 010-3456-7890               │
│         ✅ 화물                         │ ← 지게차 불가
└────────────────────────────────────────┘
```

### 3. 운전자 풀 (차량-운전자 배정 관리)

```
┌────────────────────────────┐
│ 운전자 풀              5명  │
├────────────────────────────┤
│ ┌────────────────────────┐ │
│ │ 김철수                  │ │
│ │ 1종 대형               │ │
│ │ 010-1234-5678          │ │
│ │ 08:00~18:00            │ │
│ │ 🎓 지게차 자격증        │ │ ← 자격증 보유
│ └────────────────────────┘ │
│                            │
│ ┌────────────────────────┐ │
│ │ 이영수                  │ │
│ │ 1종 보통               │ │
│ │ 010-2345-6789          │ │
│ │ 09:00~19:00            │ │
│ │ 🚜 지게차 (5년)        │ │ ← 경력 있음
│ └────────────────────────┘ │
│                            │
│ ┌────────────────────────┐ │
│ │ 박민수                  │ │
│ │ 1종 대형               │ │
│ │ 010-3456-7890          │ │
│ │ 07:00~17:00            │ │
│ └────────────────────────┘ │ ← 지게차 없음
└────────────────────────────┘
```

---

## 🔍 필터 기능

### 인사 관리 페이지 필터

```
필터:
  직급: [전체▼]
  고용형태: [전체▼]
  재직: [전체▼]
  면허: [전체▼]
  화물자격증: [전체▼]
  지게차운전: [전체▼] ⭐
    ├─ 전체
    ├─ 자격증 보유
    ├─ 운전 가능 (자격증 무관)
    └─ 운전 불가
```

### 필터 로직

```python
# 지게차 운전 필터
if forklift_filter == "certified":
    # 자격증 보유자만
    query = query.filter(Employee.has_forklift_license == True)
    
elif forklift_filter == "can_operate":
    # 운전 가능자 (자격증 무관)
    query = query.filter(Employee.can_operate_forklift == True)
    
elif forklift_filter == "cannot_operate":
    # 운전 불가
    query = query.filter(Employee.can_operate_forklift == False)
```

---

## 📡 API 설계

### 1. Employee API 응답 스키마

```python
class EmployeeResponse(BaseModel):
    id: int
    employee_code: str
    name: str
    phone: str
    
    # 운전면허
    license_type: Optional[str]
    
    # 화물운송자격증
    has_cargo_license: bool
    
    # 지게차 자격증
    has_forklift_license: bool
    forklift_license_number: Optional[str]
    
    # 지게차 운전 능력 (신규)
    can_operate_forklift: bool
    forklift_experience_years: Optional[int]
    
    # 배지 표시용 계산 필드
    @property
    def forklift_badge(self) -> str:
        """지게차 배지 문자열"""
        if self.has_forklift_license:
            if self.forklift_experience_years:
                return f"🎓 지게차 자격증 (경력 {self.forklift_experience_years}년)"
            return "🎓 지게차 자격증"
        elif self.can_operate_forklift:
            if self.forklift_experience_years:
                return f"🚜 지게차 가능 (경력 {self.forklift_experience_years}년)"
            return "🚜 지게차 가능"
        return ""
```

### 2. 필터링 API

```python
GET /api/v1/employees/drivers?forklift=can_operate
GET /api/v1/employees/drivers?forklift=certified
GET /api/v1/employees/drivers?forklift=cannot_operate
```

---

## 🎯 활용 방안

### 1. 배차 시 활용

**지게차 작업이 필요한 배송**:
```python
# 지게차 운전 가능한 운전자 우선 배정
drivers = Employee.query.filter(
    Employee.role == "DRIVER",
    Employee.is_active == True,
    Employee.can_operate_forklift == True  # 자격증 유무 무관
).order_by(
    # 자격증 보유자 우선
    Employee.has_forklift_license.desc(),
    # 경력 많은 순
    Employee.forklift_experience_years.desc()
).all()
```

### 2. 통계 및 보고서

```python
# 지게차 운전 가능 인원 통계
total_drivers = count(role == "DRIVER")
certified = count(has_forklift_license == True)
can_operate = count(can_operate_forklift == True)
cannot_operate = total_drivers - can_operate

통계:
  전체 운전직: 50명
  자격증 보유: 20명 (40%)
  운전 가능: 35명 (70%)
  운전 불가: 15명 (30%)
```

### 3. 교육 계획 수립

```python
# 운전 가능하지만 자격증 없는 직원
training_candidates = Employee.query.filter(
    Employee.can_operate_forklift == True,
    Employee.has_forklift_license == False
).all()

→ 자격증 취득 교육 대상자 선정
```

---

## 📋 구현 체크리스트

### Backend
- [ ] Employee 모델에 필드 추가
  - [ ] `can_operate_forklift: bool`
  - [ ] `forklift_experience_years: Optional[int]`
- [ ] 마이그레이션 스크립트 작성
- [ ] API 스키마 업데이트
- [ ] 필터링 로직 추가

### Frontend
- [ ] 인사 카드 모달 - 자격증 탭 수정
  - [ ] "지게차 운전 능력" 섹션 추가
  - [ ] 체크박스: 운전 가능 여부
  - [ ] 입력: 운전 경력(년)
- [ ] 사원 카드 배지 표시 로직 수정
  - [ ] 자격증 보유: "🎓 지게차 자격증"
  - [ ] 운전 가능: "🚜 지게차 가능 (N년)"
- [ ] 필터 옵션 추가
  - [ ] 자격증 보유
  - [ ] 운전 가능 (자격증 무관)
  - [ ] 운전 불가
- [ ] 운전자 풀 배지 표시 업데이트

---

## 🎉 기대 효과

### 1. 정확한 인력 파악
- ✅ 자격증 유무뿐만 아니라 실제 운전 능력 파악
- ✅ 경력 정보로 숙련도 판단

### 2. 효율적인 배차
- ✅ 지게차 작업이 필요한 배송에 적합한 인력 배정
- ✅ 자격증 보유자 우선, 경력 많은 순으로 정렬

### 3. 교육 계획 수립
- ✅ 운전 가능하지만 자격증 없는 직원 → 교육 대상
- ✅ 자격증 만료 예정자 → 갱신 안내

### 4. 법적 리스크 관리
- ✅ 자격증 보유 여부 명확히 구분
- ✅ 실제 운전 능력은 참고용으로만 활용

---

**문서 작성**: 2026-02-27  
**설계자**: AI Assistant  
**상태**: ✅ 설계 완료
