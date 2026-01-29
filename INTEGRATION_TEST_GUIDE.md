# 🧪 완벽한 통합 테스트 가이드

**최종 업데이트:** 2026-01-28  
**목적:** 배포 후 전체 시스템 검증

---

## 📋 테스트 체크리스트

### ✅ Phase 1: Infrastructure 테스트

#### 1.1 Docker 컨테이너 상태
```bash
cd /root/uvis
docker-compose -f docker-compose.prod.yml ps
```

**기대 결과:**
```
NAME            STATUS
uvis-backend    Up (healthy)
uvis-db         Up (healthy)
uvis-frontend   Up (healthy)
uvis-nginx      Up (healthy)
uvis-redis      Up (healthy)
```

#### 1.2 네트워크 연결
```bash
# Backend → Database
docker exec uvis-backend pg_isready -h db -U uvis_user

# Backend → Redis
docker exec uvis-backend redis-cli -h redis ping

# Frontend → Backend (내부)
docker exec uvis-frontend curl -s http://backend:8000/health
```

#### 1.3 포트 리스닝
```bash
netstat -tlnp | grep -E ':(80|3000|5432|6379|8000)'
```

**기대 결과:**
```
tcp  0.0.0.0:80      LISTEN  (nginx)
tcp  0.0.0.0:3000    LISTEN  (frontend)
tcp  0.0.0.0:5432    LISTEN  (postgres)
tcp  0.0.0.0:6379    LISTEN  (redis)
tcp  0.0.0.0:8000    LISTEN  (backend)
```

---

### ✅ Phase 2: Backend API 테스트

#### 2.1 Health Check
```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

**기대 결과:**
```json
{
  "status": "healthy",
  "app_name": "Cold Chain Dispatch System",
  "environment": "production"
}
```

#### 2.2 API 문서 접근
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs
```

**기대 결과:** `200`

#### 2.3 인증 엔드포인트
```bash
# 로그인 테스트
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@example.com", "password": "admin123"}' | python3 -m json.tool
```

**기대 결과:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin@example.com",
    ...
  }
}
```

#### 2.4 주요 API 엔드포인트 체크
```bash
# 토큰 저장
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@example.com", "password": "admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 차량 목록 조회
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/vehicles | python3 -m json.tool | head -20

# 주문 목록 조회
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/orders | python3 -m json.tool | head -20

# 거래처 목록 조회
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/clients | python3 -m json.tool | head -20
```

---

### ✅ Phase 3: Frontend 테스트

#### 3.1 메인 페이지 접근
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

**기대 결과:** `200`

#### 3.2 정적 자원 로딩
```bash
# JavaScript 번들
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/assets/index-*.js

# CSS 번들
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/assets/index-*.css
```

**기대 결과:** 모두 `200`

#### 3.3 API Proxy 테스트
```bash
# Frontend nginx → Backend API
curl -s http://localhost:3000/api/v1/health | python3 -m json.tool
```

**기대 결과:** Backend health 응답과 동일

---

### ✅ Phase 4: Database 테스트

#### 4.1 데이터베이스 연결
```bash
docker exec uvis-db psql -U uvis_user -d uvis_db -c "\l"
```

#### 4.2 테이블 존재 확인
```bash
docker exec uvis-db psql -U uvis_user -d uvis_db -c "\dt"
```

**기대 결과:** 주요 테이블 목록
```
 public | users              | table
 public | clients            | table
 public | vehicles           | table
 public | orders             | table
 public | dispatches         | table
 ...
```

#### 4.3 샘플 데이터 확인
```bash
# 사용자 수
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT COUNT(*) FROM users;"

# 차량 수
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT COUNT(*) FROM vehicles;"
```

---

### ✅ Phase 5: Redis 캐시 테스트

#### 5.1 Redis 연결
```bash
docker exec uvis-redis redis-cli ping
```

**기대 결과:** `PONG`

#### 5.2 캐시 키 확인
```bash
docker exec uvis-redis redis-cli keys "*"
```

---

### ✅ Phase 6: 외부 접근 테스트

#### 6.1 웹 브라우저 테스트

다음 URL을 브라우저에서 접속:

| URL | 설명 | 기대 결과 |
|-----|------|----------|
| `http://139.150.11.99` | Frontend 메인 | 로그인 페이지 |
| `http://139.150.11.99:3000` | Frontend 직접 | 로그인 페이지 |
| `http://139.150.11.99:8000/docs` | API 문서 | Swagger UI |
| `http://139.150.11.99:8000/health` | Health Check | JSON 응답 |

#### 6.2 외부 API 테스트 (curl)
```bash
# 로컬에서 실행 (서버 외부)
curl -s http://139.150.11.99:8000/health | python3 -m json.tool
```

---

### ✅ Phase 7: 기능 테스트 (브라우저)

#### 7.1 로그인
- [ ] 관리자 계정으로 로그인
- [ ] 드라이버 계정으로 로그인
- [ ] 잘못된 자격증명 거부 확인

#### 7.2 대시보드
- [ ] 대시보드 로딩
- [ ] 통계 정보 표시
- [ ] 차트 렌더링

#### 7.3 차량 관리
- [ ] 차량 목록 조회
- [ ] 차량 상세 조회
- [ ] 차량 추가 (관리자만)
- [ ] 차량 수정
- [ ] 차량 삭제

#### 7.4 주문 관리
- [ ] 주문 목록 조회
- [ ] 주문 생성
- [ ] 주문 상세 조회
- [ ] 주문 수정
- [ ] 주문 삭제

#### 7.5 배차 관리
- [ ] 배차 목록 조회
- [ ] 배차 생성
- [ ] 배차 최적화
- [ ] 경로 표시 (지도)
- [ ] 배차 완료 처리

#### 7.6 실시간 모니터링
- [ ] 차량 위치 실시간 표시
- [ ] WebSocket 연결 확인
- [ ] 지도 상 차량 아이콘 표시
- [ ] 차량 정보 툴팁

#### 7.7 UVIS GPS 연동
- [ ] GPS 데이터 조회
- [ ] 실시간 위치 업데이트
- [ ] 차량 매칭 확인

---

### ✅ Phase 8: 성능 테스트

#### 8.1 응답 시간 측정
```bash
# Health endpoint
time curl -s http://localhost:8000/health > /dev/null

# API endpoint (authenticated)
time curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/vehicles > /dev/null
```

**기대 결과:** < 200ms

#### 8.2 동시 접속 테스트
```bash
# 간단한 부하 테스트 (ab 사용)
ab -n 100 -c 10 http://localhost:8000/health
```

---

### ✅ Phase 9: 보안 테스트

#### 9.1 인증 없이 API 접근 시도
```bash
curl -s -o /dev/null -w "%{http_code}" \
  http://localhost:8000/api/v1/vehicles
```

**기대 결과:** `401 Unauthorized`

#### 9.2 CORS 헤더 확인
```bash
curl -I http://localhost:8000/health
```

**기대 결과:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

#### 9.3 보안 헤더 확인
```bash
curl -I http://localhost:3000
```

**기대 결과:**
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

---

### ✅ Phase 10: 로그 및 모니터링

#### 10.1 Backend 로그 확인
```bash
docker-compose -f docker-compose.prod.yml logs --tail=50 backend
```

**기대 결과:** 에러 없음, 정상 로그만 표시

#### 10.2 Frontend 로그 확인
```bash
docker-compose -f docker-compose.prod.yml logs --tail=20 frontend
```

#### 10.3 Database 로그 확인
```bash
docker-compose -f docker-compose.prod.yml logs --tail=20 db
```

#### 10.4 디스크 사용량 확인
```bash
df -h | grep -E 'Filesystem|/dev/(sda|vda)'
docker system df
```

#### 10.5 메모리 사용량 확인
```bash
free -h
docker stats --no-stream
```

---

## 🚨 문제 발생 시 대응

### Backend가 unhealthy인 경우
```bash
# 1. 로그 확인
docker-compose -f docker-compose.prod.yml logs --tail=100 backend

# 2. 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 3. 환경변수 확인
docker exec uvis-backend env | grep -E 'DATABASE_URL|REDIS_URL|NAVER_MAP'
```

### Frontend가 로드되지 않는 경우
```bash
# 1. Nginx 설정 확인
docker exec uvis-frontend nginx -t

# 2. 로그 확인
docker-compose -f docker-compose.prod.yml logs --tail=50 frontend

# 3. 빌드 아티팩트 확인
docker exec uvis-frontend ls -la /usr/share/nginx/html
```

### Database 연결 실패
```bash
# 1. PostgreSQL 상태 확인
docker exec uvis-db pg_isready -U uvis_user

# 2. 연결 테스트
docker exec uvis-backend psql -h db -U uvis_user -d uvis_db -c "SELECT 1;"

# 3. 로그 확인
docker-compose -f docker-compose.prod.yml logs --tail=50 db
```

---

## 📊 테스트 결과 보고서 템플릿

```
==============================================
Cold Chain Dispatch System - 통합 테스트 결과
==============================================

테스트 일시: $(date)
배포 커밋: $(git log -1 --oneline)

[ ] Phase 1: Infrastructure ✅
[ ] Phase 2: Backend API ✅
[ ] Phase 3: Frontend ✅
[ ] Phase 4: Database ✅
[ ] Phase 5: Redis Cache ✅
[ ] Phase 6: 외부 접근 ✅
[ ] Phase 7: 기능 테스트 ✅
[ ] Phase 8: 성능 테스트 ✅
[ ] Phase 9: 보안 테스트 ✅
[ ] Phase 10: 로그 및 모니터링 ✅

총 테스트 항목: 60개
통과: __개
실패: __개

주요 이슈:
- 

권장 사항:
- 

==============================================
```

---

## 🎯 테스트 자동화 스크립트

모든 테스트를 한 번에 실행하려면:

```bash
#!/bin/bash
# test-all.sh

cd /root/uvis

echo "=== Phase 1: Infrastructure ==="
docker-compose -f docker-compose.prod.yml ps

echo "=== Phase 2: Backend Health ==="
curl -s http://localhost:8000/health | python3 -m json.tool

echo "=== Phase 3: Frontend ==="
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000

echo "=== Phase 4: Database ==="
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT COUNT(*) FROM users;"

echo "=== Phase 5: Redis ==="
docker exec uvis-redis redis-cli ping

echo "All tests completed!"
```

**성공을 기원합니다! 🚀**
