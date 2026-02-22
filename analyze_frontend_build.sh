#!/bin/bash

echo "================================================================"
echo "🔍 프론트엔드 빌드 WebSocket URL 상세 분석"
echo "================================================================"
echo ""

# RealtimeDashboardPage 파일 찾기
echo "1️⃣ RealtimeDashboardPage 파일 찾기..."
echo "────────────────────────────────────────────────────────────────"
DASHBOARD_FILE=$(docker exec uvis-frontend find /usr/share/nginx/html/assets -name "RealtimeDashboardPage-*.js" -type f 2>/dev/null | head -1)

if [ -z "$DASHBOARD_FILE" ]; then
    echo "❌ RealtimeDashboardPage-*.js 파일을 찾을 수 없습니다!"
    echo ""
    echo "모든 JavaScript 파일:"
    docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/*.js
    exit 1
fi

echo "✅ 파일 발견: $DASHBOARD_FILE"
docker exec uvis-frontend ls -lh "$DASHBOARD_FILE"
echo ""

# WebSocket URL 추출
echo "2️⃣ 파일 내 WebSocket URL 추출..."
echo "────────────────────────────────────────────────────────────────"

echo "모든 'ws://' URL:"
docker exec uvis-frontend grep -o 'ws://[^"'"'"' ]*' "$DASHBOARD_FILE" 2>/dev/null | sort -u
echo ""

echo "모든 'wss://' URL:"
docker exec uvis-frontend grep -o 'wss://[^"'"'"' ]*' "$DASHBOARD_FILE" 2>/dev/null | sort -u
echo ""

echo "모든 '/api/v1/' 경로:"
docker exec uvis-frontend grep -o '/api/v1/[^"'"'"' ]*' "$DASHBOARD_FILE" 2>/dev/null | grep -i ws | sort -u
echo ""

# 특정 패턴 검색
echo "3️⃣ 잘못된 패턴 검색..."
echo "────────────────────────────────────────────────────────────────"

echo "❌ 잘못된 경로: '/api/v1/ws/alerts' (dispatches 누락)"
WRONG_COUNT=$(docker exec uvis-frontend grep -o '/api/v1/ws/alerts' "$DASHBOARD_FILE" 2>/dev/null | wc -l)
echo "   발견: $WRONG_COUNT 개"
if [ $WRONG_COUNT -gt 0 ]; then
    echo "   ⚠️  이 파일을 교체해야 합니다!"
fi
echo ""

echo "✅ 올바른 경로: '/api/v1/dispatches/ws/dashboard'"
CORRECT_DASHBOARD=$(docker exec uvis-frontend grep -o '/api/v1/dispatches/ws/dashboard' "$DASHBOARD_FILE" 2>/dev/null | wc -l)
echo "   발견: $CORRECT_DASHBOARD 개"
echo ""

echo "✅ 올바른 경로: '/api/v1/dispatches/ws/alerts'"
CORRECT_ALERTS=$(docker exec uvis-frontend grep -o '/api/v1/dispatches/ws/alerts' "$DASHBOARD_FILE" 2>/dev/null | wc -l)
echo "   발견: $CORRECT_ALERTS 개"
echo ""

# 파일 타임스탬프
echo "4️⃣ 파일 타임스탬프..."
echo "────────────────────────────────────────────────────────────────"
docker exec uvis-frontend stat "$DASHBOARD_FILE" | grep -E "Modify:|File:"
echo ""

# 소스 파일 확인
echo "5️⃣ 소스 파일 확인 (/root/uvis/frontend)..."
echo "────────────────────────────────────────────────────────────────"
if [ -f /root/uvis/frontend/src/hooks/useRealtimeData.ts ]; then
    echo "useRealtimeData.ts WebSocket URL:"
    grep -E "ws[s]?://" /root/uvis/frontend/src/hooks/useRealtimeData.ts || \
    grep -E "/api/v1/.+ws" /root/uvis/frontend/src/hooks/useRealtimeData.ts | head -5
    echo ""
    
    echo "useRealtimeData.ts 파일 수정 시간:"
    stat /root/uvis/frontend/src/hooks/useRealtimeData.ts | grep Modify
else
    echo "⚠️  소스 파일을 찾을 수 없습니다."
fi
echo ""

# dist 디렉토리 확인
echo "6️⃣ 로컬 dist 디렉토리 확인..."
echo "────────────────────────────────────────────────────────────────"
if [ -d /root/uvis/frontend/dist/assets ]; then
    echo "로컬 빌드 파일:"
    ls -lht /root/uvis/frontend/dist/assets/RealtimeDashboardPage-*.js 2>/dev/null | head -3
    echo ""
    
    LOCAL_DASHBOARD=$(ls -1 /root/uvis/frontend/dist/assets/RealtimeDashboardPage-*.js 2>/dev/null | head -1)
    if [ -n "$LOCAL_DASHBOARD" ]; then
        echo "로컬 빌드 파일의 WebSocket URL:"
        grep -o '/api/v1/.*ws.*' "$LOCAL_DASHBOARD" 2>/dev/null | head -5
    fi
else
    echo "⚠️  dist 디렉토리가 없습니다. 빌드가 필요합니다."
fi
echo ""

# 결론
echo "================================================================"
echo "📊 분석 결과"
echo "================================================================"
echo ""

if [ $WRONG_COUNT -gt 0 ]; then
    echo "🔴 문제 발견: 잘못된 WebSocket URL이 빌드 파일에 존재합니다!"
    echo ""
    echo "해결 방법:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. 소스 파일 수정:"
    echo "   vi /root/uvis/frontend/src/hooks/useRealtimeData.ts"
    echo "   또는"
    echo "   sed -i 's|/api/v1/ws/alerts|/api/v1/dispatches/ws/alerts|g' \\"
    echo "       /root/uvis/frontend/src/hooks/useRealtimeData.ts"
    echo ""
    echo "2. 프론트엔드 다시 빌드:"
    echo "   cd /root/uvis/frontend && npm run build"
    echo ""
    echo "3. 컨테이너에 배포:"
    echo "   docker exec uvis-frontend rm -rf /usr/share/nginx/html/*"
    echo "   docker cp /root/uvis/frontend/dist/. uvis-frontend:/usr/share/nginx/html/"
    echo ""
    echo "4. 컨테이너 재시작:"
    echo "   docker restart uvis-frontend"
    echo ""
elif [ $CORRECT_DASHBOARD -eq 0 ] && [ $CORRECT_ALERTS -eq 0 ]; then
    echo "🟡 경고: WebSocket URL을 찾을 수 없습니다!"
    echo "   빌드 파일이 올바르지 않을 수 있습니다."
    echo ""
elif [ $CORRECT_DASHBOARD -gt 0 ] && [ $CORRECT_ALERTS -gt 0 ]; then
    echo "✅ 빌드 파일의 WebSocket URL이 올바릅니다!"
    echo ""
    echo "브라우저에서도 실패한다면:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. 브라우저 캐시 완전 삭제 (시간 범위: 전체)"
    echo "2. 브라우저 완전 종료 (작업 관리자에서 프로세스 확인)"
    echo "3. 시크릿/인코그니토 모드로 재시작"
    echo "4. F12 → Network 탭 → Disable cache 체크"
    echo "5. http://139.150.11.99/realtime 접속"
    echo "6. Ctrl+Shift+R로 강력 새로고침"
    echo ""
else
    echo "🟡 부분적 문제: 일부 WebSocket URL만 올바릅니다."
    echo "   Dashboard: $CORRECT_DASHBOARD 개"
    echo "   Alerts: $CORRECT_ALERTS 개"
    echo ""
fi
