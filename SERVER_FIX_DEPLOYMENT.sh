#!/bin/bash
# 서버 배포 완전 수정 스크립트
# 위치: /root/uvis

set -e  # 에러 발생 시 중단

echo "🔧 Cold Chain Dispatch System - 배포 수정 시작"
echo "=============================================="
echo ""

# 1. 기존 컨테이너 완전 정리
echo "📦 Step 1/7: 기존 컨테이너 정리..."
docker-compose down 2>/dev/null || true
docker rm -f coldchain-backend coldchain-postgres coldchain-nginx uvis-backend uvis-frontend uvis-nginx 2>/dev/null || true
echo "✅ 기존 컨테이너 정리 완료"
echo ""

# 2. .env 파일 검증 및 수정
echo "📝 Step 2/7: .env 파일 검증..."

if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example에서 복사합니다..."
    cp .env.example .env
fi

# SECRET_KEY 확인
if ! grep -q "^SECRET_KEY=" .env || [ -z "$(grep "^SECRET_KEY=" .env | cut -d'=' -f2)" ]; then
    echo "🔑 SECRET_KEY 생성 중..."
    SECRET_KEY=$(openssl rand -hex 32)
    if grep -q "^SECRET_KEY=" .env; then
        sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
    else
        echo "SECRET_KEY=$SECRET_KEY" >> .env
    fi
fi

# DB_PASSWORD 확인
if ! grep -q "^DB_PASSWORD=" .env || [ -z "$(grep "^DB_PASSWORD=" .env | cut -d'=' -f2)" ]; then
    echo "🔐 DB_PASSWORD 설정 중..."
    DB_PASSWORD="uvis_secure_password_2024"
    if grep -q "^DB_PASSWORD=" .env; then
        sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=$DB_PASSWORD|" .env
    else
        echo "DB_PASSWORD=$DB_PASSWORD" >> .env
    fi
fi

# DATABASE_URL 확인
if ! grep -q "^DATABASE_URL=" .env || [ -z "$(grep "^DATABASE_URL=" .env | cut -d'=' -f2)" ]; then
    echo "🗄️  DATABASE_URL 설정 중..."
    DB_NAME=$(grep "^DB_NAME=" .env | cut -d'=' -f2 || echo "uvis_db")
    DB_USER=$(grep "^DB_USER=" .env | cut -d'=' -f2 || echo "uvis_user")
    DB_PASSWORD=$(grep "^DB_PASSWORD=" .env | cut -d'=' -f2)
    DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}"
    
    if grep -q "^DATABASE_URL=" .env; then
        sed -i "s|^DATABASE_URL=.*|DATABASE_URL=$DATABASE_URL|" .env
    else
        echo "DATABASE_URL=$DATABASE_URL" >> .env
    fi
fi

# NAVER_MAP API 키 확인 (필수)
if ! grep -q "^NAVER_MAP_CLIENT_ID=" .env || [ -z "$(grep "^NAVER_MAP_CLIENT_ID=" .env | cut -d'=' -f2)" ]; then
    echo "⚠️  NAVER_MAP_CLIENT_ID가 설정되지 않았습니다."
    echo "   - 네이버 클라우드 플랫폼에서 발급받으세요: https://console.ncloud.com/"
    echo "   - 임시로 플레이스홀더를 설정합니다."
    if grep -q "^NAVER_MAP_CLIENT_ID=" .env; then
        sed -i "s|^NAVER_MAP_CLIENT_ID=.*|NAVER_MAP_CLIENT_ID=your_naver_client_id_here|" .env
    else
        echo "NAVER_MAP_CLIENT_ID=your_naver_client_id_here" >> .env
    fi
fi

if ! grep -q "^NAVER_MAP_CLIENT_SECRET=" .env || [ -z "$(grep "^NAVER_MAP_CLIENT_SECRET=" .env | cut -d'=' -f2)" ]; then
    if grep -q "^NAVER_MAP_CLIENT_SECRET=" .env; then
        sed -i "s|^NAVER_MAP_CLIENT_SECRET=.*|NAVER_MAP_CLIENT_SECRET=your_naver_client_secret_here|" .env
    else
        echo "NAVER_MAP_CLIENT_SECRET=your_naver_client_secret_here" >> .env
    fi
fi

echo "✅ .env 파일 검증 완료"
echo ""

# 3. 환경 변수 확인 (마스킹)
echo "🔍 Step 3/7: 환경 변수 확인..."
echo "   DB_NAME=$(grep "^DB_NAME=" .env | cut -d'=' -f2)"
echo "   DB_USER=$(grep "^DB_USER=" .env | cut -d'=' -f2)"
echo "   DB_PASSWORD=****** (설정됨)"
echo "   SECRET_KEY=****** (설정됨)"
echo "   DATABASE_URL=****** (설정됨)"
echo ""

# 4. Docker 이미지 빌드
echo "🏗️  Step 4/7: Docker 이미지 빌드..."
docker-compose build --no-cache backend frontend
echo "✅ Docker 이미지 빌드 완료"
echo ""

# 5. 서비스 시작
echo "🚀 Step 5/7: 서비스 시작..."
docker-compose up -d
echo "✅ 서비스 시작 완료"
echo ""

# 6. 서비스 안정화 대기
echo "⏳ Step 6/7: 서비스 안정화 대기 (60초)..."
sleep 60
echo ""

# 7. 상태 확인
echo "📊 Step 7/7: 서비스 상태 확인..."
echo ""
echo "=== Docker 컨테이너 상태 ==="
docker-compose ps
echo ""

echo "=== 백엔드 로그 (최근 30줄) ==="
docker-compose logs --tail=30 backend
echo ""

echo "=== 프론트엔드 로그 (최근 10줄) ==="
docker-compose logs --tail=10 frontend
echo ""

echo "=== Nginx 로그 (최근 10줄) ==="
docker-compose logs --tail=10 nginx
echo ""

echo "=== 헬스체크 ==="
echo "Backend Health:"
curl -s http://localhost:8000/health || echo "❌ Backend health check failed"
echo ""
echo ""

echo "Frontend (via Nginx):"
curl -s -I http://localhost/ | head -5 || echo "❌ Frontend access failed"
echo ""

echo "=== 포트 리스닝 확인 ==="
netstat -tuln | grep -E ":(80|8000|5173|5432|6379) " || echo "포트 확인 실패"
echo ""

echo "=============================================="
echo "🎉 배포 수정 스크립트 완료!"
echo ""
echo "✅ 다음 단계:"
echo "   1. 위의 헬스체크 결과를 확인하세요"
echo "   2. 브라우저에서 http://YOUR_SERVER_IP 접속"
echo "   3. 로그인 후 'IoT 센서 모니터링' 메뉴 확인"
echo ""
echo "⚠️  문제가 지속되면:"
echo "   - docker-compose logs backend"
echo "   - docker-compose logs nginx"
echo "   - docker-compose logs frontend"
echo "   위 명령어로 상세 로그를 확인하세요"
echo "=============================================="
