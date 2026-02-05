# ⚡ 서버 배포 빠른 실행 가이드

## 🚀 한 번에 실행하기 (5분 소요)

```bash
cd /root/uvis && \
git fetch origin genspark_ai_developer && \
git reset --hard origin/genspark_ai_developer && \
chmod +x SERVER_FINAL_FIX.sh && \
./SERVER_FINAL_FIX.sh
```

---

## ✅ 성공 확인

```bash
# Health Check
curl -s http://localhost:8000/health

# 예상 결과:
# {"status":"healthy","app_name":"Cold Chain Dispatch System","environment":"production"}
```

---

## 🌐 접속 URL

| 서비스 | URL |
|--------|-----|
| **API 문서** | http://YOUR_SERVER_IP:8000/docs |
| **Health** | http://YOUR_SERVER_IP:8000/health |
| **API Root** | http://YOUR_SERVER_IP:8000/ |
| **Frontend** | http://YOUR_SERVER_IP/ (배포 후) |

---

## 🔍 문제 발생 시

```bash
# 로그 확인
docker-compose logs backend | tail -50

# 컨테이너 상태
docker-compose ps

# 환경변수 확인
cat .env | grep SECRET_KEY

# Backend 재시작
docker-compose restart backend
```

---

## 📋 해결된 문제들

✅ **NotificationLevel 에러** - monitoring.py 수정  
✅ **SECRET_KEY 누락** - .env 자동 생성  
✅ **순환 import** - database.py 재구성  
✅ **metadata 충돌** - notification_metadata로 변경  
✅ **Models export** - __init__.py 완전 수정  

---

## 🎯 최신 Commit

**Commit:** 46dc8f2  
**Branch:** genspark_ai_developer  
**PR:** https://github.com/rpaakdi1-spec/3-/pull/4

---

## 📞 다음 단계

1. ✅ Backend 정상 작동 확인
2. 🔄 Frontend 배포 (npm install 필요)
3. 🔧 NAVER MAP API 키 설정
4. 🌐 Nginx 및 Frontend 빌드

---

**빠른 도움말:** `cat SERVER_DEPLOYMENT_FINAL.md` - 상세 가이드 보기
