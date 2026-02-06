#!/bin/bash

echo "=== Phase 8 Integration Testing ==="
echo ""

# Test 1: Frontend Health
echo "1. Testing Frontend..."
FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" http://139.150.11.99/)
if [ "$FRONTEND" = "200" ]; then
    echo "   ✅ Frontend: OK (HTTP $FRONTEND)"
else
    echo "   ❌ Frontend: FAIL (HTTP $FRONTEND)"
fi

# Test 2: Backend Health
echo "2. Testing Backend Health..."
BACKEND=$(curl -s http://139.150.11.99:8000/health)
if echo "$BACKEND" | grep -q "healthy"; then
    echo "   ✅ Backend Health: OK"
else
    echo "   ❌ Backend Health: FAIL"
fi

# Test 3: Phase 8 APIs
echo "3. Testing Phase 8 APIs..."
TOKEN=$(curl -s -X POST http://139.150.11.99:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo "   ✅ Login: OK (Token acquired)"
    
    # Test Financial Dashboard
    DASH=$(curl -s -w "%{http_code}" -o /dev/null \
      "http://139.150.11.99:8000/api/v1/billing/enhanced/dashboard/financial?start_date=2026-01-01&end_date=2026-02-28" \
      -H "Authorization: Bearer $TOKEN")
    if [ "$DASH" = "200" ]; then
        echo "   ✅ Financial Dashboard API: OK (HTTP $DASH)"
    else
        echo "   ❌ Financial Dashboard API: FAIL (HTTP $DASH)"
    fi
    
    # Test Charge Preview
    PREVIEW=$(curl -s -X POST http://139.150.11.99:8000/api/v1/billing/enhanced/preview \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"client_id":1,"distance_km":50,"total_pallets":10,"total_weight_kg":1500,"is_weekend":false,"is_urgent":false,"requires_temperature_control":false,"dispatch_date":"2026-02-06"}' \
      | grep -o '"total_amount":[0-9.]*')
    if [ -n "$PREVIEW" ]; then
        echo "   ✅ Charge Preview API: OK ($PREVIEW)"
    else
        echo "   ❌ Charge Preview API: FAIL"
    fi
else
    echo "   ❌ Login: FAIL"
fi

echo ""
echo "=== Integration Test Complete ==="
