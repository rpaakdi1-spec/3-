#!/bin/bash

# AI API 키 설정 자동화 스크립트
# 사용법: bash setup_ai_api.sh

set -e

echo "=================================================="
echo "🔑 AI API 키 설정 스크립트"
echo "=================================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 현재 디렉토리 확인
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ 에러: .env 파일을 찾을 수 없습니다!${NC}"
    echo "   현재 디렉토리: $(pwd)"
    echo "   올바른 디렉토리로 이동하세요: cd /root/uvis"
    exit 1
fi

echo -e "${GREEN}✅ .env 파일 발견${NC}"
echo ""

# Step 1: 백업
echo "📦 Step 1: .env 파일 백업 중..."
BACKUP_FILE=".env.backup_$(date +%Y%m%d_%H%M%S)"
cp .env "$BACKUP_FILE"
echo -e "${GREEN}✅ 백업 완료: $BACKUP_FILE${NC}"
echo ""

# Step 2: 기존 AI 설정 확인
echo "🔍 Step 2: 기존 AI 설정 확인 중..."
if grep -q "OPENAI_API_KEY" .env; then
    EXISTING_KEY=$(grep "OPENAI_API_KEY" .env | cut -d'=' -f2)
    if [ ! -z "$EXISTING_KEY" ] && [ "$EXISTING_KEY" != "your-api-key-here" ]; then
        echo -e "${YELLOW}⚠️  이미 API 키가 설정되어 있습니다!${NC}"
        echo "   현재 키: ${EXISTING_KEY:0:20}..."
        echo ""
        read -p "   덮어쓰시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "   설정을 취소합니다."
            exit 0
        fi
    fi
fi
echo ""

# Step 3: API 키 입력
echo "📝 Step 3: OpenAI API 키 입력"
echo ""
echo "   OpenAI API 키를 발급받으세요:"
echo "   👉 https://platform.openai.com/api-keys"
echo ""
read -p "   OpenAI API 키 입력 (sk-proj-... 또는 sk-...): " OPENAI_KEY

# API 키 검증
if [ -z "$OPENAI_KEY" ]; then
    echo -e "${RED}❌ API 키가 입력되지 않았습니다!${NC}"
    exit 1
fi

if [[ ! $OPENAI_KEY =~ ^sk- ]]; then
    echo -e "${YELLOW}⚠️  경고: API 키가 'sk-'로 시작하지 않습니다!${NC}"
    read -p "   계속하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo ""

# Step 4: Gemini API 키 입력 (선택)
echo "📝 Step 4: Gemini API 키 입력 (선택 사항)"
echo ""
echo "   Google Gemini API 키를 발급받으세요:"
echo "   👉 https://makersuite.google.com/app/apikey"
echo ""
read -p "   Gemini API 키 입력 (선택, 엔터로 건너뛰기): " GEMINI_KEY
echo ""

# Step 5: AI 모델 선택
echo "📝 Step 5: AI 모델 선택"
echo ""
echo "   1) gpt-4           (고품질, 비용 높음)"
echo "   2) gpt-3.5-turbo   (빠름, 비용 낮음) [추천]"
echo ""
read -p "   선택 (1/2) [기본: 2]: " MODEL_CHOICE

if [ "$MODEL_CHOICE" = "1" ]; then
    AI_MODEL="gpt-4"
else
    AI_MODEL="gpt-3.5-turbo"
fi

echo -e "${GREEN}✅ 선택한 모델: $AI_MODEL${NC}"
echo ""

# Step 6: .env 파일 업데이트
echo "💾 Step 6: .env 파일 업데이트 중..."

# 기존 AI 설정 제거
sed -i '/# AI API Configuration/,/^$/d' .env
sed -i '/OPENAI_API_KEY/d' .env
sed -i '/GEMINI_API_KEY/d' .env
sed -i '/ENABLE_AI_FEATURES/d' .env
sed -i '/AI_MODEL/d' .env

# 새 AI 설정 추가
cat >> .env << EOF

# ==========================================
# AI API Configuration (Added: $(date +%Y-%m-%d))
# ==========================================

# OpenAI API Key
OPENAI_API_KEY=$OPENAI_KEY

EOF

if [ ! -z "$GEMINI_KEY" ]; then
    cat >> .env << EOF
# Gemini API Key
GEMINI_API_KEY=$GEMINI_KEY

EOF
fi

cat >> .env << EOF
# AI Features
ENABLE_AI_FEATURES=true
AI_MODEL=$AI_MODEL
AI_MODEL_TEMPERATURE=0.7

# AI Cost Limits (Optional)
AI_MAX_COST_PER_REQUEST=0.5
AI_DAILY_BUDGET=10.0
EOF

echo -e "${GREEN}✅ .env 파일 업데이트 완료${NC}"
echo ""

# Step 7: 설정 확인
echo "🔍 Step 7: 설정 확인"
echo ""
echo "   OPENAI_API_KEY: ${OPENAI_KEY:0:20}..."
echo "   AI_MODEL: $AI_MODEL"
if [ ! -z "$GEMINI_KEY" ]; then
    echo "   GEMINI_API_KEY: ${GEMINI_KEY:0:20}..."
fi
echo ""

# Step 8: Backend 재시작
echo "🔄 Step 8: Backend 재시작"
echo ""
read -p "   Backend 컨테이너를 재시작하시겠습니까? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "   Backend 재시작 중..."
    
    if [ -f "docker-compose.prod.yml" ]; then
        docker-compose -f docker-compose.prod.yml restart backend
    elif [ -f "docker-compose.yml" ]; then
        docker-compose restart backend
    else
        echo -e "${YELLOW}⚠️  docker-compose 파일을 찾을 수 없습니다!${NC}"
        echo "   수동으로 재시작하세요:"
        echo "   docker-compose -f docker-compose.prod.yml restart backend"
        exit 1
    fi
    
    echo ""
    echo "   ⏳ 30초 대기 중 (Backend 초기화)..."
    sleep 30
    
    echo -e "${GREEN}✅ Backend 재시작 완료${NC}"
else
    echo "   Backend 재시작을 건너뛰었습니다."
    echo "   수동으로 재시작하세요:"
    echo "   docker-compose -f docker-compose.prod.yml restart backend"
fi
echo ""

# Step 9: 테스트
echo "✅ Step 9: 설정 테스트"
echo ""
read -p "   설정을 테스트하시겠습니까? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "   🔍 Health Check..."
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health || echo "failed")
    
    if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
        echo -e "   ${GREEN}✅ Backend 정상 작동${NC}"
    else
        echo -e "   ${RED}❌ Backend 응답 없음${NC}"
        echo "   로그 확인: docker logs uvis-backend --tail 50"
    fi
    
    echo ""
    echo "   🔍 AI 사용 통계..."
    AI_STATS=$(curl -s http://localhost:8000/api/v1/ai-usage/stats || echo "failed")
    
    if [[ $AI_STATS == *"total_requests"* ]]; then
        echo -e "   ${GREEN}✅ AI API 정상 작동${NC}"
        echo ""
        echo "   통계:"
        echo "$AI_STATS" | jq '.' 2>/dev/null || echo "$AI_STATS"
    else
        echo -e "   ${YELLOW}⚠️  AI API 응답 확인 필요${NC}"
        echo "   응답: $AI_STATS"
    fi
fi

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 AI API 키 설정 완료!${NC}"
echo "=================================================="
echo ""
echo "📊 다음 단계:"
echo ""
echo "   1. 브라우저에서 확인:"
echo "      http://139.150.11.99"
echo ""
echo "   2. AI 채팅 메뉴에서 테스트"
echo ""
echo "   3. AI 비용 대시보드에서 실시간 데이터 확인"
echo ""
echo "   4. 비용 모니터링:"
echo "      curl -s http://localhost:8000/api/v1/ai-usage/cost-summary?period=1d | jq '.'"
echo ""
echo "📚 참고 문서:"
echo "   - AI_API_SETUP_GUIDE.md"
echo "   - QUICK_START_NEXT_STEPS.md"
echo ""
echo "🔒 보안 팁:"
echo "   - API 키를 절대 공개하지 마세요!"
echo "   - OpenAI 플랫폼에서 사용량 제한 설정"
echo "   - 정기적으로 비용 확인"
echo ""
echo "=================================================="
