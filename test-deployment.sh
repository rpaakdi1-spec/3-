#!/bin/bash

###############################################################################
# UVIS Phase 16 기능 테스트 스크립트
# 버전: 1.0
# 날짜: 2026-02-26
###############################################################################

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 설정
API_URL="${API_URL:-http://localhost:8000/api/v1}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost}"
TEST_USERNAME="${TEST_USERNAME:-admin}"
TEST_PASSWORD="${TEST_PASSWORD:-password}"

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 테스트 시작
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         UVIS Phase 16 기능 테스트 스크립트 v1.0           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 테스트 결과 추적
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    local test_name=$1
    local test_command=$2
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log_info "테스트 $TOTAL_TESTS: $test_name"
    
    if eval "$test_command"; then
        log_success "$test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        log_error "$test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# 1. 인증 테스트
echo ""
echo "═══════════════════════════════════════"
echo "  1. 인증 시스템 테스트"
echo "═══════════════════════════════════════"

log_info "로그인 시도 중..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$TEST_USERNAME\",\"password\":\"$TEST_PASSWORD\"}")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token // empty')

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    log_success "로그인 성공"
    log_info "토큰: ${TOKEN:0:20}..."
else
    log_error "로그인 실패!"
    log_info "응답: $LOGIN_RESPONSE"
    log_info "기본 사용자(admin/password)가 없을 수 있습니다."
    exit 1
fi

# 2. 헬스 체크 테스트
echo ""
echo "═══════════════════════════════════════"
echo "  2. 서비스 헬스 체크"
echo "═══════════════════════════════════════"

run_test "백엔드 헬스 체크" \
  "curl -s -f $API_URL/health > /dev/null"

run_test "프론트엔드 접근 가능" \
  "curl -s -f $FRONTEND_URL > /dev/null"

# 3. FCM 푸시 알림 테스트
echo ""
echo "═══════════════════════════════════════"
echo "  3. FCM 푸시 알림 테스트"
echo "═══════════════════════════════════════"

# FCM 토큰 등록 테스트
FCM_TOKEN="test-fcm-token-$(date +%s)"
log_info "FCM 토큰 등록: $FCM_TOKEN"

FCM_REGISTER=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/notifications/register-token" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"token\": \"$FCM_TOKEN\",
    \"device_type\": \"web\",
    \"device_id\": \"test-device-$(date +%s)\",
    \"app_version\": \"1.0.0\"
  }")

HTTP_CODE=$(echo "$FCM_REGISTER" | tail -n1)
RESPONSE=$(echo "$FCM_REGISTER" | sed '$ d')

if [ "$HTTP_CODE" == "200" ]; then
    log_success "FCM 토큰 등록 성공"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    log_error "FCM 토큰 등록 실패 (HTTP $HTTP_CODE)"
    log_info "응답: $RESPONSE"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# 내 토큰 목록 조회
run_test "FCM 토큰 목록 조회" \
  "curl -s -f -H 'Authorization: Bearer $TOKEN' $API_URL/notifications/my-tokens > /dev/null"

# 4. 파일 업로드 테스트
echo ""
echo "═══════════════════════════════════════"
echo "  4. 파일 업로드 시스템 테스트"
echo "═══════════════════════════════════════"

# 테스트 파일 생성
TEST_FILE="/tmp/test-upload-$(date +%s).txt"
echo "This is a test file for UVIS Phase 16 deployment" > $TEST_FILE

log_info "테스트 파일 생성: $TEST_FILE"

# 파일 업로드
FILE_UPLOAD=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/files/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$TEST_FILE")

HTTP_CODE=$(echo "$FILE_UPLOAD" | tail -n1)
RESPONSE=$(echo "$FILE_UPLOAD" | sed '$ d')

if [ "$HTTP_CODE" == "200" ]; then
    log_success "파일 업로드 성공"
    FILE_URL=$(echo "$RESPONSE" | jq -r '.file_url // .url')
    log_info "파일 URL: $FILE_URL"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    log_error "파일 업로드 실패 (HTTP $HTTP_CODE)"
    log_info "응답: $RESPONSE"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# 파일 목록 조회
run_test "파일 목록 조회" \
  "curl -s -f -H 'Authorization: Bearer $TOKEN' '$API_URL/files/list?folder=uploads' > /dev/null"

# 테스트 파일 삭제
rm -f $TEST_FILE

# 5. 채팅 시스템 테스트
echo ""
echo "═══════════════════════════════════════"
echo "  5. 실시간 채팅 시스템 테스트"
echo "═══════════════════════════════════════"

# 채팅방 생성
log_info "테스트 채팅방 생성 중..."

CHAT_ROOM=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/chat/rooms" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"테스트 채팅방 $(date +%Y%m%d-%H%M%S)\",
    \"description\": \"자동 테스트용 채팅방\"
  }")

HTTP_CODE=$(echo "$CHAT_ROOM" | tail -n1)
RESPONSE=$(echo "$CHAT_ROOM" | sed '$ d')

if [ "$HTTP_CODE" == "200" ]; then
    log_success "채팅방 생성 성공"
    ROOM_ID=$(echo "$RESPONSE" | jq -r '.id')
    log_info "채팅방 ID: $ROOM_ID"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    log_error "채팅방 생성 실패 (HTTP $HTTP_CODE)"
    log_info "응답: $RESPONSE"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    ROOM_ID=""
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# 채팅방 목록 조회
run_test "채팅방 목록 조회" \
  "curl -s -f -H 'Authorization: Bearer $TOKEN' $API_URL/chat/rooms > /dev/null"

# 채팅방 정보 조회 (채팅방이 생성된 경우)
if [ -n "$ROOM_ID" ] && [ "$ROOM_ID" != "null" ]; then
    run_test "채팅방 정보 조회" \
      "curl -s -f -H 'Authorization: Bearer $TOKEN' $API_URL/chat/rooms/$ROOM_ID > /dev/null"
    
    # 메시지 전송
    log_info "테스트 메시지 전송 중..."
    
    MESSAGE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/chat/rooms/$ROOM_ID/messages" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"content\": \"테스트 메시지: $(date)\",
        \"message_type\": \"text\"
      }")
    
    HTTP_CODE=$(echo "$MESSAGE" | tail -n1)
    
    if [ "$HTTP_CODE" == "200" ]; then
        log_success "메시지 전송 성공"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        log_error "메시지 전송 실패 (HTTP $HTTP_CODE)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # 메시지 목록 조회
    run_test "메시지 목록 조회" \
      "curl -s -f -H 'Authorization: Bearer $TOKEN' $API_URL/chat/rooms/$ROOM_ID/messages > /dev/null"
fi

# 6. UVIS 기존 기능 테스트
echo ""
echo "═══════════════════════════════════════"
echo "  6. UVIS 기존 기능 테스트"
echo "═══════════════════════════════════════"

run_test "차량 목록 조회" \
  "curl -s -f -H 'Authorization: Bearer $TOKEN' $API_URL/vehicles > /dev/null"

run_test "차량 알림 조회" \
  "curl -s -f -H 'Authorization: Bearer $TOKEN' '$API_URL/vehicles/alerts/recent?limit=10' > /dev/null"

# 테스트 요약
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  테스트 결과 요약                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "  총 테스트: $TOTAL_TESTS"
echo "  통과: $GREEN$PASSED_TESTS$NC"
echo "  실패: $RED$FAILED_TESTS$NC"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ 모든 테스트 통과!${NC}"
    echo ""
    echo "🎉 Phase 16 기능이 정상적으로 배포되었습니다!"
    exit 0
else
    echo -e "${RED}✗ 일부 테스트 실패${NC}"
    echo ""
    echo "⚠️  다음을 확인하세요:"
    echo "  1. docker-compose logs -f"
    echo "  2. docs/PRODUCTION_DEPLOYMENT_GUIDE.md 참조"
    echo "  3. .env 파일 설정 확인"
    exit 1
fi
