# 관리자 가이드 - Cold Chain Dispatch System

시스템 관리자를 위한 종합 관리 가이드입니다.

## 📋 목차

1. [시스템 관리](#시스템-관리)
2. [사용자 관리](#사용자-관리)
3. [데이터 관리](#데이터-관리)
4. [모니터링](#모니터링)
5. [백업 및 복구](#백업-및-복구)
6. [트러블슈팅](#트러블슈팅)

---

## 🔧 시스템 관리

### 시스템 설정

#### 기본 설정
```bash
# 환경 변수 설정 (.env 파일)
APP_ENV=production
APP_NAME="Cold Chain Dispatch System"
SECRET_KEY=your-secret-key-min-32-characters
```

#### API 설정
```bash
# Naver Map API
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret

# Kakao Map API
KAKAO_REST_API_KEY=your-kakao-rest-api-key

# Samsung UVIS API
UVIS_API_URL=https://api.s1.co.kr/uvis
UVIS_USERNAME=your-uvis-username
UVIS_PASSWORD=your-uvis-password
```

#### 모니터링 설정
```bash
# Sentry (에러 트래킹)
SENTRY_DSN=your-sentry-dsn

# Email 알림
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@your-domain.com

# Slack 웹훅
SLACK_WEBHOOK_URL=your-slack-webhook-url
```

### 시스템 시작/중지

```bash
# 시스템 시작
./deploy.sh start

# 시스템 중지
./deploy.sh stop

# 시스템 재시작
./deploy.sh restart

# 시스템 상태 확인
./deploy.sh status
```

### 로그 관리

```bash
# 전체 로그 확인
./deploy.sh logs

# 특정 서비스 로그
./deploy.sh logs backend
./deploy.sh logs postgres
./deploy.sh logs redis

# 실시간 로그 모니터링
docker-compose -f docker-compose.prod.yml logs -f backend

# 로그 파일 위치
- Backend: ./backend/logs/app.log
- Nginx: ./nginx_logs/access.log, ./nginx_logs/error.log
```

---

## 👥 사용자 관리

### 사용자 등록

#### 관리자 계정 생성
```python
# Python 스크립트로 관리자 생성
from backend.app.models.user import User, UserRole
from backend.app.core.security import get_password_hash
from backend.app.core.database import SessionLocal

db = SessionLocal()

admin_user = User(
    username="admin",
    email="admin@your-domain.com",
    hashed_password=get_password_hash("secure-password"),
    role=UserRole.ADMIN,
    is_active=True
)

db.add(admin_user)
db.commit()
```

#### API를 통한 사용자 생성
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_user",
    "email": "user@example.com",
    "password": "secure-password",
    "role": "dispatcher"
  }'
```

### 사용자 역할 관리

| 역할 | 권한 |
|------|------|
| **ADMIN** | 시스템 전체 관리, 사용자 관리, 설정 변경 |
| **DISPATCHER** | 주문/배차 관리, 차량/기사 관리 |
| **DRIVER** | 배차 확인, 배송 상태 업데이트 |
| **CLIENT** | 주문 조회, 배송 추적 |

### 사용자 계정 관리

```bash
# 사용자 목록 조회
curl -X GET "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 사용자 비활성화
curl -X PATCH "http://localhost:8000/api/v1/users/{user_id}" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'

# 비밀번호 재설정
curl -X POST "http://localhost:8000/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

---

## 💾 데이터 관리

### 데이터베이스 관리

#### 데이터베이스 연결 확인
```bash
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U coldchain -d coldchain_dispatch -c "SELECT version();"
```

#### 데이터베이스 백업
```bash
# 자동 백업 (deploy.sh 사용)
./deploy.sh backup

# 수동 백업
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U coldchain coldchain_dispatch > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### 데이터베이스 복구
```bash
# 백업 파일에서 복구
docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U coldchain coldchain_dispatch < backup_20260127_120000.sql
```

#### 데이터베이스 마이그레이션
```bash
# 현재 마이그레이션 버전 확인
docker-compose -f docker-compose.prod.yml exec backend \
  alembic current

# 최신 버전으로 업그레이드
docker-compose -f docker-compose.prod.yml exec backend \
  alembic upgrade head

# 특정 버전으로 다운그레이드
docker-compose -f docker-compose.prod.yml exec backend \
  alembic downgrade -1
```

#### 데이터베이스 최적화
```bash
# VACUUM 실행 (성능 최적화)
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U coldchain coldchain_dispatch -c "VACUUM ANALYZE;"

# 인덱스 사용률 확인
docker-compose -f docker-compose.prod.yml exec backend \
  python scripts/db_analyzer.py
```

### Redis 캐시 관리

#### Redis 연결 확인
```bash
docker-compose -f docker-compose.prod.yml exec redis \
  redis-cli -a your-redis-password ping
```

#### 캐시 통계 확인
```bash
curl http://localhost:8000/api/v1/cache/stats
```

#### 캐시 초기화
```bash
# 전체 캐시 삭제
curl -X DELETE http://localhost:8000/api/v1/cache/clear

# 패턴별 캐시 삭제
curl -X DELETE "http://localhost:8000/api/v1/cache/pattern/orders:*"
```

### 데이터 정리

#### 오래된 로그 삭제
```bash
# 30일 이상 된 로그 파일 삭제
find ./backend/logs -name "*.log" -mtime +30 -delete
find ./nginx_logs -name "*.log" -mtime +30 -delete
```

#### 오래된 배차 데이터 아카이브
```sql
-- 6개월 이상 된 완료 배차 아카이브
INSERT INTO dispatches_archive
SELECT * FROM dispatches
WHERE status = 'COMPLETED'
AND completed_at < NOW() - INTERVAL '6 months';

DELETE FROM dispatches
WHERE status = 'COMPLETED'
AND completed_at < NOW() - INTERVAL '6 months';
```

---

## 📊 모니터링

### 시스템 헬스체크

```bash
# 기본 헬스체크
curl http://localhost:8000/health

# 종합 헬스체크
curl http://localhost:8000/api/v1/monitoring/health

# 시스템 메트릭
curl http://localhost:8000/api/v1/monitoring/metrics
```

### 성능 모니터링

```bash
# 컨테이너 리소스 사용량
docker stats

# CPU 사용률
docker stats --no-stream | awk '{print $1, $3}'

# 메모리 사용률
docker stats --no-stream | awk '{print $1, $4}'

# 디스크 사용량
docker system df
```

### API 모니터링

```bash
# 활성 배차 수
curl http://localhost:8000/api/v1/monitoring/metrics | jq '.active_dispatches'

# 대기 중인 주문 수
curl http://localhost:8000/api/v1/monitoring/metrics | jq '.pending_orders'

# 가용 차량 수
curl http://localhost:8000/api/v1/monitoring/metrics | jq '.available_vehicles'
```

### 에러 모니터링

```bash
# Sentry 대시보드 확인
# https://sentry.io/organizations/your-org/issues/

# 최근 에러 로그 확인
tail -n 100 ./backend/logs/app.log | grep ERROR

# 에러 알림 테스트
curl -X POST "http://localhost:8000/api/v1/monitoring/test/alert" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "error",
    "title": "테스트 에러",
    "message": "에러 알림 시스템 테스트"
  }'
```

### 대시보드

```bash
# 종합 대시보드 데이터
curl http://localhost:8000/api/v1/monitoring/dashboard

# Grafana (옵션)
# http://localhost:3000

# Prometheus (옵션)
# http://localhost:9090
```

---

## 🔄 백업 및 복구

### 정기 백업 설정

#### Cron 설정
```bash
# crontab 편집
crontab -e

# 매일 새벽 2시에 백업
0 2 * * * cd /path/to/webapp && ./deploy.sh backup

# 매주 일요일 새벽 3시에 전체 백업
0 3 * * 0 cd /path/to/webapp && tar -czf /backups/full_backup_$(date +\%Y\%m\%d).tar.gz .
```

### 백업 전략

1. **일일 백업**: 데이터베이스 + Redis
2. **주간 백업**: 전체 시스템 (코드 + 데이터 + 설정)
3. **월간 백업**: 장기 보관용 아카이브

### 복구 절차

#### 데이터베이스 복구
```bash
# 1. 서비스 중지
./deploy.sh stop

# 2. 백업 파일 복구
docker-compose -f docker-compose.prod.yml up -d postgres
docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U coldchain coldchain_dispatch < backup_file.sql

# 3. 서비스 재시작
./deploy.sh start
```

#### 전체 시스템 복구
```bash
# 1. 백업 압축 해제
tar -xzf full_backup_20260127.tar.gz -C /restore/path

# 2. 설정 파일 복구
cp /restore/path/.env .env

# 3. 데이터 볼륨 복구
docker volume create --name postgres_data
docker run --rm -v postgres_data:/data -v /restore/path/postgres_data:/backup \
  alpine sh -c "cp -a /backup/* /data/"

# 4. 시스템 시작
./deploy.sh start
```

---

## 🔧 트러블슈팅

### 일반적인 문제

#### 서비스가 시작되지 않음
```bash
# 1. 로그 확인
./deploy.sh logs backend

# 2. 환경 변수 확인
docker-compose -f docker-compose.prod.yml exec backend env

# 3. 포트 충돌 확인
sudo netstat -tulpn | grep 8000

# 4. 디스크 공간 확인
df -h
```

#### 데이터베이스 연결 실패
```bash
# 1. PostgreSQL 상태 확인
docker-compose -f docker-compose.prod.yml ps postgres

# 2. PostgreSQL 로그 확인
docker-compose -f docker-compose.prod.yml logs postgres

# 3. 연결 테스트
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U coldchain -d coldchain_dispatch -c "SELECT 1;"
```

#### Redis 연결 실패
```bash
# 1. Redis 상태 확인
docker-compose -f docker-compose.prod.yml ps redis

# 2. Redis 로그 확인
docker-compose -f docker-compose.prod.yml logs redis

# 3. 연결 테스트
docker-compose -f docker-compose.prod.yml exec redis \
  redis-cli -a your-redis-password ping
```

#### 높은 메모리 사용량
```bash
# 1. 메모리 사용량 확인
docker stats --no-stream

# 2. Redis 메모리 정리
docker-compose -f docker-compose.prod.yml exec redis \
  redis-cli -a your-redis-password FLUSHDB

# 3. PostgreSQL 캐시 정리
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U coldchain coldchain_dispatch -c "DISCARD ALL;"

# 4. 컨테이너 재시작
./deploy.sh restart
```

### 긴급 상황 대응

#### 시스템 전체 다운
```bash
# 1. 즉시 상태 확인
./deploy.sh status

# 2. 로그 수집
./deploy.sh logs > emergency_logs_$(date +%Y%m%d_%H%M%S).txt

# 3. 빠른 재시작
./deploy.sh restart

# 4. 헬스체크 확인
curl http://localhost:8000/health
```

#### 데이터 손실 감지
```bash
# 1. 최신 백업 확인
ls -lh backups/ | tail -n 5

# 2. 데이터베이스 일관성 확인
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U coldchain coldchain_dispatch -c "SELECT pg_database_size('coldchain_dispatch');"

# 3. 백업에서 복구
./deploy.sh stop
# 복구 절차 수행...
./deploy.sh start
```

---

## 📞 지원 연락처

### 내부 지원팀
- **시스템 관리자**: admin@your-domain.com
- **기술 지원**: tech-support@your-domain.com
- **긴급 연락**: 010-XXXX-XXXX

### 외부 지원
- **Naver Map API**: https://console.ncloud.com/support
- **Samsung UVIS**: support@s1.co.kr
- **Sentry**: https://sentry.io/support/

---

## 📚 관련 문서

- [사용자 매뉴얼](./USER_MANUAL.md)
- [프로덕션 배포 가이드](./PRODUCTION_DEPLOYMENT_GUIDE.md)
- [API 문서](http://localhost:8000/docs)
- [보안 가이드](./SECURITY_GUIDE.md)
- [캐싱 전략 가이드](./CACHING_STRATEGY_GUIDE.md)
- [데이터베이스 최적화 가이드](./DATABASE_OPTIMIZATION_GUIDE.md)

---

**버전**: 1.0.0  
**최종 업데이트**: 2026-01-27  
**작성자**: GenSpark AI Developer
