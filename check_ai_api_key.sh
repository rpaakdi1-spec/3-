#!/bin/bash

echo "=================================================="
echo "🔍 AI API 키 확인 스크립트"
echo "=================================================="
echo ""

# 서버에서 실행할 명령어 생성
cat << 'COMMANDS'
# 서버에서 실행하세요:

# 1. .env 파일에서 OpenAI API 키 확인
echo "📝 .env 파일의 OpenAI API 키:"
grep "OPENAI_API_KEY" /root/uvis/.env 2>/dev/null || echo "❌ API 키를 찾을 수 없습니다"

echo ""

# 2. AI 기능 활성화 상태 확인
echo "🔧 AI 기능 설정:"
grep "ENABLE_AI_FEATURES\|AI_MODEL" /root/uvis/.env 2>/dev/null || echo "⚠️  AI 기능 설정이 없습니다"

echo ""

# 3. Backend 환경변수 확인 (실제 로딩된 값)
echo "🐳 Backend 컨테이너 환경변수:"
docker exec uvis-backend env | grep -E "OPENAI|AI_MODEL|ENABLE_AI" 2>/dev/null || echo "⚠️  컨테이너에서 확인 불가"

echo ""

# 4. AI 사용 통계 API 테스트
echo "📊 AI 사용 통계 API 테스트:"
curl -s http://localhost:8000/api/v1/ai-usage/stats | jq '.' 2>/dev/null || curl -s http://localhost:8000/api/v1/ai-usage/stats

echo ""

# 5. Backend 로그에서 AI 관련 확인
echo "📋 Backend 로그 (AI 관련):"
docker logs uvis-backend --tail 100 | grep -i "openai\|api.*key\|ai.*config" | tail -10

COMMANDS

echo ""
echo "=================================================="
echo "위 명령어를 복사해서 서버에서 실행하세요!"
echo "=================================================="
