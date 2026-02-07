# Phase 9 - Swagger UI 테스트 가이드

## 🎯 목표
Phase 9 재무 대시보드 리포트(PDF/Excel) API를 Swagger UI에서 직접 테스트

---

## 📋 사전 준비

### 1. Swagger UI 접속
- **URL**: http://139.150.11.99:8000/docs
- **Reports 섹션**: http://139.150.11.99:8000/docs#/Reports

### 2. 인증 토큰 발급

#### Step 1: /api/v1/auth/login 엔드포인트 찾기
- Swagger UI에서 **Auth** 또는 **Authentication** 섹션 찾기
- `POST /api/v1/auth/login` 클릭

#### Step 2: Try it out 클릭

#### Step 3: Request Body 입력
```json
{
  "username": "admin",
  "password": "admin123"
}
```

#### Step 4: Execute 클릭

#### Step 5: Response에서 토큰 복사
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```
- `access_token` 값을 복사 (전체 토큰 문자열)

#### Step 6: 인증 설정
1. Swagger UI 상단 오른쪽 **🔓 Authorize** 버튼 클릭
2. **Value** 필드에 복사한 토큰 붙여넣기
3. **Authorize** 버튼 클릭
4. **Close** 버튼 클릭

✅ 이제 모든 API 요청에 자동으로 `Authorization: Bearer <token>` 헤더가 포함됩니다.

---

## 🧪 테스트 시나리오

### Test 1: Excel 리포트 다운로드

#### 엔드포인트
`POST /api/v1/reports/financial-dashboard/excel`

#### 위치
- Swagger UI → **Reports** 섹션 → 
  **POST /api/v1/reports/financial-dashboard/excel**

#### 테스트 절차

1. **Try it out** 클릭

2. **Parameters 입력**:
   ```
   start_date: 2025-11-07
   end_date: 2026-02-07
   ```

3. **Execute** 클릭

4. **예상 결과**:
   - **Status Code**: `200 OK`
   - **Response Headers**:
     ```
     content-type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
     content-disposition: attachment; filename="financial_dashboard_2025-11-07_2026-02-07.xlsx"
     ```
   - **Download 버튼**: 브라우저에서 파일 다운로드 버튼 표시

5. **파일 다운로드**:
   - **Download** 버튼 클릭
   - 파일명: `financial_dashboard_2025-11-07_2026-02-07.xlsx`
   - 파일 크기: 약 50-200 KB

6. **Excel 파일 검증**:
   - Excel로 파일 열기
   - **시트 4개 확인**:
     - ✅ **Summary**: 14개 재무 지표 카드
     - ✅ **Monthly Trends**: 최근 12개월 월별 추이 데이터
     - ✅ **Top Clients**: Top 10 고객 목록
     - ✅ **Charts**: 차트 데이터 (네이티브 Excel 차트)
   
   - **한글 폰트 확인**:
     - 헤더: "재무 대시보드 리포트"
     - 지표명: "총 수익", "청구 금액", "수금 금액" 등
   
   - **데이터 값**:
     - 테스트 데이터 없으면 0 또는 빈 값
     - 포맷: ₩0, 0%, 0건 등

---

### Test 2: PDF 리포트 다운로드

#### 엔드포인트
`POST /api/v1/reports/financial-dashboard/pdf`

#### 위치
- Swagger UI → **Reports** 섹션 → 
  **POST /api/v1/reports/financial-dashboard/pdf**

#### 테스트 절차

1. **Try it out** 클릭

2. **Parameters 입력**:
   ```
   start_date: 2025-11-07
   end_date: 2026-02-07
   ```

3. **Execute** 클릭

4. **예상 결과**:
   - **Status Code**: `200 OK`
   - **Response Headers**:
     ```
     content-type: application/pdf
     content-disposition: attachment; filename="financial_dashboard_2025-11-07_2026-02-07.pdf"
     ```
   - **Download 버튼**: 브라우저에서 파일 다운로드 버튼 표시

5. **파일 다운로드**:
   - **Download** 버튼 클릭
   - 파일명: `financial_dashboard_2025-11-07_2026-02-07.pdf`
   - 파일 크기: 약 200 KB - 2 MB

6. **PDF 파일 검증**:
   - PDF 뷰어로 파일 열기
   
   - **페이지 1 - 재무 요약**:
     - ✅ 헤더: "재무 대시보드 리포트"
     - ✅ 기간: "2025-11-07 ~ 2026-02-07"
     - ✅ **14개 재무 지표 카드**:
       - 총 수익 (Total Revenue)
       - 청구 금액 (Invoiced Amount)
       - 수금 금액 (Collected Amount)
       - 미수금 (Outstanding)
       - 수금률 (Collection Rate)
       - 연체 건수 (Overdue Count)
       - 연체 금액 (Overdue Amount)
       - 평균 결제 기간 (Avg Payment Days)
       - 신규 고객 (New Customers)
       - 활성 고객 (Active Customers)
       - 청구 건수 (Total Invoices)
       - 평균 거래액 (Avg Transaction Value)
       - 당월 성장률 (Monthly Growth)
       - 연간 성장률 (YoY Growth)
   
   - **페이지 2 - 월별 추이 차트**:
     - ✅ 선형 차트 이미지 (Base64 인코딩)
     - ✅ X축: 월 (2025-02 ~ 2026-01)
     - ✅ Y축: 금액 (₩)
     - ✅ 범례: 총 수익, 청구 금액, 수금 금액
   
   - **페이지 3 - Top 10 고객**:
     - ✅ 테이블: 순위, 고객명, 총 거래액, 거래 건수
     - ✅ 한글 폰트 렌더링 정상
   
   - **페이지 하단**:
     - ✅ 페이지 번호: "Page 1 of 3" 등
     - ✅ 생성 일시: 현재 시간

---

## ✅ 체크리스트

### Excel 리포트
- [ ] 토큰 인증 성공
- [ ] API 호출 200 OK
- [ ] Excel 파일 다운로드 성공
- [ ] 4개 시트 존재 확인
- [ ] 한글 폰트 정상 표시
- [ ] 14개 재무 지표 데이터 확인
- [ ] 차트 시트 네이티브 Excel 차트 확인

### PDF 리포트
- [ ] 토큰 인증 성공
- [ ] API 호출 200 OK
- [ ] PDF 파일 다운로드 성공
- [ ] 한글 폰트 정상 표시
- [ ] 14개 재무 지표 카드 표시
- [ ] 월별 추이 차트 이미지 렌더링
- [ ] Top 10 고객 테이블 표시
- [ ] 페이지 번호/생성 일시 표시

---

## 🐛 트러블슈팅

### 1. 401 Unauthorized
**원인**: 토큰 만료 또는 인증 실패

**해결**:
1. `/api/v1/auth/login`으로 새 토큰 발급
2. Swagger UI **Authorize** 버튼으로 토큰 재설정

### 2. 500 Internal Server Error
**원인**: 백엔드 서비스 오류

**해결**:
1. 백엔드 로그 확인:
   ```bash
   docker logs uvis-backend --tail 50
   ```
2. BillingEnhancedService 오류 확인
3. 데이터베이스 연결 확인

### 3. 파일 다운로드 안됨
**원인**: 브라우저 다운로드 설정 문제

**해결**:
1. 브라우저 팝업 차단 해제
2. 브라우저 다운로드 권한 확인
3. F12 → Network 탭에서 응답 확인

### 4. 한글 폰트 깨짐 (PDF만)
**원인**: fonts-nanum 설치 실패

**해결**:
1. Docker 컨테이너에서 폰트 확인:
   ```bash
   docker exec -it uvis-backend fc-list | grep -i nanum
   ```
2. 폰트 없으면 Dockerfile에서 fonts-nanum 재설치
3. 백엔드 재빌드

### 5. Excel 차트 없음
**원인**: openpyxl 차트 생성 실패

**해결**:
1. openpyxl 버전 확인: `3.1.2`
2. Excel 파일 열 때 "복구" 메시지 무시
3. Charts 시트에서 데이터 확인

---

## 📊 테스트 결과 보고 양식

### Excel 리포트 테스트
```
✅ Status Code: 200 OK
✅ 파일명: financial_dashboard_2025-11-07_2026-02-07.xlsx
✅ 파일 크기: 87 KB
✅ 시트 개수: 4개 (Summary, Monthly Trends, Top Clients, Charts)
✅ 한글 폰트: 정상
✅ 14개 지표: 모두 표시
❌ 차트 시트: 차트 생성 실패 (오류 내용)
```

### PDF 리포트 테스트
```
✅ Status Code: 200 OK
✅ 파일명: financial_dashboard_2025-11-07_2026-02-07.pdf
✅ 파일 크기: 542 KB
✅ 페이지 수: 3 페이지
✅ 한글 폰트: 정상
✅ 14개 지표 카드: 모두 표시
✅ 월별 차트 이미지: 정상 렌더링
✅ Top 10 고객 테이블: 정상 표시
```

---

## 🎉 성공 기준

### ✅ Phase 9 백엔드 배포 완전 성공 조건:
1. Excel 리포트 다운로드 성공
2. PDF 리포트 다운로드 성공
3. 한글 폰트 정상 표시 (PDF)
4. 14개 재무 지표 모두 표시
5. 차트 이미지 정상 렌더링 (PDF)
6. 네이티브 Excel 차트 생성 (Excel)
7. 파일 크기 정상 (<2MB)
8. API 응답 시간 <5초

---

## 📸 스크린샷 요청 (테스트 완료 후)

1. **Swagger UI - Excel 엔드포인트**:
   - Try it out → Execute → 200 OK 응답
   - Response Headers 확인

2. **Excel 파일 열기**:
   - Summary 시트 (14개 지표)
   - Charts 시트 (네이티브 차트)

3. **Swagger UI - PDF 엔드포인트**:
   - Try it out → Execute → 200 OK 응답
   - Response Headers 확인

4. **PDF 파일 열기**:
   - 페이지 1 (14개 재무 지표 카드)
   - 페이지 2 (월별 추이 차트)
   - 페이지 3 (Top 10 고객)

---

## 🚀 다음 단계

### 성공 시:
1. ✅ Phase 9 백엔드 배포 완료 선언
2. 프런트엔드 UI 구현 시작
3. 통합 테스트 진행

### 실패 시:
1. 로그 공유: `docker logs uvis-backend --tail 100`
2. 오류 메시지 분석
3. 백엔드 코드 수정
4. 재배포

---

**테스트 가이드 작성 완료!**  
**Swagger UI**: http://139.150.11.99:8000/docs#/Reports

이제 이 가이드를 따라 테스트하고 결과를 공유해주세요!
