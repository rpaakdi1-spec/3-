#!/bin/bash

# ML Dispatch Monitoring Script
# 파일럿 롤아웃 후 1시간 동안 자동 모니터링

set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 설정
API_BASE="http://localhost:8000/api"
MONITOR_DURATION=3600  # 1시간 (초)
CHECK_INTERVAL=600     # 10분마다 체크 (초)
LOG_FILE="/root/uvis/logs/ml_monitoring_$(date +%Y%m%d_%H%M%S).log"

# 성공 기준
SUCCESS_RATE_THRESHOLD=0.90
AVG_SCORE_THRESHOLD=0.70
ERROR_RATE_THRESHOLD=0.05
RESPONSE_TIME_THRESHOLD=2.0

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_metric() {
    echo -e "${CYAN}[METRIC]${NC} $1" | tee -a "$LOG_FILE"
}

# 배너
echo ""
echo "========================================================================" | tee -a "$LOG_FILE"
echo "  📊 ML Dispatch Monitoring - Pilot 10% Rollout" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

log_info "Monitoring started at: $(date)"
log_info "Duration: $MONITOR_DURATION seconds ($((MONITOR_DURATION / 60)) minutes)"
log_info "Check interval: $CHECK_INTERVAL seconds ($((CHECK_INTERVAL / 60)) minutes)"
log_info "Log file: $LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 초기 상태 확인
log_info "Initial state check..."
STATS=$(curl -s "$API_BASE/ml-dispatch/ab-test/stats")
echo "$STATS" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 모니터링 변수
START_TIME=$(date +%s)
CHECK_COUNT=0
FAILED_CHECKS=0
ALERT_COUNT=0

# 메트릭 체크 함수
check_metrics() {
    local check_num=$1
    local elapsed=$2
    
    echo "" | tee -a "$LOG_FILE"
    echo "========================================================================" | tee -a "$LOG_FILE"
    log_info "Check #$check_num - Elapsed: $((elapsed / 60)) minutes"
    echo "========================================================================" | tee -a "$LOG_FILE"
    
    # A/B 테스트 통계 조회
    log_info "Fetching A/B test stats..."
    STATS=$(curl -s "$API_BASE/ml-dispatch/ab-test/stats")
    
    if [ $? -ne 0 ] || [ -z "$STATS" ]; then
        log_error "Failed to fetch stats"
        return 1
    fi
    
    # JSON 파싱 (jq 필요)
    if command -v jq &> /dev/null; then
        local total_users=$(echo "$STATS" | jq -r '.total_users // 0')
        local treatment_count=$(echo "$STATS" | jq -r '.treatment_count // 0')
        local treatment_pct=$(echo "$STATS" | jq -r '.actual_treatment_percentage // 0')
        
        log_metric "Total Users: $total_users"
        log_metric "Treatment Group: $treatment_count ($treatment_pct%)"
    else
        log_warning "jq not installed - displaying raw JSON"
        echo "$STATS" | tee -a "$LOG_FILE"
    fi
    
    # 성과 메트릭 조회
    log_info "Fetching performance metrics..."
    METRICS=$(curl -s "$API_BASE/ml-dispatch/ab-test/metrics")
    
    if [ $? -ne 0 ] || [ -z "$METRICS" ]; then
        log_error "Failed to fetch metrics"
        return 1
    fi
    
    if command -v jq &> /dev/null; then
        local treatment_dispatches=$(echo "$METRICS" | jq -r '.treatment.total_dispatches // 0')
        local treatment_success=$(echo "$METRICS" | jq -r '.treatment.success_rate // 0')
        local treatment_score=$(echo "$METRICS" | jq -r '.treatment.avg_score // 0')
        local treatment_time=$(echo "$METRICS" | jq -r '.treatment.avg_response_time // 0')
        
        log_metric "Treatment Dispatches: $treatment_dispatches"
        log_metric "Success Rate: $treatment_success (threshold: $SUCCESS_RATE_THRESHOLD)"
        log_metric "Avg ML Score: $treatment_score (threshold: $AVG_SCORE_THRESHOLD)"
        log_metric "Avg Response Time: ${treatment_time}s (threshold: ${RESPONSE_TIME_THRESHOLD}s)"
        
        # 성공 기준 체크
        local checks_passed=0
        local checks_total=3
        
        if (( $(echo "$treatment_success >= $SUCCESS_RATE_THRESHOLD" | bc -l) )); then
            log_success "✅ Success rate check passed"
            checks_passed=$((checks_passed + 1))
        else
            log_error "❌ Success rate below threshold"
            ALERT_COUNT=$((ALERT_COUNT + 1))
        fi
        
        if (( $(echo "$treatment_score >= $AVG_SCORE_THRESHOLD" | bc -l) )); then
            log_success "✅ ML score check passed"
            checks_passed=$((checks_passed + 1))
        else
            log_error "❌ ML score below threshold"
            ALERT_COUNT=$((ALERT_COUNT + 1))
        fi
        
        if (( $(echo "$treatment_time < $RESPONSE_TIME_THRESHOLD" | bc -l) )); then
            log_success "✅ Response time check passed"
            checks_passed=$((checks_passed + 1))
        else
            log_error "❌ Response time above threshold"
            ALERT_COUNT=$((ALERT_COUNT + 1))
        fi
        
        log_info "Checks passed: $checks_passed/$checks_total"
        
        if [ $checks_passed -lt $checks_total ]; then
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            log_warning "Some checks failed (consecutive failures: $FAILED_CHECKS)"
            
            if [ $FAILED_CHECKS -ge 3 ]; then
                log_error "🚨 THREE CONSECUTIVE FAILURES - RECOMMEND ROLLBACK"
                return 2
            fi
        else
            FAILED_CHECKS=0
        fi
    else
        log_warning "jq not installed - displaying raw JSON"
        echo "$METRICS" | tee -a "$LOG_FILE"
    fi
    
    # 백엔드 로그 에러 체크
    log_info "Checking backend logs for errors..."
    ERROR_COUNT=$(docker logs uvis-backend --since "$((CHECK_INTERVAL / 60))m" 2>&1 | grep -i "error\|exception\|failed" | wc -l)
    
    if [ $ERROR_COUNT -gt 0 ]; then
        log_warning "Found $ERROR_COUNT errors in backend logs"
        docker logs uvis-backend --since "$((CHECK_INTERVAL / 60))m" 2>&1 | grep -i "error\|exception\|failed" | tail -10 | tee -a "$LOG_FILE"
    else
        log_success "No errors in backend logs"
    fi
    
    echo "" | tee -a "$LOG_FILE"
    return 0
}

# 메인 모니터링 루프
while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    # 모니터링 종료 체크
    if [ $ELAPSED -ge $MONITOR_DURATION ]; then
        break
    fi
    
    # 체크 실행
    CHECK_COUNT=$((CHECK_COUNT + 1))
    check_metrics $CHECK_COUNT $ELAPSED
    CHECK_RESULT=$?
    
    # 긴급 롤백 권장
    if [ $CHECK_RESULT -eq 2 ]; then
        echo "" | tee -a "$LOG_FILE"
        log_error "========================================================================" 
        log_error "  🚨 CRITICAL: IMMEDIATE ROLLBACK RECOMMENDED"
        log_error "========================================================================" 
        log_error "3 consecutive checks failed - system is not meeting success criteria"
        log_error "Execute rollback: ./scripts/gradual_rollout.sh rollback"
        echo "" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # 남은 시간 계산
    REMAINING=$((MONITOR_DURATION - ELAPSED))
    log_info "Next check in $CHECK_INTERVAL seconds (Remaining: $((REMAINING / 60)) minutes)"
    
    # 대기
    sleep $CHECK_INTERVAL
done

# 최종 요약
echo "" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
log_success "🎉 Monitoring Complete - 1 Hour Pilot Phase Finished"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

log_info "Monitoring Summary:"
log_metric "Total Checks: $CHECK_COUNT"
log_metric "Failed Checks: $FAILED_CHECKS"
log_metric "Alert Count: $ALERT_COUNT"
log_metric "Duration: $((ELAPSED / 60)) minutes"
echo "" | tee -a "$LOG_FILE"

# 최종 메트릭 조회
log_info "Final Metrics:"
FINAL_STATS=$(curl -s "$API_BASE/ml-dispatch/ab-test/stats")
FINAL_METRICS=$(curl -s "$API_BASE/ml-dispatch/ab-test/metrics")

if command -v jq &> /dev/null; then
    echo "" | tee -a "$LOG_FILE"
    log_metric "Final Statistics:"
    echo "$FINAL_STATS" | jq '.' | tee -a "$LOG_FILE"
    
    echo "" | tee -a "$LOG_FILE"
    log_metric "Final Performance:"
    echo "$FINAL_METRICS" | jq '.' | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# 최종 판정
if [ $ALERT_COUNT -eq 0 ]; then
    log_success "========================================================================" 
    log_success "  ✅ PILOT PHASE SUCCESSFUL - READY FOR 30% EXPANSION"
    log_success "========================================================================" 
    log_success "All success criteria met during 1-hour monitoring"
    log_success "Next step: ./scripts/gradual_rollout.sh expand"
    echo "" | tee -a "$LOG_FILE"
    exit 0
elif [ $ALERT_COUNT -le 2 ]; then
    log_warning "========================================================================" 
    log_warning "  ⚠️  PILOT PHASE COMPLETED WITH WARNINGS"
    log_warning "========================================================================" 
    log_warning "Some alerts detected - review metrics before expanding"
    log_warning "Review log: $LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    exit 0
else
    log_error "========================================================================" 
    log_error "  ❌ PILOT PHASE FAILED - ROLLBACK RECOMMENDED"
    log_error "========================================================================" 
    log_error "Multiple alerts detected during monitoring"
    log_error "Execute rollback: ./scripts/gradual_rollout.sh rollback"
    log_error "Review log: $LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    exit 1
fi
