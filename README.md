# 팔레트 기반 AI 냉동·냉장 배차 시스템

냉동/냉장 화물 운송을 위한 AI 기반 자동 배차 시스템

## 📋 프로젝트 개요

이 시스템은 40대의 냉동/냉장 차량과 하루 평균 110건의 주문을 효율적으로 처리하기 위한 AI 배차 솔루션입니다.

### 핵심 목표

- ✅ 공차율 및 헛운행 최소화
- ✅ 온도대별(냉동/냉장/상온) 차량 자동 매칭
- ✅ 팔레트 단위 적재 관리 최적화
- ✅ 배차 담당자 의사결정 시간 70% 단축
- ✅ 실시간 GPS 모니터링 및 동적 재배차

### 주요 특징

- 🎯 **팔레트 중심 관리**: 톤수가 아닌 팔레트 개수로 적재 용량 관리
- ❄️ **온도대 제약**: 냉동(-18°C ~ -25°C), 냉장(0°C ~ 6°C) 엄격 구분
- 🗺️ **실제 경로 기반**: 네이버 지도 API로 실제 도로 거리/시간 계산
- 🚛 **삼성 UVIS 연동**: 실시간 차량 위치 및 온도 모니터링
- 🤖 **Google OR-Tools**: VRP 알고리즘으로 최적 배차 추천

## 🏗️ 기술 스택

### Backend
- **Framework**: FastAPI 0.109.0
- **Database**: SQLAlchemy 2.0 + SQLite (개발) / PostgreSQL (프로덕션)
- **AI/Optimization**: Google OR-Tools 9.8
- **Data Processing**: Pandas, OpenPyXL
- **Caching**: Redis 5.0
- **HTTP Client**: httpx, requests

### Frontend (예정)
- **Framework**: React 18 + TypeScript
- **UI Library**: Material-UI / Ant Design
- **State Management**: Redux Toolkit
- **Data Visualization**: Recharts, Leaflet

## 📁 프로젝트 구조

```
webapp/
├── backend/
│   ├── app/
│   │   ├── api/              # API 엔드포인트
│   │   ├── core/             # 핵심 설정 (config, database)
│   │   ├── models/           # SQLAlchemy 모델
│   │   ├── services/         # 비즈니스 로직
│   │   └── utils/            # 유틸리티 함수
│   ├── data/
│   │   ├── templates/        # 엑셀 템플릿
│   │   └── uploads/          # 업로드 파일
│   ├── main.py               # FastAPI 애플리케이션
│   ├── requirements.txt      # Python 의존성
│   └── dispatch.db           # SQLite 데이터베이스
├── frontend/                 # React 프론트엔드
├── tests/                    # 테스트 코드
├── docs/                     # 문서
├── logs/                     # 로그 파일
├── .env                      # 환경 변수
├── .env.example              # 환경 변수 템플릿
├── .gitignore
└── README.md
```

## 🚀 시작하기

### 사전 요구사항

- Python 3.10 이상
- Node.js 18 이상 (프론트엔드)
- Redis (선택사항)

### 설치 및 실행

#### 1. 저장소 클론

```bash
git clone <repository-url>
cd webapp
```

#### 2. 환경 변수 설정

```bash
# .env 파일 생성 (.env.example을 참고)
cp .env.example .env

# .env 파일 편집하여 필수 값 설정
# - NAVER_MAP_CLIENT_ID (필수)
# - NAVER_MAP_CLIENT_SECRET (필수)
# - SECRET_KEY (필수)
# - UVIS_API_KEY (선택)
```

#### 3. Backend 설정 및 실행

```bash
cd backend

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 애플리케이션 실행
python main.py
```

서버가 http://localhost:8000 에서 실행됩니다.

- API 문서: http://localhost:8000/docs
- 대체 API 문서: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

#### 4. Frontend 설정 및 실행 (예정)

```bash
cd frontend
npm install
npm run dev
```

## 🎯 핵심 기능

### 1. 거래처 마스터 관리

- ✅ 엑셀 일괄 업로드 지원
- ✅ 네이버 지도 API 자동 지오코딩
- ✅ 지오코딩 실패 시 수동 좌표 입력
- 거래처 구분: 상차지/하차지/양쪽
- 운영 시간 설정
- 지게차 시설 정보

### 2. AI 배차 로직

#### Hard Constraints (절대 위반 불가):
- ✅ 온도대 매칭 (냉동 → 냉동 차량만)
- ✅ 팔레트 수 초과 금지
- ✅ 중량 초과 금지
- ✅ 타임 윈도우 준수
- ✅ 기사 근무시간 준수
- ✅ 지게차 가능 거래처 확인

#### Soft Constraints (최적화 목표):
- 📉 공차거리 최소화
- 📉 총 주행거리 최소화
- ⚖️ 차량/기사 간 업무 균형

**알고리즘**: Google OR-Tools VRP (Vehicle Routing Problem)

### 3. 실시간 GPS 모니터링

- 삼성 UVIS 시스템 연동
- 10~30초 간격 위치 업데이트
- Redis 캐싱으로 빠른 조회
- 온도 이탈 실시간 알림
- 경로 이탈 감지

## 📊 데이터베이스 모델

### 주요 테이블

1. **clients** - 거래처 마스터
   - 상차지/하차지 정보
   - 좌표 및 지오코딩 상태
   - 운영 시간 및 시설 정보

2. **vehicles** - 차량 마스터
   - 온도대 구분 (냉동/냉장/겸용/상온)
   - 적재 용량 (팔레트 수, 중량)
   - UVIS 단말기 연동 정보

3. **drivers** - 기사 마스터
   - 연락처 및 근무시간
   - 자격증 정보

4. **orders** - 주문
   - 온도대 및 화물 정보
   - 타임 윈도우
   - 상차/하차 거래처

5. **dispatches** - 배차 계획
   - 차량 및 기사 배정
   - 최적화 점수
   - 총 거리 및 비용

6. **dispatch_routes** - 배차 경로 상세
   - 경로 순서
   - 각 지점별 도착/출발 시간
   - 적재 상태 추적

## 📝 엑셀 템플릿 사용법

템플릿 파일은 `backend/data/templates/` 디렉토리에 자동 생성됩니다.

### 1. 거래처 마스터 업로드 (`clients_template.xlsx`)

| 필드 | 설명 | 예시 |
|------|------|------|
| 거래처코드 | 고유 ID | CUST-0001 |
| 거래처명 | 상호명 | (주)서울냉동 |
| 구분 | 상차/하차/양쪽 | 상차 |
| 주소 | 기본 주소 | 서울 송파구 문정동 123 |
| 상차가능시작 | HH:MM 형식 | 09:00 |
| 지게차유무 | Y/N | Y |

### 2. 주문 업로드 (`orders_template.xlsx`)

| 필드 | 설명 | 예시 |
|------|------|------|
| 주문번호 | 고유 ID | ORD-001 |
| 온도대 | 냉동/냉장/상온 | 냉동 |
| 팔레트수 | 개수 | 6 |
| 중량(kg) | 킬로그램 | 3000 |

### 3. 차량 마스터 업로드 (`vehicles_template.xlsx`)

| 필드 | 설명 | 예시 |
|------|------|------|
| 차량코드 | 고유 ID | TRUCK-001 |
| UVIS단말기ID | UVIS 매핑 ID | UVIS-DVC-12345 |
| 차량타입 | 냉동/냉장/겸용/상온 | 냉동 |
| 최대팔레트 | 개수 | 16 |

## 🔐 보안 고려사항

- ✅ API 키는 환경 변수로 관리 (.env)
- ✅ Git에 민감 정보 커밋 금지 (.gitignore)
- ✅ HTTPS 통신 필수 (프로덕션)
- ✅ JWT 기반 인증 (구현 예정)
- ✅ CORS 설정으로 허용 도메인 제한

## 🛣️ 로드맵

### ✅ Phase 1: PoC (4주) - 진행 중

- [x] 프로젝트 구조 설정
- [x] 데이터베이스 모델 설계
- [x] 기본 설정 및 의존성 관리
- [x] 엑셀 템플릿 생성
- [ ] 거래처 업로드 및 지오코딩
- [ ] 주문/차량 CRUD API
- [ ] 기본 배차 로직 (5대/20건 규모)
- [ ] 간단한 웹 UI

### 📅 Phase 2: Pilot (8주)

- [ ] 실제 규모 적용 (40대/110건)
- [ ] AI 배차 고도화
- [ ] 실시간 대시보드
- [ ] UVIS 전체 연동
- [ ] 통계 리포트

### 📅 Phase 3: Production

- [ ] 동적 재배차
- [ ] ETA 예측 ML 모델
- [ ] 모바일 앱 (기사용)
- [ ] 고객용 추적 시스템

## 🤝 기여 가이드

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

This project is proprietary and confidential.

## 📞 연락처

프로젝트 관련 문의: [담당자 이메일]

---

**Made with ❤️ for Cold Chain Logistics**
