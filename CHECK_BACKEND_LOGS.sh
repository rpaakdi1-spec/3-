#!/bin/bash
# 서버에서 실행: cd /root/uvis && bash CHECK_BACKEND_LOGS.sh
cd /root/uvis

echo "=== [1] 컨테이너 상태 ==="
docker compose ps

echo ""
echo "=== [2] 백엔드 전체 시작 로그 ==="
docker compose logs backend --tail=80 2>&1

echo ""
echo "=== [3] 에러 키워드 ==="
docker compose logs backend 2>&1 | grep -iE "error|exception|traceback|failed|crash|exit|killed|fatal" | tail -30

echo ""
echo "=== [4] 직접 연결 테스트 ==="
curl -sv http://localhost:8000/health 2>&1 | tail -20

echo ""
echo "=== [5] 백엔드 프로세스 확인 ==="
docker compose exec backend ps aux 2>/dev/null || echo "컨테이너 실행 중 아님"

echo ""
echo "=== [6] 컨테이너 내부 Python 문법 검사 ==="
docker compose exec backend python3 -m py_compile /app/app/api/dispatch_documents.py && echo "✅ syntax OK" || echo "❌ syntax ERROR"

