#!/bin/bash
# ===================================================================
# Redis 연결 디버그 스크립트
# 백엔드 컨테이너 내부에서 Redis 연결 테스트
# ===================================================================

echo "====================================================================="
echo "Redis 연결 디버그"
echo "====================================================================="
echo ""

cd /root/uvis

# 1. 환경 변수 확인
echo "=== 1. Docker Compose 환경 변수 ==="
docker-compose exec backend env | grep REDIS | sort
echo ""

# 2. Python 테스트 스크립트 생성
echo "=== 2. Redis 연결 테스트 스크립트 실행 ==="
docker-compose exec backend python3 << 'PYTHON_EOF'
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

print("=== Test 1: Connection without password ===")
try:
    r1 = Redis(host='redis', port=6379, decode_responses=False)
    result = r1.ping()
    print(f"PING result: {result}")
    print("✅ Success - No password needed!")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print()
print("=== Test 2: Connection with empty string password ===")
try:
    r2 = Redis(host='redis', port=6379, password='', decode_responses=False)
    result = r2.ping()
    print(f"PING result: {result}")
    print("✅ Success!")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print()
print("=== Test 3: Connection with None password ===")
try:
    r3 = Redis(host='redis', port=6379, password=None, decode_responses=False)
    result = r3.ping()
    print(f"PING result: {result}")
    print("✅ Success!")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print()
print("=== Test 4: Connection with REDIS_PASSWORD from env ===")
try:
    env_password = os.getenv('REDIS_PASSWORD', '')
    print(f"Using password from env: '{env_password}' (length: {len(env_password)})")
    
    if env_password:
        r4 = Redis(host='redis', port=6379, password=env_password, decode_responses=False)
    else:
        print("Password is empty, connecting without password...")
        r4 = Redis(host='redis', port=6379, decode_responses=False)
    
    result = r4.ping()
    print(f"PING result: {result}")
    print("✅ Success!")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print()
print("=== Test 5: Connection using REDIS_URL ===")
try:
    redis_url = os.getenv('REDIS_URL', '')
    if redis_url:
        print(f"REDIS_URL: {redis_url}")
        r5 = Redis.from_url(redis_url, decode_responses=False)
        result = r5.ping()
        print(f"PING result: {result}")
        print("✅ Success!")
    else:
        print("REDIS_URL not set")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
PYTHON_EOF

echo ""
echo "====================================================================="
echo "테스트 완료"
echo "====================================================================="
echo ""
echo "어떤 테스트가 성공했는지 확인하고 알려주세요!"
