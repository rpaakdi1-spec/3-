# Phase 9: 고급 리포팅 시스템 구현 계획

**작성일**: 2026-02-07  
**상태**: 🚀 시작  
**우선순위**: 높음  
**예상 소요**: 3-4일  

---

## 📋 목표

Phase 8 청구/정산 데이터를 **PDF 및 Excel 형식**으로 내보내기 기능 구현

---

## 🎯 구현 범위

### 1️⃣ 리포트 종류

#### 우선순위 1: 재무 대시보드 리포트 (핵심)
- **내용**:
  - 14개 재무 지표 (총 수익, 청구액, 수금액, 미수금, 수금률 등)
  - 월별 추이 차트 (수익, 청구, 수금)
  - Top 10 고객 목록
  - 기간: 사용자 선택 (start_date ~ end_date)

- **포맷**:
  - PDF: 인쇄/프레젠테이션용 (로고, 차트 이미지 포함)
  - Excel: 데이터 분석용 (피벗 테이블, 차트 시트)

#### 우선순위 2: 청구서 리포트
- **내용**:
  - 청구서 목록 (고객명, 청구액, 상태, 기한)
  - 청구 통계 (총 건수, 총 금액, 상태별 통계)
  - 필터: 기간, 고객, 상태

- **포맷**:
  - PDF: 요약 + 목록
  - Excel: 상세 데이터 + 피벗

#### 우선순위 3: 정산 리포트
- **내용**:
  - 정산 내역 (정산일, 금액, 수수료, 순액)
  - 정산 통계 (총 정산액, 평균 수수료율)
  - 필터: 기간, 상태

- **포맷**:
  - PDF: 요약 + 목록
  - Excel: 상세 데이터

#### 우선순위 4: 수금 현황 리포트
- **내용**:
  - 수금률 분석
  - 연체 현황 (건수, 금액)
  - 고객별 수금 현황

- **포맷**:
  - PDF: 차트 중심
  - Excel: 데이터 중심

---

## 🛠️ 기술 스택

### Backend (Python)

#### PDF 생성
- **라이브러리**: `WeasyPrint` (HTML → PDF)
  - 한글 폰트 지원 우수
  - CSS 스타일링 지원
  - 차트 이미지 삽입 가능

- **설치**:
  ```bash
  pip install weasyprint
  pip install pillow  # 이미지 처리
  ```

- **한글 폰트**:
  - 나눔고딕 (`NanumGothic.ttf`)
  - 서버에 폰트 설치 필요

#### Excel 생성
- **라이브러리**: `openpyxl` (이미 설치됨)
  - 다중 시트 지원
  - 차트 삽입
  - 스타일링 (색상, 테두리, 정렬)

- **추가 설치**:
  ```bash
  pip install openpyxl  # 이미 설치됨 확인
  ```

#### 차트 생성
- **라이브러리**: `matplotlib` 또는 `plotly`
  - PDF용: 이미지 생성 (PNG)
  - Excel용: 네이티브 차트 삽입

- **설치**:
  ```bash
  pip install matplotlib
  pip install plotly
  ```

#### 템플릿 엔진
- **라이브러리**: `Jinja2` (이미 FastAPI에 포함)
  - HTML 템플릿 렌더링
  - 변수 치환, 반복문, 조건문

### Frontend (React + TypeScript)

- **기존 컴포넌트 재사용**:
  - DatePicker (날짜 범위 선택)
  - Button (내보내기 버튼)
  - Modal (리포트 옵션 선택)

- **새 컴포넌트**:
  - `ReportExportButton.tsx`: 내보내기 버튼
  - `ReportExportModal.tsx`: 옵션 선택 모달
  - `ReportHistoryPage.tsx`: 리포트 히스토리 (옵션)

---

## 📂 프로젝트 구조

### Backend

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── reports.py          # 🆕 리포트 API 엔드포인트
│   ├── services/
│   │   ├── report_generator.py        # 🆕 리포트 생성 서비스
│   │   ├── pdf_generator.py           # 🆕 PDF 생성
│   │   └── excel_generator.py         # 🆕 Excel 생성
│   ├── templates/
│   │   └── reports/                   # 🆕 PDF 템플릿 (HTML)
│   │       ├── financial_dashboard.html
│   │       ├── invoices.html
│   │       ├── settlements.html
│   │       └── collection_status.html
│   └── static/
│       └── fonts/                     # 🆕 한글 폰트
│           └── NanumGothic.ttf
├── requirements.txt                   # 🔧 업데이트 (weasyprint, matplotlib)
└── Dockerfile                         # 🔧 업데이트 (폰트 설치)
```

### Frontend

```
frontend/
└── src/
    ├── components/
    │   └── reports/                   # 🆕 리포트 컴포넌트
    │       ├── ReportExportButton.tsx
    │       └── ReportExportModal.tsx
    ├── api/
    │   └── reports.ts                 # 🆕 리포트 API 클라이언트
    └── pages/
        └── ReportHistoryPage.tsx      # 🆕 리포트 히스토리 (옵션)
```

---

## 🔧 구현 단계

### 1단계: 백엔드 기본 설정 (1-2시간)
- [ ] Python 패키지 설치 (`weasyprint`, `matplotlib`)
- [ ] 한글 폰트 다운로드 및 설정
- [ ] 기본 리포트 서비스 클래스 구조 생성

### 2단계: PDF 생성 구현 (4-6시간)
- [ ] HTML 템플릿 작성 (Jinja2)
- [ ] 재무 대시보드 PDF 생성 함수
- [ ] 차트 이미지 생성 (matplotlib)
- [ ] 한글 폰트 적용 및 테스트

### 3단계: Excel 생성 구현 (3-4시간)
- [ ] 재무 대시보드 Excel 생성 함수
- [ ] 다중 시트 구조 (데이터/차트/요약)
- [ ] 스타일링 (색상, 테두리, 정렬)
- [ ] 차트 삽입 (openpyxl 네이티브)

### 4단계: API 엔드포인트 구현 (2-3시간)
- [ ] `/api/v1/reports/financial-dashboard/pdf`
- [ ] `/api/v1/reports/financial-dashboard/excel`
- [ ] 파라미터: `start_date`, `end_date`, `format`
- [ ] 파일 다운로드 응답 (StreamingResponse)

### 5단계: 프론트엔드 UI 구현 (3-4시간)
- [ ] 재무 대시보드 페이지에 "리포트 다운로드" 버튼 추가
- [ ] 리포트 옵션 선택 모달 (PDF/Excel)
- [ ] API 호출 및 파일 다운로드 처리
- [ ] 로딩 상태 및 에러 처리

### 6단계: 추가 리포트 구현 (옵션, 4-6시간)
- [ ] 청구서 리포트 (PDF/Excel)
- [ ] 정산 리포트 (PDF/Excel)
- [ ] 수금 현황 리포트 (PDF/Excel)

### 7단계: 리포트 히스토리 (옵션, 3-4시간)
- [ ] 리포트 생성 이력 DB 테이블
- [ ] 리포트 재다운로드 기능
- [ ] 리포트 히스토리 페이지

### 8단계: 테스트 및 배포 (2-3시간)
- [ ] 백엔드 단위 테스트
- [ ] 프론트엔드 통합 테스트
- [ ] Docker 빌드 및 배포
- [ ] 프로덕션 검증

---

## 📊 예상 일정

### 최소 구현 (재무 대시보드 리포트만)
- **소요 시간**: 1-2일
- **범위**: 재무 대시보드 PDF/Excel 다운로드

### 표준 구현 (4가지 리포트)
- **소요 시간**: 3-4일
- **범위**: 재무, 청구서, 정산, 수금 리포트

### 전체 구현 (리포트 히스토리 포함)
- **소요 시간**: 4-5일
- **범위**: 모든 리포트 + 히스토리 + 재다운로드

---

## 🎨 리포트 디자인

### PDF 리포트 구조

```
┌─────────────────────────────────────┐
│  [회사 로고]  Cold Chain System     │
│  재무 대시보드 리포트                │
│  기간: 2025-11-07 ~ 2026-02-07      │
├─────────────────────────────────────┤
│  📊 주요 지표                        │
│  ┌──────┬──────┬──────┬──────┐      │
│  │총수익│청구액│수금액│미수금│      │
│  │ 0원  │ 0원  │ 0원  │ 0원  │      │
│  └──────┴──────┴──────┴──────┘      │
│                                     │
│  📈 월별 추이                        │
│  [차트 이미지]                       │
│                                     │
│  👥 Top 10 고객                     │
│  1. 고객A - 0원                     │
│  2. 고객B - 0원                     │
│  ...                                │
├─────────────────────────────────────┤
│  생성일: 2026-02-07 17:30:00        │
│  페이지 1 / 2                       │
└─────────────────────────────────────┘
```

### Excel 리포트 구조

```
Sheet 1: 요약 (Summary)
┌────────────┬─────────┐
│ 지표       │ 값      │
├────────────┼─────────┤
│ 총 수익    │ 0원     │
│ 청구액     │ 0원     │
│ 수금액     │ 0원     │
│ 미수금     │ 0원     │
│ 수금률     │ 0%      │
└────────────┴─────────┘

Sheet 2: 월별 데이터 (Monthly Data)
┌────────┬──────┬──────┬──────┐
│ 월     │ 수익 │ 청구 │ 수금 │
├────────┼──────┼──────┼──────┤
│ 2025-11│  0원 │  0원 │  0원 │
│ 2025-12│  0원 │  0원 │  0원 │
└────────┴──────┴──────┴──────┘

Sheet 3: 차트 (Charts)
[차트 객체 삽입]
```

---

## 🔒 보안 고려사항

- **인증**: Bearer 토큰 필수
- **권한**: ADMIN만 리포트 생성 가능
- **데이터 필터링**: 사용자 역할별 데이터 제한
- **파일 크기 제한**: 최대 50MB
- **Rate Limiting**: 사용자당 분당 10회

---

## 📈 성공 지표

- [ ] 재무 대시보드 PDF 다운로드 성공
- [ ] 재무 대시보드 Excel 다운로드 성공
- [ ] 한글 폰트 정상 표시
- [ ] 차트 이미지 정상 삽입
- [ ] 14개 지표 모두 표시
- [ ] 파일 크기 < 5MB
- [ ] 생성 시간 < 10초
- [ ] 프로덕션 배포 완료

---

## 🚀 다음 단계

### 1️⃣ 기술 스택 확정 및 패키지 설치
```bash
cd /home/user/webapp/backend
pip install weasyprint matplotlib pillow
```

### 2️⃣ 한글 폰트 다운로드
- 나눔고딕 TTF 파일 다운로드
- `backend/app/static/fonts/` 저장

### 3️⃣ 기본 서비스 클래스 생성
- `backend/app/services/report_generator.py`
- `backend/app/services/pdf_generator.py`
- `backend/app/services/excel_generator.py`

### 4️⃣ HTML 템플릿 작성
- `backend/app/templates/reports/financial_dashboard.html`

### 5️⃣ API 엔드포인트 구현
- `backend/app/api/v1/endpoints/reports.py`

---

## 📚 참고 자료

- WeasyPrint 문서: https://doc.courtbouillon.org/weasyprint/
- OpenPyXL 문서: https://openpyxl.readthedocs.io/
- Matplotlib 문서: https://matplotlib.org/
- Jinja2 문서: https://jinja.palletsprojects.com/

---

**작성자**: Claude Code Assistant  
**작성일**: 2026-02-07  
**마지막 업데이트**: 2026-02-07
