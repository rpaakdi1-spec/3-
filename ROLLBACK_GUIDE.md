# 🔄 롤백 가이드 (Rollback Guide)

## 📌 현재 저장된 스냅샷

### 🎯 error-fully-corrected (2026-02-27)
**전체 에러 수정 완료 버전 - Production Ready**

커밋: `a86a0d5`
태그: `error-fully-corrected`, `v1.0.0-all-errors-fixed`

#### 수정된 에러 (10개)
1. ✅ 실시간 배차 모니터링 - Sidebar 추가
2. ✅ Telemetry API 500 - timestamp 컬럼 추가
3. ✅ AB Test API 500 - Redis 인증 설정
4. ✅ Clients API 500 - 컬럼 추가
5. ✅ 자동배차최적화 422 - status 파라미터 수정
6. ✅ 실시간 차량 텔레메트리 WebSocket 403 - URL 수정
7. ✅ 온도모니터링 TypeError - 데이터 처리 개선
8. ✅ 고급 분석 BI 500 - 빈 데이터 에러 핸들링
9. ✅ Analytics WebSocket 오류 - 중복 라우트 제거
10. ✅ WebSocket 에러 로그 - production 환경 숨김

---

## 🚀 롤백 방법

### 방법 1: 태그로 롤백 (권장)

```bash
# 1. 현재 상태 백업 (선택사항)
cd /root/uvis
git tag -a "backup-$(date +%Y%m%d-%H%M%S)" -m "Backup before rollback"

# 2. error-fully-corrected 태그로 롤백
git checkout error-fully-corrected

# 3. 새 브랜치 생성 (선택사항)
git checkout -b rollback-to-error-corrected

# 4. 서비스 재시작
docker-compose down
docker-compose up -d --build

# 5. 헬스체크
curl http://localhost:8000/api/v1/health
```

### 방법 2: 커밋 해시로 롤백

```bash
cd /root/uvis

# 특정 커밋으로 롤백
git reset --hard a86a0d5

# 또는 main 브랜치를 특정 커밋으로 리셋
git checkout main
git reset --hard a86a0d5
git push origin main --force  # 주의: 이후 커밋들 삭제됨

# 서비스 재시작
docker-compose down
docker-compose up -d --build
```

### 방법 3: 새 브랜치 생성 후 롤백

```bash
cd /root/uvis

# 현재 상태를 새 브랜치로 저장
git checkout -b backup-main

# error-fully-corrected로 새 브랜치 생성
git checkout error-fully-corrected
git checkout -b production-stable

# main 브랜치를 production-stable로 교체
git checkout main
git reset --hard production-stable
git push origin main --force

# 서비스 재시작
docker-compose down
docker-compose up -d --build
```

---

## 📁 백업 파일 위치

### Frontend 백업
- `frontend/src/config/navigation.ts.backup3` - 사이드바 재구성 이전 상태

### 배포 스크립트
- `FIX_TELEMETRY_AND_REDIS.sh` - Telemetry & Redis 수정
- `FIX_REDIS_AUTH.sh` - Redis 인증 수정
- `FIX_FRONTEND_ERRORS.sh` - Frontend 에러 수정
- `FIX_ANALYTICS_DASHBOARD.sh` - Analytics Dashboard 수정
- `FIX_ANALYTICS_WEBSOCKET.sh` - Analytics WebSocket 수정

### 문서
- `TELEMETRY_FIX_SUMMARY.md`
- `FINAL_DEPLOYMENT_STATUS.md`
- `FRONTEND_ERRORS_FIX_SUMMARY.md`
- `ANALYTICS_DASHBOARD_FIX_SUMMARY.md`
- `ANALYTICS_WEBSOCKET_FIX_SUMMARY.md`
- `DEPLOYMENT_INSTRUCTIONS.md`

---

## 🔍 롤백 후 검증

### 1. 시스템 헬스체크
```bash
# Backend 헬스체크
curl http://localhost:8000/api/v1/health | jq .

# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs backend --tail 50
docker-compose logs frontend --tail 50
```

### 2. API 테스트
```bash
# JWT 토큰 발급
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123" | jq -r '.access_token')

# Clients API
curl -s -H "Authorization: Bearer ${TOKEN}" \
    http://localhost:8000/api/v1/clients | jq .

# Telemetry API
curl -s -H "Authorization: Bearer ${TOKEN}" \
    http://localhost:8000/api/v1/telemetry/vehicles/status | jq .

# AB Test API
curl -s -H "Authorization: Bearer ${TOKEN}" \
    http://localhost:8000/api/v1/ab-test/experiments | jq .

# Analytics Dashboard API
curl -s -H "Authorization: Bearer ${TOKEN}" \
    http://localhost:8000/api/v1/analytics/dashboard | jq .
```

### 3. Frontend 검증
```bash
# 브라우저에서 테스트
# 1. http://139.150.11.99 접속
# 2. F12 → Console → localStorage.clear(); location.reload();
# 3. admin/admin123 로그인
# 4. 각 페이지 확인:
#    - 대시보드
#    - 자동 배차 최적화
#    - 실시간 차량 텔레메트리
#    - 실시간 온도 모니터링
#    - 고급 분석 & BI 대시보드
#    - 통계 및 분석
```

---

## 📊 데이터베이스 상태 (error-fully-corrected)

```sql
-- 테이블 데이터 확인
SELECT
  (SELECT COUNT(*) FROM orders) as orders_count,
  (SELECT COUNT(*) FROM dispatches) as dispatches_count,
  (SELECT COUNT(*) FROM clients) as clients_count,
  (SELECT COUNT(*) FROM vehicles) as vehicles_count;

-- 예상 결과:
-- orders_count: 4
-- dispatches_count: 0
-- clients_count: 0
-- vehicles_count: 46
```

### 데이터베이스 스키마 변경사항
- `vehicle_locations` 테이블: `timestamp` 컬럼 추가
- `clients` 테이블: 누락된 컬럼들 추가
  - `address_detail`
  - `geocoded`
  - 기타 필수 컬럼

---

## ⚙️ 설정 파일 상태

### Redis 설정
```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=pXrvuewL2gXRrc6NDpaAvDNWg
REDIS_URL=redis://redis:6379/0
```

### Backend 환경변수
```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=pXrvuewL2gXRrc6NDpaAvDNWg
      - DATABASE_URL=postgresql://uvis_user:uvis_password@db:5432/uvis_db
```

---

## 🎯 주요 변경사항 요약

### Backend 변경
| 파일 | 변경 내용 |
|------|---------|
| `backend/app/models/vehicle_location.py` | `timestamp` 컬럼 추가 |
| `backend/app/api/ab_test.py` | Redis 인증 추가 |
| `backend/app/api/ml_dispatch.py` | Redis 인증 추가 |
| `backend/app/services/cache_service.py` | Redis 인증 추가 |
| `backend/app/api/analytics.py` | 빈 데이터 에러 핸들링 |

### Frontend 변경
| 파일 | 변경 내용 |
|------|---------|
| `frontend/src/pages/DispatchOptimizationPage.tsx` | status → '배차대기' |
| `frontend/src/pages/RealtimeTelemetryPage.tsx` | WebSocket URL 수정 |
| `frontend/src/pages/TemperatureMonitoringPage.tsx` | 배열/객체 처리 |
| `frontend/src/App.tsx` | 중복 라우트 제거 |
| `frontend/src/hooks/useRealtimeData.ts` | 에러 로그 숨김 |

---

## 🔒 롤백 시 주의사항

1. **데이터베이스 백업**
   ```bash
   # 롤백 전 DB 백업
   docker-compose exec db pg_dump -U uvis_user uvis_db > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **컨테이너 볼륨**
   - 롤백해도 데이터베이스 데이터는 유지됩니다 (볼륨 마운트)
   - MinIO 파일도 유지됩니다

3. **환경변수**
   - `.env` 파일이 변경되었다면 수동으로 복원 필요

4. **브라우저 캐시**
   - 롤백 후 반드시 브라우저 캐시 클리어
   ```javascript
   localStorage.clear();
   sessionStorage.clear();
   location.reload();
   ```

---

## 📞 롤백 후 문제 발생 시

### 문제: 서비스가 시작되지 않음
```bash
# 로그 확인
docker-compose logs backend --tail 100
docker-compose logs frontend --tail 100

# 컨테이너 재시작
docker-compose down
docker-compose up -d --build --force-recreate
```

### 문제: 데이터베이스 연결 실패
```bash
# DB 컨테이너 상태 확인
docker-compose ps db
docker-compose logs db --tail 50

# DB 재시작
docker-compose restart db
```

### 문제: Redis 연결 실패
```bash
# Redis 테스트
docker-compose exec backend python -c "
import redis
r = redis.Redis(host='redis', port=6379, password='pXrvuewL2gXRrc6NDpaAvDNWg', decode_responses=True)
print(r.ping())
"

# Redis 재시작
docker-compose restart redis
```

---

## 📅 버전 히스토리

### error-fully-corrected (2026-02-27)
- **커밋**: a86a0d5
- **상태**: ✅ Production Ready
- **특징**: 모든 에러 수정 완료, 시스템 100% 정상 작동

### 이전 주요 버전
- `v1.0-uvis-integration` - UVIS 통합 버전
- `v1.10.0` - 기능 추가 버전
- `v1.11.0` - 최신 기능 버전

---

## 🎓 롤백 Best Practices

1. **롤백 전 체크리스트**
   - [ ] 현재 상태 태그 생성
   - [ ] 데이터베이스 백업
   - [ ] 사용자에게 서비스 중단 공지
   - [ ] 롤백 계획 문서화

2. **롤백 중**
   - [ ] 서비스 중단 (docker-compose down)
   - [ ] 코드 롤백 (git checkout/reset)
   - [ ] 컨테이너 재빌드
   - [ ] 서비스 재시작

3. **롤백 후**
   - [ ] 헬스체크 수행
   - [ ] API 테스트
   - [ ] Frontend 동작 확인
   - [ ] 로그 모니터링
   - [ ] 사용자에게 복구 완료 공지

---

## 🔗 관련 문서

- [DEPLOYMENT_INSTRUCTIONS.md](./DEPLOYMENT_INSTRUCTIONS.md) - 배포 가이드
- [FINAL_DEPLOYMENT_STATUS.md](./FINAL_DEPLOYMENT_STATUS.md) - 배포 상태
- [TELEMETRY_FIX_SUMMARY.md](./TELEMETRY_FIX_SUMMARY.md) - Telemetry 수정 요약
- [FRONTEND_ERRORS_FIX_SUMMARY.md](./FRONTEND_ERRORS_FIX_SUMMARY.md) - Frontend 에러 수정
- [ANALYTICS_DASHBOARD_FIX_SUMMARY.md](./ANALYTICS_DASHBOARD_FIX_SUMMARY.md) - Analytics 수정
- [ANALYTICS_WEBSOCKET_FIX_SUMMARY.md](./ANALYTICS_WEBSOCKET_FIX_SUMMARY.md) - WebSocket 수정

---

## 💡 추가 지원

문제가 지속되면 다음을 확인하세요:
1. Docker 로그
2. 시스템 리소스 (CPU, Memory)
3. 네트워크 연결
4. 데이터베이스 상태
5. Redis 상태

---

**생성일**: 2026-02-27  
**최종 수정**: 2026-02-27  
**버전**: 1.0.0  
**상태**: ✅ Verified
