# 거래처별 배차 템플릿 가이드

## 📋 개요

거래처마다 다른 배차 형식을 자동으로 파싱하기 위한 템플릿 시스템입니다.

## 🎯 기능

- **자동 거래처 식별**: 배차 텍스트에서 키워드로 거래처 자동 감지
- **고정 좌표 사용**: API 비용 절감 (좌표 재계산 불필요)
- **커스터마이징 가능**: 거래처별 파싱 규칙 완전 맞춤 설정
- **쉬운 관리**: 데이터베이스에 저장되어 UI에서 수정 가능

---

## 📦 데이터베이스 마이그레이션

### 1. 테이블 생성

```bash
# 서버에서 실행:
cd /root/uvis
docker compose exec db psql -U uvis_user -d uvis_db < backend/migrations/create_dispatch_template.sql
```

### 2. 확인

```sql
-- 템플릿 목록 조회
SELECT id, name, is_active, default_pickup_address 
FROM dispatch_templates;

-- 목우촌 템플릿 상세 조회
SELECT * FROM dispatch_templates WHERE name = '목우촌';
```

---

## 🔧 템플릿 구조

### 필수 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `name` | string | 템플릿 이름 (예: "목우촌", "하림") |
| `detection_keywords` | JSON array | 식별 키워드 (예: `["목우촌", "mokwoojon"]`) |
| `parsing_rules` | JSON object | 파싱 규칙 (아래 참조) |

### 선택 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `default_pickup_address` | string | 기본 상차지 주소 |
| `default_delivery_address` | string | 기본 하차지 주소 |
| `pickup_latitude` | float | 상차지 위도 (고정값) |
| `pickup_longitude` | float | 상차지 경도 (고정값) |
| `delivery_latitude` | float | 하차지 위도 (고정값) |
| `delivery_longitude` | float | 하차지 경도 (고정값) |

---

## 📐 파싱 규칙 (parsing_rules)

### JSON 구조

```json
{
  "time_pattern": "(\\d{1,2}:\\d{2})",
  "product_pattern": "식육|육가공",
  "tonnage_pattern": "(\\d+\\.?\\d*)톤",
  "temperature_keywords": {
    "냉동": "FROZEN",
    "냉장": "REFRIGERATED"
  },
  "default_temperature": "REFRIGERATED",
  "pallet_calculation": {
    "18": 18,
    "11": 16,
    "5": 10,
    "default_multiplier": 2
  },
  "delivery_time_offset_hours": 4,
  "notes_template": "자동 파싱: {client_name} 배차"
}
```

### 상세 설명

#### 1. `time_pattern` (정규식)
- 시간 추출 패턴
- 예: `"(\\d{1,2}:\\d{2})"` → `13:00`, `9:30`

#### 2. `product_pattern` (정규식)
- 제품명 추출 패턴
- 예: `"식육|육가공"` → "식육", "육가공"

#### 3. `tonnage_pattern` (정규식)
- 톤수 추출 패턴
- 예: `"(\\d+\\.?\\d*)톤"` → `18톤`, `11.5톤`

#### 4. `temperature_keywords` (매핑)
- 온도대 키워드 → enum 매핑
- `"냉동"` → `"FROZEN"`
- `"냉장"` → `"REFRIGERATED"`
- 키워드 없으면 `default_temperature` 사용

#### 5. `pallet_calculation` (매핑)
- 톤수 → 팔레트 수 변환
- `18톤` → `18 팔레트`
- `11톤` → `16 팔레트`
- `5톤` → `10 팔레트`
- 그 외 → `톤수 × default_multiplier`

#### 6. `delivery_time_offset_hours` (숫자)
- 하차 시간 = 상차 시간 + offset
- 예: `4` → 13:00 상차 → 17:00 하차

#### 7. `notes_template` (문자열 템플릿)
- 주문 노트 자동 생성
- `{client_name}` → 거래처 이름으로 치환

---

## ✏️ 새 템플릿 추가 방법

### 예시: "하림" 템플릿 추가

```sql
INSERT INTO dispatch_templates (
    name,
    description,
    is_active,
    detection_keywords,
    default_pickup_address,
    default_delivery_address,
    pickup_latitude,
    pickup_longitude,
    delivery_latitude,
    delivery_longitude,
    parsing_rules
) VALUES (
    '하림',
    '하림 배차 자동 파싱 템플릿',
    TRUE,
    '["하림", "harim"]'::jsonb,
    '전북 익산시 함열읍 익산대로 111',
    '경기도 용인시 처인구 남사읍 경기동로 222',
    35.9, -- 예시 좌표
    126.9,
    37.2,
    127.1,
    '{
        "time_pattern": "(\\d{1,2}:\\d{2})",
        "product_pattern": "닭|치킨",
        "tonnage_pattern": "(\\d+\\.?\\d*)톤",
        "temperature_keywords": {
            "냉동": "FROZEN"
        },
        "default_temperature": "FROZEN",
        "pallet_calculation": {
            "15": 20,
            "10": 15,
            "default_multiplier": 2
        },
        "delivery_time_offset_hours": 3,
        "notes_template": "자동 파싱: 하림 배차"
    }'::jsonb
);
```

---

## 🔄 템플릿 수정 방법

### SQL로 직접 수정

```sql
-- 목우촌 템플릿의 하차 시간 offset을 5시간으로 변경
UPDATE dispatch_templates
SET parsing_rules = jsonb_set(
    parsing_rules,
    '{delivery_time_offset_hours}',
    '5'::jsonb
)
WHERE name = '목우촌';

-- 새 온도대 키워드 추가
UPDATE dispatch_templates
SET parsing_rules = jsonb_set(
    parsing_rules,
    '{temperature_keywords,상온}',
    '"AMBIENT"'::jsonb
)
WHERE name = '목우촌';
```

### API로 수정 (추후 구현 예정)

```http
PATCH /api/v1/dispatch-templates/{id}
Content-Type: application/json

{
  "parsing_rules": {
    "delivery_time_offset_hours": 5
  }
}
```

---

## 🧪 테스트

### 1. 템플릿 조회 테스트

```bash
# 서버에서 실행:
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT 
    id,
    name,
    is_active,
    detection_keywords,
    default_pickup_address,
    parsing_rules->>'delivery_time_offset_hours' as offset_hours
FROM dispatch_templates
WHERE is_active = TRUE;
"
```

### 2. 목우촌 배차 파싱 테스트

브라우저에서:
1. 주문 목록 → **배차 일괄 등록**
2. 텍스트 입력:
```
**3/7(금)목우촌 오후배차**
13:00 / 식육18톤(냉동)
13:30 / 식육11톤
```
3. **파싱하기** 클릭
4. 자동으로 목우촌 템플릿 적용 확인

---

## 📝 향후 계획

### Phase 1: UI 관리 페이지 (진행 중)
- [ ] 템플릿 목록 조회
- [ ] 템플릿 생성/수정/삭제
- [ ] 파싱 규칙 비주얼 에디터
- [ ] 실시간 파싱 미리보기

### Phase 2: 고급 기능
- [ ] 템플릿 복사 기능
- [ ] 템플릿 버전 관리
- [ ] 파싱 실패 로그 수집
- [ ] AI 기반 템플릿 자동 생성

---

## 🆘 문제 해결

### Q1: 템플릿이 자동으로 선택되지 않아요
**A**: `detection_keywords`에 배차 텍스트에 포함된 키워드가 있는지 확인하세요.

```sql
-- 키워드 확인
SELECT name, detection_keywords FROM dispatch_templates;

-- 키워드 추가
UPDATE dispatch_templates
SET detection_keywords = detection_keywords || '["새키워드"]'::jsonb
WHERE name = '목우촌';
```

### Q2: 파싱 결과가 이상해요
**A**: `parsing_rules`의 정규식 패턴을 확인하세요.

```sql
-- 파싱 규칙 확인
SELECT name, parsing_rules FROM dispatch_templates WHERE name = '목우촌';

-- 패턴 수정
UPDATE dispatch_templates
SET parsing_rules = jsonb_set(
    parsing_rules,
    '{time_pattern}',
    '"(\\d{1,2}:\\d{2})"'::jsonb
)
WHERE name = '목우촌';
```

### Q3: 좌표가 적용되지 않아요
**A**: 좌표 필드가 NULL이 아닌지 확인하세요.

```sql
-- 좌표 확인
SELECT name, pickup_latitude, pickup_longitude 
FROM dispatch_templates 
WHERE name = '목우촌';

-- 좌표 설정
UPDATE dispatch_templates
SET 
    pickup_latitude = 35.8087,
    pickup_longitude = 126.8919
WHERE name = '목우촌';
```

---

## 📞 문의

템플릿 관련 문의사항이 있으시면 개발팀에 연락주세요.
