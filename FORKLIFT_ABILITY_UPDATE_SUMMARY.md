# 지게차 운전능력 필드 추가 - 업데이트 요약

**날짜**: 2026-02-27  
**커밋**: a642923  
**작성자**: GenSpark AI Assistant

---

## 📋 변경 사항 요약

### 1. 핵심 변경사항
**기존**: 지게차 자격증 보유 여부만 관리  
**변경**: 자격증 보유 여부와 별개로 **지게차 운전 능력** 필드 추가

### 2. 목적
- **운전 실태 파악**: 자격증이 없더라도 실제 지게차 운전 가능 여부 파악
- **배차 최적화**: 자격증과 무관하게 실제 운전 가능 인력 배치
- **교육 계획**: 자격증 미보유자 중 운전 가능 인력 식별하여 교육 계획 수립

---

## 🔧 데이터베이스 설계

### Employee 모델에 추가될 필드

```python
class Employee(Base):
    # ... 기존 필드들 ...
    
    # 자격증 정보
    has_cargo_license = Column(Boolean, default=False, nullable=False, 
                              comment='화물운송자격증 보유 여부')
    has_forklift_certificate = Column(Boolean, default=False, nullable=False,
                                     comment='지게차운전기능사 자격증 보유 여부')
    
    # 🆕 운전 능력 정보 (자격증과 별개)
    can_drive_forklift = Column(Boolean, default=False, nullable=False,
                               comment='지게차 운전 가능 여부 (자격증 무관, 실태 파악용)')
    
    # 자격증 상세 정보
    forklift_certificate_number = Column(String(50), comment='지게차 자격증 번호')
    forklift_certificate_issue_date = Column(Date, comment='지게차 자격증 발급일')
    forklift_certificate_expiry_date = Column(Date, comment='지게차 자격증 만료일')
```

### 필드 설명

| 필드명 | 타입 | 설명 | 용도 |
|--------|------|------|------|
| `has_forklift_certificate` | Boolean | 지게차운전기능사 자격증 보유 여부 | 법적 요건 확인 |
| `can_drive_forklift` | Boolean | 지게차 실제 운전 가능 여부 | 운영 배차 결정 |
| `forklift_certificate_number` | String | 자격증 번호 | 자격증 관리 |
| `forklift_certificate_issue_date` | Date | 발급일 | 유효성 확인 |
| `forklift_certificate_expiry_date` | Date | 만료일 | 갱신 알림 |

---

## 🎨 UI/UX 설계

### 1. 운전자 풀 (Driver Pool) 카드 표시

```
┌─────────────────────────────────────┐
│ 👤 김철수 (D001)                     │
│ 📞 010-1234-5678                     │
│ 🚗 1종 대형                          │
│ 📦 화물자격증 ✓                      │
│ 🔧 지게차 가능 ✓  [자격증 ✓]        │ ← 새로 추가
│ ⏰ 08:00-18:00 (10시간)             │
└─────────────────────────────────────┘
```

**표시 로직**:
- `🔧 지게차 가능 ✓`: `can_drive_forklift = true`
- `[자격증 ✓]`: `has_forklift_certificate = true`
- `[자격증 ✗]`: `has_forklift_certificate = false`

### 2. 필터 옵션

```
[상태 ▼] [차종 ▼] [면허 ▼] [배정상태 ▼] [🆕 지게차운전 ▼]
                                      └─ 전체
                                      └─ 운전 가능 (자격증 보유)
                                      └─ 운전 가능 (자격증 미보유)
                                      └─ 운전 불가
```

### 3. 인사카드 모달 - 자격증 탭

```
┌─────────────────────────────────────────────┐
│ [기본정보] [근무정보] [자격증] [급여정보]    │
├─────────────────────────────────────────────┤
│                                              │
│ 🚗 운전면허                                  │
│ ├─ 면허종류: [1종 대형 ▼]                   │
│ ├─ 면허번호: [____________]                 │
│ └─ 발급일: [____-__-__]                     │
│                                              │
│ 📦 화물운송자격증                            │
│ ├─ 보유여부: [✓] 보유  [ ] 미보유           │
│ ├─ 자격번호: [____________]                 │
│ └─ 유효기간: [____-__-__]                   │
│                                              │
│ 🔧 지게차 운전                               │ ← 새로 추가
│ ├─ 운전가능: [✓] 가능  [ ] 불가             │
│ ├─ 자격증보유: [✓] 보유  [ ] 미보유         │
│ ├─ 자격번호: [____________]                 │
│ ├─ 발급일: [____-__-__]                     │
│ └─ 만료일: [____-__-__]                     │
│                                              │
│ 💡 참고: 자격증 미보유 시에도 운전 가능     │
│         여부를 체크하면 실태 파악에 활용됩니다 │
└─────────────────────────────────────────────┘
```

---

## 🔍 필터링 로직

### 지게차 운전 능력 필터

```typescript
// 필터 상태
const [forkliftAbilityFilter, setForkliftAbilityFilter] = useState<'all' | 'with_cert' | 'without_cert' | 'unable'>('all');

// 필터링 로직
const filteredDrivers = drivers.filter(driver => {
  // ... 기존 필터들 ...
  
  // 지게차 운전 능력 필터
  if (forkliftAbilityFilter !== 'all') {
    if (forkliftAbilityFilter === 'with_cert') {
      // 운전 가능 + 자격증 보유
      if (!driver.can_drive_forklift || !driver.has_forklift_certificate) return false;
    } else if (forkliftAbilityFilter === 'without_cert') {
      // 운전 가능 + 자격증 미보유
      if (!driver.can_drive_forklift || driver.has_forklift_certificate) return false;
    } else if (forkliftAbilityFilter === 'unable') {
      // 운전 불가
      if (driver.can_drive_forklift) return false;
    }
  }
  
  return true;
});
```

---

## 📊 활용 시나리오

### 시나리오 1: 자격증 미보유 운전자 관리
**상황**: 김철수는 지게차 자격증은 없지만 실제 운전 가능  
**등록**:
- `can_drive_forklift = true`
- `has_forklift_certificate = false`

**활용**:
- 배차 시 지게차 작업 가능 인력으로 배정 가능
- 자격증 취득 교육 대상자로 식별
- 운전자 풀에서 "지게차 가능 (자격증 미보유)" 배지 표시

### 시나리오 2: 자격증 보유 비운전자
**상황**: 박영희는 지게차 자격증은 있지만 현재 운전 불가 (부상 등)  
**등록**:
- `can_drive_forklift = false`
- `has_forklift_certificate = true`

**활용**:
- 배차 시 지게차 작업에서 제외
- 복귀 후 즉시 지게차 작업 배정 가능
- 자격증 관리 및 갱신 알림 유지

### 시나리오 3: 완전 보유 운전자
**상황**: 이민수는 자격증 보유 + 실제 운전 가능  
**등록**:
- `can_drive_forklift = true`
- `has_forklift_certificate = true`

**활용**:
- 우선 배차 대상
- 운전자 풀에서 "지게차 가능 (자격증 보유)" 배지 표시
- 법적 요건 + 실제 가능 모두 충족

---

## 🔄 마이그레이션 계획

### 1. 데이터베이스 마이그레이션

```sql
-- 1단계: 컬럼 추가
ALTER TABLE employees 
ADD COLUMN can_drive_forklift BOOLEAN DEFAULT FALSE NOT NULL 
COMMENT '지게차 운전 가능 여부 (자격증 무관, 실태 파악용)';

ALTER TABLE employees 
ADD COLUMN has_forklift_certificate BOOLEAN DEFAULT FALSE NOT NULL 
COMMENT '지게차운전기능사 자격증 보유 여부';

ALTER TABLE employees 
ADD COLUMN forklift_certificate_number VARCHAR(50) 
COMMENT '지게차 자격증 번호';

ALTER TABLE employees 
ADD COLUMN forklift_certificate_issue_date DATE 
COMMENT '지게차 자격증 발급일';

ALTER TABLE employees 
ADD COLUMN forklift_certificate_expiry_date DATE 
COMMENT '지게차 자격증 만료일';

-- 2단계: 기존 데이터 마이그레이션 (필요 시)
-- 기존에 has_forklift_license 필드가 있었다면
UPDATE employees 
SET has_forklift_certificate = has_forklift_license,
    can_drive_forklift = has_forklift_license
WHERE has_forklift_license = TRUE;
```

### 2. API 엔드포인트 업데이트

```python
# GET /api/v1/employees/drivers
# Response 예시
{
  "total": 50,
  "items": [
    {
      "id": 1,
      "employee_code": "D001",
      "name": "김철수",
      "phone": "010-1234-5678",
      "license_type": "1종 대형",
      "has_cargo_license": true,
      "can_drive_forklift": true,          # 🆕 추가
      "has_forklift_certificate": false,    # 🆕 추가
      "work_hours": "08:00-18:00"
    }
  ]
}

# GET /api/v1/employees/drivers?can_drive_forklift=true&has_forklift_certificate=false
# 지게차 운전 가능 + 자격증 미보유 운전자 조회
```

---

## 📦 구현 단계

### Phase 1: 백엔드 (1일)
- [x] Employee 모델에 필드 추가
- [ ] 마이그레이션 스크립트 작성
- [ ] API 스키마 업데이트 (Pydantic)
- [ ] 필터링 로직 구현

### Phase 2: 프론트엔드 (2일)
- [ ] 운전자 풀 카드 UI 업데이트
- [ ] 지게차 운전 능력 필터 추가
- [ ] 인사카드 모달 자격증 탭 수정
- [ ] 배지 표시 로직 구현

### Phase 3: 테스트 & 배포 (1일)
- [ ] 필터링 로직 테스트
- [ ] UI/UX 통합 테스트
- [ ] 마이그레이션 테스트
- [ ] 프로덕션 배포

---

## 🎯 기대 효과

### 1. 운영 효율성 향상
- **배차 정확도**: 실제 운전 가능 인력 파악으로 배차 실패율 감소
- **인력 활용**: 자격증 미보유자도 실제 가능하면 배치 가능

### 2. 인사 관리 개선
- **교육 계획**: 운전 가능 + 자격증 미보유자 우선 교육
- **자격증 관리**: 보유자의 만료일 추적 및 갱신 알림

### 3. 법적 리스크 관리
- **명확한 구분**: 자격증 보유와 실제 능력 분리 관리
- **감사 대비**: 자격증 보유 현황 명확히 파악

---

## 📝 다음 단계

1. **Phase 1 시작**: 백엔드 모델 및 마이그레이션 구현
2. **데이터 정리**: 기존 운전자 데이터의 지게차 능력 정보 수집
3. **UI 프로토타입**: 운전자 풀 카드 디자인 확정
4. **테스트 계획**: 필터링 및 배차 시나리오 테스트 케이스 작성

---

## 🔗 관련 문서

- `HR_SYSTEM_DESIGN.md` - 전체 인사 시스템 설계
- `FORKLIFT_ABILITY_DESIGN.md` - 지게차 운전능력 필드 상세 설계
- `VEHICLE_DRIVER_ASSIGNMENT_FIX.md` - 차량-운전자 배정 시스템

---

**커밋**: a642923  
**리포지토리**: https://github.com/rpaakdi1-spec/3-  
**브랜치**: main
