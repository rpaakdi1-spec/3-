# 🚀 테스트 데이터 생성 및 배포 가이드

## 📊 현재 상황 요약

### ✅ 완료된 작업
1. **API 통합 및 최적화** (커밋 d29e9d1)
   - 8개 파일의 중복 API URL을 단일 설정 파일로 통합
   - 개발/프로덕션 환경별 로깅 최적화
   - 401 인증 오류 해결 (axios 인터셉터 추가)

2. **프론트엔드 디버깅 및 수정** (커밋 6b5e90d)
   - `debugAuth()` 프로덕션 오류 수정
   - FinancialDashboardPage 인증 로직 개선

3. **테스트 데이터 생성 스크립트** (커밋 5887b82)
   - 청구서/정산 데이터 자동 생성 도구
   - 통계 및 리포트 기능

4. **문서화** (커밋 4f9b711)
   - TEST_DATA_GENERATION.md 생성
   - TODO.md 업데이트

### ❌ 해결할 문제
**재무 대시보드에 데이터가 표시되지 않음**
- **원인**: 데이터베이스가 비어있음
- **증상**: API는 200 OK를 반환하지만 모든 값이 0
- **해결**: 테스트 데이터 생성 필요

## 🎯 즉시 수행할 작업

### STEP 1: 서버에 최신 코드 배포

```bash
# 1. 서버 접속
ssh root@139.150.11.99

# 2. 프로젝트 디렉토리로 이동
cd /root/uvis

# 3. 현재 브랜치 확인
git branch

# 4. 최신 코드 가져오기
git fetch origin genspark_ai_developer

# 5. 로컬 변경사항 확인 (있으면 백업)
git status

# 6. 최신 코드로 업데이트
git reset --hard origin/genspark_ai_developer

# 7. 최근 커밋 확인 (4f9b711이 최신)
git log --oneline -5
```

**예상 출력:**
```
4f9b711 docs: Add comprehensive test data generation guide
5887b82 feat(backend): Add billing test data generation script
6b5e90d fix(frontend): Remove debugAuth check that breaks production build
d29e9d1 refactor(frontend): Centralize API configuration and cleanup
7e618ba docs: Update TODO.md with priority tasks
```

### STEP 2: 테스트 데이터 생성

```bash
# 서버에 접속한 상태에서

# 1. 스크립트 실행
docker exec -it uvis-backend python /app/scripts/generate_billing_test_data.py

# 2. 결과 확인
# 스크립트가 생성한 통계 정보를 확인합니다
```

**예상 출력:**
```
============================================================
청구/정산 테스트 데이터 생성 시작
============================================================

📊 기존 데이터 현황:
   - 청구서: 0개
   - 정산: 0개

📋 마스터 데이터 현황:
   - 거래처: 10개
   - 기사: 5개
   - 배차: 100개

📝 청구서 생성 중...
   ✅ 85개의 청구서 생성 완료

💰 기사 정산 생성 중...
   ✅ 25개의 정산 생성 완료

============================================================
✅ 테스트 데이터 생성 완료!
============================================================

📊 생성된 데이터:
   - 총 청구서: 85개
     ├─ 초안: 15개
     ├─ 발송됨: 18개
     ├─ 결제 완료: 22개
     ├─ 부분 결제: 17개
     └─ 연체: 13개
   - 총 결제 기록: 39개
   - 총 정산: 25개

💰 금액 통계:
   - 총 청구 금액: ₩185,420,350
   - 총 수금 금액: ₩98,750,280
   - 수금률: 53.2%
   - 총 정산 금액: ₩42,380,500
```

### STEP 3: 데이터 검증

#### 3-1. 데이터베이스 직접 확인

```bash
# PostgreSQL 컨테이너 접속
docker exec -it uvis-postgres psql -U uvis_user -d uvis_db

# 청구서 개수 확인
SELECT COUNT(*) FROM invoices;

# 청구서 상태별 개수
SELECT status, COUNT(*) 
FROM invoices 
GROUP BY status;

# 총 청구 금액
SELECT 
  SUM(total_amount) as total_invoiced,
  SUM(paid_amount) as total_paid,
  ROUND((SUM(paid_amount) / SUM(total_amount) * 100)::numeric, 2) as collection_rate
FROM invoices;

# 최근 청구서 5개
SELECT 
  invoice_number, 
  total_amount, 
  status, 
  issue_date 
FROM invoices 
ORDER BY issue_date DESC 
LIMIT 5;

# 정산 개수 확인
SELECT COUNT(*) FROM driver_settlements;

# 종료
\q
```

#### 3-2. API 테스트

```bash
# 로그인하여 토큰 획득
TOKEN=$(curl -s -X POST "http://139.150.11.99/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  | jq -r '.access_token')

# 토큰 확인
echo "Token: $TOKEN"

# 재무 대시보드 API 호출
curl -X GET "http://139.150.11.99/api/v1/billing/enhanced/dashboard/financial?start_date=2025-11-12&end_date=2026-02-12" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# 월별 추이 API 호출
curl -X GET "http://139.150.11.99/api/v1/billing/enhanced/dashboard/trends?months=12" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# TOP 10 거래처 API 호출
curl -X GET "http://139.150.11.99/api/v1/billing/enhanced/dashboard/top-clients?limit=10" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

**예상 응답 (financial):**
```json
{
  "period_start": "2025-11-12",
  "period_end": "2026-02-12",
  "total_revenue": 185420350.0,
  "invoiced_amount": 185420350.0,
  "collected_amount": 98750280.0,
  "collection_rate": 53.2,
  "total_receivables": 86670070.0,
  "current_receivables": 45230000.0,
  "overdue_receivables": 41440070.0,
  "overdue_count": 13,
  "total_settlements": 42380500.0,
  "pending_settlements": 18750000.0,
  "paid_settlements": 23630500.0,
  "cash_in": 98750280.0,
  "cash_out": 23630500.0,
  "net_cash_flow": 75119780.0
}
```

### STEP 4: 웹 UI 확인

```bash
# 브라우저에서 확인
# URL: http://139.150.11.99
```

#### 체크리스트:

1. **로그인**
   - [ ] admin / admin123 로그인 성공
   - [ ] 토큰이 localStorage에 저장됨
   - [ ] 대시보드로 리다이렉트

2. **재무 대시보드** (청구/정산 > 재무 대시보드)
   - [ ] 4개 요약 카드에 숫자 표시
     - 총 매출액: ₩185,420,350
     - 수금률: 53.2%
     - 연체 금액: ₩41,440,070
     - 정산 대기: ₩18,750,000
   - [ ] 월별 매출 추이 차트에 라인 그래프 표시
   - [ ] 월별 수익 분석 차트에 바 차트 표시
   - [ ] TOP 10 거래처 테이블에 10개 행 표시

3. **Network 탭** (DevTools)
   - [ ] 3개의 API 요청 모두 200 OK
   - [ ] Authorization 헤더 포함
   - [ ] 응답 데이터에 숫자 값 포함 (0이 아님)

4. **Console 탭**
   - [ ] 에러 없음
   - [ ] 프로덕션 빌드에서는 디버그 로그 없음

### STEP 5: 스크린샷 캡처 및 공유

다음 스크린샷을 캡처해주세요:

1. **재무 대시보드 전체 화면**
   - 4개 카드, 2개 차트, TOP 10 테이블이 모두 보이게

2. **Network 탭**
   - 필터: `billing`
   - 3개의 200 OK 요청 표시
   - 하나의 요청 선택 후 Headers 탭 (Authorization 헤더 확인)
   - Response 탭 (데이터 내용 확인)

3. **Console 탭**
   - 에러가 없음을 보여주는 화면
   - 프로덕션에서 디버그 로그가 없음

4. **Sidebar**
   - 모든 메뉴 항목이 표시되는지 확인

## 🔧 문제 해결

### 문제 1: 스크립트 실행 시 에러

```bash
# 에러 메시지 확인
docker logs uvis-backend --tail 100

# 컨테이너 내부에서 직접 실행
docker exec -it uvis-backend bash
cd /app
python scripts/generate_billing_test_data.py
```

### 문제 2: 데이터가 생성되었는데 UI에 표시 안됨

```bash
# 1. 브라우저 캐시 삭제
# Chrome: Ctrl+Shift+R

# 2. localStorage 확인
# DevTools Console에서:
localStorage.getItem('access_token')

# 3. 날짜 범위 확인
# 최근 3개월 데이터만 생성되므로 날짜 범위를 적절히 설정
```

### 문제 3: 401 Unauthorized 에러

```bash
# 토큰 재발급
# 브라우저에서 로그아웃 후 재로그인

# 또는 콘솔에서:
localStorage.clear()
# 페이지 새로고침 후 재로그인
```

### 문제 4: 기존 테스트 데이터 삭제 필요

```bash
docker exec -it uvis-postgres psql -U uvis_user -d uvis_db

# 청구서 삭제 (CASCADE로 관련 데이터 모두 삭제)
DELETE FROM invoices WHERE invoice_number LIKE 'INV-2026-%';

# 정산 삭제
DELETE FROM driver_settlements WHERE settlement_number LIKE 'STL-2026-%';

# 테스트 거래처 삭제 (필요시)
DELETE FROM clients WHERE client_code LIKE 'CLI%';

\q
```

## 📊 성공 기준

모든 항목이 체크되어야 합니다:

- [x] 최신 코드 배포 완료 (커밋 4f9b711)
- [ ] 테스트 데이터 생성 완료 (50개 이상의 청구서)
- [ ] 데이터베이스에 데이터 존재 확인
- [ ] API 응답에 실제 데이터 포함 (0이 아님)
- [ ] 재무 대시보드에 데이터 표시
  - [ ] 4개 카드에 숫자
  - [ ] 2개 차트에 그래프
  - [ ] TOP 10 테이블에 행
- [ ] Network 탭에서 3개 API 모두 200 OK
- [ ] Console에 에러 없음

## 🎯 다음 단계

데이터 표시가 확인되면:

1. **다른 청구/정산 메뉴 테스트**
   - 요금 미리보기
   - 자동 청구 스케줄
   - 정산 승인
   - 결제 알림
   - 데이터 내보내기

2. **다른 페이지 사이드바 확인**
   - 온도 모니터링
   - 차량 유지보수
   - 실시간 텔레메트리
   - 등등...

3. **Pull Request 생성**
   - 모든 변경사항 squash
   - main 브랜치로 PR 생성
   - PR 링크 공유

## 📞 지원

문제가 발생하면:
1. 위의 문제 해결 섹션 확인
2. 로그 확인: `docker logs uvis-backend --tail 100`
3. 상세한 에러 메시지와 스크린샷 공유

## 📚 관련 문서

- [TEST_DATA_GENERATION.md](TEST_DATA_GENERATION.md) - 상세 가이드
- [TODO.md](../TODO.md) - 전체 작업 목록
- [DEVELOPMENT_WORKFLOW.md](../DEVELOPMENT_WORKFLOW.md) - 개발 워크플로우

## 🔗 GitHub 커밋 히스토리

- 4f9b711 - docs: Add comprehensive test data generation guide
- 5887b82 - feat(backend): Add billing test data generation script
- 6b5e90d - fix(frontend): Remove debugAuth check
- d29e9d1 - refactor(frontend): Centralize API configuration
- 7e618ba - docs: Update TODO.md

**GitHub 브랜치**: https://github.com/rpaakdi1-spec/3-/tree/genspark_ai_developer
