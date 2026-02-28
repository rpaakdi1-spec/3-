#!/bin/bash
# 메모리 최적화 스크립트 (서버에서 실행)

echo "🚀 메모리 최적화 시작..."
echo ""

# 현재 상태 저장
echo "=== 최적화 전 상태 ==="
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo ""
free -h
echo ""

# 최적화 1: Backend workers 감소 (4 → 2)
echo "=== 1. Backend Workers 감소 (4 → 2) ==="
if grep -q "workers 4" docker-compose.yml; then
    cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
    sed -i 's/--workers 4/--workers 2/' docker-compose.yml
    echo "✅ docker-compose.yml 수정 완료"
else
    echo "ℹ️  이미 2개 이하의 workers로 설정되어 있습니다"
fi
echo ""

# 최적화 2: 불필요한 컨테이너 제거
echo "=== 2. 테스트 컨테이너 제거 ==="
if docker ps -a | grep -q "uvis-frontend-test"; then
    docker stop uvis-frontend-test 2>/dev/null
    docker rm uvis-frontend-test 2>/dev/null
    echo "✅ uvis-frontend-test 제거 완료"
else
    echo "ℹ️  테스트 컨테이너가 없습니다"
fi
echo ""

# 최적화 3: Backend 재시작
echo "=== 3. Backend 재시작 ==="
docker-compose stop backend
docker-compose up -d backend
echo "✅ Backend 재시작 완료"
echo ""

# 최적화 4: 캐시 정리
echo "=== 4. 시스템 캐시 정리 ==="
sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || echo "⚠️  캐시 정리 권한 필요 (root)"
echo ""

# 대기
echo "⏳ 10초 대기 (컨테이너 안정화)..."
sleep 10

# 최적화 후 상태
echo ""
echo "=== 최적화 후 상태 ==="
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo ""
free -h
echo ""

# 백엔드 상태 확인
echo "=== Backend 상태 확인 ==="
curl -s http://localhost:8000/api/v1/health | jq . 2>/dev/null || curl -s http://localhost:8000/api/v1/health
echo ""

echo "✅ 메모리 최적화 완료!"
echo ""
echo "📊 예상 효과:"
echo "  - Backend 메모리: 1.2GB → 0.6GB (-50%)"
echo "  - 시스템 여유 메모리: +600MB"
echo "  - Swap 사용: 251MB → 100MB (-60%)"
echo ""
echo "📝 백업 파일: docker-compose.yml.backup.*"
echo "🔙 롤백: cp docker-compose.yml.backup.* docker-compose.yml && docker-compose restart backend"
