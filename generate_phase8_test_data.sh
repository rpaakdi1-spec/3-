#!/bin/bash

# Phase 8 테스트 데이터 생성 스크립트
# 샘플 청구서, 자동 청구 스케줄, 정산 승인, 결제 알림 데이터를 생성합니다.

set -e

echo "=========================================="
echo "  Phase 8 테스트 데이터 생성"
echo "=========================================="
echo ""

# 설정
API_URL="${API_URL:-http://localhost:8000}"
USERNAME="${USERNAME:-admin}"
PASSWORD="${PASSWORD:-admin123}"

# 토큰 획득
echo "1. 로그인 중..."
TOKEN=$(curl -s -X POST "${API_URL}/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${USERNAME}&password=${PASSWORD}" | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ 로그인 실패!"
    exit 1
fi

echo "✅ 로그인 성공"
echo ""

# 2. 자동 청구 스케줄 샘플 생성
echo "2. 자동 청구 스케줄 생성 중..."

# 거래처 ID 조회
CLIENT_IDS=$(curl -s -X GET "${API_URL}/api/v1/clients?limit=5" \
  -H "Authorization: Bearer $TOKEN" | \
  grep -o '"id":[0-9]*' | cut -d':' -f2 | head -3)

if [ -z "$CLIENT_IDS" ]; then
    echo "⚠️  거래처 없음. 먼저 거래처를 생성하세요."
else
    COUNTER=1
    for CLIENT_ID in $CLIENT_IDS; do
        BILLING_DAY=$((5 * COUNTER))
        
        RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/billing/enhanced/auto-schedule" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d "{
            \"client_id\": ${CLIENT_ID},
            \"enabled\": true,
            \"billing_day\": ${BILLING_DAY},
            \"auto_send_email\": true,
            \"send_reminder\": true,
            \"reminder_days\": 3
          }")
        
        if echo "$RESPONSE" | grep -q '"id"'; then
            echo "  ✅ 거래처 ${CLIENT_ID}: 매월 ${BILLING_DAY}일 자동 청구 설정"
        else
            echo "  ⚠️  거래처 ${CLIENT_ID}: 이미 설정되어 있거나 생성 실패"
        fi
        
        COUNTER=$((COUNTER + 1))
    done
fi

echo ""

# 3. 청구서 샘플 생성
echo "3. 샘플 청구서 생성 중..."

# 최근 완료된 배차 조회
DISPATCH_IDS=$(curl -s -X GET "${API_URL}/api/v1/dispatches?status=COMPLETED&limit=5" \
  -H "Authorization: Bearer $TOKEN" | \
  grep -o '"id":[0-9]*' | cut -d':' -f2 | head -3)

if [ -z "$DISPATCH_IDS" ]; then
    echo "⚠️  완료된 배차 없음. 먼저 배차를 생성하세요."
else
    for DISPATCH_ID in $DISPATCH_IDS; do
        # 배차 정보로 청구서 생성 시도
        RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/billing/invoices/generate" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d "{
            \"dispatch_ids\": [${DISPATCH_ID}]
          }")
        
        if echo "$RESPONSE" | grep -q '"invoice_number"'; then
            INVOICE_NUM=$(echo "$RESPONSE" | grep -o '"invoice_number":"[^"]*' | cut -d'"' -f4)
            echo "  ✅ 배차 ${DISPATCH_ID}: 청구서 ${INVOICE_NUM} 생성"
        else
            echo "  ⚠️  배차 ${DISPATCH_ID}: 청구서 생성 실패 (이미 청구되었을 수 있음)"
        fi
    done
fi

echo ""

# 4. 정산 승인 샘플 생성
echo "4. 정산 승인 샘플 생성 중..."

# 최근 정산 조회
SETTLEMENT_IDS=$(curl -s -X GET "${API_URL}/api/v1/billing/settlements?status=PENDING&limit=3" \
  -H "Authorization: Bearer $TOKEN" | \
  grep -o '"id":[0-9]*' | cut -d':' -f2 | head -2)

if [ -z "$SETTLEMENT_IDS" ]; then
    echo "⚠️  대기 중인 정산 없음."
else
    for SETTLEMENT_ID in $SETTLEMENT_IDS; do
        # 정산 승인 생성
        RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/billing/enhanced/settlement-approval" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d "{
            \"settlement_id\": ${SETTLEMENT_ID},
            \"action\": \"approve\",
            \"notes\": \"테스트 승인 - 자동 생성된 샘플 데이터\"
          }")
        
        if echo "$RESPONSE" | grep -q '"id"'; then
            echo "  ✅ 정산 ${SETTLEMENT_ID}: 승인 완료"
        else
            echo "  ⚠️  정산 ${SETTLEMENT_ID}: 승인 실패 (이미 처리되었을 수 있음)"
        fi
    done
fi

echo ""

# 5. 결제 알림 샘플 생성
echo "5. 결제 알림 샘플 생성 중..."

# 미결제 청구서 조회
INVOICE_IDS=$(curl -s -X GET "${API_URL}/api/v1/billing/invoices?status=SENT&limit=5" \
  -H "Authorization: Bearer $TOKEN" | \
  grep -o '"id":[0-9]*' | cut -d':' -f2 | head -3)

if [ -z "$INVOICE_IDS" ]; then
    echo "⚠️  미결제 청구서 없음."
else
    REMINDER_TYPES=("BEFORE_DUE" "DUE_DATE" "OVERDUE")
    COUNTER=0
    
    for INVOICE_ID in $INVOICE_IDS; do
        REMINDER_TYPE=${REMINDER_TYPES[$COUNTER]}
        
        RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/billing/enhanced/payment-reminder" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d "{
            \"invoice_id\": ${INVOICE_ID},
            \"reminder_type\": \"${REMINDER_TYPE}\",
            \"days_until_due\": $((3 - COUNTER)),
            \"channels\": [\"email\", \"sms\"]
          }")
        
        if echo "$RESPONSE" | grep -q '"id"'; then
            echo "  ✅ 청구서 ${INVOICE_ID}: ${REMINDER_TYPE} 알림 생성"
        else
            echo "  ⚠️  청구서 ${INVOICE_ID}: 알림 생성 실패"
        fi
        
        COUNTER=$(((COUNTER + 1) % 3))
    done
fi

echo ""

# 6. 내보내기 작업 샘플 생성
echo "6. 내보내기 작업 샘플 생성..."

FORMATS=("excel" "pdf")
EXPORT_TYPES=("invoice" "settlement")

for i in {0..1}; do
    FORMAT=${FORMATS[$i]}
    EXPORT_TYPE=${EXPORT_TYPES[$i]}
    
    RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/billing/enhanced/export" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"export_type\": \"${EXPORT_TYPE}\",
        \"format\": \"${FORMAT}\",
        \"filters\": {
          \"start_date\": \"2026-02-01\",
          \"end_date\": \"2026-02-06\"
        }
      }")
    
    if echo "$RESPONSE" | grep -q '"task_id"'; then
        TASK_ID=$(echo "$RESPONSE" | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)
        echo "  ✅ ${EXPORT_TYPE} ${FORMAT} 내보내기 작업 생성: ${TASK_ID}"
    else
        echo "  ⚠️  ${EXPORT_TYPE} ${FORMAT} 내보내기 실패"
    fi
done

echo ""

# 7. 생성된 데이터 확인
echo "=========================================="
echo "  생성된 데이터 확인"
echo "=========================================="
echo ""

echo "📊 자동 청구 스케줄:"
curl -s -X GET "${API_URL}/api/v1/billing/enhanced/auto-schedule" \
  -H "Authorization: Bearer $TOKEN" | \
  grep -o '"client_id":[0-9]*' | wc -l | xargs echo "  - 총" | sed 's/$/ 개/'

echo ""
echo "📄 정산 승인:"
curl -s -X GET "${API_URL}/api/v1/billing/enhanced/settlement-approval" \
  -H "Authorization: Bearer $TOKEN" | \
  grep -o '"settlement_id":[0-9]*' | wc -l | xargs echo "  - 총" | sed 's/$/ 개/'

echo ""
echo "🔔 결제 알림:"
curl -s -X GET "${API_URL}/api/v1/billing/enhanced/payment-reminder" \
  -H "Authorization: Bearer $TOKEN" | \
  grep -o '"invoice_id":[0-9]*' | wc -l | xargs echo "  - 총" | sed 's/$/ 개/'

echo ""
echo "📤 내보내기 작업:"
curl -s -X GET "${API_URL}/api/v1/billing/enhanced/export" \
  -H "Authorization: Bearer $TOKEN" | \
  grep -o '"task_id":"[^"]*' | wc -l | xargs echo "  - 총" | sed 's/$/ 개/'

echo ""
echo "=========================================="
echo "✅ 테스트 데이터 생성 완료!"
echo "=========================================="
echo ""
echo "브라우저에서 확인:"
echo "  http://139.150.11.99/billing/financial-dashboard"
echo "  http://139.150.11.99/billing/auto-schedule"
echo "  http://139.150.11.99/billing/settlement-approval"
echo "  http://139.150.11.99/billing/payment-reminder"
echo "  http://139.150.11.99/billing/export-task"
echo ""
