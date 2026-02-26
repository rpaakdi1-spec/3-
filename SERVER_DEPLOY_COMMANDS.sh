#!/bin/bash
# 규칙 타입 수정 배포 스크립트

echo "=========================================="
echo "규칙 타입 수정 배포 시작"
echo "=========================================="

# 1. 최신 코드 받기
echo ""
echo "📥 1. Git에서 최신 코드 가져오기..."
cd /root/uvis
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer

echo ""
echo "✅ 최신 코드 받기 완료"
git log --oneline -3

# 2. 프론트엔드 빌드
echo ""
echo "🔨 2. 프론트엔드 빌드 시작..."
cd /root/uvis/frontend

# 백업 생성
echo "   📦 기존 빌드 백업 중..."
if [ -d "dist" ]; then
    tar -czf dist-backup-$(date +%Y%m%d_%H%M%S).tar.gz dist/
    echo "   ✅ 백업 완료: dist-backup-$(date +%Y%m%d_%H%M%S).tar.gz"
fi

# 새로 빌드
echo "   🔨 새 빌드 시작..."
rm -rf dist/
npm run build

echo ""
echo "✅ 빌드 완료"
echo ""
echo "📊 빌드 결과:"
ls -lh dist/assets/ | grep -E "(DispatchRulesPage|index\.js|index\.css)" | head -5

# 3. Docker 컨테이너 재시작
echo ""
echo "🔄 3. Docker 컨테이너 재시작..."
cd /root/uvis
docker-compose restart frontend

sleep 3

# 4. 배포 확인
echo ""
echo "🔍 4. 배포 상태 확인..."
docker-compose ps | grep frontend

echo ""
echo "📝 컨테이너 로그 (최근 20줄):"
docker-compose logs frontend --tail=20

# 5. 헬스 체크
echo ""
echo "🏥 5. 헬스 체크..."
sleep 2
curl -I http://localhost:80 2>&1 | head -5

echo ""
echo "=========================================="
echo "✅ 배포 완료!"
echo "=========================================="
echo ""
echo "📋 다음 단계:"
echo "1. 브라우저에서 http://139.150.11.99/dispatch-rules 접속"
echo "2. 브라우저 캐시 삭제:"
echo "   - Chrome/Edge: Ctrl+Shift+Delete → 전체 기간 → 삭제"
echo "   - 또는 시크릿 모드(Ctrl+Shift+N)에서 접속"
echo "3. 규칙 수정 버튼 클릭 → 규칙 타입 변경 테스트"
echo ""
echo "⚠️  브라우저 캐시를 삭제하지 않으면 변경사항이 보이지 않습니다!"
echo ""
