# 🚀 Phase 16 배포 - 빠른 참조 가이드

## 📌 현재 상태
- **Phase 16 개발:** ✅ 100% 완료
- **코드 커밋:** ✅ 완료 (커밋 2933c11)
- **서버 배포:** ⏳ 대기 중
- **서버:** 139.150.11.99

## 🎯 서버에서 실행할 명령어

```bash
# 1. SSH 접속
ssh root@139.150.11.99

# 2. 프로젝트 디렉토리
cd /root/uvis

# 3. 최신 코드 가져오기
git rebase --abort
git fetch origin
git reset --hard origin/main

# 4. 커밋 확인 (2933c11 또는 04af91b 확인)
git log --oneline -3

# 5. Backend 재빌드 & 재시작
docker-compose stop backend
docker-compose build --no-cache backend
docker-compose up -d backend

# 6. 30초 대기 후 상태 확인
sleep 30
docker-compose ps

# 7. Health Check
curl http://localhost:8000/api/v1/health
curl -I http://localhost/

# 8. 성공 확인 - 모든 컨테이너가 Up (healthy) 상태여야 함
```

## ✅ 예상 결과

### 정상 컨테이너 상태
```
NAME            STATUS
uvis-backend    Up (healthy)
uvis-frontend   Up (healthy)
uvis-minio      Up (healthy)
uvis-db         Up (healthy)
uvis-redis      Up (healthy)
```

### Health Check 응답
```json
{
  "status": "healthy",
  "app_name": "Cold Chain Dispatch System",
  "environment": "production"
}
```

## 🧪 배포 후 테스트

### 브라우저에서 확인
1. **메인:** http://139.150.11.99
2. **채팅:** http://139.150.11.99/chat
3. **파일:** http://139.150.11.99/files
4. **API 문서:** http://139.150.11.99:8000/docs
5. **MinIO:** http://139.150.11.99:9001 (admin/uvis_minio_secure_2024)

### 통합 테스트
```bash
cd /root/uvis
./test-deployment.sh
```

## 🔧 트러블슈팅

### Backend가 여전히 unhealthy면
```bash
docker-compose restart backend
sleep 30
docker-compose logs backend | tail -50
```

### 전체 재시작이 필요하면
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
sleep 60
docker-compose ps
```

## 📖 상세 가이드

- **FCM 수정 배포:** `DEPLOY_FCM_FIX.md`
- **전체 상태 보고:** `PHASE_16_FINAL_DEPLOYMENT_STATUS.md`
- **서버 배포 상세:** `docs/SERVER_DEPLOYMENT_INSTRUCTIONS.md`

## 🎉 완료 체크리스트

- [ ] SSH 접속
- [ ] 최신 코드 pull
- [ ] Backend 재빌드
- [ ] 컨테이너 상태 확인 (모두 healthy)
- [ ] Health check 성공
- [ ] 웹사이트 접속 성공
- [ ] 채팅 페이지 동작 확인
- [ ] 파일 업로드 동작 확인
- [ ] 통합 테스트 통과

---

**작성:** 2026-02-27  
**커밋:** 2933c11  
**저장소:** https://github.com/rpaakdi1-spec/3-
