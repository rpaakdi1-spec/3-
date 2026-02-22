#!/bin/bash
# 실시간 배차 최적화 페이지 성능 개선 - 빠른 배포 스크립트
# 작성일: 2026-02-22
# 프로젝트: UVIS 통합 배차 관리 시스템

set -e  # 에러 발생 시 중단

echo "=================================="
echo "🚀 UVIS 최적화 페이지 배포 시작"
echo "=================================="
echo ""

# 프로젝트 디렉토리로 이동
cd /root/uvis

# 1. Git 최신 코드 가져오기
echo "📥 1/5: Git 최신 코드 가져오는 중..."
git fetch origin
git pull origin main
echo "✅ Git pull 완료!"
echo ""

# 2. Frontend 재빌드
echo "🔨 2/5: Frontend 재빌드 중..."
cd /root/uvis/frontend

# 캐시 제거
rm -rf node_modules/.cache

# 빌드 실행
npm run build

# 빌드 결과 확인
if [ $? -eq 0 ]; then
    echo "✅ Frontend 빌드 성공!"
else
    echo "❌ Frontend 빌드 실패!"
    exit 1
fi
echo ""

# 3. Nginx 재시작
echo "🔄 3/5: Nginx 재시작 중..."
cd /root/uvis
docker-compose restart nginx

if [ $? -eq 0 ]; then
    echo "✅ Nginx 재시작 완료!"
else
    echo "❌ Nginx 재시작 실패!"
    exit 1
fi
echo ""

# 4. 백엔드 재시작 (선택사항 - Naver Map API 변경사항 적용)
echo "🔄 4/5: 백엔드 재시작 중..."
docker-compose restart backend
sleep 5  # 백엔드 시작 대기
echo "✅ 백엔드 재시작 완료!"
echo ""

# 5. 배포 확인
echo "🧪 5/5: 배포 상태 확인 중..."

# 컨테이너 상태 확인
echo ""
echo "=== Docker 컨테이너 상태 ==="
docker-compose ps

# 백엔드 로그 확인
echo ""
echo "=== 백엔드 최근 로그 (마지막 10줄) ==="
docker logs uvis-backend --tail 10

echo ""
echo "=================================="
echo "✅ 배포 완료!"
echo "=================================="
echo ""
echo "📍 테스트 URL:"
echo "   http://139.150.11.99/optimization"
echo ""
echo "🔍 확인 사항:"
echo "   1. 페이지 로딩 시간 < 1초"
echo "   2. 차량 목록 정상 표시"
echo "   3. Console 에러 없음 (F12 → Console)"
echo ""
echo "📊 성능 테스트 명령어:"
echo "   TOKEN=\$(curl -s -X POST \"http://localhost:8000/api/v1/auth/login\" \\"
echo "     -H \"Content-Type: application/x-www-form-urlencoded\" \\"
echo "     -d \"username=admin&password=admin123\" | jq -r '.access_token')"
echo ""
echo "   time curl -s \"http://localhost:8000/api/v1/vehicles/?include_gps=false&limit=10\" \\"
echo "     -H \"Authorization: Bearer \$TOKEN\" | jq '.items[0]'"
echo ""
echo "📝 자세한 내용: /root/uvis/OPTIMIZATION_PAGE_FIX.md"
echo ""
