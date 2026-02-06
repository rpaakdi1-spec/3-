# Phase 8: 결제/정산 시스템 강화

## 📋 현재 상태 분석

### ✅ 기존 구현 (Phase 3-B Week 1)
- **BillingService**
  - ✅ `calculate_dispatch_charge()`: 배차 요금 계산
  - ✅ `generate_invoice_for_client()`: 청구서 생성
  - ✅ `record_payment()`: 결제 기록
  - ✅ `get_overdue_invoices()`: 연체 청구서 조회
  
- **DriverSettlementService**
  - ✅ `generate_driver_settlement()`: 기사 정산서 생성
  - ✅ `mark_settlement_paid()`: 정산 완료 처리

- **데이터베이스 테이블**
  - ✅ billing_policies (청구 정책)
  - ✅ invoices (청구서)
  - ✅ invoice_line_items (청구서 항목)
  - ✅ payments (결제)
  - ✅ driver_settlements (기사 정산)
  - ✅ driver_settlement_items (정산 항목)

### 🎯 Phase 8 강화 목표

#### 1. 자동화 시스템
- [ ] **자동 청구서 생성 스케줄러**
  - 매월 자동 청구서 생성 (cron job)
  - 청구 주기별 자동 처리 (IMMEDIATE/WEEKLY/MONTHLY/CUSTOM)
  - 실패 시 재시도 로직
  - 관리자 알림

- [ ] **자동 정산 스케줄러**
  - 매주/매월 자동 정산서 생성
  - 승인 대기 상태로 생성
  - 관리자 알림

#### 2. 실시간 요금 계산 API
- [ ] **요금 미리보기 엔드포인트**
  - POST `/api/v1/billing/preview`
  - 실시간 요금 계산 (거리, 팔레트, 날짜 기반)
  - 할증/할인 상세 표시
  - 프론트엔드 실시간 표시용

#### 3. 전자세금계산서 연동
- [ ] **전자세금계산서 모델 추가**
  - TaxInvoice 테이블 생성
  - 국세청 연동 상태 추적
  
- [ ] **API 연동 준비**
  - Barobill/Popbill API 클라이언트 구현
  - 발행/취소/조회 기능
  - Webhook 수신 처리

#### 4. 결제 알림 시스템
- [ ] **알림 템플릿 생성**
  - 청구서 발행 알림
  - 결제 완료 알림
  - 연체 알림 (D-7, D-3, D-day, D+7)
  
- [ ] **다중 채널 지원**
  - 이메일 알림 (SMTP)
  - SMS 알림 (연동 준비)
  - 푸시 알림 (FCM)

#### 5. 정산 승인 워크플로우
- [ ] **승인 프로세스 추가**
  - 정산서 생성 → 승인 대기
  - 관리자 검토 → 승인/반려
  - 승인 후 지급 처리
  
- [ ] **승인 이력 추적**
  - 승인자, 승인 시각 기록
  - 반려 사유 기록
  - 수정 요청 처리

#### 6. 리포트 다운로드
- [ ] **Excel 내보내기**
  - 청구서 목록 Excel
  - 정산서 목록 Excel
  - 상세 거래 내역 Excel
  
- [ ] **PDF 청구서 생성**
  - 정식 청구서 양식 PDF
  - 로고/서명 포함
  - 이메일 첨부 가능

#### 7. 대시보드 강화
- [ ] **재무 대시보드**
  - 월별 매출 현황
  - 미수금 현황
  - 정산 대기 금액
  - 현금 흐름 차트

## 🏗️ 구현 순서

### Week 1: 자동화 & 실시간 API
1. 자동 청구서 생성 스케줄러
2. 자동 정산 스케줄러
3. 실시간 요금 미리보기 API
4. 알림 시스템 기본 구조

### Week 2: 전자세금계산서 & 승인 워크플로우
1. TaxInvoice 모델 추가
2. 전자세금계산서 API 클라이언트
3. 정산 승인 워크플로우
4. 승인 이력 추적

### Week 3: 리포트 & 대시보드
1. Excel 내보내기 기능
2. PDF 청구서 생성
3. 재무 대시보드
4. 통계 API

## 📊 기술 스택

- **스케줄러**: APScheduler
- **PDF 생성**: ReportLab / WeasyPrint
- **Excel**: openpyxl
- **이메일**: SMTP + Jinja2 템플릿
- **전자세금계산서**: Barobill/Popbill SDK

## 🎯 성공 지표

- ✅ 청구서 생성 자동화율 100%
- ✅ 정산 처리 시간 50% 단축
- ✅ 수동 작업 오류율 0%
- ✅ 관리자 만족도 향상
