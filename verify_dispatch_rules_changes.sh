#!/bin/bash

echo "=== 변경사항 확인 ==="

echo -e "\n1. DispatchRuleUpdate 스키마에 rule_type 필드 추가됨:"
grep -A12 "class DispatchRuleUpdate" backend/app/api/v1/endpoints/dispatch_rules.py | grep -E "class|rule_type|priority|is_active"

echo -e "\n2. DELETE 엔드포인트가 hard delete로 변경됨:"
grep -A18 "@router.delete" backend/app/api/v1/endpoints/dispatch_rules.py | grep -E "delete|Hard delete|db.query|db.delete|logger"

echo -e "\n✅ 변경 완료!"
echo -e "\n다음 명령어로 서버에 반영하세요:"
echo "ssh root@139.150.11.99"
echo "cd /root/uvis"
echo "git pull origin main  # 또는 변경된 파일 복사"
echo "docker-compose restart backend"
echo "sleep 10"
echo "docker logs uvis-backend --tail 20"

