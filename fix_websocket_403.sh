#!/bin/bash
# WebSocket 403 에러 완전 수정 스크립트

echo "======================================"
echo "WebSocket 403 에러 수정 시작"
echo "======================================"
echo ""

cd /root/uvis/backend

# 1. 현재 파일 백업
echo "=== 1. 현재 WebSocket 파일 백업 ==="
docker exec uvis-backend cp /app/app/api/v1/websocket.py /app/app/api/v1/websocket.py.backup.403fix.$(date +%Y%m%d_%H%M%S)
echo "✅ 백업 완료"
echo ""

# 2. 새 WebSocket 코드 복사
echo "=== 2. 수정된 WebSocket 코드 배포 ==="
if [ -f "/root/uvis/frontend/websocket_403_fix.py" ]; then
    docker cp /root/uvis/frontend/websocket_403_fix.py uvis-backend:/app/app/api/v1/websocket.py
    echo "✅ 새 코드 복사 완료"
else
    echo "❌ 수정 파일을 찾을 수 없습니다: /root/uvis/frontend/websocket_403_fix.py"
    echo "   다음 명령어로 파일을 서버에 업로드해주세요:"
    echo "   scp -P 2829 websocket_403_fix.py root@139.150.11.99:/root/uvis/frontend/"
    exit 1
fi
echo ""

# 3. Backend 재시작
echo "=== 3. Backend 컨테이너 재시작 ==="
docker restart uvis-backend
echo "✅ 재시작 명령 실행"
echo ""

# 4. 재시작 대기
echo "=== 4. 서비스 시작 대기 (30초) ==="
for i in {30..1}; do
    echo -ne "\r대기 중... $i초  "
    sleep 1
done
echo ""
echo "✅ 대기 완료"
echo ""

# 5. 로그 확인
echo "=== 5. 최근 Backend 로그 확인 ==="
docker logs uvis-backend --tail 30
echo ""

# 6. WebSocket 연결 테스트
echo "=== 6. WebSocket 403 에러 확인 ==="
docker logs uvis-backend --tail 50 | grep -E "WebSocket|403|✅|🔵" | tail -10
echo ""

echo "======================================"
echo "배포 완료!"
echo "======================================"
echo ""
echo "🌐 브라우저 테스트:"
echo "1. http://139.150.11.99 접속"
echo "2. 강력 새로고침 (Ctrl + Shift + F5)"
echo "3. F12 → Console 탭 확인"
echo "4. Network 탭 → WS 필터 → /api/v1/ws/dashboard 확인"
echo ""
echo "✅ 예상 결과: WebSocket 연결 성공 (101 Switching Protocols)"
echo "❌ 만약 여전히 403이면:"
echo "   - diagnose_websocket_403.sh 스크립트 실행"
echo "   - Nginx 설정 확인 필요"
echo ""
