# 서버-샌드박스 동기화 및 전체 오류 검사 가이드

## 🎯 목표
스테이징 서버(139.150.11.99)와 샌드박스 환경을 완전히 일치시켜 배포 전 모든 오류를 사전에 검사

---

## 📋 방법 1: 서버 상태를 샌드박스로 복제

### 1단계: 서버에서 전체 상태 수집

스테이징 서버에서 실행:

```bash
#!/bin/bash
# 서버 상태 수집 스크립트

cd /root/uvis

# 1. Git 상태
echo "=== Git 상태 ===" > /tmp/server_state.txt
git log --oneline -10 >> /tmp/server_state.txt
git status >> /tmp/server_state.txt
git branch -a >> /tmp/server_state.txt

# 2. 환경 변수 (.env 파일)
echo "" >> /tmp/server_state.txt
echo "=== 환경 변수 ===" >> /tmp/server_state.txt
cat .env >> /tmp/server_state.txt

# 3. Docker Compose 설정
echo "" >> /tmp/server_state.txt
echo "=== Docker Compose 설정 ===" >> /tmp/server_state.txt
cat docker-compose.yml >> /tmp/server_state.txt

# 4. 데이터베이스 스키마
echo "" >> /tmp/server_state.txt
echo "=== 데이터베이스 스키마 ===" >> /tmp/server_state.txt
docker-compose exec -T db pg_dump -U uvis_user -d uvis_db --schema-only > /tmp/db_schema.sql

# 5. Alembic 마이그레이션 상태
echo "" >> /tmp/server_state.txt
echo "=== Alembic 상태 ===" >> /tmp/server_state.txt
docker-compose run --rm backend alembic current >> /tmp/server_state.txt
docker-compose run --rm backend alembic history >> /tmp/server_state.txt

# 6. 패키지 버전
echo "" >> /tmp/server_state.txt
echo "=== Backend 패키지 ===" >> /tmp/server_state.txt
cat backend/requirements.txt >> /tmp/server_state.txt

echo "" >> /tmp/server_state.txt
echo "=== Frontend 패키지 ===" >> /tmp/server_state.txt
cat frontend/package.json >> /tmp/server_state.txt

# 7. Docker 이미지 및 컨테이너 상태
echo "" >> /tmp/server_state.txt
echo "=== Docker 상태 ===" >> /tmp/server_state.txt
docker-compose ps >> /tmp/server_state.txt
docker images | grep uvis >> /tmp/server_state.txt

# 8. 실행 중인 프로세스 및 포트
echo "" >> /tmp/server_state.txt
echo "=== 포트 상태 ===" >> /tmp/server_state.txt
netstat -tuln | grep -E "3000|8000|5432|6379" >> /tmp/server_state.txt

echo "서버 상태 수집 완료: /tmp/server_state.txt"
echo "데이터베이스 스키마: /tmp/db_schema.sql"
```

### 2단계: 서버 상태를 샌드박스로 전송

```bash
# 서버에서 파일 다운로드 (로컬 머신에서 실행)
scp root@139.150.11.99:/tmp/server_state.txt ./
scp root@139.150.11.99:/tmp/db_schema.sql ./
scp root@139.150.11.99:/root/uvis/.env ./server_env

# 또는 GitHub을 통해 전송 (서버에서)
cd /root/uvis
git add .env.example  # .env를 .env.example로 복사
git commit -m "chore: Add server environment template"
git push origin main
```

### 3단계: 샌드박스에서 서버 상태 재현

샌드박스에서 실행:

```bash
cd /home/user/webapp

# 1. 최신 코드 가져오기
git pull origin main

# 2. .env 파일 동기화 (서버에서 가져온 것 사용)
# 로컬에서 복사한 server_env를 사용
cp ~/server_env .env

# 3. Docker Compose로 전체 스택 실행
docker-compose down -v  # 볼륨 포함 전체 제거
docker-compose up -d --build

# 4. 데이터베이스 스키마 복원
docker-compose exec -T db psql -U uvis_user -d uvis_db < ~/db_schema.sql

# 5. Alembic 마이그레이션 동기화
cd backend
docker-compose run --rm backend alembic stamp heads
docker-compose run --rm backend alembic current
cd ..

# 6. 프론트엔드 의존성 동기화
cd frontend
npm install --legacy-peer-deps
npm run build
cd ..

# 7. 백엔드 의존성 동기화
cd backend
docker-compose exec backend pip install -r requirements.txt
cd ..
```

---

## 📋 방법 2: 샌드박스에서 전체 빌드 테스트

### 완전한 CI/CD 파이프라인 시뮬레이션

```bash
#!/bin/bash
# 샌드박스 전체 테스트 스크립트

set -e  # 에러 발생 시 중단

cd /home/user/webapp

echo "=========================================="
echo "Phase 10 전체 빌드 및 테스트 시작"
echo "=========================================="

# 1. 코드 정리
echo "1. 코드 정리 중..."
git clean -fd
git reset --hard HEAD
git pull origin main

# 2. 환경 변수 확인
echo "2. 환경 변수 확인 중..."
if [ ! -f .env ]; then
    echo "ERROR: .env 파일이 없습니다."
    exit 1
fi

if ! grep -q "DB_PASSWORD" .env; then
    echo "ERROR: DB_PASSWORD가 설정되지 않았습니다."
    exit 1
fi

export $(cat .env | grep -v '^#' | xargs)
echo "✓ 환경 변수 확인 완료"

# 3. Docker 전체 재빌드
echo "3. Docker 전체 재빌드 중..."
docker-compose down -v
docker-compose build --no-cache
echo "✓ Docker 빌드 완료"

# 4. 컨테이너 시작
echo "4. 컨테이너 시작 중..."
docker-compose up -d
sleep 30
echo "✓ 컨테이너 시작 완료"

# 5. 데이터베이스 마이그레이션
echo "5. 데이터베이스 마이그레이션 중..."
docker-compose exec -T backend alembic upgrade heads || \
docker-compose exec -T backend alembic stamp heads
echo "✓ 마이그레이션 완료"

# 6. 백엔드 헬스 체크
echo "6. 백엔드 헬스 체크 중..."
MAX_RETRY=30
RETRY=0
while [ $RETRY -lt $MAX_RETRY ]; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✓ 백엔드 헬스 체크 성공"
        break
    fi
    RETRY=$((RETRY+1))
    echo "  재시도 중... ($RETRY/$MAX_RETRY)"
    sleep 2
done

if [ $RETRY -eq $MAX_RETRY ]; then
    echo "ERROR: 백엔드 헬스 체크 실패"
    docker-compose logs backend --tail=50
    exit 1
fi

# 7. 프론트엔드 빌드 테스트
echo "7. 프론트엔드 빌드 테스트 중..."
cd frontend
npm install --legacy-peer-deps
npm run build
cd ..
echo "✓ 프론트엔드 빌드 완료"

# 8. TypeScript 컴파일 체크
echo "8. TypeScript 컴파일 체크 중..."
cd frontend
npx tsc --noEmit --skipLibCheck 2>&1 | tee /tmp/ts_errors.log
TS_ERRORS=$(cat /tmp/ts_errors.log | grep "error TS" | wc -l)
echo "TypeScript 에러 수: $TS_ERRORS"
cd ..

if [ $TS_ERRORS -gt 0 ]; then
    echo "WARNING: TypeScript 에러가 있습니다."
    cat /tmp/ts_errors.log | grep "error TS" | head -20
fi

# 9. API 엔드포인트 테스트
echo "9. API 엔드포인트 테스트 중..."

# 9-1. Health Check
echo "  9-1. Health Check..."
curl -s http://localhost:8000/health | jq . || echo "FAILED"

# 9-2. OpenAPI Docs
echo "  9-2. OpenAPI Docs..."
curl -s http://localhost:8000/docs > /dev/null && echo "✓ Swagger UI OK" || echo "FAILED"

# 9-3. Phase 10 API
echo "  9-3. Phase 10 Dispatch Rules API..."
curl -s http://localhost:8000/api/v1/dispatch-rules | jq . || echo "FAILED"

# 9-4. 기타 주요 API
echo "  9-4. Orders API..."
curl -s http://localhost:8000/api/v1/orders | jq . || echo "FAILED"

echo "  9-5. Vehicles API..."
curl -s http://localhost:8000/api/v1/vehicles | jq . || echo "FAILED"

# 10. 데이터베이스 테이블 확인
echo "10. 데이터베이스 테이블 확인 중..."
echo "  Phase 10 테이블:"
docker-compose exec -T db psql -U uvis_user -d uvis_db -c "\dt" | grep -E "dispatch_rules|rule_execution"
echo "✓ Phase 10 테이블 존재 확인"

# 11. 로그 수집
echo "11. 로그 수집 중..."
docker-compose logs backend --tail=100 > /tmp/backend.log
docker-compose logs frontend --tail=50 > /tmp/frontend.log
docker-compose logs db --tail=50 > /tmp/db.log
echo "✓ 로그 수집 완료"

# 12. 컨테이너 상태 확인
echo "12. 컨테이너 상태 확인 중..."
docker-compose ps
UNHEALTHY=$(docker-compose ps | grep -v "Up" | grep -v "NAME" | wc -l)

if [ $UNHEALTHY -gt 0 ]; then
    echo "WARNING: 일부 컨테이너가 정상 상태가 아닙니다."
    docker-compose ps
fi

# 13. 포트 확인
echo "13. 포트 확인 중..."
netstat -tuln | grep -E "3000|8000|5432|6379"
echo "✓ 포트 확인 완료"

# 14. 메모리 및 디스크 사용량
echo "14. 리소스 사용량 확인 중..."
docker stats --no-stream
df -h | grep -E "/$|/var"

# 15. 최종 리포트 생성
echo "=========================================="
echo "전체 테스트 완료!"
echo "=========================================="
echo ""
echo "리포트:"
echo "  - TypeScript 에러: $TS_ERRORS 개"
echo "  - 컨테이너 비정상: $UNHEALTHY 개"
echo "  - 로그 위치: /tmp/backend.log, /tmp/frontend.log, /tmp/db.log"
echo ""
echo "다음 단계:"
echo "  1. TypeScript 에러 확인: cat /tmp/ts_errors.log"
echo "  2. 백엔드 로그 확인: cat /tmp/backend.log"
echo "  3. 프론트엔드 로그 확인: cat /tmp/frontend.log"
echo "  4. Swagger UI 접속: http://localhost:8000/docs"
echo "  5. Frontend 접속: http://localhost:3000"
echo ""

if [ $TS_ERRORS -eq 0 ] && [ $UNHEALTHY -eq 0 ]; then
    echo "✅ 모든 테스트 통과! 서버 배포 준비 완료!"
    exit 0
else
    echo "⚠️  일부 이슈 발견. 로그를 확인하세요."
    exit 1
fi
```

---

## 📋 방법 3: 차이점 비교 스크립트

### 서버와 샌드박스 차이점 자동 비교

```bash
#!/bin/bash
# 서버-샌드박스 차이점 비교 스크립트

echo "=========================================="
echo "서버-샌드박스 차이점 분석"
echo "=========================================="

# 1. Git 커밋 비교
echo "1. Git 커밋 비교:"
echo "  샌드박스:"
git log --oneline -1
echo "  서버 (복사한 정보 기준):"
# 서버에서 가져온 정보와 비교

# 2. 의존성 버전 비교
echo ""
echo "2. Backend 의존성 비교:"
echo "  샌드박스:"
cat backend/requirements.txt | grep -E "fastapi|sqlalchemy|alembic" | head -5
echo "  서버:"
# 서버에서 가져온 requirements.txt와 비교

echo ""
echo "3. Frontend 의존성 비교:"
echo "  샌드박스:"
cat frontend/package.json | grep -E "@mui|react|vite" | head -10
echo "  서버:"
# 서버에서 가져온 package.json과 비교

# 4. 환경 변수 비교
echo ""
echo "4. 환경 변수 비교:"
echo "  샌드박스 .env 키:"
cat .env | grep -v '^#' | grep '=' | cut -d '=' -f 1 | sort
echo "  서버 .env 키:"
# 서버에서 가져온 .env와 비교

# 5. 데이터베이스 스키마 비교
echo ""
echo "5. 데이터베이스 테이블 비교:"
echo "  샌드박스:"
docker-compose exec -T db psql -U uvis_user -d uvis_db -c "\dt" | wc -l
echo "  서버:"
# 서버 테이블 수와 비교

# 6. Alembic 마이그레이션 비교
echo ""
echo "6. Alembic 마이그레이션 비교:"
echo "  샌드박스:"
docker-compose run --rm backend alembic current
echo "  서버:"
# 서버 마이그레이션 상태와 비교
```

---

## 📋 방법 4: 자동화된 통합 테스트

### pytest를 사용한 전체 API 테스트

```python
# tests/integration/test_phase10_integration.py

import pytest
import requests
import time

BASE_URL = "http://localhost:8000"

class TestPhase10Integration:
    """Phase 10 전체 통합 테스트"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """테스트 전 대기"""
        time.sleep(1)
    
    def test_health_check(self):
        """헬스 체크"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_openapi_docs(self):
        """OpenAPI 문서 접근"""
        response = requests.get(f"{BASE_URL}/docs")
        assert response.status_code == 200
    
    def test_dispatch_rules_list(self):
        """규칙 목록 조회"""
        response = requests.get(f"{BASE_URL}/api/v1/dispatch-rules")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_dispatch_rules_create(self):
        """규칙 생성"""
        rule_data = {
            "name": "Test Rule",
            "description": "Integration test rule",
            "rule_type": "assignment",
            "priority": 50,
            "conditions": {"field": "distance_km", "operator": "<=", "value": 5},
            "actions": [{"type": "assign_driver", "params": {"driver_id": 1}}]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/dispatch-rules",
            json=rule_data
        )
        assert response.status_code in [200, 201]
        
        # 생성된 규칙 확인
        rule_id = response.json()["id"]
        
        # 조회
        response = requests.get(f"{BASE_URL}/api/v1/dispatch-rules/{rule_id}")
        assert response.status_code == 200
        
        # 삭제
        response = requests.delete(f"{BASE_URL}/api/v1/dispatch-rules/{rule_id}")
        assert response.status_code == 200
    
    def test_database_tables_exist(self):
        """데이터베이스 테이블 존재 확인"""
        # Docker exec를 통해 확인
        import subprocess
        result = subprocess.run(
            ["docker-compose", "exec", "-T", "db", "psql", 
             "-U", "uvis_user", "-d", "uvis_db", 
             "-c", "\\dt"],
            capture_output=True,
            text=True
        )
        assert "dispatch_rules" in result.stdout
        assert "rule_execution_logs" in result.stdout
```

테스트 실행:

```bash
cd /home/user/webapp

# pytest 설치
pip install pytest requests

# 통합 테스트 실행
pytest tests/integration/test_phase10_integration.py -v

# 전체 테스트 실행
pytest tests/ -v --tb=short
```

---

## 📋 방법 5: Docker Compose를 사용한 격리 테스트

### 완전히 격리된 환경에서 테스트

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  db-test:
    image: postgres:15
    environment:
      POSTGRES_DB: uvis_test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - "5433:5432"
  
  redis-test:
    image: redis:7-alpine
    ports:
      - "6380:6379"
  
  backend-test:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DB_HOST: db-test
      DB_PORT: 5432
      DB_NAME: uvis_test_db
      DB_USER: test_user
      DB_PASSWORD: test_password
      REDIS_HOST: redis-test
    depends_on:
      - db-test
      - redis-test
    ports:
      - "8001:8000"
    command: >
      bash -c "
        alembic upgrade heads &&
        uvicorn main:app --host 0.0.0.0 --port 8000
      "
  
  frontend-test:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3001:80"
    depends_on:
      - backend-test
```

테스트 실행:

```bash
# 테스트 환경 시작
docker-compose -f docker-compose.test.yml up -d --build

# 테스트 실행
pytest tests/integration/ --base-url=http://localhost:8001

# 테스트 환경 종료
docker-compose -f docker-compose.test.yml down -v
```

---

## 🎯 권장 워크플로우

### 배포 전 전체 체크리스트

```bash
#!/bin/bash
# 배포 전 최종 체크리스트

echo "=========================================="
echo "Phase 10 배포 전 최종 체크리스트"
echo "=========================================="

ERRORS=0

# 1. Git 상태
echo "✓ Git 상태 확인"
git status | grep "nothing to commit" || ((ERRORS++))

# 2. 최신 코드
echo "✓ 최신 코드 확인"
git fetch origin main
git diff origin/main | wc -l | grep "^0$" || ((ERRORS++))

# 3. 환경 변수
echo "✓ 환경 변수 확인"
grep -q "DB_PASSWORD" .env || ((ERRORS++))

# 4. Docker 빌드
echo "✓ Docker 빌드 테스트"
docker-compose build || ((ERRORS++))

# 5. TypeScript 컴파일
echo "✓ TypeScript 컴파일 테스트"
cd frontend && npx tsc --noEmit --skipLibCheck && cd .. || ((ERRORS++))

# 6. Backend 테스트
echo "✓ Backend 테스트"
cd backend && pytest tests/ -v && cd .. || ((ERRORS++))

# 7. 마이그레이션 체크
echo "✓ 마이그레이션 체크"
docker-compose run --rm backend alembic check || ((ERRORS++))

# 8. API 엔드포인트 테스트
echo "✓ API 엔드포인트 테스트"
curl -s http://localhost:8000/health | grep "ok" || ((ERRORS++))

# 결과
echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ 모든 체크 통과! 배포 준비 완료!"
    exit 0
else
    echo "❌ $ERRORS 개의 에러 발견. 수정 후 재시도하세요."
    exit 1
fi
```

---

## 📝 요약

### 빠른 선택 가이드

| 방법 | 소요 시간 | 정확도 | 추천 상황 |
|------|----------|--------|----------|
| **방법 1: 서버 복제** | 30분 | ⭐⭐⭐⭐⭐ | 정확한 복제 필요 |
| **방법 2: 전체 빌드 테스트** | 10분 | ⭐⭐⭐⭐ | 빠른 검증 |
| **방법 3: 차이점 비교** | 5분 | ⭐⭐⭐ | 빠른 확인 |
| **방법 4: 통합 테스트** | 5분 | ⭐⭐⭐⭐ | 자동화 |
| **방법 5: 격리 테스트** | 15분 | ⭐⭐⭐⭐⭐ | 완전 격리 |

### 권장 조합

1. **일반 배포**: 방법 2 (전체 빌드 테스트)
2. **중요 배포**: 방법 2 + 방법 4 (빌드 + 통합 테스트)
3. **프로덕션 배포**: 방법 1 + 방법 4 + 방법 5 (완전 복제 + 테스트)

---

**작성**: 2026-02-08  
**버전**: 1.0  
**상태**: Production Ready
