# Phase 8 긴급 수정: 401 오류 해결 및 배포 가이드

**수정 일시**: 2026-02-07  
**심각도**: 🔴 **High** (사용자 기능 차단)  
**상태**: ✅ **수정 완료** - 배포 대기 중

---

## 🔍 발견된 문제

### 문제 1: URL 파라미터 중첩 오류
```javascript
❌ 잘못된 URL:
GET /api/v1/billing/enhanced/dashboard/financial?start_date%5Bstart_date%5D=2025-11-07&start_date%5Bend_date%5D=2026-02-07

디코딩:
?start_date[start_date]=2025-11-07&start_date[end_date]=2026-02-07
```

**원인**: 객체를 그대로 파라미터로 전달
```typescript
// 잘못된 코드
await BillingEnhancedAPI.getFinancialDashboard(dateRange);
// dateRange = { start_date: '2025-11-07', end_date: '2026-02-07' }
```

### 문제 2: Authorization 헤더 누락
- axios 요청 시 Bearer 토큰이 자동으로 추가되지 않음
- 401 Unauthorized 오류 발생
- 자동 로그인 리다이렉트 없음

---

## ✅ 적용된 수정사항

### 수정 1: FinancialDashboardPage.tsx
```typescript
// Before (잘못됨)
const summaryData = await BillingEnhancedAPI.getFinancialDashboard(dateRange);

// After (수정됨)
const summaryData = await BillingEnhancedAPI.getFinancialDashboard(
  dateRange.start_date, 
  dateRange.end_date
);
```

**결과**:
```
✅ 올바른 URL:
GET /api/v1/billing/enhanced/dashboard/financial?start_date=2025-11-07&end_date=2026-02-07
```

### 수정 2: billing-enhanced.ts - Axios 인터셉터 추가
```typescript
// Create axios instance with interceptor
const api = axios.create();

// Request interceptor: Add auth token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login on 401
      localStorage.removeItem('access_token');
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 수정 3: 모든 axios 호출을 api 인스턴스로 변경
```typescript
// Before
await axios.get<FinancialSummary>(`${API_BASE_URL}/dashboard/financial`, { params });

// After
await api.get<FinancialSummary>(`${API_BASE_URL}/dashboard/financial`, { params });
```

---

## 🚀 프로덕션 서버 배포 가이드

### 1단계: 최신 코드 가져오기 (5분)
```bash
# 프로덕션 서버 접속 후
cd /root/uvis

# 현재 브랜치 확인
git branch

# 최신 수정사항 가져오기
git fetch origin
git checkout phase8-verification
git pull origin phase8-verification

# 수정된 파일 확인
git log --oneline -1
# 출력: f688630 fix(phase8): Fix 401 authentication error in Financial Dashboard

git show --stat
# 출력:
# frontend/src/pages/FinancialDashboardPage.tsx
# frontend/src/api/billing-enhanced.ts
```

### 2단계: 프론트엔드 빌드 (3분)
```bash
cd /root/uvis/frontend

# 의존성 확인 (선택사항)
npm install

# 프로덕션 빌드
npm run build

# 빌드 성공 확인
ls -lh dist/
# dist/assets/*.js 파일들이 생성되어야 함
```

### 3단계: Docker 이미지 재빌드 (2분)
```bash
cd /root/uvis

# 프론트엔드 이미지 재빌드 (캐시 없이)
docker-compose build --no-cache frontend

# 빌드 완료 확인
docker images | grep uvis-frontend
```

### 4단계: 컨테이너 재시작 (1분)
```bash
cd /root/uvis

# 프론트엔드 컨테이너만 재시작
docker-compose up -d frontend

# 컨테이너 상태 확인
docker ps | grep uvis-frontend
# STATUS가 "Up" 상태여야 함

# 로그 확인
docker logs uvis-frontend --tail 50
# Nginx 시작 메시지 확인
```

### 5단계: 배포 검증 (3분)
```bash
# 헬스 체크
curl -s http://139.150.11.99/ | head -5

# 프론트엔드 번들 확인
curl -I http://139.150.11.99/assets/index-*.js
# HTTP/1.1 200 OK 확인

# 백엔드 API 확인 (이미 정상)
curl -s http://139.150.11.99:8000/health
# {"status":"healthy",...}
```

---

## 🧪 브라우저 테스트

### 1단계: 캐시 완전 삭제
```
1. 브라우저 열기 (Chrome/Firefox)
2. Ctrl + Shift + Delete (캐시 삭제 창)
3. "쿠키 및 기타 사이트 데이터" 체크
4. "캐시된 이미지 및 파일" 체크
5. "모든 기간" 선택
6. "데이터 삭제" 클릭
```

### 2단계: 재로그인
```
1. http://139.150.11.99/ 접속
2. admin / admin123 로그인
3. 로그인 성공 확인
```

### 3단계: 재무 대시보드 테스트
```
1. 사이드바 → "청구/정산" 클릭
2. "재무 대시보드" 클릭
3. URL 확인:
   http://139.150.11.99/billing/financial-dashboard
4. 페이지 로드 확인 (3초 이내)
5. F12 → Console 탭 열기
6. 빨간 오류 메시지 없는지 확인
```

### 4단계: Network 탭 확인
```
1. F12 → Network 탭
2. 페이지 새로고침 (F5)
3. "financial" 요청 찾기
4. Status: 200 OK 확인
5. Request URL 확인:
   ✅ http://139.150.11.99/api/v1/billing/enhanced/dashboard/financial?start_date=2025-11-07&end_date=2026-02-07
6. Request Headers → Authorization 확인:
   ✅ Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## ✅ 성공 기준

### API 요청
- ✅ Status: 200 OK (❌ 401 Unauthorized 아님)
- ✅ URL: 평탄한 파라미터 (중첩 없음)
  ```
  ✅ ?start_date=2025-11-07&end_date=2026-02-07
  ❌ ?start_date[start_date]=2025-11-07&start_date[end_date]=2026-02-07
  ```
- ✅ Headers: Authorization: Bearer [token]

### 데이터 표시
- ✅ 재무 지표 카드 렌더링
- ✅ 14개 지표 데이터 표시
- ✅ 차트 렌더링
- ✅ 로딩 상태 정상

### 콘솔 오류
- ✅ 빨간 오류 메시지 없음
- ✅ 401 Unauthorized 없음
- ✅ Failed to load dashboard data 없음

---

## 🔄 롤백 계획 (필요 시)

### 빠른 롤백
```bash
cd /root/uvis

# 이전 버전으로 되돌리기
git checkout b27481e  # 수정 이전 커밋

# 프론트엔드 재빌드
cd frontend && npm run build && cd ..

# Docker 재빌드 및 재시작
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### 완전 롤백
```bash
cd /root/uvis

# main 브랜치로 전환
git checkout main
git pull origin main

# 재빌드
cd frontend && npm run build && cd ..
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

## 📊 배포 체크리스트

### 배포 전
- [x] 코드 수정 완료
- [x] Git 커밋 및 푸시
- [x] 로컬 테스트 (선택사항)
- [ ] 프로덕션 서버 백업

### 배포 중
- [ ] 최신 코드 가져오기 (`git pull`)
- [ ] 프론트엔드 빌드 (`npm run build`)
- [ ] Docker 이미지 재빌드
- [ ] 컨테이너 재시작
- [ ] 로그 확인

### 배포 후
- [ ] 헬스 체크
- [ ] 브라우저 캐시 삭제
- [ ] 재로그인
- [ ] 재무 대시보드 테스트
- [ ] F12 Console 오류 확인
- [ ] Network 탭 200 OK 확인
- [ ] 6개 Phase 8 페이지 모두 테스트

---

## 🎯 예상 결과

### Before (수정 전)
```
❌ GET /api/v1/billing/enhanced/dashboard/financial
   ?start_date[start_date]=2025-11-07&start_date[end_date]=2026-02-07
❌ Status: 401 Unauthorized
❌ Error: Failed to load dashboard data
```

### After (수정 후)
```
✅ GET /api/v1/billing/enhanced/dashboard/financial
   ?start_date=2025-11-07&end_date=2026-02-07
✅ Status: 200 OK
✅ Authorization: Bearer [token]
✅ Response: { period_start: "2025-11-07", period_end: "2026-02-07", ... }
✅ Dashboard: 재무 지표 14개 표시
```

---

## 📞 문제 발생 시

### 컨테이너 재시작
```bash
docker-compose restart frontend
docker-compose restart backend
```

### 로그 확인
```bash
# 프론트엔드 로그
docker logs uvis-frontend --tail 100

# 백엔드 로그
docker logs uvis-backend --tail 100

# 모든 컨테이너 상태
docker ps -a
```

### 긴급 지원
```bash
# 디버깅 정보 수집
cd /root/uvis
git log --oneline -5 > debug_info.txt
docker ps >> debug_info.txt
curl -I http://139.150.11.99/ >> debug_info.txt
cat debug_info.txt
```

---

## 📝 수정 요약

| 파일 | 변경 내용 | 영향 |
|-----|---------|------|
| FinancialDashboardPage.tsx | 파라미터 전달 방식 수정 | 재무 대시보드 |
| billing-enhanced.ts | Axios 인터셉터 추가 | 모든 Phase 8 API |

**변경 라인 수**:
- 삽입: 73줄
- 삭제: 31줄
- 순증: 42줄

**영향 범위**:
- 재무 대시보드
- 자동 청구 스케줄
- 정산 승인
- 결제 알림
- 데이터 내보내기
- 모든 Phase 8 기능

---

## 🎉 기대 효과

### 수정 후
- ✅ 401 오류 완전 해결
- ✅ 모든 Phase 8 페이지 정상 작동
- ✅ 자동 토큰 관리
- ✅ 토큰 만료 시 자동 로그인 리다이렉트
- ✅ 사용자 경험 개선

### 부가 효과
- ✅ 향후 API 추가 시 자동으로 토큰 포함
- ✅ 인증 오류 일괄 처리
- ✅ 코드 유지보수성 향상

---

## 🚀 즉시 배포 명령 (한 줄)

```bash
cd /root/uvis && git fetch origin && git checkout phase8-verification && git pull origin phase8-verification && cd frontend && npm run build && cd .. && docker-compose build --no-cache frontend && docker-compose up -d frontend && echo "✅ 배포 완료! 브라우저 캐시 삭제 후 테스트하세요."
```

**실행 시간**: 약 5-7분

---

**작성일**: 2026-02-07 07:00 UTC  
**최종 업데이트**: 2026-02-07 07:00 UTC  
**커밋 해시**: f688630  
**상태**: ✅ **수정 완료** - 배포 대기 중
