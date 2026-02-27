# 빠른 참조 가이드 (Quick Reference Guide)

## 🚀 즉시 실행 가능한 명령어

### 서버 배포 (Server Deployment)
```bash
# 1. 최신 코드 가져오기
cd /root/uvis
git pull origin main

# 2. 네이버 지도 API 배포 (필수)
bash DEPLOY_NAVER_MAP.sh

# 3. WebSocket 수정 배포 (필요시)
bash FIX_WEBSOCKET_OVERLOAD.sh

# 4. 전체 시스템 재시작
docker-compose down
docker-compose up -d --build
```

### 시스템 상태 확인
```bash
# Docker 컨테이너 상태
docker-compose ps

# Backend API 상태
curl http://139.150.11.99/api/v1/health

# 로그 확인
docker-compose logs --tail=100 -f
```

### 긴급 롤백
```bash
cd /root/uvis
git checkout error-fully-corrected
docker-compose down
docker-compose up -d --build
```

---

## 🔧 네이버 지도 API 활성화 (수동 작업 필수)

### Naver Cloud Console에서 실행:
1. https://www.ncloud.com/ 로그인
2. **Console** → **Services** → **AI·NAVER API** → **Maps**
3. Application 선택 (Client ID: `oimsa0yj4k`)
4. **Web Service URL** 섹션에 추가:
   ```
   http://139.150.11.99
   http://139.150.11.99/vehicles
   http://139.150.11.99*
   ```
5. **저장** 후 **5-10분 대기** (DNS 전파)

### 테스트:
```
http://139.150.11.99/vehicles
로그인: admin / admin123
지도 정상 표시 확인
```

---

## 📊 중요 URL

| 서비스 | URL |
|--------|-----|
| 메인 시스템 | http://139.150.11.99 |
| Backend API | http://139.150.11.99/api/v1 |
| Health Check | http://139.150.11.99/api/v1/health |
| Prometheus | http://139.150.11.99:9090 |
| Grafana | http://139.150.11.99:3000 |
| GitHub Repo | https://github.com/rpaakdi1-spec/3- |

---

## 🆘 문제 해결

### 브라우저 과부하 (WebSocket 문제)
```javascript
// 브라우저 콘솔에서 실행
localStorage.clear();
sessionStorage.clear();
location.reload();
```

### 지도 안 나올 때
1. Naver Cloud URL 등록 재확인
2. 5-10분 대기 (DNS 전파)
3. 브라우저 캐시 삭제 (Ctrl+Shift+R)
4. 시크릿 모드로 테스트

### Backend 오류
```bash
# 로그 확인
docker-compose logs backend --tail=100

# 백엔드 재시작
docker-compose restart backend
```

### Database 문제
```bash
# PostgreSQL 접속
docker exec -it uvis-postgres psql -U postgres -d uvis_db

# 테이블 확인
\dt

# 데이터 확인
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM vehicles;
```

---

## 📁 중요 문서

| 문서 | 용도 |
|------|------|
| `CURRENT_SYSTEM_STATUS.md` | 전체 시스템 현황 |
| `ERROR_FULLY_CORRECTED_SNAPSHOT.md` | 스냅샷 요약 |
| `ROLLBACK_GUIDE.md` | 롤백 가이드 |
| `NAVER_MAP_SETUP_GUIDE.md` | 네이버 지도 설정 |
| `ADDITIONAL_ENGINE_PROPOSAL.md` | 추가 엔진 제안서 |
| `WEBSOCKET_OVERLOAD_FIX_SUMMARY.md` | WebSocket 수정 내용 |

---

## 🎯 다음 할 일 (To-Do)

### 즉시 (Immediate)
- [ ] 네이버 지도 API URL 등록 (Naver Cloud Console)
- [ ] 서버에서 `bash DEPLOY_NAVER_MAP.sh` 실행
- [ ] 지도 동작 테스트

### 단기 (1-2주)
- [ ] 실제 고객 데이터 입력
- [ ] 차량 데이터 입력
- [ ] 주문 데이터 입력
- [ ] ML 모델 훈련 완료 확인

### 중기 (1개월)
- [ ] ML Auto-Training Scheduler 구현
- [ ] Enhanced Dispatch Simulation 구현

---

## 📞 연락처

**GitHub**: rpaakdi1-spec  
**Repository**: https://github.com/rpaakdi1-spec/3-

---

**Last Updated**: 2026-02-27
