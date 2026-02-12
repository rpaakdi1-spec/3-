# 📋 TODO List - Cold Chain 프로젝트

> **최종 업데이트:** 2026-02-12  
> **브랜치:** genspark_ai_developer  
> **최근 커밋:** 4cbfb4f

---

## 🎯 즉시 확인할 사항

### 1️⃣ 재무 대시보드 UI 확인
- [ ] 4개 요약 카드에 실제 데이터 표시되는지
- [ ] 차트 2개가 정상적으로 렌더링되는지
- [ ] TOP 10 거래처 테이블에 데이터가 있는지
- [ ] 로딩 상태가 정상적으로 작동하는지

### 2️⃣ 다른 청구/정산 메뉴 테스트
각 메뉴 클릭 후 정상 작동 여부 확인:
- [ ] **요금 미리보기** - 폼 입력 및 계산 기능
- [ ] **자동 청구 스케줄** - 스케줄 목록 표시
- [ ] **정산 승인** - 승인 대기 목록
- [ ] **결제 알림** - 알림 목록
- [ ] **데이터 내보내기** - 내보내기 작업 목록

### 3️⃣ 다른 페이지들 사이드바 확인
Layout이 추가된 18개 페이지 모두 확인:
- [ ] 온도 모니터링
- [ ] 온도 분석
- [ ] 차량 유지보수
- [ ] AI 예측 정비
- [ ] 실시간 텔레메트리
- [ ] 자동 배차 최적화
- [ ] 고급 분석 & BI
- [ ] IoT 센서 페이지들
- [ ] 설정 페이지

---

## 🔧 코드 정리 및 최적화

### 4️⃣ API 클라이언트 통합
현재 여러 파일에 API URL이 중복 정의되어 있습니다:

**확인된 중복:**
```
frontend/src/services/api.ts → API_BASE_URL = '/api/v1'
frontend/src/api/client.ts → API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
frontend/src/api/analytics.ts
frontend/src/services/analyticsService.ts → API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
frontend/src/api/billing-enhanced.ts → API_BASE_URL = '/api/v1/billing/enhanced'
```

**해야 할 작업:**
- [ ] 단일 API 설정 파일 생성 (`src/config/api.ts`)
- [ ] 모든 API 클라이언트가 이 설정을 사용하도록 수정
- [ ] 환경변수 통일 (`VITE_API_URL` vs `VITE_API_BASE_URL`)

**예시 구조:**
```typescript
// src/config/api.ts
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || '/api/v1',
  BILLING_URL: '/api/v1/billing/enhanced',
  TIMEOUT: 30000,
};
```

### 5️⃣ 디버그 로그 제거 (프로덕션 준비)
개발용 로그들을 제거하거나 환경별 분기 처리:
- [ ] `billing-enhanced.ts`의 console.log 제거/조건부 처리
- [ ] `authDebug.ts` 유틸리티를 개발 환경에서만 활성화
- [ ] Sidebar의 디버그 로그 제거

**예시:**
```typescript
const isDev = import.meta.env.DEV;
if (isDev) {
  console.log('🔐 [Billing API] Token attached:', token);
}
```

---

## 📝 문서화

### 6️⃣ API 문서 업데이트
- [ ] Billing Enhanced API 엔드포인트 문서화
- [ ] 인증 흐름 문서화
- [ ] 에러 핸들링 가이드 작성

**생성할 문서:**
- `docs/api/billing-enhanced.md`
- `docs/authentication.md`
- `docs/error-handling.md`

### 7️⃣ 배포 가이드 작성
- [ ] 프론트엔드 빌드 및 배포 절차
- [ ] 환경변수 설정 가이드
- [ ] 트러블슈팅 가이드

**생성할 문서:**
- `docs/deployment/frontend.md`
- `docs/deployment/backend.md`
- `docs/deployment/troubleshooting.md`

---

## 🧪 테스트

### 8️⃣ 통합 테스트
- [ ] 로그인 → 대시보드 → 각 메뉴 전체 흐름 테스트
- [ ] 토큰 만료 시나리오 테스트
- [ ] 권한별 메뉴 접근 테스트 (ADMIN, MANAGER, DISPATCHER, VIEWER)

**테스트 시나리오:**
```
1. 로그인 (admin/admin123)
2. 대시보드 확인 (통계 표시)
3. 각 메뉴 순회 (22개 메뉴)
4. 로그아웃
5. 다른 권한으로 재로그인 (권한 테스트)
```

### 9️⃣ 성능 테스트
- [ ] API 응답 속도 측정
- [ ] 프론트엔드 번들 크기 최적화
- [ ] 불필요한 리렌더링 최적화

**측정 항목:**
- 초기 로딩 시간 (< 3초 목표)
- API 평균 응답 시간 (< 500ms 목표)
- 번들 크기 (< 500KB 목표)

---

## 🔒 보안 강화

### 🔟 보안 점검
- [ ] 토큰 저장 방식 검토 (localStorage vs httpOnly cookie)
- [ ] CORS 설정 재검토
- [ ] API Rate Limiting 확인
- [ ] XSS/CSRF 방어 검토

**보안 체크리스트:**
```
✓ JWT 토큰 만료 시간 설정 (30분)
✓ HTTPS 사용 (프로덕션)
✓ SQL Injection 방어 (SQLAlchemy ORM)
? localStorage 토큰 저장 (httpOnly cookie로 변경 검토)
? XSS 방어 (React 기본 제공, 추가 검증 필요)
```

---

## 🚀 기능 개선

### 1️⃣1️⃣ 재무 대시보드 개선
- [ ] 날짜 범위 선택 UI 개선 (DatePicker 추가)
- [ ] 데이터 새로고침 자동화 (polling)
- [ ] 차트 인터랙션 개선 (툴팁, 줌 등)
- [ ] 엑셀/PDF 내보내기 기능

**기능 상세:**
```typescript
// DatePicker 추가 예시
import { DateRangePicker } from '@/components/ui/DateRangePicker';

<DateRangePicker
  value={dateRange}
  onChange={setDateRange}
  maxDate={new Date()}
/>
```

### 1️⃣2️⃣ 에러 핸들링 개선
- [ ] 사용자 친화적인 에러 메시지
- [ ] Toast 알림 추가 (react-hot-toast)
- [ ] 재시도 로직 구현
- [ ] 오프라인 상태 감지

**구현 예시:**
```typescript
try {
  const data = await fetchData();
} catch (error) {
  if (error.response?.status === 401) {
    toast.error('로그인이 필요합니다.');
    navigate('/login');
  } else if (error.response?.status === 500) {
    toast.error('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
  } else {
    toast.error('데이터를 불러올 수 없습니다.');
  }
}
```

---

## 📊 모니터링

### 1️⃣3️⃣ 로깅 및 모니터링
- [ ] 프론트엔드 에러 추적 (Sentry 등)
- [ ] API 호출 모니터링
- [ ] 사용자 행동 분석 (Google Analytics 등)
- [ ] 성능 메트릭 수집

**모니터링 도구 후보:**
- Sentry (에러 추적)
- Google Analytics 4 (사용자 분석)
- Prometheus + Grafana (백엔드 메트릭)
- LogRocket (세션 리플레이)

---

## 🎨 UI/UX 개선

### 1️⃣4️⃣ 사용자 경험 개선
- [ ] 로딩 스켈레톤 추가
- [ ] 빈 상태(Empty State) UI 추가
- [ ] 반응형 디자인 최적화 (모바일)
- [ ] 다크 모드 지원

**UI 컴포넌트 추가:**
```tsx
// LoadingSkeleton.tsx
export const TableSkeleton = () => (
  <div className="space-y-2">
    {[1, 2, 3, 4, 5].map(i => (
      <div key={i} className="h-12 bg-gray-200 animate-pulse rounded" />
    ))}
  </div>
);

// EmptyState.tsx
export const EmptyState = ({ title, description, icon }) => (
  <div className="text-center py-12">
    {icon}
    <h3 className="text-lg font-medium">{title}</h3>
    <p className="text-gray-500">{description}</p>
  </div>
);
```

---

## 🔄 Git 워크플로우

### 1️⃣5️⃣ 현재 변경사항 PR 생성
- [ ] 최신 코드를 main 브랜치와 동기화
- [ ] 모든 커밋 스쿼시 (squash)
- [ ] Pull Request 생성 및 설명 작성
- [ ] PR 링크 공유

**커밋 히스토리:**
```
4cbfb4f - fix(frontend): Add auth debugging utilities and enhanced logging
348f2b3 - fix(frontend): Add detailed logging to billing-enhanced API client
01082ce - fix(frontend): Remove duplicate Layout import statements
11046cb - fix(frontend): Add Layout wrapper to 18 pages
c9e437c - fix(frontend): Add Layout wrapper to TemperatureMonitoringPage
7d10a3b - fix(frontend): Improve sidebar scrolling and add debug logging
7144803 - fix(frontend): Align FinancialDashboardPage with backend API
9c47647 - fix(frontend): Fix circular reference in billing-enhanced axios client
6cb524a - fix(frontend): Add auth headers to billing-enhanced API
```

**PR 생성 절차:**
```bash
# 1. main과 동기화
git fetch origin main
git rebase origin/main

# 2. 커밋 스쿼시 (최근 9개 커밋)
git reset --soft HEAD~9
git commit -m "feat: Implement billing enhanced module with full authentication

- Add billing enhanced API client with auth headers
- Fix circular axios reference and Layout wrapper issues
- Implement financial dashboard with charts and tables
- Add auth debugging utilities
- Improve sidebar scrolling and menu visibility

Fixes sidebar disappearing issue across 18+ pages.
Resolves 401 Unauthorized errors on billing API."

# 3. 푸시 (force push 필요)
git push -f origin genspark_ai_developer

# 4. GitHub에서 PR 생성
# main <- genspark_ai_developer
```

---

## 📅 우선순위별 분류

### 🔴 긴급 (지금 바로)
1. ✅ ~~401 에러 해결~~ → **완료!**
2. ✅ ~~사이드바 사라짐 문제 해결~~ → **완료!**
3. 재무 대시보드 UI 데이터 확인
4. 다른 청구/정산 메뉴 정상 작동 확인

### 🟡 중요 (이번 주 내)
5. API 클라이언트 통합 및 중복 제거
6. 디버그 로그 정리
7. Pull Request 생성
8. 다른 18개 페이지 사이드바 확인

### 🟢 보통 (다음 주)
9. 통합 테스트
10. 문서화
11. 보안 점검
12. 에러 핸들링 개선

### 🔵 장기 (추후)
13. 기능 개선 (DatePicker, 자동 새로고침 등)
14. UI/UX 개선 (스켈레톤, 다크모드)
15. 모니터링 시스템
16. 성능 최적화

---

## 🎯 지금 당장 할 일

### ✅ 완료된 작업
- [x] 401 Unauthorized 에러 해결
  - billing-enhanced.ts에 axios 인터셉터 추가
  - Authorization 헤더 자동 첨부
- [x] 사이드바 사라짐 문제 해결
  - 19개 페이지에 Layout 컴포넌트 추가
  - 중복 import 제거
- [x] 인증 디버깅 유틸리티 추가
  - authDebug.ts 생성
  - 상세 로깅 추가

### 🔜 다음 작업
1. **재무 대시보드 스크린샷 1장** 공유 (데이터 표시 확인)
2. **다른 청구/정산 메뉴들** 각각 클릭해서 정상 작동 확인
3. **Console에 에러 없는지** 최종 확인

---

## 📁 관련 파일

### 수정된 파일 목록
```
frontend/src/api/billing-enhanced.ts        - API 클라이언트 (인터셉터 추가)
frontend/src/utils/authDebug.ts             - 인증 디버깅 유틸리티 (신규)
frontend/src/pages/FinancialDashboardPage.tsx
frontend/src/pages/TemperatureMonitoringPage.tsx
frontend/src/pages/TemperatureAnalyticsPage.tsx
frontend/src/pages/VehicleMaintenancePage.tsx
frontend/src/pages/MLPredictionsPage.tsx
frontend/src/pages/RealtimeTelemetryPage.tsx
frontend/src/pages/DispatchOptimizationPage.tsx
frontend/src/pages/AnalyticsDashboardPage.tsx
frontend/src/pages/ChargePreviewPage.tsx
frontend/src/pages/AutoInvoiceSchedulePage.tsx
frontend/src/pages/SettlementApprovalPage.tsx
frontend/src/pages/PaymentReminderPage.tsx
frontend/src/pages/ExportTaskPage.tsx
frontend/src/pages/BillingPage.tsx
frontend/src/pages/IoTSensorsPage.tsx
frontend/src/pages/IoTSensorDetailPage.tsx
frontend/src/pages/IoTAlertsPage.tsx
frontend/src/pages/RecurringOrdersPage.tsx
frontend/src/pages/SettingsPage.tsx
frontend/src/components/common/Sidebar.tsx
```

### 백엔드 관련 파일
```
backend/app/api/v1/billing_enhanced.py      - Billing API 엔드포인트
backend/app/schemas/billing_enhanced.py     - 데이터 스키마
backend/app/services/billing_enhanced_service.py - 비즈니스 로직
backend/app/models/billing_enhanced.py      - 데이터베이스 모델
backend/app/api/auth.py                     - 인증 로직
backend/app/services/auth_service.py        - JWT 서비스
```

---

## 🔗 참고 링크

- **GitHub Repository:** https://github.com/rpaakdi1-spec/3-.git
- **Branch:** genspark_ai_developer
- **Frontend URL:** http://139.150.11.99
- **API Base URL:** http://139.150.11.99/api/v1

---

## 📝 메모

### 알려진 이슈
- [ ] API 클라이언트 중복 정의 (6개 파일)
- [ ] 환경변수 불일치 (VITE_API_URL vs VITE_API_BASE_URL)
- [ ] 개발용 console.log 제거 필요

### 개선 아이디어
- 재무 대시보드에 실시간 업데이트 기능
- 차트 데이터 CSV 다운로드
- 모바일 반응형 개선
- 다국어 지원 (i18n)

---

**마지막 업데이트:** 2026-02-12  
**작성자:** AI Assistant  
**버전:** 1.0
