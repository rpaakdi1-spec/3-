# 재무 대시보드 차트 표시 문제 해결 가이드

## 🚨 현재 상태
- ✅ Excel/PDF 다운로드: **정상 작동**
- ❌ 요약 카드 (총 매출, 수금액, 미수금): **표시되지 않음**
- ❌ 월별 추이 차트: **표시되지 않음**
- ❌ 상위 고객 TOP 10 차트: **표시되지 않음**

---

## 📋 진단 절차

### 1단계: 진단 스크립트 실행

```bash
cd /root/uvis
chmod +x diagnose_charts.sh check_dashboard_component.sh
./diagnose_charts.sh
./check_dashboard_component.sh
```

### 2단계: 브라우저 콘솔 확인

1. 브라우저에서 재무 대시보드 페이지 열기 (`청구/정산` → `재무 대시보드`)
2. **F12** 키를 눌러 개발자 도구 열기
3. **Console** 탭으로 이동
4. 다음 항목 확인:
   - ❌ **빨간색 오류 메시지**가 있는지 확인
   - 📊 **API 호출 로그**가 있는지 확인 (`Fetching financial dashboard...`)
   - ✅ **API 응답 로그**가 있는지 확인 (`API Response:`)

### 3단계: 네트워크 요청 확인

1. **F12** → **Network** 탭으로 이동
2. **Disable cache** 체크박스 선택
3. **Ctrl+Shift+R**로 페이지 강력 새로고침
4. 필터에 `financial` 입력
5. `/api/v1/billing/enhanced/dashboard/financial` 요청 확인:
   - **Status**: 200 OK인지 확인
   - **Response** 탭에서 데이터 구조 확인:
     ```json
     {
       "summary": {
         "total_revenue": 숫자,
         "total_collected": 숫자,
         "total_unpaid": 숫자
       },
       "monthly_trends": [...],
       "top_clients": [...]
     }
     ```

### 4단계: Elements (DOM) 구조 확인

1. **F12** → **Elements** 탭으로 이동
2. `<div id="root">` 요소 찾기
3. 재무 대시보드 컴포넌트 구조 확인:
   - 요약 카드 `<div>` 요소가 있는지
   - 차트 `<svg>` 요소가 있는지
   - "데이터가 없습니다" 같은 메시지가 있는지

---

## 🔧 가능한 원인 및 해결 방법

### 원인 1: Recharts 라이브러리 미설치

**확인:**
```bash
cd /root/uvis/frontend
grep "recharts" package.json
```

**해결:**
```bash
cd /root/uvis/frontend
npm install recharts --save
npm run build

cd /root/uvis
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker-compose restart frontend
```

### 원인 2: API 응답 데이터 구조 불일치

**확인:**
브라우저 Console에서:
```javascript
// API 응답 확인
fetch('http://139.150.11.99/api/v1/billing/enhanced/dashboard/financial?start_date=2026-01-01&end_date=2026-02-12', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
  }
})
.then(r => r.json())
.then(data => console.log('API Data:', data))
```

**해결:**
API 응답이 없거나 빈 배열인 경우, 백엔드에서 테스트 데이터 생성 필요.

### 원인 3: 컴포넌트 렌더링 조건 문제

**확인:**
```bash
cd /root/uvis
grep -A 5 "data &&" frontend/src/pages/FinancialDashboardPage.tsx
```

컴포넌트가 `data && data.summary` 같은 조건으로 렌더링되는지 확인.

**해결:**
조건부 렌더링 로직 수정 필요. 예:
```typescript
// 잘못된 예
{data && <SummaryCard />}

// 올바른 예
{data?.summary && <SummaryCard data={data.summary} />}
```

### 원인 4: CSS/스타일 문제

차트가 `height: 0` 또는 `display: none`으로 숨겨져 있을 수 있음.

**확인:**
브라우저 Elements 탭에서 차트 요소의 Computed 스타일 확인.

**해결:**
부모 컨테이너에 명시적 높이 설정:
```tsx
<div style={{ height: '400px' }}>
  <ResponsiveContainer width="100%" height="100%">
    <LineChart data={data.monthly_trends}>
      ...
    </LineChart>
  </ResponsiveContainer>
</div>
```

### 원인 5: JavaScript 번들링 오류

빌드 시 컴포넌트가 포함되지 않았을 수 있음.

**확인:**
```bash
cd /root/uvis
grep -r "FinancialDashboardPage" frontend/dist/assets/*.js | head -3
```

**해결:**
클린 빌드:
```bash
cd /root/uvis/frontend
rm -rf node_modules dist
npm install
npm run build

cd /root/uvis
docker-compose stop frontend
docker-compose rm -f frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

## 🎯 빠른 해결 방법

가장 가능성 높은 원인부터 순서대로 시도:

### 방법 1: Recharts 설치 확인 및 재빌드

```bash
cd /root/uvis

# 1. Recharts 확인 및 설치
cd frontend
if ! grep -q '"recharts"' package.json; then
    echo "Installing recharts..."
    npm install recharts --save
fi

# 2. 빌드
npm run build

# 3. 배포
cd /root/uvis
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker-compose restart frontend

# 4. 대기
sleep 15

# 5. 확인
docker ps | grep frontend
```

### 방법 2: 디버깅 버전 배포

현재 FinancialDashboardPage.tsx에 console.log 추가:

```bash
cd /root/uvis

# 백업
cp frontend/src/pages/FinancialDashboardPage.tsx frontend/src/pages/FinancialDashboardPage.tsx.backup

# 파일 수정 (console.log 추가)
# ... (아래 스크립트 참조)
```

---

## 📊 기대 결과

모든 문제가 해결되면:

1. **요약 카드** 3개가 표시됨:
   - 총 매출: ₩XXX,XXX
   - 수금액: ₩XXX,XXX
   - 미수금: ₩XXX,XXX

2. **월별 추이 차트** (Line Chart):
   - X축: 월 (YYYY-MM)
   - Y축: 금액
   - 파란색 선: 총 매출
   - 초록색 선: 수금액

3. **상위 고객 TOP 10** (Bar Chart):
   - X축: 고객명
   - Y축: 총 매출액
   - 파란색 막대

---

## 🆘 추가 지원 필요 시

위 방법으로 해결되지 않을 경우, 다음 정보를 제공해 주세요:

1. `./diagnose_charts.sh` 출력 결과 전체
2. 브라우저 Console 탭의 오류 메시지 (스크린샷)
3. 브라우저 Network 탭의 `/api/v1/billing/enhanced/dashboard/financial` 응답 (스크린샷)
4. 브라우저 Elements 탭의 재무 대시보드 DOM 구조 (스크린샷)

---

## 📝 체크리스트

진단 및 해결 과정에서 확인할 항목:

- [ ] `diagnose_charts.sh` 실행 완료
- [ ] `check_dashboard_component.sh` 실행 완료
- [ ] 브라우저 Console 확인
- [ ] 브라우저 Network 확인
- [ ] API 응답에 데이터 있음
- [ ] Recharts 패키지 설치 확인
- [ ] 컴포넌트 파일 존재 확인
- [ ] 빌드 파일에 FinancialDashboardPage 포함 확인
- [ ] 컨테이너에 최신 빌드 파일 배포 확인
- [ ] 브라우저 캐시 클리어 (Ctrl+Shift+R)

---

**마지막 업데이트**: 2026-02-12
**버전**: 1.0
