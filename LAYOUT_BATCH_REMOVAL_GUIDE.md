# UVIS Layout 일괄 제거 가이드

## 📋 문제 상황
- **증상**: 일부 화면에서 메뉴가 표시되지 않고, 사이드바가 사라지는 문제
- **원인**: 36개 이상의 페이지가 개별적으로 `<Layout>` 컴포넌트를 import하고 사용
- **영향**: App.tsx의 전역 Layout과 충돌하여 UI 일관성 상실

## 🎯 해결 방안
모든 페이지에서 Layout을 제거하고, App.tsx의 단일 Layout만 사용

## 📦 제공 파일
- `batch_remove_layout.sh` - Layout 일괄 제거 자동화 스크립트

## 🚀 실행 방법

### 1단계: 스크립트 복사 및 실행 권한 부여
```bash
# 스크립트를 서버로 복사
cp /home/user/webapp/batch_remove_layout.sh /root/uvis/

# 실행 권한 부여
chmod +x /root/uvis/batch_remove_layout.sh

# 스크립트 실행
cd /root/uvis
./batch_remove_layout.sh
```

### 2단계: 빌드 테스트
```bash
cd /root/uvis/frontend
rm -rf dist/
npm run build
```

**예상 결과**: 빌드 성공 (약 15초 소요)

### 3단계: Docker 이미지 재빌드
```bash
cd /root/uvis
docker-compose build --no-cache frontend
```

**예상 결과**: 이미지 빌드 성공 (약 3-4분 소요)

### 4단계: 컨테이너 재시작
```bash
docker-compose up -d frontend
sleep 10
docker-compose ps | grep frontend
```

**예상 결과**: frontend 컨테이너 `Up` 상태

### 5단계: 브라우저 테스트
1. **캐시 완전 삭제** (필수!)
   - Chrome: `Ctrl + Shift + Delete`
   - 기간: `전체 기간`
   - 항목: `쿠키 및 기타 사이트 데이터`, `캐시된 이미지 및 파일` 모두 체크
   - Chrome 완전 종료 후 재시작

2. **로그인**
   - URL: `http://139.150.11.99/login`
   - 계정: `admin` / `admin123`

3. **UI 일관성 확인**
   - ✅ 모든 페이지에서 사이드바 표시
   - ✅ 모든 페이지에서 상단 네비게이션 표시
   - ✅ 페이지 전환 시 레이아웃 유지
   - ✅ 메뉴 클릭 시 정상 동작

## 🔍 스크립트 동작 과정

### 1단계: 백업 생성
```
/root/uvis/frontend/src/pages/layout_removal_backup_YYYYMMDD_HHMMSS/
└── [모든 .tsx 파일 백업]
```

### 2단계: Layout 분석
- LoginPage.tsx를 제외한 모든 페이지 스캔
- Layout import와 태그 사용 여부 확인

### 3단계: 자동 제거
각 파일마다:
1. 개별 백업 생성 (`파일명.before_removal`)
2. `import Layout from ...` 라인 삭제
3. `<Layout>` 태그 삭제
4. `</Layout>` 태그 삭제
5. 연속된 빈 줄 정리
6. 검증 후 원본 파일 교체

### 4단계: 최종 검증
- Layout 문자열이 남아있는 파일 확인
- 결과 보고서 출력

## 📊 처리 대상 페이지 (예상 44개)

<details>
<summary>전체 목록 보기</summary>

1. ABTestMonitorPage.tsx
2. AIChatPage.tsx
3. AnalyticsDashboardPage.tsx
4. AnalyticsPage.tsx
5. BillingPage.tsx
6. ChargePreviewPage.tsx
7. ClientsPage.tsx
8. DashboardPage.tsx
9. DispatchesPage.tsx
10. DispatchMonitoringDashboard.tsx
11. DispatchOptimizationPage.tsx
12. DispatchRulesPage.tsx
13. FrequentRoutesPage.tsx
14. GeocodingTestPage.tsx
15. MaintenancePage.tsx
16. OptimizationPage.tsx (이미 처리됨)
17. OrderCalendarPage.tsx
18. OrdersPage.tsx
19. RealtimeDashboardPage.tsx
20. RealtimeTelemetryPage.tsx
21. RecurringOrdersPage.tsx
22. ReportsPage.tsx
23. RouteAnalysisPage.tsx
24. SettingsPage.tsx
25. TemperatureAnalyticsPage.tsx
26. TemperatureMonitoringPage.tsx
27. TrackingPage.tsx
28. UvisGPSMonitoring.tsx
29. VehicleMaintenancePage.tsx
30. VehiclesPage.tsx
... (총 44개)

</details>

## ⚠️ 주의사항

### 백업 확인
- 스크립트는 자동으로 백업을 생성합니다
- 백업 위치: `/root/uvis/frontend/src/pages/layout_removal_backup_[timestamp]/`
- 문제 발생 시 백업에서 복구 가능

### 복구 방법 (문제 발생 시)
```bash
cd /root/uvis/frontend/src/pages

# 전체 복구
BACKUP_DIR=$(ls -dt layout_removal_backup_* | head -1)
cp "$BACKUP_DIR"/*.tsx ./

# 또는 개별 파일 복구
cp DashboardPage.tsx.before_removal DashboardPage.tsx
```

### LoginPage는 제외
- LoginPage.tsx는 Layout을 사용하지 않아야 합니다
- 스크립트는 자동으로 LoginPage를 건너뜁니다

### App.tsx 확인
Layout은 **App.tsx에만** 존재해야 합니다:

```tsx
// App.tsx의 올바른 구조
function App() {
  return (
    <Routes>
      {/* 로그인 페이지 - Layout 없음 */}
      <Route path="/login" element={<LoginPage />} />
      
      {/* 인증된 페이지 - Layout으로 감싸짐 */}
      <Route element={<Layout><Outlet /></Layout>}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/orders" element={<OrdersPage />} />
        {/* ... 기타 페이지 ... */}
      </Route>
    </Routes>
  );
}
```

## 🧪 테스트 체크리스트

### 빌드 테스트
- [ ] `npm run build` 성공
- [ ] dist/ 폴더 생성됨
- [ ] 빌드 시간 15초 이내
- [ ] 에러 메시지 없음

### 배포 테스트
- [ ] Docker 이미지 빌드 성공
- [ ] 컨테이너 정상 실행
- [ ] 컨테이너 헬스체크 통과

### UI 테스트
- [ ] 로그인 페이지 정상 표시 (Layout 없음)
- [ ] 대시보드 사이드바 표시됨
- [ ] 주문 관리 페이지 사이드바 표시됨
- [ ] 실시간 배차 모니터링 사이드바 표시됨
- [ ] 최적화 페이지 사이드바 표시됨
- [ ] 모든 메뉴 항목 클릭 가능
- [ ] 페이지 전환 시 레이아웃 유지

### 성능 테스트
- [ ] 페이지 로딩 시간 1초 이내
- [ ] API 응답 시간 100ms 이내
- [ ] 콘솔 에러 없음

## 🐛 문제 해결

### "Permission denied" 오류
```bash
chmod +x /root/uvis/batch_remove_layout.sh
```

### 빌드 실패
```bash
# 백업에서 복구
cd /root/uvis/frontend/src/pages
BACKUP_DIR=$(ls -dt layout_removal_backup_* | head -1)
cp "$BACKUP_DIR"/*.tsx ./

# 다시 빌드
cd /root/uvis/frontend
rm -rf dist/ node_modules/.vite
npm run build
```

### 일부 페이지만 수정하고 싶을 때
스크립트를 수정하여 특정 파일만 처리:
```bash
# 예: DashboardPage만 처리
LAYOUT_FILES="DashboardPage.tsx"
```

### 브라우저 캐시 문제
```bash
# 시크릿 모드로 테스트
# 또는 다른 브라우저로 테스트
# Firefox, Safari 등
```

## 📈 예상 결과

### 처리 전
```
📊 Layout을 사용하는 페이지: 44 개
```

### 처리 후
```
✅ 성공: 44 개
❌ 실패: 0 개
📊 Layout이 남아있는 페이지: 0 개
✅ 모든 페이지에서 Layout 제거 완료!
```

### 빌드 결과
```
✓ built in 14.98s
dist/assets/index-[hash].js     185.41 kB │ gzip: 64.70 kB
dist/assets/OptimizationPage-[hash].js  16.91 kB │ gzip: 5.06 kB
... (기타 파일들)
```

## 🔄 롤백 가이드

만약 문제가 발생하면:

```bash
# 1. 백업에서 전체 복구
cd /root/uvis/frontend/src/pages
BACKUP_DIR=$(ls -dt layout_removal_backup_* | head -1)
echo "복구할 백업: $BACKUP_DIR"
cp "$BACKUP_DIR"/*.tsx ./

# 2. 재빌드
cd /root/uvis/frontend
rm -rf dist/
npm run build

# 3. 재배포
cd /root/uvis
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

## 📞 지원

문제가 지속되면:
1. 스크립트 실행 로그 저장
2. 빌드 에러 메시지 캡처
3. 브라우저 콘솔 스크린샷
4. Docker 로그 확인

```bash
# 로그 수집
./batch_remove_layout.sh > layout_removal.log 2>&1
npm run build > build.log 2>&1
docker logs uvis-frontend > frontend.log 2>&1
```

## ✅ 성공 기준

1. ✅ 모든 페이지에서 Layout import 제거
2. ✅ 빌드 성공 (에러 없음)
3. ✅ 모든 페이지에서 사이드바 표시
4. ✅ 메뉴 항목 정상 동작
5. ✅ 페이지 로딩 시간 1초 이내
6. ✅ 콘솔 에러 없음

---

**작성일**: 2026-02-23  
**버전**: 1.0  
**프로젝트**: UVIS 냉장냉동 배차 시스템
