# 🚀 빠른 시작 가이드 (Quick Start Guide)

## 현재 상태

✅ **Phase 1 - 핵심 인프라 구축 완료**

- [x] 프로젝트 구조 설정
- [x] 데이터베이스 모델 설계 (6개 테이블)
- [x] FastAPI 백엔드 설정
- [x] 엑셀 템플릿 생성 기능
- [x] 네이버 지도 API 서비스 통합
- [x] 환경 설정 및 의존성 관리

## 🌐 서비스 URL

**API 서버**: https://8000-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai

- **API 문서 (Swagger)**: https://8000-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai/docs
- **대체 문서 (ReDoc)**: https://8000-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai/redoc
- **Health Check**: https://8000-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai/health

## 📊 데이터베이스 구조

### 1. clients (거래처 마스터)
```sql
- id: 고유 ID
- code: 거래처 코드 (CUST-0001)
- name: 거래처명
- client_type: 상차/하차/양쪽
- address: 주소
- latitude/longitude: 좌표
- geocoded: 지오코딩 완료 여부
- pickup/delivery times: 운영 시간
- has_forklift: 지게차 유무
```

### 2. vehicles (차량 마스터)
```sql
- id: 고유 ID
- code: 차량 코드 (TRUCK-001)
- plate_number: 차량번호
- vehicle_type: 냉동/냉장/겸용/상온
- max_pallets: 최대 팔레트 수
- max_weight_kg: 최대 중량
- uvis_device_id: UVIS 단말기 ID
- status: 차량 상태
```

### 3. drivers (기사 마스터)
```sql
- id: 고유 ID
- code: 기사 코드 (DRV-001)
- name: 기사명
- phone: 전화번호
- work_start_time/work_end_time: 근무 시간
- max_work_hours: 최대 근무 시간
```

### 4. orders (주문)
```sql
- id: 고유 ID
- order_number: 주문번호 (ORD-001)
- temperature_zone: 냉동/냉장/상온
- pickup_client_id: 상차 거래처
- delivery_client_id: 하차 거래처
- pallet_count: 팔레트 수
- weight_kg: 중량
- status: 주문 상태
```

### 5. dispatches (배차 계획)
```sql
- id: 고유 ID
- dispatch_number: 배차번호
- dispatch_date: 배차 일자
- vehicle_id: 차량
- driver_id: 기사
- total_orders: 총 주문 건수
- total_distance_km: 총 거리
- optimization_score: 최적화 점수
```

### 6. dispatch_routes (배차 경로)
```sql
- id: 고유 ID
- dispatch_id: 배차 ID
- sequence: 경로 순서
- route_type: 차고지출발/상차/하차/차고지복귀
- order_id: 주문 ID
- estimated_arrival_time: 예상 도착 시간
```

## 📝 엑셀 템플릿

템플릿 파일은 자동 생성되어 `backend/data/templates/`에 저장됩니다:

### 1. clients_template.xlsx
| 거래처코드 | 거래처명 | 구분 | 주소 | 상차가능시작 | 지게차유무 |
|-----------|---------|------|------|------------|-----------|
| CUST-0001 | (주)서울냉동 | 상차 | 서울 송파구... | 09:00 | Y |

### 2. orders_template.xlsx
| 주문번호 | 온도대 | 팔레트수 | 중량(kg) | 상차거래처코드 | 하차거래처코드 |
|---------|--------|---------|---------|-------------|-------------|
| ORD-001 | 냉동 | 6 | 3000 | CUST-0001 | CUST-0002 |

### 3. vehicles_template.xlsx
| 차량코드 | 차량번호 | 차량타입 | 최대팔레트 | UVIS단말기ID |
|---------|---------|---------|-----------|-------------|
| TRUCK-001 | 12가3456 | 냉동 | 16 | UVIS-DVC-12345 |

### 4. drivers_template.xlsx
| 기사코드 | 기사명 | 전화번호 | 근무시작시간 | 근무종료시간 |
|---------|--------|---------|------------|------------|
| DRV-001 | 김기사 | 010-1234-5678 | 08:00 | 18:00 |

## 🔌 API 엔드포인트 (예정)

### 거래처 관리
- `GET /api/v1/clients` - 거래처 목록 조회
- `POST /api/v1/clients` - 거래처 등록
- `POST /api/v1/clients/upload` - 엑셀 일괄 업로드
- `POST /api/v1/clients/geocode` - 지오코딩 실행

### 차량 관리
- `GET /api/v1/vehicles` - 차량 목록 조회
- `POST /api/v1/vehicles` - 차량 등록
- `POST /api/v1/vehicles/upload` - 엑셀 일괄 업로드

### 주문 관리
- `GET /api/v1/orders` - 주문 목록 조회
- `POST /api/v1/orders` - 주문 등록
- `POST /api/v1/orders/upload` - 엑셀 일괄 업로드

### 배차 관리
- `POST /api/v1/dispatches/optimize` - AI 최적 배차 생성
- `GET /api/v1/dispatches` - 배차 목록 조회
- `PUT /api/v1/dispatches/{id}/confirm` - 배차 확정

## 🎯 다음 단계

### 즉시 개발 가능한 항목:

1. **CRUD API 구현** (우선순위: 높음)
   - 거래처/차량/기사/주문 CRUD 엔드포인트
   - 엑셀 업로드 API 구현
   - 지오코딩 자동 실행

2. **AI 배차 로직** (우선순위: 높음)
   - Google OR-Tools VRP 적용
   - Hard constraints 구현
   - Soft constraints 최적화

3. **기본 웹 UI** (우선순위: 중간)
   - React 프론트엔드 설정
   - 데이터 입력 폼
   - 배차 결과 시각화

## 🛠️ 로컬 개발 환경 설정

### 1. 저장소 클론
```bash
git clone <repository-url>
cd webapp
```

### 2. 백엔드 설정
```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필수 값 입력:
# - SECRET_KEY (자동 생성됨)
# - NAVER_MAP_CLIENT_ID (필수)
# - NAVER_MAP_CLIENT_SECRET (필수)

# 서버 실행
python main.py
```

### 3. 간편 실행 (스크립트 사용)
```bash
# 루트 디렉토리에서
./start.sh
```

## 📚 참고 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [Google OR-Tools](https://developers.google.com/optimization)
- [네이버 지도 API](https://www.ncloud.com/product/applicationService/maps)

## 🔐 보안 주의사항

- ⚠️ `.env` 파일을 절대 Git에 커밋하지 마세요
- ⚠️ API 키를 코드에 직접 작성하지 마세요
- ⚠️ 프로덕션 환경에서는 HTTPS를 필수로 사용하세요

## 📞 문의

프로젝트 관련 문의는 개발팀에 연락 바랍니다.

---

**Made with ❤️ for Cold Chain Logistics**
