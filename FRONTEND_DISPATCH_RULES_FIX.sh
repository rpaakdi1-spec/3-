#!/bin/bash
# Dispatch Rules Frontend Fix Script
# This script helps diagnose and fix the frontend PUT request issue

set -e

echo "=================================================="
echo "Dispatch Rules Frontend Fix Diagnostic"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Test Backend API
echo -e "${YELLOW}1. Testing Backend API${NC}"
echo "Testing PUT with correct format..."

RESPONSE=$(curl -s -X PUT http://localhost:8000/api/v1/dispatch-rules/3 \
  -H "Content-Type: application/json" \
  -d '{"rule_update": {"name": "BackendTest", "priority": 777}}')

echo "Response: $RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q '"id"'; then
    echo -e "${GREEN}✅ Backend PUT endpoint works correctly${NC}"
else
    echo -e "${RED}❌ Backend PUT endpoint issue${NC}"
    exit 1
fi

# 2. Test Backend with wrong format
echo ""
echo -e "${YELLOW}2. Testing Backend with Wrong Format (should fail)${NC}"
echo "Testing PUT without rule_update wrapper..."

WRONG_RESPONSE=$(curl -s -X PUT http://localhost:8000/api/v1/dispatch-rules/3 \
  -H "Content-Type: application/json" \
  -d '{"name": "WrongTest", "priority": 666}')

echo "Response: $WRONG_RESPONSE"
echo ""

if echo "$WRONG_RESPONSE" | grep -q "422\|missing"; then
    echo -e "${GREEN}✅ Backend correctly rejects wrong format (expected)${NC}"
else
    echo -e "${YELLOW}⚠️ Backend response unexpected${NC}"
fi

# 3. Show current rules
echo ""
echo -e "${YELLOW}3. Current Dispatch Rules${NC}"
curl -s http://localhost:8000/api/v1/dispatch-rules/ | jq -r '.[] | "\(.id): \(.name) (priority: \(.priority))"'

# 4. Nginx logs check
echo ""
echo -e "${YELLOW}4. Recent Nginx Logs (last 10 PUT requests)${NC}"
docker logs uvis-frontend --tail 200 2>/dev/null | grep -i "PUT.*dispatch-rules" | tail -10 || echo "No PUT requests found in logs"

# 5. Backend logs check
echo ""
echo -e "${YELLOW}5. Recent Backend Logs (last 10 PUT requests)${NC}"
docker logs uvis-backend --tail 200 2>/dev/null | grep -i "PUT.*dispatch-rules" | tail -10 || echo "No PUT requests found in logs"

# 6. Instructions
echo ""
echo "=================================================="
echo -e "${GREEN}Frontend Fix Instructions${NC}"
echo "=================================================="
echo ""
echo "The backend requires the PUT request body to be wrapped:"
echo ""
echo -e "${RED}❌ Wrong (Frontend is currently sending):${NC}"
echo '  {
    "name": "규칙명",
    "priority": 100
  }'
echo ""
echo -e "${GREEN}✅ Correct (Frontend should send):${NC}"
echo '  {
    "rule_update": {
      "name": "규칙명",
      "priority": 100
    }
  }'
echo ""
echo "=================================================="
echo "Testing Steps:"
echo "=================================================="
echo ""
echo "1. Open browser: http://139.150.11.99/dispatch-rules"
echo "2. Open Developer Tools (F12)"
echo "3. Go to Network tab"
echo "4. Try to edit a dispatch rule"
echo "5. Find the PUT request to /api/v1/dispatch-rules/{id}"
echo "6. Check the 'Payload' tab:"
echo "   - If you see {\"name\":\"...\"} → Wrong format"
echo "   - If you see {\"rule_update\":{\"name\":\"...\"}} → Correct format"
echo ""
echo "7. If wrong format, check Console tab for JavaScript errors"
echo ""
echo "=================================================="
echo "Browser Console Test"
echo "=================================================="
echo ""
echo "Run this in browser console to test:"
echo ""
cat << 'EOF'
fetch('/api/v1/dispatch-rules/3', {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    rule_update: {
      name: '브라우저테스트',
      priority: 888
    }
  })
})
.then(r => r.json())
.then(data => {
  if (data.id && data.name === '브라우저테스트') {
    console.log('✅ SUCCESS:', data);
    alert('수정 성공! ID: ' + data.id + ', Version: ' + data.version);
  } else {
    console.error('❌ UNEXPECTED:', data);
  }
})
.catch(err => console.error('❌ ERROR:', err));
EOF

echo ""
echo "=================================================="
echo "Quick Fix for Frontend Code"
echo "=================================================="
echo ""
echo "Find the dispatch rules API client file and wrap the data:"
echo ""
echo "// BEFORE"
echo "api.put(\`/api/v1/dispatch-rules/\${id}\`, data)"
echo ""
echo "// AFTER"  
echo "api.put(\`/api/v1/dispatch-rules/\${id}\`, { rule_update: data })"
echo ""
echo "=================================================="
echo "Diagnostic Complete"
echo "=================================================="
