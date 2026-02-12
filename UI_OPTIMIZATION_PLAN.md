# UI 최적화 계획

## 📋 목차
1. [현재 상태 분석](#현재-상태-분석)
2. [WebSocket 오류 수정](#websocket-오류-수정)
3. [성능 최적화](#성능-최적화)
4. [UI/UX 개선](#uiux-개선)
5. [실행 계획](#실행-계획)

---

## 🔍 현재 상태 분석

### 백엔드 문제
- ❌ **WebSocket 오류**: `Error broadcasting dashboard metrics: ASSIGNED`
- ❌ **비동기 처리 오류**: `ChunkedIteratorResult can't be used in 'await' expression`
- 🔧 **근본 원인**: 동기 SQLAlchemy를 비동기 await와 함께 사용

### 프론트엔드 상태
- ✅ **빌드 성공**: 11.95초, 1.5MB
- ✅ **배포 완료**: Docker 컨테이너 실행 중
- ⚠️ **잠재적 개선 영역**: 로딩 속도, 렌더링 최적화, 사이드바 동작

---

## 🔧 WebSocket 오류 수정

### 문제 분석
```python
# ❌ 잘못된 코드 (현재)
from sqlalchemy.ext.asyncio import AsyncSession

async def _collect_dashboard_metrics(self, db: AsyncSession) -> dict:
    active_dispatches = await db.scalar(active_dispatches_query)  # 동기 세션에 await 사용
```

### 해결 방법
```python
# ✅ 올바른 코드 (수정 후)
from sqlalchemy.orm import Session

def _collect_dashboard_metrics(self, db: Session) -> dict:
    active_dispatches = db.scalar(active_dispatches_query)  # await 제거
```

### 수정 사항
1. **AsyncSession → Session 변경**
2. **async def → def 변경** (_collect_dashboard_metrics 메서드)
3. **await 제거** (4개 db.scalar 호출)
4. **await 제거** (db.execute 호출)

### 배포 스크립트
```bash
# 프로덕션 서버에서 실행:
cd /root/uvis
bash /path/to/fix_websocket_production.sh
```

이 스크립트는:
- ✅ 백업 생성
- ✅ WebSocket 오류 수정 적용
- ✅ Docker 이미지 재빌드 (캐시 없이)
- ✅ 백엔드 재시작
- ✅ 로그 확인 및 검증

---

## ⚡ 성능 최적화

### A. 백엔드 최적화

#### 1. WebSocket 브로드캐스트 최적화
```python
# 현재: 5초마다 모든 메트릭 브로드캐스트
self.broadcast_interval = 5  # seconds

# 개선안: 변경된 데이터만 브로드캐스트
# - 메트릭 변경 감지
# - 델타만 전송
# - 클라이언트 측 캐싱
```

#### 2. 데이터베이스 쿼리 최적화
```python
# 개선 사항:
# - 인덱스 추가 (status, created_at)
# - 쿼리 결과 캐싱 (Redis)
# - 배치 쿼리 사용
```

### B. 프론트엔드 최적화

#### 1. 코드 스플리팅 & Lazy Loading
```typescript
// ❌ 현재: 모든 페이지 한 번에 로드
import DashboardPage from './pages/DashboardPage';
import OrdersPage from './pages/OrdersPage';

// ✅ 개선: Lazy loading
const DashboardPage = React.lazy(() => import('./pages/DashboardPage'));
const OrdersPage = React.lazy(() => import('./pages/OrdersPage'));

<Suspense fallback={<LoadingSpinner />}>
  <Routes>
    <Route path="/dashboard" element={<DashboardPage />} />
  </Routes>
</Suspense>
```

#### 2. React 렌더링 최적화
```typescript
// ❌ 불필요한 re-render
const DashboardCard = ({ title, value }) => {
  return <div>{title}: {value}</div>;
};

// ✅ React.memo로 최적화
const DashboardCard = React.memo(({ title, value }) => {
  return <div>{title}: {value}</div>;
});

// ✅ useMemo로 계산 최적화
const expensiveCalculation = useMemo(() => {
  return data.reduce((sum, item) => sum + item.value, 0);
}, [data]);
```

#### 3. WebSocket 연결 최적화
```typescript
// 현재 개선 가능 영역:
// - 재연결 로직 개선
// - 연결 풀링
// - 메시지 배치 처리
```

### C. 번들 크기 최적화

#### 현재 번들 크기
```
dist/assets/index-*.js: ~1.5MB (gzipped ~450KB)
```

#### 최적화 전략
1. **Tree shaking**: 사용하지 않는 코드 제거
2. **라이브러리 최적화**:
   - `lodash` → `lodash-es` (tree-shakeable)
   - `moment` → `date-fns` (더 작음)
3. **동적 import**: 차트 라이브러리 lazy load
4. **이미지 최적화**: WebP 포맷, 지연 로딩

---

## 🎨 UI/UX 개선

### 1. 사이드바 최적화 (✅ 이미 적용됨)
```typescript
// ✅ 현재 구현: 항상 펼쳐진 상태
const [expandedMenus, setExpandedMenus] = React.useState<Record<string, boolean>>({
  billing: true, // 청구/정산 메뉴 확장
});

// 메뉴 토글 비활성화
const toggleMenu = (key: string) => {
  // 아무 동작도 하지 않음 - 항상 확장 상태 유지
};
```

### 2. 로딩 상태 개선
```typescript
// 개선 사항:
// - 스켈레톤 로딩 추가
// - 프로그레스 바
// - 낙관적 업데이트 (Optimistic UI)
```

### 3. 에러 처리 개선
```typescript
// 개선 사항:
// - 에러 바운더리 추가
// - 사용자 친화적 에러 메시지
// - 재시도 옵션
```

### 4. 반응형 디자인 개선
```css
/* 개선 사항:
 * - 모바일 최적화
 * - 태블릿 레이아웃
 * - 터치 인터랙션
 */
```

---

## 📅 실행 계획

### Phase 1: WebSocket 오류 수정 (우선순위: 🔴 높음)
**목표**: WebSocket 브로드캐스트 오류 완전 제거

**작업**:
1. ✅ `realtime_metrics_service.py` 수정
   - AsyncSession → Session 변경
   - await 제거 (동기 호출로 변경)
2. ✅ 배포 스크립트 작성
3. ⏳ 프로덕션 배포
4. ⏳ 로그 모니터링 (24시간)

**예상 시간**: 30분
**배포 방법**:
```bash
cd /root/uvis
bash fix_websocket_production.sh
```

**검증 방법**:
```bash
# 1. 로그 확인
docker logs uvis-backend 2>&1 | grep -i "error broadcasting" | tail -20

# 2. WebSocket 연결 테스트
# 브라우저에서 http://139.150.11.99/ 접속
# 개발자 도구 → 네트워크 → WS 탭 확인

# 3. 대시보드 실시간 업데이트 확인
# 메트릭이 5초마다 자동 갱신되는지 확인
```

---

### Phase 2: 프론트엔드 성능 최적화 (우선순위: 🟡 중간)
**목표**: 로딩 속도 30% 개선, 렌더링 최적화

**작업**:
1. ⏳ 코드 스플리팅 적용 (React.lazy)
2. ⏳ React.memo 적용 (주요 컴포넌트)
3. ⏳ useMemo/useCallback 적용
4. ⏳ 번들 분석 및 최적화

**예상 시간**: 2-3시간

**파일**:
- `frontend/src/App.tsx` (라우팅)
- `frontend/src/components/Dashboard.tsx`
- `frontend/src/components/RealtimeDashboard.tsx`
- `frontend/src/pages/*.tsx`

**검증 방법**:
```bash
# 빌드 크기 비교
npm run build
# Before: ~1.5MB
# After: <1.2MB (목표)

# Lighthouse 점수
# Performance: >90 (목표)
```

---

### Phase 3: 고급 최적화 (우선순위: 🟢 낮음)
**목표**: 장기적 성능 개선

**작업**:
1. ⏳ Redis 캐싱 추가 (메트릭 데이터)
2. ⏳ WebSocket 메시지 배치 처리
3. ⏳ 데이터베이스 인덱스 최적화
4. ⏳ CDN 설정 (정적 파일)

**예상 시간**: 4-6시간

---

## 🚀 즉시 실행 가능한 명령

### 1. WebSocket 오류 수정 (프로덕션 서버에서 실행)
```bash
cd /root/uvis

# 방법 1: 자동 스크립트 사용 (권장)
bash fix_websocket_production.sh

# 방법 2: 수동 실행
docker-compose stop backend
docker-compose rm -f backend
docker rmi uvis-backend
docker-compose build --no-cache backend
docker-compose up -d backend
sleep 30
docker logs uvis-backend --since 30s 2>&1 | grep -i "error broadcasting"
```

### 2. 로그 모니터링
```bash
# 실시간 로그 확인
docker logs -f uvis-backend

# WebSocket 오류만 필터링
docker logs uvis-backend 2>&1 | grep -i "error broadcasting" | tail -20

# 최근 5분 로그
docker logs uvis-backend --since 5m
```

### 3. 프론트엔드 테스트
```bash
# 브라우저에서:
# http://139.150.11.99/

# 테스트 시나리오:
# 1. 로그인 (admin/admin123)
# 2. 대시보드 접속
# 3. 개발자 도구 (F12) → 네트워크 → WS 탭
# 4. WebSocket 연결 상태 확인
# 5. 5초마다 메시지 수신 확인
```

---

## ✅ 체크리스트

### WebSocket 오류 수정
- [ ] `realtime_metrics_service.py` 백업
- [ ] AsyncSession → Session 변경
- [ ] await 제거 (8개소)
- [ ] Docker 이미지 재빌드
- [ ] 백엔드 재시작
- [ ] 로그 확인 (오류 없음)
- [ ] WebSocket 연결 테스트
- [ ] 실시간 업데이트 확인

### 프론트엔드 최적화 (선택)
- [ ] 코드 스플리팅 적용
- [ ] React.memo 적용
- [ ] useMemo/useCallback 적용
- [ ] 번들 크기 분석
- [ ] 빌드 및 테스트
- [ ] 배포

### 모니터링
- [ ] 24시간 로그 모니터링
- [ ] 성능 메트릭 수집
- [ ] 사용자 피드백 수집

---

## 📞 문제 해결

### Q1: WebSocket 오류가 계속 발생하면?
```bash
# A: 상세 로그 확인
docker logs uvis-backend 2>&1 | grep -A 10 "Error broadcasting"

# 전체 traceback 확인
docker logs uvis-backend 2>&1 | grep -A 20 "Traceback"
```

### Q2: 백엔드 재시작 후 연결 안 되면?
```bash
# A: 컨테이너 상태 확인
docker ps -a | grep uvis

# 헬스 체크
curl -s http://localhost:8000/health | python3 -m json.tool
```

### Q3: 프론트엔드 빌드 실패하면?
```bash
# A: 캐시 정리 후 재빌드
cd /root/uvis/frontend
npm cache clean --force
rm -rf node_modules package-lock.json
export NODE_OPTIONS="--max-old-space-size=4096"
npm install --legacy-peer-deps
npm run build
```

---

## 📊 기대 효과

### 백엔드
- ✅ WebSocket 오류 0건
- ✅ 실시간 메트릭 안정적 브로드캐스트
- ✅ CPU 사용률 감소 (~10%)

### 프론트엔드
- ✅ 초기 로딩 시간 30% 감소
- ✅ 번들 크기 20% 감소
- ✅ Lighthouse 성능 점수 >90

### 사용자 경험
- ✅ 실시간 대시보드 정상 작동
- ✅ 페이지 전환 속도 향상
- ✅ 에러 메시지 감소

---

## 📝 다음 단계

1. **즉시 실행**: WebSocket 오류 수정 배포
2. **모니터링**: 24시간 로그 관찰
3. **프론트엔드 최적화**: 성능 개선 적용 (선택)
4. **Git 커밋**: 모든 변경사항 커밋 및 PR 생성
5. **문서화**: 변경 사항 문서 업데이트

---

**작성일**: 2026-02-07
**작성자**: AI Assistant
**버전**: 1.0
