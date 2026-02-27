#!/bin/bash
# ===================================================================
# Redis 연결 디버그 스크립트 (수정버전)
# ===================================================================

echo "====================================================================="
echo "Redis 연결 디버그"
echo "====================================================================="
echo ""

cd /root/uvis

# 1. .env 파일에서 Redis 설정 확인
echo "=== 1. .env 파일의 Redis 설정 ==="
grep REDIS .env 2>/dev/null || echo ".env 파일에 REDIS 설정 없음"
echo ""

# 2. docker-compose.yml에서 Redis 설정 확인
echo "=== 2. docker-compose.yml의 backend 환경 변수 ==="
grep -A 2 "REDIS" docker-compose.yml | head -20
echo ""

# 3. 백엔드 컨테이너 환경 변수 확인
echo "=== 3. 백엔드 컨테이너 실제 환경 변수 ==="
docker-compose exec -T backend env | grep REDIS | sort
echo ""

# 4. Redis 컨테이너 설정 확인
echo "=== 4. Redis 컨테이너 시작 명령어 ==="
docker-compose ps redis --format json | jq -r '.[0].Command' 2>/dev/null || docker-compose ps redis
echo ""

# 5. Python 테스트 (heredoc 대신 파일 사용)
echo "=== 5. Redis 연결 테스트 ==="
cat > /tmp/test_redis.py << 'PYEOF'
import os
from redis import Redis

print("=== Environment Variables ===")
redis_host = os.getenv('REDIS_HOST', 'NOT SET')
redis_port = os.getenv('REDIS_PORT', 'NOT SET')
redis_password = os.getenv('REDIS_PASSWORD', 'NOT SET')
redis_url = os.getenv('REDIS_URL', 'NOT SET')

print(f"REDIS_HOST: {redis_host}")
print(f"REDIS_PORT: {redis_port}")
print(f"REDIS_PASSWORD: '{redis_password}' (length: {len(redis_password) if redis_password != 'NOT SET' else 0})")
print(f"REDIS_URL: {redis_url}")
print()

# Test 1: Without password
print("=== Test 1: Connection without password ===")
try:
    r1 = Redis(host='redis', port=6379, decode_responses=False)
    result = r1.ping()
    print(f"✅ Success! PING result: {result}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print()

# Test 2: With password from env
print("=== Test 2: Connection with REDIS_PASSWORD from env ===")
try:
    env_password = os.getenv('REDIS_PASSWORD', '')
    print(f"Password from env: '{env_password}' (length: {len(env_password)})")
    
    if env_password and env_password != 'NOT SET':
        r2 = Redis(host='redis', port=6379, password=env_password, decode_responses=False)
        result = r2.ping()
        print(f"✅ Success! PING result: {result}")
    else:
        print("⚠️ No password in environment, trying without password...")
        r2 = Redis(host='redis', port=6379, decode_responses=False)
        result = r2.ping()
        print(f"✅ Success! PING result: {result}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print()

# Test 3: Using REDIS_URL
print("=== Test 3: Connection using REDIS_URL ===")
try:
    redis_url = os.getenv('REDIS_URL', '')
    print(f"REDIS_URL: {redis_url}")
    
    if redis_url and redis_url != 'NOT SET' and not '{' in redis_url:
        r3 = Redis.from_url(redis_url, decode_responses=False)
        result = r3.ping()
        print(f"✅ Success! PING result: {result}")
    else:
        print("⚠️ REDIS_URL contains template variables or not set")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
PYEOF

docker cp /tmp/test_redis.py uvis-backend:/tmp/test_redis.py
docker-compose exec -T backend python3 /tmp/test_redis.py
echo ""

# 6. 직접 Redis CLI 테스트
echo "=== 6. Redis CLI 직접 테스트 ==="
echo "A. 비밀번호 없이:"
docker-compose exec -T redis redis-cli ping 2>&1 | head -3

echo ""
echo "B. .env의 비밀번호 사용:"
REDIS_PW=$(grep "REDIS_PASSWORD=" .env 2>/dev/null | cut -d'=' -f2)
if [ ! -z "$REDIS_PW" ]; then
    echo "비밀번호: $REDIS_PW"
    docker-compose exec -T redis redis-cli -a "$REDIS_PW" ping 2>&1 | grep -v "Warning"
else
    echo ".env에 REDIS_PASSWORD 없음"
fi

echo ""
echo "====================================================================="
echo "디버그 완료"
echo "====================================================================="
