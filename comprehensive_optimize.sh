#!/bin/bash
# 종합 메모리 및 디스크 최적화 스크립트

echo "🚀 종합 시스템 최적화 시작..."
echo ""

# 현재 상태 저장
echo "=== 최적화 전 상태 ==="
echo "📊 컨테이너 메모리:"
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo ""
echo "💾 시스템 메모리:"
free -h
echo ""
echo "💿 Docker 디스크 사용량:"
docker system df
echo ""

# 최적화 1: Docker 캐시 정리
echo "=== 1. Docker 빌드 캐시 정리 (15.13GB) ==="
docker builder prune -af --filter "until=24h"
echo "✅ 빌드 캐시 정리 완료"
echo ""

# 최적화 2: 미사용 이미지 정리
echo "=== 2. 미사용 Docker 이미지 정리 (8.5GB) ==="
docker image prune -af --filter "until=72h"
echo "✅ 미사용 이미지 정리 완료"
echo ""

# 최적화 3: 미사용 볼륨 정리
echo "=== 3. 미사용 Docker 볼륨 정리 (789MB) ==="
docker volume prune -f
echo "✅ 미사용 볼륨 정리 완료"
echo ""

# 최적화 4: Backend workers 감소
echo "=== 4. Backend Workers 감소 (4 → 2) ==="
cd /root/uvis
if grep -q "workers 4" docker-compose.yml; then
    cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
    sed -i 's/--workers 4/--workers 2/' docker-compose.yml
    echo "✅ docker-compose.yml 수정 완료"
    
    # Backend 재시작
    echo "🔄 Backend 재시작 중..."
    docker-compose stop backend
    docker-compose up -d backend
    echo "✅ Backend 재시작 완료"
else
    echo "ℹ️  이미 2개 이하의 workers로 설정됨"
fi
echo ""

# 최적화 5: 테스트 컨테이너 제거
echo "=== 5. 테스트 컨테이너 제거 ==="
if docker ps -a | grep -q "uvis-frontend-test"; then
    docker stop uvis-frontend-test 2>/dev/null
    docker rm uvis-frontend-test 2>/dev/null
    echo "✅ uvis-frontend-test 제거 완료"
else
    echo "ℹ️  테스트 컨테이너 없음"
fi
echo ""

# 최적화 6: 시스템 캐시 정리
echo "=== 6. 시스템 캐시 정리 ==="
sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null && echo "✅ 캐시 정리 완료" || echo "⚠️  root 권한 필요"
echo ""

# 대기
echo "⏳ 15초 대기 (시스템 안정화)..."
sleep 15

# 최적화 후 상태
echo ""
echo "=== ✅ 최적화 후 상태 ==="
echo "📊 컨테이너 메모리:"
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo ""
echo "💾 시스템 메모리:"
free -h
echo ""
echo "💿 Docker 디스크 사용량:"
docker system df
echo ""

# 백엔드 헬스 체크
echo "=== 🏥 Backend 상태 확인 ==="
sleep 5
curl -s http://localhost:8000/api/v1/health | jq . 2>/dev/null || curl -s http://localhost:8000/api/v1/health
echo ""
echo ""

echo "✅ 종합 시스템 최적화 완료!"
echo ""
echo "📊 예상 효과:"
echo "  💾 메모리:"
echo "    - Backend: 1.2GB → 0.6GB (-50%)"
echo "    - 시스템 여유: 891MB → 1.5GB (+68%)"
echo "    - Swap 사용: 251MB → 100MB (-60%)"
echo ""
echo "  💿 디스크:"
echo "    - 빌드 캐시: 15.13GB → 0GB (100% 정리)"
echo "    - 미사용 이미지: 8.5GB → 0GB (100% 정리)"
echo "    - 미사용 볼륨: 789MB → 0GB (100% 정리)"
echo "    - 총 절약: ~24GB"
echo ""
echo "📝 백업 파일: /root/uvis/docker-compose.yml.backup.*"
echo "🔙 롤백 (필요시):"
echo "    cd /root/uvis"
echo "    cp docker-compose.yml.backup.* docker-compose.yml"
echo "    docker-compose restart backend"
echo ""
echo "📈 모니터링:"
echo "    watch -n 5 'docker stats --no-stream'"
