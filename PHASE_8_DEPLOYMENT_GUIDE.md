# Phase 8: Frontend Deployment Guide 🚀

**Date**: 2026-02-06  
**Branch**: genspark_ai_developer  
**Latest Commit**: 71cc2f3

---

## 📋 배포 체크리스트

### ✅ 완료된 작업
- [x] Phase 8 백엔드 구현 완료
- [x] Phase 8 데이터베이스 마이그레이션 적용
- [x] Phase 8 백엔드 프로덕션 배포
- [x] Phase 8 프론트엔드 구현 완료
- [x] Git 커밋 및 푸시 완료

### 🚀 다음 배포 단계

#### 1. 프론트엔드 의존성 설치

```bash
# 프로덕션 서버에서 실행
cd /root/uvis/frontend

# Node.js 버전 확인 (v16+ 필요)
node --version

# 의존성 설치 (이미 설치되어 있을 수 있음)
npm install

# Recharts 설치 확인 (Phase 8 필수)
npm list recharts

# 없으면 설치
npm install recharts
```

#### 2. 프론트엔드 빌드

```bash
cd /root/uvis/frontend

# 환경 변수 설정 확인
cat .env.production

# 프로덕션 빌드
npm run build

# 빌드 결과 확인
ls -lh dist/
```

#### 3. 프론트엔드 배포

**Option A: Docker 사용**
```bash
cd /root/uvis

# Frontend 컨테이너 재빌드
docker-compose build --no-cache frontend

# Frontend 재시작
docker-compose up -d frontend

# 로그 확인
docker-compose logs frontend --tail=50
```

**Option B: Nginx 직접 배포**
```bash
cd /root/uvis/frontend

# 기존 파일 백업
sudo cp -r /var/www/html /var/www/html.backup.$(date +%Y%m%d_%H%M%S)

# 새 빌드 파일 복사
sudo cp -r dist/* /var/www/html/

# 권한 설정
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

# Nginx 재시작
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. 동작 확인

```bash
# Frontend 접속 테스트
curl -I http://139.150.11.99/

# API 헬스체크
curl http://139.150.11.99:8000/health

# Phase 8 API 테스트
curl http://139.150.11.99:8000/api/v1/billing/enhanced/health
```

---

## 🧪 수동 테스트 가이드

### 1. 재무 대시보드 테스트

**URL**: http://139.150.11.99/billing/financial-dashboard

**테스트 절차**:
1. ✅ 페이지 접속 (로그인 필요)
2. ✅ 요약 카드 4개 표시 확인
   - 총 매출
   - 수금액
   - 미수금
   - 미지급 정산
3. ✅ 월별 매출 추이 차트 확인
   - Line Chart 렌더링
   - 데이터 포인트 hover 시 tooltip
4. ✅ 월별 회수율 차트 확인
   - Bar Chart 렌더링
5. ✅ 주요 거래처 TOP 10 테이블 확인
   - 순위, 거래처명, 금액 표시
   - 회수율 색상 구분
6. ✅ 날짜 범위 필터 작동 확인
7. ✅ 새로고침 버튼 작동 확인
8. ✅ 반응형 디자인 확인 (모바일/태블릿)

**예상 결과**:
- 모든 차트와 테이블이 정상 표시
- 데이터가 백엔드 API에서 정상 로드
- 필터링 및 새로고침이 정상 작동

**문제 해결**:
- 차트가 표시되지 않으면: `recharts` 패키지 설치 확인
- API 오류 발생 시: 백엔드 로그 확인
- 인증 오류 시: 로그인 상태 및 토큰 확인

---

### 2. 실시간 요금 계산기 테스트

**URL**: http://139.150.11.99/billing/charge-preview

**테스트 절차**:
1. ✅ 페이지 접속 (로그인 필요)
2. ✅ 입력 폼 확인
3. ✅ 기본 요금 계산 테스트:
   ```
   거래처 ID: 1
   운행 거리: 50 km
   팔레트 수: 0
   중량: 0 kg
   배차 날짜: (오늘)
   특수 조건: 모두 체크 해제
   → "요금 계산하기" 클릭
   ```
4. ✅ 계산 결과 확인:
   - 총 예상 요금 표시
   - 거리 요금 상세 내역
   - 기본 요금 합계

5. ✅ 팔레트 추가 테스트:
   ```
   팔레트 수: 10
   → "요금 계산하기" 클릭
   ```
   - 팔레트 요금 추가 확인

6. ✅ 할증 테스트:
   ```
   ☑️ 주말 배차
   ☑️ 긴급 배송
   ☑️ 온도 관리 필요
   → "요금 계산하기" 클릭
   ```
   - 할증 요금 섹션 표시
   - 주말/긴급/온도 할증 금액

7. ✅ 유효성 검증 테스트:
   ```
   거래처 ID: 0 (또는 빈 값)
   → "요금 계산하기" 클릭
   ```
   - 오류 메시지 표시 확인

8. ✅ 반응형 디자인 확인

**예상 결과**:
- 입력값에 따라 정확한 요금 계산
- 할증 및 할인이 올바르게 적용
- 유효성 검증이 정상 작동
- 반응형 레이아웃이 모든 기기에서 정상 표시

**문제 해결**:
- API 오류 시: 백엔드 `/api/v1/billing/enhanced/preview` 엔드포인트 확인
- 계산 결과가 0원인 경우: 백엔드 BillingPolicy 설정 확인
- 할증/할인이 적용되지 않는 경우: 백엔드 정책 데이터 확인

---

## 🔧 설정 파일

### Frontend .env.production

```bash
# 프로덕션 환경변수
VITE_API_URL=http://139.150.11.99:8000
VITE_WS_URL=ws://139.150.11.99:8000/ws
VITE_APP_NAME="Cold Chain Dispatch System"
VITE_APP_VERSION="1.0.0"
```

### Backend 환경변수 확인

```bash
# 프로덕션 서버에서 확인
cd /root/uvis/backend
cat .env | grep -E "DATABASE_URL|CORS_ORIGINS|API_PREFIX"

# 예상 값
# DATABASE_URL=postgresql://uvis_user:uvis_password@db:5432/uvis_db
# CORS_ORIGINS=http://139.150.11.99,http://localhost:5173
# API_PREFIX=/api/v1
```

---

## 📊 API 엔드포인트 테스트

### 1. 재무 대시보드 API

```bash
# 토큰 획득 (admin 로그인)
TOKEN=$(curl -X POST http://139.150.11.99:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 재무 대시보드 데이터 조회
curl -X GET "http://139.150.11.99:8000/api/v1/billing/enhanced/dashboard/financial?start_date=2026-01-01&end_date=2026-02-28" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# 월별 추이 조회
curl -X GET "http://139.150.11.99:8000/api/v1/billing/enhanced/dashboard/trends?months=12" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# 주요 거래처 조회
curl -X GET "http://139.150.11.99:8000/api/v1/billing/enhanced/dashboard/top-clients?limit=10" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 2. 실시간 요금 계산 API

```bash
# 요금 미리보기
curl -X POST http://139.150.11.99:8000/api/v1/billing/enhanced/preview \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "distance_km": 50.0,
    "total_pallets": 10,
    "total_weight_kg": 1500.0,
    "is_weekend": false,
    "is_urgent": false,
    "requires_temperature_control": false,
    "dispatch_date": "2026-02-06"
  }' \
  | jq
```

**예상 응답**:
```json
{
  "base_amount": 150000.0,
  "surcharge_amount": 0.0,
  "discount_amount": 0.0,
  "total_amount": 150000.0,
  "details": {
    "distance_charge": 100000.0,
    "pallet_charge": 50000.0,
    "weight_charge": 0.0,
    "weekend_surcharge": 0.0,
    "urgent_surcharge": 0.0,
    "temperature_surcharge": 0.0,
    "volume_discount": 0.0
  }
}
```

---

## 🚨 문제 해결 가이드

### 문제 1: Recharts 차트가 표시되지 않음

**증상**: 재무 대시보드에서 차트 영역이 비어있음

**원인**: recharts 패키지 미설치 또는 버전 호환성 문제

**해결**:
```bash
cd /root/uvis/frontend

# recharts 재설치
npm uninstall recharts
npm install recharts@latest

# 빌드 재실행
npm run build
```

### 문제 2: API 호출 시 CORS 오류

**증상**: 브라우저 콘솔에 CORS 오류 표시

**원인**: 백엔드 CORS 설정에 프론트엔드 URL 미포함

**해결**:
```bash
cd /root/uvis/backend

# .env 파일 수정
nano .env

# CORS_ORIGINS에 추가
CORS_ORIGINS=http://139.150.11.99,http://localhost:5173

# 백엔드 재시작
docker-compose restart backend
```

### 문제 3: 인증 토큰 만료

**증상**: API 호출 시 401 Unauthorized 오류

**원인**: access_token 만료

**해결**:
- 브라우저에서 재로그인
- 또는 localStorage에서 토큰 수동 갱신

### 문제 4: 빌드 오류 발생

**증상**: `npm run build` 실행 시 오류

**원인**: TypeScript 타입 오류 또는 의존성 문제

**해결**:
```bash
cd /root/uvis/frontend

# node_modules 재설치
rm -rf node_modules package-lock.json
npm install

# TypeScript 캐시 클리어
npm run build -- --force
```

---

## 📦 필요한 패키지 목록

### Frontend Dependencies

**필수 패키지** (이미 설치되어 있어야 함):
- `react` (^18.0.0)
- `react-dom` (^18.0.0)
- `react-router-dom` (^6.0.0)
- `axios` (^1.0.0)
- `lucide-react` (^0.200.0)
- `tailwindcss` (^3.0.0)

**Phase 8 신규 필수**:
- `recharts` (^2.5.0 이상)

**설치 확인**:
```bash
cd /root/uvis/frontend
npm list react react-dom react-router-dom axios lucide-react recharts
```

**일괄 설치**:
```bash
npm install react react-dom react-router-dom axios lucide-react recharts
```

---

## 🎯 성공 기준

### ✅ 배포 성공 확인

1. **Frontend 접속**
   - URL: http://139.150.11.99
   - 로그인 페이지 정상 표시
   - 로그인 성공 (admin/admin123)

2. **재무 대시보드**
   - URL: http://139.150.11.99/billing/financial-dashboard
   - 요약 카드 4개 표시
   - 차트 2개 렌더링
   - 테이블 데이터 표시

3. **실시간 요금 계산기**
   - URL: http://139.150.11.99/billing/charge-preview
   - 입력 폼 표시
   - 계산 기능 작동
   - 결과 정상 표시

4. **API 연동**
   - 백엔드 API 정상 응답
   - 데이터 로딩 성공
   - 오류 처리 정상

5. **반응형 디자인**
   - 데스크톱 레이아웃 정상
   - 태블릿 레이아웃 정상
   - 모바일 레이아웃 정상

---

## 📈 모니터링

### 프론트엔드 로그

```bash
# Docker 사용 시
docker-compose logs frontend --tail=100 -f

# Nginx 로그
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 백엔드 로그

```bash
# Docker 사용 시
docker-compose logs backend --tail=100 -f

# Phase 8 API 관련 로그 필터링
docker-compose logs backend | grep -i "billing_enhanced"
```

### 브라우저 개발자 도구

1. F12 키로 개발자 도구 열기
2. **Console** 탭: JavaScript 오류 확인
3. **Network** 탭: API 호출 및 응답 확인
4. **Application** 탭: localStorage의 access_token 확인

---

## 🚀 다음 단계

### 단기 (1-2일)
1. ✅ 프론트엔드 의존성 설치 및 빌드
2. ✅ 프론트엔드 배포
3. ✅ 통합 테스트 수행
4. ✅ 버그 수정 및 미세 조정

### 중기 (1주)
1. 자동 청구 스케줄 페이지 구현
2. 정산 승인 워크플로우 페이지 구현
3. 결제 알림 관리 페이지 구현
4. 내보내기 작업 관리 페이지 구현

### 장기 (1-2주)
1. 기존 BillingPage와 Phase 8 페이지 통합
2. 사이드바 네비게이션 메뉴 업데이트
3. 사용자 가이드 및 도움말 작성
4. 성능 최적화 및 로딩 속도 개선

---

## 📞 지원 및 문의

### 기술 문서
- Phase 8 백엔드: `PHASE_8_BILLING_ENHANCED_COMPLETE.md`
- Phase 8 프론트엔드: `PHASE_8_FRONTEND_COMPLETE.md`
- API 문서: http://139.150.11.99:8000/docs

### Git Repository
- Repository: https://github.com/rpaakdi1-spec/3-.git
- Branch: `genspark_ai_developer`
- Latest Commit: `71cc2f3`

---

**작성일**: 2026-02-06  
**상태**: ✅ Phase 8 Frontend Ready for Deployment
