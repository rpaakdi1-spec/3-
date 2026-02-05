#!/bin/bash
# 서버 최종 수정 스크립트 - NotificationLevel 이슈 해결
# 위치: /root/uvis에서 실행

set -e

echo "🔧 Cold Chain - 최종 수정 시작"
echo "================================"
echo ""

cd /root/uvis

# 1. 최신 코드 가져오기
echo "📥 Step 1/5: 최신 코드 가져오기..."
git fetch origin genspark_ai_developer
git reset --hard origin/genspark_ai_developer
echo "✅ 최신 코드 적용 완료 (commit 33f1c87)"
echo ""

# 2. .env 파일 확인 및 수정
echo "📝 Step 2/5: .env 파일 확인..."

# SECRET_KEY 확인 및 생성
if ! grep -q "^SECRET_KEY=" .env || [ -z "$(grep "^SECRET_KEY=" .env | cut -d'=' -f2 | tr -d ' ')" ] || grep -q "^SECRET_KEY=your-secret-key-here" .env; then
    echo "🔑 SECRET_KEY 생성 중..."
    SECRET_KEY=$(openssl rand -hex 32)
    if grep -q "^SECRET_KEY=" .env; then
        sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
    else
        echo "SECRET_KEY=$SECRET_KEY" >> .env
    fi
    echo "   ✅ SECRET_KEY 생성 완료"
fi

# DB 관련 환경 변수 확인
if ! grep -q "^DB_NAME=" .env || [ -z "$(grep "^DB_NAME=" .env | cut -d'=' -f2 | tr -d ' ')" ]; then
    echo "DB_NAME=uvis_db" >> .env
fi

if ! grep -q "^DB_USER=" .env || [ -z "$(grep "^DB_USER=" .env | cut -d'=' -f2 | tr -d ' ')" ]; then
    echo "DB_USER=uvis_user" >> .env
fi

if ! grep -q "^DB_PASSWORD=" .env || [ -z "$(grep "^DB_PASSWORD=" .env | cut -d'=' -f2 | tr -d ' ')" ]; then
    echo "DB_PASSWORD=uvis_secure_password_2024" >> .env
fi

# DATABASE_URL 생성
DB_NAME=$(grep "^DB_NAME=" .env | cut -d'=' -f2 | tr -d ' ')
DB_USER=$(grep "^DB_USER=" .env | cut -d'=' -f2 | tr -d ' ')
DB_PASSWORD=$(grep "^DB_PASSWORD=" .env | cut -d'=' -f2 | tr -d ' ')
DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}"

if grep -q "^DATABASE_URL=" .env; then
    sed -i "s|^DATABASE_URL=.*|DATABASE_URL=$DATABASE_URL|" .env
else
    echo "DATABASE_URL=$DATABASE_URL" >> .env
fi

echo "✅ .env 파일 확인 완료"
echo "   DB_NAME=$DB_NAME"
echo "   DB_USER=$DB_USER"
echo "   DB_PASSWORD=****** (설정됨)"
echo "   SECRET_KEY=****** (설정됨)"
echo ""

# 3. docker-compose.yml에 env_file 추가 (백업 후)
echo "📋 Step 3/5: docker-compose.yml 수정..."
cp docker-compose.yml docker-compose.yml.backup_$(date +%Y%m%d_%H%M%S)

# Python 스크립트로 env_file 추가
cat > /tmp/fix_docker_compose.py << 'EOF'
import yaml
import sys

try:
    with open('docker-compose.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if 'services' in config and 'backend' in config['services']:
        backend = config['services']['backend']
        
        # env_file 추가 (없는 경우에만)
        if 'env_file' not in backend:
            backend['env_file'] = ['.env']
            print("✅ env_file 추가됨")
        else:
            print("✅ env_file 이미 존재함")
        
        with open('docker-compose.yml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        sys.exit(0)
    else:
        print("❌ backend 서비스를 찾을 수 없음")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ 오류: {e}")
    sys.exit(1)
EOF

python3 /tmp/fix_docker_compose.py
echo ""

# 4. Backend 재빌드 및 시작
echo "🏗️  Step 4/5: Backend 재빌드 및 시작..."
docker-compose build --no-cache backend
docker-compose up -d --force-recreate backend
echo "✅ Backend 재시작 완료"
echo ""

# 5. 안정화 대기 및 확인
echo "⏳ Step 5/5: Backend 안정화 대기 (90초)..."
sleep 90
echo ""

echo "================================"
echo "📊 최종 상태 확인"
echo "================================"
echo ""

echo "=== 컨테이너 상태 ==="
docker-compose ps backend
echo ""

echo "=== Backend 로그 (최근 50줄) ==="
docker-compose logs --tail=50 backend | tail -30
echo ""

echo "=== 헬스 체크 (3회 시도) ==="
HEALTH=""
for i in {1..3}; do
    echo "시도 $i/3..."
    HEALTH=$(curl -s http://localhost:8000/health)
    if [ -n "$HEALTH" ]; then
        echo "$HEALTH"
        break
    fi
    sleep 5
done
echo ""

if echo "$HEALTH" | grep -q "healthy"; then
    echo "🎉🎉🎉 성공! Backend가 정상 작동합니다! 🎉🎉🎉"
    echo ""
    echo "✅ 접속 URL:"
    echo "   - API 문서: http://YOUR_SERVER_IP:8000/docs"
    echo "   - Health: http://YOUR_SERVER_IP:8000/health"
    echo "   - Root: http://YOUR_SERVER_IP:8000/"
    echo ""
    echo "📖 API 문서 확인:"
    curl -s http://localhost:8000/docs | grep -o "<title>.*</title>" || echo "문서 로딩 중..."
    echo ""
    echo ""
    echo "🔄 다음 단계: Frontend 배포"
    echo "   Frontend도 배포하려면:"
    echo "   1. frontend/package.json 디렉토리에서: npm install"
    echo "   2. docker-compose build frontend"
    echo "   3. docker-compose up -d frontend nginx"
else
    echo "⚠️ 여전히 문제가 있습니다."
    echo ""
    echo "📋 전체 Backend 로그:"
    docker-compose logs backend | tail -50
    echo ""
    echo "🔍 디버깅 명령어:"
    echo "   - docker-compose logs backend"
    echo "   - docker exec uvis-backend env | grep SECRET_KEY"
    echo "   - docker exec uvis-backend cat /app/.env"
fi

echo ""
echo "================================"
echo "✅ 스크립트 완료"
echo "================================"
