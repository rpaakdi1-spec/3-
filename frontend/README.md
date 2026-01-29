# Cold Chain Dispatch System - Frontend

React + TypeScript + Vite 기반 프론트엔드 애플리케이션

## 🚀 기술 스택

- **React 18**: UI 라이브러리
- **TypeScript**: 타입 안정성
- **Vite**: 빌드 도구
- **Tailwind CSS**: 스타일링
- **Zustand**: 상태 관리
- **React Router**: 라우팅
- **Axios**: HTTP 클라이언트
- **Chart.js**: 차트 시각화
- **React Leaflet**: 지도 표시
- **React Hot Toast**: 토스트 알림
- **Lucide React**: 아이콘
- **QRCode.react**: QR 코드 생성

## 📁 프로젝트 구조

```
src/
├── api/              # API 클라이언트
│   └── client.ts
├── components/       # React 컴포넌트
│   ├── common/       # 공통 컴포넌트
│   ├── dashboard/    # 대시보드 컴포넌트
│   ├── orders/       # 주문 컴포넌트
│   ├── dispatches/   # 배차 컴포넌트
│   └── tracking/     # 추적 컴포넌트
├── pages/            # 페이지 컴포넌트
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   ├── OrdersPage.tsx
│   ├── DispatchesPage.tsx
│   └── TrackingPage.tsx
├── store/            # Zustand 스토어
│   └── authStore.ts
├── types/            # TypeScript 타입 정의
│   └── index.ts
├── styles/           # 스타일 파일
│   └── index.css
├── App.tsx           # 메인 App 컴포넌트
└── main.tsx          # 진입점
```

## 🛠️ 설치 및 실행

### 1. 의존성 설치

```bash
cd frontend
npm install
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 API URL을 설정하세요:

```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### 3. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 http://localhost:5173 접속

### 4. 프로덕션 빌드

```bash
npm run build
```

빌드된 파일은 `dist/` 디렉토리에 생성됩니다.

### 5. 프로덕션 미리보기

```bash
npm run preview
```

## 🎨 주요 기능

### 1. 인증 시스템
- JWT 기반 로그인/로그아웃
- 자동 토큰 갱신
- Protected Routes

### 2. 대시보드
- 실시간 통계 표시
- 주간 배송 추이 차트
- 차량 현황 표시
- 빠른 작업 링크

### 3. 주문 관리
- 주문 목록 조회
- 검색 및 필터링
- 주문 상태별 통계
- 주문 상세 정보

### 4. 배차 관리
- 실시간 배차 목록
- 지도에 차량 위치 표시 (Leaflet)
- 배차 상태별 통계
- 배차 상세 정보

### 5. 배송 추적 (공개)
- 추적번호로 배송 조회
- 실시간 위치 확인
- 배송 이력 타임라인
- QR 코드 공유

## 🎯 컴포넌트

### 공통 컴포넌트

- **Button**: 재사용 가능한 버튼 컴포넌트
- **Card**: 카드 레이아웃 컴포넌트
- **Input**: 입력 필드 컴포넌트
- **Loading**: 로딩 스피너 컴포넌트
- **Layout**: 메인 레이아웃 (사이드바 포함)
- **Sidebar**: 네비게이션 사이드바

### 페이지 컴포넌트

- **LoginPage**: 로그인 페이지
- **DashboardPage**: 대시보드
- **OrdersPage**: 주문 관리
- **DispatchesPage**: 배차 관리 및 실시간 모니터링
- **TrackingPage**: 배송 추적 (공개 페이지)

## 📱 반응형 디자인

모든 페이지는 다음 화면 크기에 최적화되어 있습니다:

- **Mobile**: < 768px
- **Tablet**: 768px ~ 1024px
- **Desktop**: > 1024px

## 🔐 인증 흐름

1. 사용자가 로그인 페이지에서 credentials 입력
2. API 서버로 로그인 요청
3. JWT 토큰 수신 및 localStorage에 저장
4. 모든 API 요청에 Bearer 토큰 포함
5. 토큰 만료 시 자동으로 로그인 페이지로 리다이렉트

## 🗺️ 지도 기능

React Leaflet을 사용하여 OpenStreetMap 기반 지도 표시:

- 실시간 차량 위치 마커
- 배송 경로 표시
- 마커 클릭 시 상세 정보 팝업

## 📊 차트 기능

Chart.js를 사용하여 다양한 통계 차트 표시:

- 라인 차트: 주간 배송 추이
- 바 차트: 월간 실적
- 파이 차트: 배송 상태 분포

## 🎨 스타일링

Tailwind CSS 유틸리티 클래스 사용:

- 일관된 디자인 시스템
- 반응형 디자인
- 다크 모드 준비
- 커스텀 색상 팔레트

## 🧪 개발 팁

### 1. API 모킹

개발 중 백엔드 없이 작업하려면 API 모킹을 사용하세요:

```typescript
// src/api/client.ts에서
const mockOrders = [
  { id: 1, order_number: 'ORD001', ... },
];

async getOrders() {
  // return await this.client.get('/orders');
  return { items: mockOrders };
}
```

### 2. Hot Module Replacement (HMR)

Vite는 HMR을 지원하므로 코드 변경 시 즉시 반영됩니다.

### 3. TypeScript 에러 확인

```bash
npx tsc --noEmit
```

## 🐛 트러블슈팅

### 1. Leaflet 지도가 표시되지 않음

Leaflet CSS가 올바르게 import되었는지 확인:

```typescript
import 'leaflet/dist/leaflet.css';
```

### 2. CORS 에러

백엔드 API 서버에서 CORS를 허용해야 합니다:

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 환경 변수가 적용되지 않음

- Vite는 `VITE_` 접두사가 필요합니다
- 환경 변수 변경 후 dev 서버를 재시작하세요

## 📦 배포

### Docker를 사용한 배포

```bash
# 프로덕션 빌드
docker build -t coldchain-frontend -f Dockerfile .

# 컨테이너 실행
docker run -p 80:80 coldchain-frontend
```

### Nginx를 사용한 배포

빌드 후 `dist/` 디렉토리를 Nginx의 웹 루트에 복사:

```bash
npm run build
cp -r dist/* /var/www/html/
```

## 📚 추가 리소스

- [React 공식 문서](https://react.dev/)
- [TypeScript 공식 문서](https://www.typescriptlang.org/)
- [Vite 공식 문서](https://vitejs.dev/)
- [Tailwind CSS 공식 문서](https://tailwindcss.com/)
- [React Leaflet 공식 문서](https://react-leaflet.js.org/)
- [Chart.js 공식 문서](https://www.chartjs.org/)

## 🤝 기여

버그 리포트, 기능 제안, Pull Request를 환영합니다!

## 📄 라이선스

MIT License

---

**작성일**: 2026-01-27  
**작성자**: GenSpark AI Developer  
**버전**: 1.0.0
