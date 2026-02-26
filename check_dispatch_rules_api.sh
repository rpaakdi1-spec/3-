#!/bin/bash

echo "=== 1. Backend API 테스트 ==="
echo "GET /api/v1/dispatch-rules (목록 조회)"
curl -s http://139.150.11.99:8000/api/v1/dispatch-rules | jq '.' | head -50

echo -e "\n=== 2. 첫 번째 규칙 ID 가져오기 ==="
RULE_ID=$(curl -s http://139.150.11.99:8000/api/v1/dispatch-rules | jq -r '.[0].id // empty')

if [ -z "$RULE_ID" ]; then
  echo "❌ 규칙이 없습니다. 먼저 규칙을 생성해야 합니다."
else
  echo "✅ 규칙 ID: $RULE_ID"
  
  echo -e "\n=== 3. GET /api/v1/dispatch-rules/$RULE_ID (단일 규칙 조회) ==="
  curl -s http://139.150.11.99:8000/api/v1/dispatch-rules/$RULE_ID | jq '.'
  
  echo -e "\n=== 4. PUT /api/v1/dispatch-rules/$RULE_ID (수정 테스트) ==="
  curl -s -X PUT \
    -H "Content-Type: application/json" \
    -d '{
      "rule_update": {
        "name": "테스트_수정_규칙",
        "description": "수정 테스트",
        "priority": 999
      }
    }' \
    http://139.150.11.99:8000/api/v1/dispatch-rules/$RULE_ID | jq '.'
  
  echo -e "\n=== 5. 수정 결과 확인 ==="
  curl -s http://139.150.11.99:8000/api/v1/dispatch-rules/$RULE_ID | jq '.name, .priority, .version'
  
  echo -e "\n=== 6. DELETE 테스트는 건너뜀 (데이터 보존) ==="
  echo "DELETE를 테스트하려면 다음 명령 실행:"
  echo "curl -X DELETE http://139.150.11.99:8000/api/v1/dispatch-rules/$RULE_ID"
fi

echo -e "\n=== 7. Backend 로그 확인 (최근 30줄) ==="
ssh root@139.150.11.99 "docker logs uvis-backend --tail 30 2>&1 | grep -i 'dispatch-rules\|PUT\|DELETE\|error'" || echo "SSH 접근 불가"

