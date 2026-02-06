# Phase 8 프론트엔드 개발 계획

## 🎯 목표

Phase 8 백엔드 API를 활용하여 사용자 친화적인 재무/청구/정산 관리 화면 구현

## 📊 구현할 화면 목록

### 1. 재무 대시보드 (Financial Dashboard) ⭐ 최우선
**경로**: `/billing/dashboard`

**주요 기능**:
- 📊 실시간 재무 요약 카드
  - 총 매출
  - 미수금 현황
  - 정산 대기 금액
  - 현금 흐름
- 📈 월별 매출/수금 추이 차트 (Line Chart)
- 🏆 주요 고객 매출 순위 (Bar Chart)
- 📉 수금률 및 연체율 표시
- 📅 기간 선택 필터 (이번 달/지난 달/최근 3개월/최근 12개월)

**사용 API**:
- `GET /api/v1/billing/enhanced/dashboard/financial`
- `GET /api/v1/billing/enhanced/dashboard/trends`
- `GET /api/v1/billing/enhanced/dashboard/top-clients`

---

### 2. 요금 미리보기 컴포넌트 (Charge Preview) ⭐ 최우선
**위치**: 배차 등록 화면 내 컴포넌트

**주요 기능**:
- 📝 입력 폼
  - 고객 선택
  - 배차 날짜
  - 거리 (km)
  - 팔레트 수
  - 무게 (kg) - 선택사항
  - 차량 타입 (냉동/냉장/일반)
  - 긴급 여부
- 💰 실시간 요금 계산 결과 표시
  - 기본 요금 상세
  - 할증 내역
  - 할인 내역
  - 부가세
  - 최종 금액 (강조)
- 💡 안내 메시지 (주말 할증, 물량 할인 등)
- 🔄 자동 재계산 (입력값 변경 시)

**사용 API**:
- `POST /api/v1/billing/enhanced/preview`

---

### 3. 청구서 목록 및 상세 화면
**경로**: `/billing/invoices`

**목록 화면 기능**:
- 📋 청구서 테이블
  - 청구서 번호
  - 고객명
  - 청구 기간
  - 총 금액
  - 결제 금액
  - 미수금
  - 상태 (발행/결제/연체 등)
  - 발행일/결제기한
- 🔍 필터링
  - 기간 선택
  - 고객 선택
  - 상태 필터
- 📊 요약 통계
  - 총 청구 금액
  - 총 수금 금액
  - 총 미수금
- 📥 Excel 내보내기 버튼

**상세 화면 기능**:
- 청구서 정보
- 청구 항목 (line items)
- 결제 이력
- 전자세금계산서 상태
- PDF 다운로드 버튼
- 결제 처리 버튼 (관리자)

**사용 API**:
- `GET /api/v1/billing/invoices` (기존)
- `POST /api/v1/billing/enhanced/export`

---

### 4. 정산서 목록 및 승인 화면
**경로**: `/billing/settlements`

**목록 화면 기능**:
- 📋 정산서 테이블
  - 정산서 번호
  - 기사명
  - 정산 기간
  - 총 금액
  - 배차 건수
  - 승인 상태 (대기/승인/반려)
  - 생성일
- 🔍 필터링
  - 기간 선택
  - 기사 선택
  - 승인 상태
- 📊 요약 통계
  - 총 정산 금액
  - 승인 대기 건수
  - 지급 완료 금액

**승인 화면 기능**:
- 정산서 상세 정보
- 정산 항목 (배차별 수익)
- 승인 이력
- ✅ 승인 버튼
- ❌ 반려 버튼 (사유 입력)
- 💬 메모 입력

**사용 API**:
- `GET /api/v1/billing/settlements` (기존)
- `POST /api/v1/billing/enhanced/settlement-approval`
- `GET /api/v1/billing/enhanced/settlement-approval/{id}/history`

---

### 5. 자동 청구 스케줄 설정 화면
**경로**: `/billing/auto-schedule`

**주요 기능**:
- 📋 고객별 스케줄 목록
  - 고객명
  - 청구일
  - 활성화 상태
  - 이메일 자동 발송 여부
  - 다음 생성 예정일
- ➕ 스케줄 추가/수정 모달
  - 고객 선택
  - 청구일 선택 (1-28일)
  - 이메일 자동 발송 토글
  - 결제 알림 설정
  - 알림일 선택 (D-7, D-3, D-day)
- 🔄 활성화/비활성화 토글
- 📅 마지막 실행 이력

**사용 API**:
- `GET /api/v1/billing/enhanced/auto-schedule`
- `POST /api/v1/billing/enhanced/auto-schedule`

---

### 6. 통계 및 분석 화면
**경로**: `/billing/analytics`

**주요 기능**:
- 📊 청구 통계
  - 상태별 청구서 건수/금액
  - 평균 청구 금액
  - 수금 효율
- 📈 정산 통계
  - 승인율
  - 평균 승인 소요일
  - 기사별 정산 현황
- 📉 월별 비교 차트
- 📅 기간 선택 필터

**사용 API**:
- `GET /api/v1/billing/enhanced/statistics/billing`
- `GET /api/v1/billing/enhanced/statistics/settlement`

---

## 🎨 UI/UX 디자인 가이드

### 컬러 스킴
- **주요 색상**:
  - 매출/수익: `#10b981` (green-500)
  - 지출/비용: `#ef4444` (red-500)
  - 대기/보류: `#f59e0b` (amber-500)
  - 정보: `#3b82f6` (blue-500)

### 컴포넌트 라이브러리
- **차트**: Recharts / Chart.js
- **테이블**: TanStack Table (React Table v8)
- **폼**: React Hook Form + Zod
- **UI**: Tailwind CSS + shadcn/ui
- **아이콘**: Lucide React

### 레이아웃
- **대시보드**: 4x2 그리드 카드 레이아웃
- **테이블**: 반응형 테이블 + 페이지네이션
- **차트**: 최소 높이 300px, 반응형

---

## 📁 파일 구조

```
frontend/src/
├── pages/
│   └── billing/
│       ├── Dashboard.tsx              # 재무 대시보드
│       ├── InvoiceList.tsx           # 청구서 목록
│       ├── InvoiceDetail.tsx         # 청구서 상세
│       ├── SettlementList.tsx        # 정산서 목록
│       ├── SettlementApproval.tsx    # 정산 승인
│       ├── AutoSchedule.tsx          # 자동 청구 스케줄
│       └── Analytics.tsx             # 통계 분석
├── components/
│   └── billing/
│       ├── ChargePreview.tsx         # 요금 미리보기
│       ├── FinancialSummaryCard.tsx  # 재무 요약 카드
│       ├── RevenueTrendChart.tsx     # 매출 추이 차트
│       ├── TopClientsChart.tsx       # 주요 고객 차트
│       ├── InvoiceTable.tsx          # 청구서 테이블
│       ├── SettlementTable.tsx       # 정산서 테이블
│       └── ApprovalForm.tsx          # 승인 폼
├── hooks/
│   └── billing/
│       ├── useBillingDashboard.ts    # 대시보드 데이터 훅
│       ├── useChargePreview.ts       # 요금 미리보기 훅
│       ├── useInvoices.ts            # 청구서 관리 훅
│       ├── useSettlements.ts         # 정산서 관리 훅
│       └── useAutoSchedule.ts        # 자동 스케줄 훅
└── api/
    └── billing-enhanced.ts           # Phase 8 API 클라이언트
```

---

## 🚀 구현 우선순위

### Week 1: 핵심 기능
1. ⭐ **재무 대시보드** - 가장 중요한 화면
2. ⭐ **요금 미리보기** - 배차 등록 시 필수
3. **청구서 목록** - 기존 화면 개선

### Week 2: 관리 기능
4. **정산 승인 화면** - 워크플로우 구현
5. **자동 청구 스케줄** - 자동화 설정
6. **통계 분석** - 인사이트 제공

### Week 3: 최적화 & 개선
7. 차트 성능 최적화
8. 에러 처리 강화
9. 반응형 디자인 개선
10. 사용자 피드백 반영

---

## 📊 기술 스택

- **React 18** + TypeScript
- **React Router v6** - 라우팅
- **TanStack Query (React Query)** - 서버 상태 관리
- **Zustand** - 클라이언트 상태 관리
- **Axios** - HTTP 클라이언트
- **React Hook Form** - 폼 관리
- **Zod** - 유효성 검증
- **Recharts** - 차트 라이브러리
- **Tailwind CSS** - 스타일링
- **shadcn/ui** - UI 컴포넌트
- **Lucide React** - 아이콘

---

## 🎯 성공 지표

### 사용성
- ✅ 요금 미리보기 응답 시간 < 500ms
- ✅ 대시보드 로딩 시간 < 2초
- ✅ 차트 렌더링 시간 < 1초

### 기능성
- ✅ 모든 Phase 8 API 활용
- ✅ 실시간 데이터 업데이트
- ✅ 에러 처리 100% 커버

### 디자인
- ✅ 반응형 디자인 (모바일/태블릿/데스크톱)
- ✅ 접근성 기준 준수
- ✅ 일관된 디자인 시스템

---

## 📝 다음 단계

1. API 클라이언트 함수 작성
2. 커스텀 훅 구현
3. 재무 대시보드 화면 구현
4. 요금 미리보기 컴포넌트 구현
5. 청구서/정산서 목록 화면 개선
6. 테스트 및 최적화
