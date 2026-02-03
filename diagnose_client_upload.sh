#!/bin/bash

echo "================================================================================"
echo "🔍 거래처 엑셀 업로드 문제 진단"
echo "================================================================================"

echo ""
echo "1️⃣ 백엔드 헬스 체크"
echo "--------------------------------------------------------------------------------"
HEALTH_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)
echo "Health endpoint: HTTP $HEALTH_CODE"

if [ "$HEALTH_CODE" != "200" ]; then
    echo "❌ Backend is not healthy!"
    echo "Checking backend logs..."
    docker logs uvis-backend --tail 50
    exit 1
fi

echo "✅ Backend is healthy"

echo ""
echo "2️⃣ 거래처 API 엔드포인트 테스트"
echo "--------------------------------------------------------------------------------"

echo "Testing GET /api/v1/clients/"
CLIENTS_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/clients/)
echo "GET /api/v1/clients/: HTTP $CLIENTS_CODE"

echo ""
echo "Testing GET /api/v1/clients/template/download"
TEMPLATE_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/clients/template/download)
echo "GET /api/v1/clients/template/download: HTTP $TEMPLATE_CODE"

echo ""
echo "3️⃣ 거래처 업로드 엔드포인트 테스트 (빈 파일)"
echo "--------------------------------------------------------------------------------"

# Create a test Excel file
cat > /tmp/test_clients.csv << 'EOF'
거래처코드,거래처명,거래처구분,주소,상세주소,전화번호,담당자,이메일
TEST001,테스트거래처,BOTH,서울시 강남구 테헤란로 123,1층,02-1234-5678,홍길동,test@example.com
EOF

echo "Testing POST /api/v1/clients/upload"
UPLOAD_CODE=$(curl -s -o /tmp/upload_response.json -w '%{http_code}' \
    -X POST http://localhost:8000/api/v1/clients/upload?auto_geocode=false \
    -F "file=@/tmp/test_clients.csv" \
    -H "Content-Type: multipart/form-data")

echo "POST /api/v1/clients/upload: HTTP $UPLOAD_CODE"

if [ "$UPLOAD_CODE" == "401" ]; then
    echo "❌ 401 Unauthorized Error"
    echo "Response:"
    cat /tmp/upload_response.json 2>/dev/null || echo "No response body"
    echo ""
    echo "This suggests an authentication issue."
    echo "Checking if authentication middleware is enabled..."
elif [ "$UPLOAD_CODE" == "200" ] || [ "$UPLOAD_CODE" == "201" ]; then
    echo "✅ Upload endpoint is working!"
    echo "Response:"
    cat /tmp/upload_response.json | jq . 2>/dev/null || cat /tmp/upload_response.json
else
    echo "⚠️  Upload returned HTTP $UPLOAD_CODE"
    echo "Response:"
    cat /tmp/upload_response.json 2>/dev/null || echo "No response body"
fi

echo ""
echo "4️⃣ 백엔드 최근 로그 확인"
echo "--------------------------------------------------------------------------------"
echo "Recent errors:"
docker logs uvis-backend --tail 100 | grep -E "ERROR|401|Unauthorized|upload" | tail -20

echo ""
echo "5️⃣ CORS 설정 확인"
echo "--------------------------------------------------------------------------------"
echo "Testing CORS preflight..."
curl -s -X OPTIONS http://localhost:8000/api/v1/clients/upload \
    -H "Origin: http://139.150.11.99" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: content-type" \
    -v 2>&1 | grep -E "< HTTP|< Access-Control"

echo ""
echo "================================================================================"
echo "진단 완료!"
echo ""
echo "다음 단계:"
echo "  1. 401 에러가 보이면: 인증 미들웨어 설정 확인 필요"
echo "  2. 500 에러가 보이면: 백엔드 로그에서 상세 에러 확인"
echo "  3. CORS 에러가 보이면: CORS 설정 확인 필요"
echo "================================================================================"

# Cleanup
rm -f /tmp/test_clients.csv /tmp/upload_response.json
