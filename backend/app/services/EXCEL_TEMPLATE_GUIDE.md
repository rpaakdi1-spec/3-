# Excel Template Service - 자동 양식 업데이트 가이드

## 개요

이 서비스는 **엑셀 템플릿 생성**과 **엑셀 업로드 파싱**을 중앙에서 관리합니다.
필드를 추가하거나 수정할 때 한 곳만 변경하면 템플릿과 업로드 로직이 자동으로 업데이트됩니다.

## 파일 구조

```
backend/app/services/
├── excel_template_service.py  # 템플릿 생성 및 매핑 정의
└── excel_upload_service.py    # 엑셀 업로드 파싱 (템플릿 서비스의 매핑 사용)
```

## 필드 추가/수정 방법

### 1️⃣ 데이터베이스 모델 수정

**예시: 차량(Vehicle) 모델에 새 필드 추가**

```python
# backend/app/models/vehicle.py
class Vehicle(Base, IDMixin, TimestampMixin):
    # ... 기존 필드 ...
    
    # 새 필드 추가
    insurance_expiry_date: Mapped[Optional[date]] = mapped_column(
        Date, 
        comment="보험만료일"
    )
```

### 2️⃣ 마이그레이션 생성 및 실행

```bash
# 마이그레이션 파일 생성
cd backend
alembic revision --autogenerate -m "add_insurance_expiry_to_vehicle"

# 마이그레이션 실행
alembic upgrade head
```

### 3️⃣ API 스키마 업데이트

```python
# backend/app/schemas/vehicle.py
class VehicleBase(BaseModel):
    # ... 기존 필드 ...
    
    # 새 필드 추가
    insurance_expiry_date: Optional[date] = Field(
        None, 
        description="보험만료일"
    )
```

### 4️⃣ 엑셀 템플릿 서비스 매핑 업데이트 ✨

**이 단계가 핵심입니다!**

```python
# backend/app/services/excel_template_service.py

class ExcelTemplateService:
    COLUMN_MAPPINGS = {
        "vehicles": {
            # ... 기존 매핑 ...
            
            # 새 매핑 추가 (포맷: "한글 헤더": (field_name, 예시값, 기본값))
            "보험만료일": ("insurance_expiry_date", "2026-12-31", ""),
        }
    }
```

### 5️⃣ 완료! 🎉

이제 다음이 **자동으로** 업데이트됩니다:
- ✅ 엑셀 템플릿 다운로드 → "보험만료일" 열 포함
- ✅ 엑셀 업로드 → "보험만료일" 자동 파싱
- ✅ 컬럼 순서 자동 관리

## 매핑 포맷 설명

```python
"한글 헤더": (field_name, example_value, default_value)
```

| 파라미터 | 설명 | 예시 |
|---------|------|------|
| `"한글 헤더"` | 엑셀 파일의 컬럼 헤더 (한글) | `"보험만료일"` |
| `field_name` | 데이터베이스 필드명 | `"insurance_expiry_date"` |
| `example_value` | 예시 행에 표시될 값 | `"2026-12-31"` |
| `default_value` | 빈 행의 기본값 | `""` (빈 문자열) |

## 예시: 주문 관리에 새 필드 추가

### 시나리오
주문에 "배송메모" 필드를 추가하고 싶습니다.

### 1️⃣ 모델 수정
```python
# backend/app/models/order.py
delivery_memo: Mapped[Optional[str]] = mapped_column(
    String(200), 
    comment="배송메모"
)
```

### 2️⃣ 스키마 수정
```python
# backend/app/schemas/order.py
delivery_memo: Optional[str] = Field(None, max_length=200, description="배송메모")
```

### 3️⃣ 템플릿 매핑 추가
```python
# backend/app/services/excel_template_service.py
COLUMN_MAPPINGS = {
    "orders": {
        # ... 기존 매핑 ...
        "배송메모": ("delivery_memo", "문 앞에 놓아주세요", ""),
    }
}
```

### 4️⃣ 완료!
- ✅ 주문 양식 다운로드 → "배송메모" 열 자동 추가
- ✅ 엑셀 업로드 → "배송메모" 자동 파싱

## 엔터티 타입별 매핑

현재 지원하는 엔터티 타입:

| 엔터티 | 파일명 | 시트명 |
|--------|--------|--------|
| `clients` | `clients_template.xlsx` | 거래처 |
| `orders` | `orders_template.xlsx` | 주문 |
| `vehicles` | `vehicles_template.xlsx` | 차량 |
| `drivers` | `drivers_template.xlsx` | 기사 |

## API 사용 예시

### 템플릿 다운로드 API
```python
# backend/app/api/vehicles.py
from app.services.excel_template_service import ExcelTemplateService

@router.get("/template/download")
async def download_template():
    template_path = ExcelTemplateService.create_vehicles_template()
    return FileResponse(
        template_path,
        filename="vehicles_template.xlsx"
    )
```

### 엑셀 업로드 API
```python
# backend/app/api/vehicles.py
from app.services.excel_upload_service import ExcelUploadService

@router.post("/upload")
async def upload_vehicles(file: UploadFile, db: Session = Depends(get_db)):
    content = await file.read()
    result = await ExcelUploadService.upload_vehicles(db, content)
    return result
```

## 템플릿 정보 조회

템플릿의 구조 정보를 프로그래밍 방식으로 조회:

```python
from app.services.excel_template_service import ExcelTemplateService

# 차량 템플릿 정보 조회
info = ExcelTemplateService.get_template_info("vehicles")

# 출력 예시:
# {
#   "entity_type": "vehicles",
#   "num_columns": 19,
#   "columns": [
#     {
#       "korean_header": "차량코드",
#       "field_name": "code",
#       "example_value": "예시-V001",
#       "default_value": ""
#     },
#     ...
#   ]
# }
```

## 자주 묻는 질문 (FAQ)

### Q1: 컬럼 순서는 어떻게 정해지나요?
**A:** `COLUMN_MAPPINGS` 딕셔너리의 순서대로 컬럼이 생성됩니다. Python 3.7+는 딕셔너리 순서를 보장합니다.

### Q2: 기존 필드를 제거하면 어떻게 되나요?
**A:** `COLUMN_MAPPINGS`에서 해당 항목을 제거하면 템플릿과 업로드 로직에서 자동으로 제거됩니다.

### Q3: 필드명(한글 헤더)을 변경하려면?
**A:** `COLUMN_MAPPINGS`에서 한글 헤더를 변경하면 됩니다. 단, 기존 엑셀 파일과의 호환성이 깨질 수 있습니다.

### Q4: 여러 언어를 지원할 수 있나요?
**A:** 가능합니다. `COLUMN_MAPPINGS`를 언어별로 분리하고, 요청 헤더의 언어 설정에 따라 다른 매핑을 사용하도록 확장할 수 있습니다.

## 장점

✅ **중앙 관리**: 한 곳에서 모든 필드 정의
✅ **자동 동기화**: 템플릿과 업로드 로직 자동 일치
✅ **유지보수 용이**: 필드 추가/수정 시 한 줄만 변경
✅ **실수 방지**: 오타나 불일치 문제 사전 차단
✅ **확장 가능**: 새 엔터티 타입 쉽게 추가

## 변경 이력

### v2.0 (2026-01-29)
- 🎉 중앙 집중식 매핑 시스템 도입
- ✨ `get_korean_to_field_mapping()` 메서드 추가
- ✨ `get_template_info()` 메서드 추가
- 🔄 업로드 서비스가 템플릿 서비스의 매핑 사용

### v1.0 (이전)
- 각 함수에서 개별적으로 매핑 정의 (하드코딩)

## 참고

- 템플릿 파일 저장 위치: `backend/data/templates/`
- 로거: `loguru` 사용
- 엑셀 엔진: `openpyxl`
