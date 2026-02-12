#!/bin/bash

echo "=========================================="
echo "ML 모델 학습 스크립트"
echo "=========================================="
echo ""

API_URL="http://localhost:8000/api/v1"

# 1단계: 로그인
echo "1. 로그인 중..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin")

echo "Login Response: $LOGIN_RESPONSE"
echo ""

# 토큰 추출
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ 로그인 실패! 비밀번호를 확인하세요."
    echo "다른 비밀번호로 시도 중..."
    
    LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=admin&password=admin123")
    
    TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
    
    if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
        echo "❌ 로그인 실패!"
        exit 1
    fi
fi

echo "✅ 로그인 성공!"
echo "Token: ${TOKEN:0:20}..."
echo ""

# 2단계: ML 통계 확인 (학습 전)
echo "2. ML 통계 확인 (학습 전)..."
STATS_BEFORE=$(curl -s "$API_URL/ml/statistics?days=7" \
  -H "Authorization: Bearer $TOKEN")
echo "$STATS_BEFORE" | jq '.'
echo ""

# 3단계: ML 모델 학습 시작
echo "3. ML 모델 학습 시작..."
echo "⚠️  학습에는 1-2분 정도 소요될 수 있습니다..."
echo ""

TRAIN_RESPONSE=$(curl -s -X POST "$API_URL/ml/train" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "학습 결과:"
echo "$TRAIN_RESPONSE" | jq '.'
echo ""

# 4단계: 학습 후 통계 확인
echo "4. ML 통계 확인 (학습 후)..."
sleep 3
STATS_AFTER=$(curl -s "$API_URL/ml/statistics?days=7" \
  -H "Authorization: Bearer $TOKEN")
echo "$STATS_AFTER" | jq '.'
echo ""

# 5단계: ML 모델 목록 확인
echo "5. ML 모델 목록 확인..."
MODELS=$(curl -s "$API_URL/ml/models?limit=10" \
  -H "Authorization: Bearer $TOKEN")
echo "$MODELS" | jq '.'
echo ""

echo "=========================================="
echo "✅ ML 학습 프로세스 완료!"
echo "=========================================="
