#!/bin/bash

echo "=========================================="
echo "네이버 지도 API URL 등록 확인"
echo "=========================================="
echo ""

CLIENT_ID="oimsa0yj4k"
TEST_URLS=(
    "http://139.150.11.99"
    "http://139.150.11.99/vehicles"
    "http://localhost"
)

echo "📋 설정 정보:"
echo "   Client ID: $CLIENT_ID"
echo "   API Script URL: https://oapi.map.naver.com/openapi/v3/maps.js?ncpClientId=$CLIENT_ID"
echo ""

echo "🔍 테스트 방법:"
echo ""
echo "1️⃣  브라우저 테스트 (권장):"
echo "   - 브라우저에서 http://139.150.11.99/test_naver_map.html 열기"
echo "   - 지도가 보이면: ✅ URL 등록됨"
echo "   - 에러 발생하면: ❌ URL 미등록"
echo ""

echo "2️⃣  콘솔에서 직접 확인:"
echo "   curl -s 'https://oapi.map.naver.com/openapi/v3/maps.js?ncpClientId=$CLIENT_ID' | head -20"
echo ""

echo "3️⃣  네이버 클라우드 콘솔에서 확인:"
echo "   1) https://www.ncloud.com/ 로그인"
echo "   2) Console → Services → AI·NAVER API → Maps"
echo "   3) Application 선택 (Client ID: $CLIENT_ID)"
echo "   4) Web Service URL 섹션 확인"
echo ""

echo "📝 등록되어야 할 URL 목록:"
for url in "${TEST_URLS[@]}"; do
    echo "   ✓ $url"
done
echo "   ✓ http://139.150.11.99/*"
echo ""

echo "🔧 URL이 등록되지 않은 경우:"
echo "   1) Naver Cloud Console 접속"
echo "   2) 위 URL들을 Web Service URL에 추가"
echo "   3) 저장 후 5-10분 대기"
echo "   4) 브라우저 캐시 삭제 후 재테스트"
echo ""

echo "=========================================="
echo "API 스크립트 응답 확인 중..."
echo "=========================================="
echo ""

# Try to fetch the script
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "https://oapi.map.naver.com/openapi/v3/maps.js?ncpClientId=$CLIENT_ID" | head -50)
http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)

if [ "$http_code" = "200" ]; then
    echo "✅ API 스크립트 다운로드 성공 (HTTP 200)"
    echo ""
    echo "📄 스크립트 내용 (처음 10줄):"
    echo "$response" | grep -v "HTTP_CODE:" | head -10
    echo "..."
    echo ""
    echo "⚠️  주의: 스크립트는 다운로드되지만, 실제 지도 사용 시 URL 검증이 발생합니다."
    echo "   브라우저에서 http://139.150.11.99/test_naver_map.html 를 열어 최종 확인하세요."
else
    echo "❌ API 스크립트 다운로드 실패 (HTTP $http_code)"
    echo "   Client ID가 유효하지 않을 수 있습니다."
fi

echo ""
echo "=========================================="
echo "최종 확인 방법"
echo "=========================================="
echo ""
echo "서버에서 테스트 파일을 배포하세요:"
echo "  cp test_naver_map.html /root/uvis/frontend/public/"
echo "  # 또는"
echo "  docker cp test_naver_map.html uvis-frontend:/usr/share/nginx/html/"
echo ""
echo "그 다음 브라우저에서 확인:"
echo "  http://139.150.11.99/test_naver_map.html"
echo ""

