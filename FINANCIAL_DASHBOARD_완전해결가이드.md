# 재무 대시보드 차트 미표시 문제 - 완전 해결 가이드

## 🎯 문제 요약

**증상**: 재무 대시보드 페이지는 로드되지만 UI 요소가 표시되지 않음
- ❌ 요약 카드 (총 매출, 수금액, 미수금)
- ❌ 월별 추이 차트
- ❌ TOP 10 고객 차트

**확인된 사항**:
- ✅ 백엔드 API는 정상 작동 (200 OK, 유효한 데이터 반환)
- ✅ Excel/PDF 다운로드 정상 작동
- ✅ 프론트엔드 코드는 올바름 (Recharts 포함)

## 🔍 근본 원인

**서버에 배포된 빌드가 오래된 버전입니다.**

프론트엔드 코드는 샌드박스(`/home/user/webapp`)에서는 올바르게 수정되었지만,
프로덕션 서버(`/root/uvis`)에는 **아직 배포되지 않았거나** 빌드가 완료되지 않았습니다.

## ✅ 해결 방법

### 🚀 원클릭 배포 (추천)

서버(`/root/uvis`)에서 다음 명령을 실행하세요:

```bash
cd /root/uvis && \
cd frontend && \
npm run build && \
cd /root/uvis && \
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/ && \
docker-compose restart frontend && \
sleep 15 && \
echo "✅ 배포 완료! 브라우저에서 Ctrl+Shift+R로 새로고침하세요."
```

### 📋 단계별 설명

#### 1️⃣ 프론트엔드 빌드
```bash
cd /root/uvis/frontend
npm run build
```
예상 시간: 30-60초

#### 2️⃣ Docker 컨테이너에 배포
```bash
cd /root/uvis
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
```

#### 3️⃣ 컨테이너 재시작
```bash
docker-compose restart frontend
sleep 15
```

#### 4️⃣ 확인
```bash
docker-compose ps | grep frontend
```

## 🧪 테스트 방법

### 1. 브라우저 접속
- URL: `http://139.150.11.99`
- 로그인: `admin` / `admin123`

### 2. 메뉴 이동
**청구/정산 → 재무 대시보드**

### 3. 강력 새로고침 (중요!)
- **Windows/Linux**: `Ctrl + Shift + R`
- **macOS**: `Cmd + Shift + R`

### 4. 확인 사항

#### ✅ 표시되어야 할 UI 요소:

1. **요약 카드 (4개)**
   - 총 매출: ₩31,744,234
   - 수금액: ₩9,682,242 (회수율 30.5%)
   - 미수금: ₩22,061,992
   - 미지급 정산: ₩0

2. **날짜 범위 선택**
   - 시작일/종료일 입력 필드

3. **액션 버튼**
   - 새로고침 버튼
   - Excel 다운로드 버튼
   - PDF 다운로드 버튼

4. **월별 매출 추이 차트** (라인 차트)
   - 파란색: 매출
   - 초록색: 수금
   - 보라색: 정산

5. **월별 순이익 차트** (바 차트)
   - 초록색 막대

6. **주요 거래처 TOP 10 테이블**
   - 순위, 거래처명, 총 매출, 청구 건수, 회수율

7. **빠른 작업 버튼들** (하단)
   - 청구서 생성
   - 연체 관리
   - 정산 처리

### 5. 개발자 도구 확인 (F12)

#### Console 탭
정상적인 로그:
```
Failed to load dashboard data: ...
```
이런 에러가 **없어야** 합니다.

#### Network 탭
- `/api/v1/billing/enhanced/dashboard/financial`: **200 OK**
- `/api/v1/billing/enhanced/monthly-trends`: **200 OK**
- `/api/v1/billing/enhanced/top-clients`: **200 OK**

## 🐛 문제 해결

### 문제 1: UI가 여전히 표시되지 않음

**확인 사항:**
```bash
# 서버에서 빌드 파일 확인
cd /root/uvis/frontend/dist/assets
ls -lh | grep Financial

# FinancialDashboardPage-*.js 파일이 있어야 함
```

**해결:**
```bash
# 빌드 캐시 완전 제거 후 재빌드
cd /root/uvis/frontend
rm -rf dist node_modules/.vite
npm run build
cd /root/uvis
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker-compose restart frontend
```

### 문제 2: API 에러 (401, 403)

**확인:**
```bash
# 토큰 발급
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# API 테스트
curl -X GET "http://localhost:8000/api/v1/billing/enhanced/dashboard/financial?start_date=2026-01-01&end_date=2026-02-12" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

**예상 응답:**
```json
{
  "period_start": "2026-01-01",
  "period_end": "2026-02-12",
  "total_revenue": 31744234.92,
  "collected_amount": 9682242.89,
  "total_receivables": 22061992.03,
  ...
}
```

### 문제 3: Recharts 로딩 실패

**확인:**
```bash
# Recharts가 빌드에 포함되었는지 확인
cd /root/uvis/frontend/dist/assets
grep -l "recharts\|LineChart" *.js
```

**해결:**
```bash
cd /root/uvis/frontend
npm install recharts@^2.10.0
npm run build
cd /root/uvis
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker-compose restart frontend
```

### 문제 4: 브라우저 캐시

**해결:**
1. 강력 새로고침: `Ctrl + Shift + R`
2. 또는 개발자 도구 → Network 탭 → "Disable cache" 체크
3. 또는 시크릿/프라이빗 모드에서 접속

## 📊 기술 상세

### 프론트엔드 구조

**파일**: `frontend/src/pages/FinancialDashboardPage.tsx`

**사용 API:**
- `BillingEnhancedAPI.getFinancialDashboard(start, end)` - 요약 데이터
- `BillingEnhancedAPI.getMonthlyTrends(?, ?, months)` - 월별 추이
- `BillingEnhancedAPI.getTopClients(start, end, limit)` - TOP 고객
- `BillingEnhancedAPI.downloadFinancialDashboardExcel(...)` - Excel 다운로드
- `BillingEnhancedAPI.downloadFinancialDashboardPDF(...)` - PDF 다운로드

**사용 라이브러리:**
- React 18
- Recharts 2.10.0 (LineChart, BarChart)
- Lucide React (아이콘)
- Tailwind CSS (스타일링)

**상태 관리:**
```typescript
const [summary, setSummary] = useState<FinancialSummary | null>(null);
const [trends, setTrends] = useState<MonthlyTrend[]>([]);
const [topClients, setTopClients] = useState<TopClient[]>([]);
const [loading, setLoading] = useState(false);
```

### 백엔드 API

**엔드포인트**: `/api/v1/billing/enhanced/dashboard/financial`

**응답 구조**:
```json
{
  "period_start": "2026-01-01",
  "period_end": "2026-02-12",
  "total_revenue": 31744234.92,
  "invoiced_amount": 31744234.92,
  "collected_amount": 9682242.89,
  "collection_rate": 30.5,
  "total_receivables": 22061992.03,
  "current_receivables": 16804581.97,
  "overdue_receivables": 5257410.06,
  "overdue_count": 3,
  "total_settlements": 0.0,
  "pending_settlements": 0.0,
  "paid_settlements": 0.0,
  "cash_in": 9682242.89,
  "cash_out": 0.0,
  "net_cash_flow": 9682242.89
}
```

## 📝 체크리스트

배포 전:
- [ ] 프론트엔드 코드 수정 완료
- [ ] `frontend/src/pages/FinancialDashboardPage.tsx` 존재
- [ ] Recharts가 `package.json`에 포함됨
- [ ] API 함수들이 `frontend/src/api/billing-enhanced.ts`에 정의됨

배포:
- [ ] `npm run build` 실행
- [ ] 빌드 성공 (에러 없음)
- [ ] `dist` 폴더 생성됨
- [ ] Docker 컨테이너에 복사
- [ ] 컨테이너 재시작

테스트:
- [ ] 브라우저에서 페이지 접속
- [ ] 강력 새로고침 (Ctrl+Shift+R)
- [ ] 요약 카드 4개 표시됨
- [ ] 월별 추이 차트 표시됨
- [ ] 월별 순이익 차트 표시됨
- [ ] TOP 10 테이블 표시됨
- [ ] 다운로드 버튼 작동
- [ ] Console 에러 없음

## 🎓 재발 방지

앞으로 코드 수정 시:

1. **항상 빌드**: `npm run build`
2. **항상 배포**: `docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/`
3. **항상 재시작**: `docker-compose restart frontend`
4. **항상 새로고침**: 브라우저에서 `Ctrl+Shift+R`
5. **Git 커밋**: 변경사항 커밋 및 푸시
6. **문서화**: 이 가이드 참고

## 📞 추가 지원

문제가 지속되면:

1. **스크린샷 제공**:
   - 브라우저 Console 탭
   - Network 탭
   - 실제 화면

2. **로그 확인**:
   ```bash
   docker-compose logs frontend | tail -50
   docker-compose logs backend | tail -50
   ```

3. **빌드 로그 확인**:
   ```bash
   cd /root/uvis/frontend
   npm run build 2>&1 | tee build.log
   ```

---

**작성일**: 2026-02-14
**버전**: 1.0
**상태**: 해결 방법 제공 완료
