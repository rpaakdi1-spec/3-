#!/bin/bash
# Test All API Endpoints
# This script tests the main API endpoints to verify fixes

set -e

echo "🧪 Testing UVIS API Endpoints"
echo "=============================="
echo ""

echo "1️⃣  Getting authentication token..."
echo "--------------------------------"
TOKEN_RESPONSE=$(curl -s -X POST http://139.150.11.99/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123")

TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
else
    echo "✅ Token obtained: ${TOKEN:0:20}..."
fi

echo ""
echo "2️⃣  Testing Vehicle API (without trailing slash)..."
echo "-------------------------------------------------"
VEHICLE_RESPONSE=$(curl -s -X GET "http://139.150.11.99/api/v1/vehicles" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP_CODE:%{http_code}" \
  -o /tmp/vehicle_test.json)

HTTP_CODE=$(echo "$VEHICLE_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Vehicle API returns 200 OK (redirect fixed!)"
    cat /tmp/vehicle_test.json | python3 -m json.tool | head -20
elif [ "$HTTP_CODE" = "307" ]; then
    echo "⚠️  Still getting 307 redirect"
    LOCATION=$(curl -s -I -X GET "http://139.150.11.99/api/v1/vehicles" | grep -i location)
    echo "Redirect to: $LOCATION"
else
    echo "❌ Unexpected status: $HTTP_CODE"
    cat /tmp/vehicle_test.json
fi

echo ""
echo "3️⃣  Testing Vehicle API (with trailing slash)..."
echo "----------------------------------------------"
curl -s -X GET "http://139.150.11.99/api/v1/vehicles/" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP_CODE:%{http_code}\n" | head -20

echo ""
echo "4️⃣  Testing Dashboard Stats API..."
echo "-------------------------------"
STATS_RESPONSE=$(curl -s -X GET "http://139.150.11.99/api/v1/dispatches/stats/summary" \
  -H "Authorization: Bearer $TOKEN")

echo "$STATS_RESPONSE" | python3 -m json.tool || echo "$STATS_RESPONSE"

TOTAL_DISPATCHES=$(echo "$STATS_RESPONSE" | python3 -c "import sys,json;print(json.load(sys.stdin).get('total_dispatches', 'N/A'))" 2>/dev/null || echo "N/A")
echo "Total Dispatches: $TOTAL_DISPATCHES"

if [ "$TOTAL_DISPATCHES" != "N/A" ]; then
    echo "✅ Dashboard stats API works"
else
    echo "❌ Dashboard stats API error"
fi

echo ""
echo "5️⃣  Testing WebSocket Endpoint (Connection Test)..."
echo "-------------------------------------------------"
# Note: This is a connection test, actual WebSocket requires wscat or browser
WS_TEST=$(curl -s -I -X GET "http://139.150.11.99/api/v1/ws/dashboard?token=$TOKEN" \
  -H "Upgrade: websocket" \
  -H "Connection: Upgrade" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==")

WS_STATUS=$(echo "$WS_TEST" | head -1 | grep -oE "[0-9]{3}")
echo "WebSocket upgrade response: $WS_STATUS"

if [ "$WS_STATUS" = "101" ]; then
    echo "✅ WebSocket upgrade successful (101 Switching Protocols)"
elif [ "$WS_STATUS" = "403" ]; then
    echo "❌ WebSocket authentication failed (403 Forbidden)"
    echo "Backend needs token validation fix"
else
    echo "⚠️  Unexpected response: $WS_STATUS"
fi

echo ""
echo "6️⃣  Checking Backend Logs for Errors..."
echo "------------------------------------"
ERROR_COUNT=$(docker logs uvis-backend --tail 50 | grep -c "Error broadcasting\|ChunkedIteratorResult" || echo "0")
echo "Recent broadcast errors: $ERROR_COUNT"

if [ "$ERROR_COUNT" = "0" ]; then
    echo "✅ No broadcast errors in recent logs"
else
    echo "❌ Still seeing broadcast errors:"
    docker logs uvis-backend --tail 50 | grep "Error broadcasting\|ChunkedIteratorResult" | head -5
fi

echo ""
echo "7️⃣  Testing Other Key Endpoints..."
echo "-------------------------------"

# Clients
echo -n "Clients API: "
curl -s -X GET "http://139.150.11.99/api/v1/clients" \
  -H "Authorization: Bearer $TOKEN" \
  -w "HTTP %{http_code}\n" \
  -o /dev/null

# Orders
echo -n "Orders API: "
curl -s -X GET "http://139.150.11.99/api/v1/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -w "HTTP %{http_code}\n" \
  -o /dev/null

# Dispatches
echo -n "Dispatches API: "
curl -s -X GET "http://139.150.11.99/api/v1/dispatches" \
  -H "Authorization: Bearer $TOKEN" \
  -w "HTTP %{http_code}\n" \
  -o /dev/null

echo ""
echo "================================"
echo "✅ API Test Complete!"
echo "================================"
echo ""
echo "Summary:"
echo "--------"
echo "- Login: ✅"
echo "- Vehicle API redirect: Check status above"
echo "- Dashboard stats: Check status above"
echo "- WebSocket: Check status above"
echo "- Other APIs: Check status above"
echo ""
echo "📝 Next steps based on results:"
echo "1. If vehicle API still returns 307, run: ./fix_vehicle_api_redirect.sh"
echo "2. If WebSocket returns 403, backend needs code changes"
echo "3. If broadcast errors persist, run: ./diagnose_async_errors.sh"
