#!/bin/bash

# ========================================
# 서버 .env 파일 업데이트 스크립트
# ========================================
# 실행: bash /root/uvis/update_env.sh

echo "=================================================="
echo "🔧 서버 .env 파일 업데이트"
echo "=================================================="
echo ""

# 백업
echo "📦 백업 생성 중..."
cp /root/uvis/.env /root/uvis/.env.backup_$(date +%Y%m%d_%H%M%S)
echo "✅ 백업 완료"
echo ""

# UVIS API 설정 업데이트
echo "🔧 UVIS API 설정 업데이트 중..."
sed -i '/# Samsung UVIS API/,/UVIS_API_KEY=.*$/d' /root/uvis/.env

cat >> /root/uvis/.env << 'EOF'

# Samsung UVIS API
# 인터페이스 사양서: 인터페이스사양서_광신특수_20260127.pdf
UVIS_API_URL=https://s1.u-vis.com/uvisc/InterfaceAction.do
UVIS_SERIAL_KEY=S1910-3A84-4559--CC4
UVIS_ACCESS_KEY_METHOD=GetAccessKeyWithValues
UVIS_ACCESS_KEY_TTL=300
EOF

echo "✅ UVIS API 설정 완료"
echo ""

# OpenAI API 키 확인
echo "🔍 OpenAI API 키 확인 중..."
if grep -q "OPENAI_API_KEY=sk-proj-" /root/uvis/.env; then
    echo "✅ OpenAI API 키가 이미 설정되어 있습니다"
else
    echo "⚠️  OpenAI API 키가 없습니다. 추가 중..."
    cat >> /root/uvis/.env << 'EOF'

# ==========================================
# AI API Configuration (Added: 2026-02-02)
# ==========================================

# OpenAI API Key (필수) - 실제 키로 교체하세요
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# AI 기능 활성화
ENABLE_AI_FEATURES=true

# AI 모델 설정
AI_MODEL=gpt-3.5-turbo
AI_MODEL_TEMPERATURE=0.7

# AI 비용 제한
AI_MAX_COST_PER_REQUEST=0.5
AI_DAILY_BUDGET=10.0
AI_MONTHLY_BUDGET=100.0

# AI 토큰 제한
AI_MAX_TOKENS=1000

# AI 응답 캐싱
AI_ENABLE_CACHE=true
AI_CACHE_TTL=3600
EOF
    echo "✅ OpenAI API 키 추가 완료"
fi

echo ""
echo "=================================================="
echo "✅ .env 파일 업데이트 완료!"
echo "=================================================="
echo ""

# 설정 확인
echo "📋 현재 설정:"
echo ""
echo "UVIS API:"
grep "UVIS_" /root/uvis/.env
echo ""
echo "OpenAI API:"
grep "OPENAI_API_KEY" /root/uvis/.env | sed 's/\(sk-proj-[^=]*\).*/\1.../'
echo ""

# Backend 재시작 확인
echo "🔄 Backend를 재시작하시겠습니까? (Y/n): "
read -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "Backend 재시작 중..."
    cd /root/uvis
    docker-compose -f docker-compose.prod.yml restart backend
    
    echo "⏳ 30초 대기 중..."
    sleep 30
    
    echo "✅ Backend 재시작 완료"
    echo ""
    
    # 테스트
    echo "🧪 설정 테스트 중..."
    echo ""
    echo "Health Check:"
    curl -s http://localhost:8000/health | jq '.' || curl -s http://localhost:8000/health
    echo ""
    echo "AI 사용 통계:"
    curl -s http://localhost:8000/api/v1/ai-usage/stats | jq '.' || curl -s http://localhost:8000/api/v1/ai-usage/stats
fi

echo ""
echo "=================================================="
echo "🎉 완료!"
echo "=================================================="
