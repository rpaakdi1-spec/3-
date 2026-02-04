#!/bin/bash
# NLP 파싱 405 오류 진단 스크립트

echo "🔍 NLP 파싱 405 오류 종합 진단"
echo "=" | awk '{s=sprintf("%80s","");gsub(/ /,"=",$0);print}'
echo ""

echo "1️⃣ 백엔드 로그 확인 (parse 관련):"
docker logs uvis-backend --tail 100 | grep -i "parse\|nlp\|POST\|405\|method" | tail -20

echo ""
echo "2️⃣ 백엔드 컨테이너 상태:"
docker ps | grep backend

echo ""
echo "3️⃣ 직접 백엔드 API 호출 (Nginx 우회):"
curl -X POST http://localhost:8000/api/v1/orders/parse-nlp \
  -H "Content-Type: application/json" \
  -d '{"text":"[02/04] 테스트\n동이천 → 호남\n10판 1대(상온)"}' 2>&1 | head -c 300

echo ""
echo ""
echo "4️⃣ Nginx를 통한 API 호출:"
curl -X POST http://localhost/api/v1/orders/parse-nlp \
  -H "Content-Type: application/json" \
  -d '{"text":"[02/04] 테스트\n동이천 → 호남\n10판 1대(상온)"}' 2>&1

echo ""
echo ""
echo "5️⃣ Nginx 액세스 로그 (최근 10줄):"
docker logs uvis-nginx 2>&1 | grep "parse-nlp" | tail -10

echo ""
echo "6️⃣ FastAPI 라우터 등록 확인:"
docker exec uvis-backend python -c "
from app.api import orders
print('Orders router endpoints:')
for route in orders.router.routes:
    print(f'  {route.methods} {route.path}')
" 2>&1 | head -20

echo ""
echo "✅ 진단 완료!"
