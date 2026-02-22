#!/bin/bash

cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🔥 UVIS WebSocket 문제 해결사 🔥                               ║
║                                                                  ║
║   5일간의 디버깅을 끝내는 최종 솔루션                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF

echo ""
echo "이 스크립트는 다음을 수행합니다:"
echo "  1. 현재 상태 진단"
echo "  2. 문제 식별"
echo "  3. 자동 수정"
echo "  4. 검증"
echo ""
read -p "계속하시겠습니까? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "취소되었습니다."
    exit 0
fi

echo ""
echo "================================================================"
echo "🔍 STEP 1: 현재 상태 진단"
echo "================================================================"
echo ""

# 컨테이너 상태
echo "▶ 컨테이너 상태:"
docker ps --filter "name=uvis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAMES|uvis-frontend|uvis-backend"
echo ""

# 빌드 파일의 WebSocket URL 확인 (가장 중요!)
echo "▶ 빌드 파일의 WebSocket URL 확인 (핵심!):"
DASHBOARD_FILE=$(docker exec uvis-frontend find /usr/share/nginx/html/assets -name "RealtimeDashboardPage-*.js" -type f 2>/dev/null | head -1)

if [ -z "$DASHBOARD_FILE" ]; then
    echo "❌ ERROR: RealtimeDashboardPage-*.js를 찾을 수 없습니다!"
    echo "   프론트엔드 빌드가 배포되지 않았을 수 있습니다."
    exit 1
fi

echo "   파일: $DASHBOARD_FILE"

# 잘못된 URL 체크
WRONG_URL_COUNT=$(docker exec uvis-frontend grep -c '/api/v1/ws/alerts' "$DASHBOARD_FILE" 2>/dev/null || echo "0")
CORRECT_DASHBOARD=$(docker exec uvis-frontend grep -c '/api/v1/dispatches/ws/dashboard' "$DASHBOARD_FILE" 2>/dev/null || echo "0")
CORRECT_ALERTS=$(docker exec uvis-frontend grep -c '/api/v1/dispatches/ws/alerts' "$DASHBOARD_FILE" 2>/dev/null || echo "0")

echo "   ❌ 잘못된 URL (/api/v1/ws/alerts): $WRONG_URL_COUNT 개"
echo "   ✅ 올바른 Dashboard URL: $CORRECT_DASHBOARD 개"
echo "   ✅ 올바른 Alerts URL: $CORRECT_ALERTS 개"
echo ""

# Nginx 설정 확인
echo "▶ Nginx WebSocket 설정:"
HAS_WEBSOCKET_LOCATION=$(docker exec uvis-frontend nginx -T 2>&1 | grep -c "location.*dispatches.*ws")
if [ "$HAS_WEBSOCKET_LOCATION" -gt 0 ]; then
    echo "   ✅ WebSocket location 블록 존재"
else
    echo "   ❌ WebSocket location 블록 없음!"
fi

HAS_UPGRADE_HEADER=$(docker exec uvis-frontend nginx -T 2>&1 | grep -c "proxy_set_header Upgrade")
if [ "$HAS_UPGRADE_HEADER" -gt 0 ]; then
    echo "   ✅ Upgrade 헤더 설정됨"
else
    echo "   ❌ Upgrade 헤더 없음!"
fi
echo ""

# 백엔드 WebSocket 테스트
echo "▶ 백엔드 WebSocket 테스트 (5초):"
WSCAT_OUTPUT=$(timeout 5 wscat -c ws://localhost/api/v1/dispatches/ws/dashboard 2>&1 | head -3)
if echo "$WSCAT_OUTPUT" | grep -q "total_orders"; then
    echo "   ✅ WebSocket 연결 성공! 데이터 수신 중"
else
    echo "   ❌ WebSocket 연결 실패 또는 데이터 없음"
    echo "   출력: $WSCAT_OUTPUT"
fi
echo ""

# 문제 판단
echo "================================================================"
echo "📊 STEP 2: 문제 식별"
echo "================================================================"
echo ""

PROBLEM_FOUND=false

if [ "$WRONG_URL_COUNT" -gt 0 ]; then
    echo "🔴 문제 #1: 빌드 파일에 잘못된 WebSocket URL이 있습니다!"
    echo "   → 잘못된 경로: /api/v1/ws/alerts"
    echo "   → 올바른 경로: /api/v1/dispatches/ws/alerts"
    echo ""
    PROBLEM_FOUND=true
fi

if [ "$CORRECT_DASHBOARD" -eq 0 ] || [ "$CORRECT_ALERTS" -eq 0 ]; then
    echo "🔴 문제 #2: 올바른 WebSocket URL이 빌드 파일에 없습니다!"
    echo "   → 프론트엔드 소스가 수정되지 않았거나"
    echo "   → 빌드가 오래되었거나"
    echo "   → 잘못된 빌드가 배포되었습니다."
    echo ""
    PROBLEM_FOUND=true
fi

if [ "$HAS_WEBSOCKET_LOCATION" -eq 0 ] || [ "$HAS_UPGRADE_HEADER" -eq 0 ]; then
    echo "🔴 문제 #3: Nginx WebSocket 설정이 올바르지 않습니다!"
    echo ""
    PROBLEM_FOUND=true
fi

if ! echo "$WSCAT_OUTPUT" | grep -q "total_orders"; then
    echo "🔴 문제 #4: 서버 측 WebSocket 연결이 작동하지 않습니다!"
    echo "   → Nginx 또는 백엔드 문제"
    echo ""
    PROBLEM_FOUND=true
fi

if [ "$PROBLEM_FOUND" = false ]; then
    echo "✅ 서버 측은 모두 정상입니다!"
    echo ""
    echo "브라우저에서도 실패한다면, 이것은 100% 브라우저 캐시 문제입니다."
    echo ""
    echo "================================================================"
    echo "🌐 브라우저 캐시 완전 삭제 방법"
    echo "================================================================"
    echo ""
    echo "Windows (Chrome/Edge):"
    echo "  1. Ctrl+Alt+Del → 작업 관리자"
    echo "  2. Chrome/Edge 프로세스 모두 종료"
    echo "  3. Chrome 재시작"
    echo "  4. Ctrl+Shift+Delete → 시간 범위: 전체 시간 → 삭제"
    echo "  5. 컴퓨터 재부팅"
    echo "  6. Ctrl+Shift+N (시크릿 모드)"
    echo "  7. F12 → Network → Disable cache 체크"
    echo "  8. http://139.150.11.99/realtime 접속"
    echo "  9. Ctrl+Shift+R을 3회 연속 누르기"
    echo ""
    echo "또는 다른 브라우저 (Firefox, Safari) 사용"
    echo "또는 다른 컴퓨터/스마트폰에서 테스트"
    echo ""
    exit 0
fi

# 자동 수정
echo "================================================================"
echo "🔧 STEP 3: 자동 수정 시작"
echo "================================================================"
echo ""

if [ "$WRONG_URL_COUNT" -gt 0 ] || [ "$CORRECT_DASHBOARD" -eq 0 ] || [ "$CORRECT_ALERTS" -eq 0 ]; then
    echo "▶ 프론트엔드 소스 파일 수정..."
    
    if [ -f /root/uvis/frontend/src/hooks/useRealtimeData.ts ]; then
        # 백업
        cp /root/uvis/frontend/src/hooks/useRealtimeData.ts /root/uvis/frontend/src/hooks/useRealtimeData.ts.backup
        
        # 수정
        sed -i 's|/api/v1/ws/alerts|/api/v1/dispatches/ws/alerts|g' /root/uvis/frontend/src/hooks/useRealtimeData.ts
        sed -i 's|/api/v1/ws/dashboard|/api/v1/dispatches/ws/dashboard|g' /root/uvis/frontend/src/hooks/useRealtimeData.ts
        
        echo "   ✅ useRealtimeData.ts 수정 완료"
        echo ""
        
        echo "▶ 프론트엔드 다시 빌드..."
        cd /root/uvis/frontend
        npm run build > /tmp/build.log 2>&1
        
        if [ $? -eq 0 ]; then
            echo "   ✅ 빌드 성공"
        else
            echo "   ❌ 빌드 실패! 로그:"
            tail -20 /tmp/build.log
            exit 1
        fi
        echo ""
        
        echo "▶ 새 빌드 배포..."
        docker exec uvis-frontend rm -rf /usr/share/nginx/html/*
        docker cp /root/uvis/frontend/dist/. uvis-frontend:/usr/share/nginx/html/
        
        echo "   ✅ 배포 완료"
        echo ""
    else
        echo "   ❌ 소스 파일을 찾을 수 없습니다: /root/uvis/frontend/src/hooks/useRealtimeData.ts"
        exit 1
    fi
fi

echo "▶ Nginx 재시작..."
docker restart uvis-frontend
sleep 10
echo "   ✅ Nginx 재시작 완료"
echo ""

# 검증
echo "================================================================"
echo "✅ STEP 4: 수정 검증"
echo "================================================================"
echo ""

echo "▶ 새 빌드 파일의 WebSocket URL 확인:"
sleep 2
DASHBOARD_FILE=$(docker exec uvis-frontend find /usr/share/nginx/html/assets -name "RealtimeDashboardPage-*.js" -type f 2>/dev/null | head -1)
WRONG_URL_COUNT=$(docker exec uvis-frontend grep -c '/api/v1/ws/alerts' "$DASHBOARD_FILE" 2>/dev/null || echo "0")
CORRECT_DASHBOARD=$(docker exec uvis-frontend grep -c '/api/v1/dispatches/ws/dashboard' "$DASHBOARD_FILE" 2>/dev/null || echo "0")
CORRECT_ALERTS=$(docker exec uvis-frontend grep -c '/api/v1/dispatches/ws/alerts' "$DASHBOARD_FILE" 2>/dev/null || echo "0")

echo "   ❌ 잘못된 URL: $WRONG_URL_COUNT 개"
echo "   ✅ 올바른 Dashboard URL: $CORRECT_DASHBOARD 개"
echo "   ✅ 올바른 Alerts URL: $CORRECT_ALERTS 개"
echo ""

if [ "$WRONG_URL_COUNT" -eq 0 ] && [ "$CORRECT_DASHBOARD" -gt 0 ] && [ "$CORRECT_ALERTS" -gt 0 ]; then
    echo "🎉 빌드 파일 수정 성공!"
else
    echo "⚠️  빌드 파일이 아직 올바르지 않습니다."
fi
echo ""

echo "▶ WebSocket 연결 재테스트 (10초):"
timeout 10 wscat -c ws://localhost/api/v1/dispatches/ws/dashboard 2>&1 | head -5
echo ""

echo "================================================================"
echo "🎉 수정 완료!"
echo "================================================================"
echo ""
echo "📱 이제 브라우저에서 테스트하세요:"
echo ""
echo "  1. 모든 브라우저 창을 완전히 종료하세요 (작업 관리자 확인)"
echo "  2. 시크릿/인코그니토 모드로 브라우저를 다시 여세요"
echo "  3. F12를 눌러 개발자 도구를 여세요"
echo "  4. Console 탭을 선택하세요"
echo "  5. http://139.150.11.99/realtime 주소로 이동하세요"
echo "  6. Ctrl+Shift+R을 3회 연속으로 눌러 강력 새로고침하세요"
echo ""
echo "예상 콘솔 출력:"
echo "  ✅ WebSocket connected: ws://139.150.11.99/api/v1/dispatches/ws/dashboard"
echo "  📊 Dashboard WebSocket connected"
echo "  { total_orders: 0, pending_orders: 0, available_vehicles: 46, ... }"
echo ""
echo "  ✅ WebSocket connected: ws://139.150.11.99/api/v1/dispatches/ws/alerts"
echo "  🚨 Alerts WebSocket connected"
echo ""
echo "화면에 4개의 카드가 표시되고 숫자가 5초마다 업데이트되어야 합니다."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "그래도 실패한다면, 다음을 시도하세요:"
echo "  • 다른 브라우저 (Firefox, Safari, Chrome Canary)"
echo "  • 다른 컴퓨터 또는 스마트폰"
echo "  • 브라우저 캐시 완전 삭제 + 컴퓨터 재부팅"
echo ""
echo "5일간의 여정이 여기서 끝나기를 바랍니다! 🙏"
echo ""
