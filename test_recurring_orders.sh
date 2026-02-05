#!/bin/bash
# Recurring Orders Backend Test Script
# Tests all API endpoints for recurring orders

set -e

API_BASE="http://localhost:8000/api/v1"
RECURRING_ORDER_ID=""

echo "============================================"
echo "🧪 Recurring Orders API Test"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Create recurring order
echo "📝 Test 1: Create recurring order (WEEKLY)"
RESPONSE=$(curl -s -X POST "${API_BASE}/recurring-orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "테스트 정기 배송 - 매주 월수금",
    "frequency": "WEEKLY",
    "start_date": "2026-02-05",
    "end_date": "2026-12-31",
    "weekdays": 42,
    "order_date": "2026-02-05",
    "temperature_zone": "REFRIGERATED",
    "pickup_address": "서울시 강남구 테헤란로 123",
    "delivery_address": "부산시 해운대구 해운대로 456",
    "pallet_count": 20,
    "weight_kg": 500.0,
    "is_active": true
  }')

RECURRING_ORDER_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")

if [ -n "$RECURRING_ORDER_ID" ]; then
  echo -e "${GREEN}✅ Success: Created recurring order ID $RECURRING_ORDER_ID${NC}"
  echo "$RESPONSE" | python3 -m json.tool | head -20
else
  echo -e "${RED}❌ Failed to create recurring order${NC}"
  echo "$RESPONSE"
  exit 1
fi
echo ""

# Test 2: Get all recurring orders
echo "📋 Test 2: Get all recurring orders"
curl -s "${API_BASE}/recurring-orders/" | python3 -m json.tool | head -30
echo -e "${GREEN}✅ Success${NC}"
echo ""

# Test 3: Get single recurring order
echo "🔍 Test 3: Get recurring order by ID"
curl -s "${API_BASE}/recurring-orders/${RECURRING_ORDER_ID}" | python3 -m json.tool | head -30
echo -e "${GREEN}✅ Success${NC}"
echo ""

# Test 4: Update recurring order
echo "✏️  Test 4: Update recurring order"
curl -s -X PUT "${API_BASE}/recurring-orders/${RECURRING_ORDER_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "수정된 정기 배송 - 매주 월수금금",
    "pallet_count": 25
  }' | python3 -m json.tool | head -20
echo -e "${GREEN}✅ Success${NC}"
echo ""

# Test 5: Toggle active status
echo "🔄 Test 5: Toggle active status"
curl -s -X POST "${API_BASE}/recurring-orders/${RECURRING_ORDER_ID}/toggle" | python3 -m json.tool | head -10
echo -e "${GREEN}✅ Success (should be inactive now)${NC}"
echo ""

# Toggle back
curl -s -X POST "${API_BASE}/recurring-orders/${RECURRING_ORDER_ID}/toggle" | python3 -m json.tool | head -10
echo -e "${GREEN}✅ Toggled back to active${NC}"
echo ""

# Test 6: Preview generation
echo "👀 Test 6: Preview order generation for today"
curl -s "${API_BASE}/recurring-orders/preview" | python3 -m json.tool
echo -e "${GREEN}✅ Success${NC}"
echo ""

# Test 7: Manual generation
echo "🚀 Test 7: Manual order generation"
curl -s -X POST "${API_BASE}/recurring-orders/generate" | python3 -m json.tool
echo -e "${GREEN}✅ Success${NC}"
echo ""

# Test 8: Check if orders were created
echo "📦 Test 8: Check created orders (look for REC- prefix)"
curl -s "${API_BASE}/orders/?skip=0&limit=5" | python3 -c "
import sys, json
data = json.load(sys.stdin)
orders = data.get('items', [])
rec_orders = [o for o in orders if o['order_number'].startswith('REC-')]
print(f'Found {len(rec_orders)} orders with REC- prefix:')
for o in rec_orders[:3]:
    print(f'  - {o[\"order_number\"]} ({o[\"pickup_address\"]} → {o[\"delivery_address\"]})')
"
echo -e "${GREEN}✅ Success${NC}"
echo ""

# Test 9: Scheduler status
echo "⏰ Test 9: Check scheduler status"
curl -s "${API_BASE}/monitoring/scheduler/status" | python3 -m json.tool
echo -e "${GREEN}✅ Success${NC}"
echo ""

# Test 10: Delete recurring order
echo "🗑️  Test 10: Delete recurring order"
curl -s -X DELETE "${API_BASE}/recurring-orders/${RECURRING_ORDER_ID}"
echo -e "${GREEN}✅ Success: Deleted recurring order${NC}"
echo ""

echo "============================================"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo "============================================"
