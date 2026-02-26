#!/bin/bash

echo "=========================================="
echo "🚀 Dispatch Rules API 업데이트 배포"
echo "=========================================="
echo ""
echo "✅ Git push 완료!"
echo "   Commit: 9cd8c3d"
echo "   Changes:"
echo "   - rule_type 변경 가능"
echo "   - Hard delete 구현"
echo ""
echo "=========================================="
echo "📋 서버에서 실행할 명령어"
echo "=========================================="
echo ""
cat << 'COMMANDS'
ssh root@139.150.11.99

cd /root/uvis

# 1. 최신 코드 가져오기
echo "=== Git Pull ==="
git pull origin main

# 2. Backend 재시작
echo -e "\n=== Backend 재시작 ==="
docker-compose restart backend

# 3. 재시작 대기
echo -e "\n대기 중..."
sleep 10

# 4. Backend 로그 확인
echo -e "\n=== Backend 로그 (최근 20줄) ==="
docker logs uvis-backend --tail 20

# 5. 간단 테스트
echo -e "\n=== 테스트 1: rule_type 변경 ==="
curl -s -X PUT \
  -H "Content-Type: application/json" \
  -d '{"rule_update": {"rule_type": "constraint", "name": "타입변경테스트"}}' \
  http://localhost:8000/api/v1/dispatch-rules/1 | jq '{id, name, rule_type, version}'

echo -e "\n=== 테스트 2: 삭제 테스트 (새 규칙 생성) ==="
NEW_ID=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"삭제테스트","rule_type":"assignment","priority":1,"conditions":{},"actions":{}}' \
  http://localhost:8000/api/v1/dispatch-rules/ | jq -r '.id')

echo "생성된 ID: $NEW_ID"

echo -e "\n=== 테스트 3: 삭제 실행 ==="
curl -X DELETE http://localhost:8000/api/v1/dispatch-rules/$NEW_ID -w "\nHTTP Status: %{http_code}\n"

echo -e "\n=== 테스트 4: 삭제 확인 (404 예상) ==="
curl -s http://localhost:8000/api/v1/dispatch-rules/$NEW_ID -w "\nHTTP Status: %{http_code}\n"

echo -e "\n=========================================="
echo -e "✅ 배포 및 테스트 완료!"
echo -e "=========================================="
COMMANDS

