#!/bin/bash

# 서버 복구 후 즉시 실행할 스크립트
# 이 파일을 서버에 복사하여 실행하세요

echo "=========================================="
echo "  서버 복구 후 즉시 점검 스크립트"
echo "=========================================="
echo ""

# 1. 기본 시스템 정보
echo "===== 1. 시스템 정보 ====="
echo "현재 시간: $(date)"
echo "서버 가동 시간: $(uptime)"
echo ""

# 2. 리소스 상태
echo "===== 2. 리소스 상태 ====="
echo ""
echo "--- 메모리 ---"
free -h
echo ""
echo "--- 디스크 ---"
df -h | grep -E "Filesystem|/dev/sda|/dev/vda"
echo ""
echo "--- CPU 로드 ---"
cat /proc/loadavg
echo ""

# 3. Docker 상태
echo "===== 3. Docker 상태 ====="
if command -v docker &> /dev/null; then
    echo "Docker 버전: $(docker --version)"
    echo ""
    echo "--- 실행 중인 컨테이너 ---"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
else
    echo "❌ Docker가 설치되지 않았습니다."
fi

# 4. UVIS 서비스 상태
echo "===== 4. UVIS 서비스 상태 ====="
if [ -d "/root/uvis" ]; then
    cd /root/uvis
    echo "--- Docker Compose 상태 ---"
    docker-compose ps
    echo ""
else
    echo "❌ /root/uvis 디렉토리를 찾을 수 없습니다."
fi

# 5. 서비스 헬스체크
echo "===== 5. 서비스 헬스체크 ====="
echo ""
echo "--- 백엔드 (포트 8000) ---"
if curl -s --max-time 5 http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 백엔드 정상"
    curl -s http://localhost:8000/health | head -5
else
    echo "❌ 백엔드 응답 없음"
fi
echo ""

echo "--- 프론트엔드 (포트 80) ---"
if curl -s --max-time 5 -I http://localhost/ > /dev/null 2>&1; then
    echo "✅ 프론트엔드 정상"
else
    echo "❌ 프론트엔드 응답 없음"
fi
echo ""

echo "--- 데이터베이스 ---"
if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ 데이터베이스 정상"
else
    echo "❌ 데이터베이스 응답 없음"
fi
echo ""

# 6. 최근 에러 로그
echo "===== 6. 최근 에러 로그 (최근 30줄) ====="
if [ -d "/root/uvis" ]; then
    cd /root/uvis
    docker-compose logs --tail=30 | grep -i "error\|exception\|fatal" || echo "에러 로그 없음"
else
    echo "로그를 확인할 수 없습니다."
fi
echo ""

# 7. 문제 진단
echo "===== 7. 문제 진단 ====="
echo ""

# 메모리 체크
MEM_AVAILABLE=$(free | grep Mem | awk '{print $7}')
MEM_TOTAL=$(free | grep Mem | awk '{print $2}')
MEM_PERCENT=$((100 - MEM_AVAILABLE * 100 / MEM_TOTAL))

if [ $MEM_PERCENT -gt 90 ]; then
    echo "⚠️  메모리 사용량 높음: ${MEM_PERCENT}%"
else
    echo "✅ 메모리 사용량 정상: ${MEM_PERCENT}%"
fi

# 디스크 체크
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️  디스크 사용량 높음: ${DISK_USAGE}%"
else
    echo "✅ 디스크 사용량 정상: ${DISK_USAGE}%"
fi

# CPU 로드 체크
LOAD_AVG=$(cat /proc/loadavg | awk '{print $1}')
echo "ℹ️  CPU 로드 평균 (1분): ${LOAD_AVG}"

echo ""
echo "=========================================="
echo "  점검 완료!"
echo "=========================================="
echo ""
echo "다음 명령어로 상세 로그를 확인하세요:"
echo "  cd /root/uvis && docker-compose logs --tail=100"
echo ""
echo "서비스를 재시작하려면:"
echo "  cd /root/uvis && docker-compose restart"
echo ""
