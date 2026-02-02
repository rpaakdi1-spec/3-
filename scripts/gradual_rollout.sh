#!/bin/bash

# Phase 3: Gradual Rollout Script
# 점진적 롤아웃 자동화 스크립트
# 
# Usage:
#   ./gradual_rollout.sh [stage]
#
# Stages:
#   pilot    - 10% rollout (파일럿)
#   expand   - 30% rollout (확대)
#   half     - 50% rollout (절반)
#   full     - 100% rollout (전면)
#   rollback - 0% rollout (롤백)

set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 설정
API_BASE="http://139.150.11.99:8000/api"
TOKEN=""  # 필요 시 인증 토큰 설정

# 롤아웃 단계별 비율
declare -A ROLLOUT_PERCENTAGES
ROLLOUT_PERCENTAGES["pilot"]=10
ROLLOUT_PERCENTAGES["expand"]=30
ROLLOUT_PERCENTAGES["half"]=50
ROLLOUT_PERCENTAGES["full"]=100
ROLLOUT_PERCENTAGES["rollback"]=0

# 각 단계별 최소 대기 시간 (초)
declare -A WAIT_TIMES
WAIT_TIMES["pilot"]=3600      # 1시간
WAIT_TIMES["expand"]=7200     # 2시간
WAIT_TIMES["half"]=14400      # 4시간
WAIT_TIMES["full"]=0          # 대기 없음

# 성공 기준
SUCCESS_RATE_THRESHOLD=0.90
AVG_SCORE_THRESHOLD=0.70
ERROR_RATE_THRESHOLD=0.05

# 함수: 로그 출력
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 함수: API 호출
call_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    local url="${API_BASE}${endpoint}"
    local auth_header=""
    
    if [ -n "$TOKEN" ]; then
        auth_header="Authorization: Bearer $TOKEN"
    fi
    
    if [ "$method" = "GET" ]; then
        curl -s -X GET "$url" ${auth_header:+-H "$auth_header"}
    else
        curl -s -X "$method" "$url" \
            ${auth_header:+-H "$auth_header"} \
            -H "Content-Type: application/json" \
            ${data:+-d "$data"}
    fi
}

# 함수: 현재 메트릭 조회
get_metrics() {
    log_info "메트릭 조회 중..."
    
    local response=$(call_api GET "/ml-dispatch/ab-test/metrics")
    echo "$response"
}

# 함수: 롤아웃 비율 업데이트
update_rollout() {
    local percentage=$1
    
    log_info "롤아웃 비율 업데이트: ${percentage}%"
    
    local response=$(call_api POST "/ml-dispatch/ab-test/rollout?percentage=${percentage}")
    
    if echo "$response" | grep -q '"success":true'; then
        log_success "롤아웃 비율 업데이트 완료: ${percentage}%"
        return 0
    else
        log_error "롤아웃 비율 업데이트 실패"
        echo "$response"
        return 1
    fi
}

# 함수: 성공 기준 체크
check_success_criteria() {
    local metrics=$1
    
    log_info "성공 기준 체크 중..."
    
    # JSON 파싱 (jq 필요)
    if ! command -v jq &> /dev/null; then
        log_warning "jq가 설치되지 않음 - 수동 확인 필요"
        echo "$metrics"
        return 0
    fi
    
    local treatment_success_rate=$(echo "$metrics" | jq -r '.treatment.success_rate // 0')
    local treatment_avg_score=$(echo "$metrics" | jq -r '.treatment.avg_score // 0')
    local improvement=$(echo "$metrics" | jq -r '.improvements.success_rate_percentage // 0')
    
    log_info "Treatment 성공률: ${treatment_success_rate}"
    log_info "Treatment 평균 점수: ${treatment_avg_score}"
    log_info "개선율: ${improvement}%"
    
    # 성공 기준 체크
    local success=true
    
    if (( $(echo "$treatment_success_rate < $SUCCESS_RATE_THRESHOLD" | bc -l) )); then
        log_error "성공률 미달: ${treatment_success_rate} < ${SUCCESS_RATE_THRESHOLD}"
        success=false
    fi
    
    if (( $(echo "$treatment_avg_score < $AVG_SCORE_THRESHOLD" | bc -l) )); then
        log_error "평균 점수 미달: ${treatment_avg_score} < ${AVG_SCORE_THRESHOLD}"
        success=false
    fi
    
    if [ "$success" = true ]; then
        log_success "✅ 모든 성공 기준 충족"
        return 0
    else
        log_error "❌ 성공 기준 미달 - 롤아웃 중단"
        return 1
    fi
}

# 함수: 대기
wait_for_period() {
    local stage=$1
    local wait_time=${WAIT_TIMES[$stage]}
    
    if [ "$wait_time" -eq 0 ]; then
        return 0
    fi
    
    log_info "대기 중... (${wait_time}초 = $((wait_time / 3600))시간)"
    
    local remaining=$wait_time
    while [ $remaining -gt 0 ]; do
        local hours=$((remaining / 3600))
        local minutes=$(( (remaining % 3600) / 60 ))
        local seconds=$((remaining % 60))
        
        printf "\r대기 시간: %02d:%02d:%02d 남음" $hours $minutes $seconds
        
        sleep 10
        remaining=$((remaining - 10))
    done
    
    echo ""
    log_success "대기 완료"
}

# 함수: 롤아웃 단계 실행
execute_stage() {
    local stage=$1
    local percentage=${ROLLOUT_PERCENTAGES[$stage]}
    
    echo ""
    log_info "========================================="
    log_info "Stage: $stage (${percentage}% 롤아웃)"
    log_info "========================================="
    
    # 1. 메트릭 확인 (rollback 제외)
    if [ "$stage" != "rollback" ] && [ "$stage" != "pilot" ]; then
        local metrics=$(get_metrics)
        
        if ! check_success_criteria "$metrics"; then
            log_error "성공 기준 미달 - 롤아웃 중단"
            
            # 자동 롤백
            log_warning "자동 롤백 실행 중..."
            update_rollout 0
            exit 1
        fi
    fi
    
    # 2. 롤아웃 비율 업데이트
    if ! update_rollout "$percentage"; then
        log_error "롤아웃 업데이트 실패"
        exit 1
    fi
    
    # 3. 대기
    if [ "$stage" != "rollback" ]; then
        wait_for_period "$stage"
    fi
    
    log_success "Stage $stage 완료"
}

# 메인 함수
main() {
    local stage=$1
    
    # 사용법 출력
    if [ -z "$stage" ]; then
        echo "Usage: $0 [stage]"
        echo ""
        echo "Stages:"
        echo "  pilot    - 10% rollout (파일럿)"
        echo "  expand   - 30% rollout (확대)"
        echo "  half     - 50% rollout (절반)"
        echo "  full     - 100% rollout (전면)"
        echo "  rollback - 0% rollout (롤백)"
        echo ""
        echo "Example:"
        echo "  $0 pilot"
        exit 1
    fi
    
    # 단계 유효성 검사
    if [ -z "${ROLLOUT_PERCENTAGES[$stage]}" ]; then
        log_error "잘못된 단계: $stage"
        exit 1
    fi
    
    # 확인
    echo ""
    log_warning "다음 롤아웃을 실행하시겠습니까?"
    log_warning "  Stage: $stage"
    log_warning "  Target: ${ROLLOUT_PERCENTAGES[$stage]}%"
    echo ""
    read -p "계속하시겠습니까? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "취소됨"
        exit 0
    fi
    
    # 실행
    execute_stage "$stage"
    
    # 완료
    echo ""
    log_success "========================================="
    log_success "롤아웃 완료: $stage (${ROLLOUT_PERCENTAGES[$stage]}%)"
    log_success "========================================="
    
    # 다음 단계 안내
    case $stage in
        pilot)
            log_info "다음 단계: ./gradual_rollout.sh expand"
            ;;
        expand)
            log_info "다음 단계: ./gradual_rollout.sh half"
            ;;
        half)
            log_info "다음 단계: ./gradual_rollout.sh full"
            ;;
        full)
            log_success "🎉 전면 롤아웃 완료!"
            ;;
        rollback)
            log_warning "롤백 완료 - 시스템 점검 필요"
            ;;
    esac
}

# 스크립트 실행
main "$@"
