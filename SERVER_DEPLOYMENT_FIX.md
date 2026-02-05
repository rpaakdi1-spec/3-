# 🚀 서버 배포 수정 가이드

## ❌ 발생한 문제
```
error while interpolating services.db.environment.POSTGRES_PASSWORD: 
required variable DB_PASSWORD is missing a value: Database password required
```

## ✅ 해결 방법

서버의 `/root/uvis` 디렉터리에서 다음 명령어를 **순서대로** 실행하세요:

---

## 📝 Step 1: 최신 코드 가져오기

```bash
cd /root/uvis
git fetch origin
git checkout main
git pull origin main
```

**Expected Output:**
```
Already on 'main'
Your branch is up to date with 'origin/main'.
```

---

## 🔧 Step 2: .env 파일 자동 수정

**Option A: 자동 스크립트 사용 (권장)**

```bash
cd /root/uvis
chmod +x fix_env.sh
./fix_env.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
- ✅ `DB_PASSWORD` 추가 (없는 경우)
- ✅ `SECRET_KEY` 생성 (openssl 사용)
- ✅ `DATABASE_URL` 생성
- ✅ 필수 환경 변수 확인

**Option B: 수동으로 추가**

```bash
cd /root/uvis

# .env 파일에 DB_PASSWORD 추가
echo "DB_PASSWORD=uvis_secure_password_2024" >> .env

# DATABASE_URL 추가 (위에서 설정한 비밀번호 사용)
echo "DATABASE_URL=postgresql://uvis_user:uvis_secure_password_2024@db:5432/uvis_db" >> .env

# SECRET_KEY 생성 및 추가
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env

# NAVER_MAP API 키 추가 (실제 키로 교체 필요)
echo "NAVER_MAP_CLIENT_ID=your_naver_client_id" >> .env
echo "NAVER_MAP_CLIENT_SECRET=your_naver_client_secret" >> .env
```

---

## 📋 Step 3: .env 확인

```bash
cd /root/uvis

# DB 설정 확인 (비밀번호는 마스킹됨)
echo "🔍 DB 설정 확인:"
grep -E "^DB_|^DATABASE_URL=" .env | grep -v PASSWORD
echo "DB_PASSWORD=****** (설정됨)"
```

**Expected Output:**
```
🔍 DB 설정 확인:
DB_NAME=uvis_db
DB_USER=uvis_user
DATABASE_URL=postgresql://uvis_user:******@db:5432/uvis_db
DB_PASSWORD=****** (설정됨)
```

---

## 🐳 Step 4: 백엔드 재빌드 및 재시작

```bash
cd /root/uvis

echo "🔄 백엔드 재빌드 중..."
docker-compose build backend

echo "🚀 백엔드 시작 중..."
docker-compose up -d backend

echo "⏳ 30초 대기 중..."
sleep 30
```

---

## ✅ Step 5: 배포 확인

```bash
cd /root/uvis

echo "📊 백엔드 상태 확인:"
docker-compose ps backend

echo ""
echo "📝 백엔드 로그 (최근 40줄):"
docker-compose logs --tail=40 backend

echo ""
echo "🌐 백엔드 헬스체크:"
curl -s http://localhost:8000/health

echo ""
echo "📖 API 문서 확인:"
curl -s http://localhost:8000/docs | grep -o "<title>.*</title>" || echo "Swagger UI 로딩 중..."
```

**Expected Output:**
```
📊 백엔드 상태 확인:
    Name                   Command               State           Ports         
coldchain-backend   uvicorn main:app --host ...   Up      0.0.0.0:8000->8000/tcp

📝 백엔드 로그 (최근 40줄):
...
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1] using StatReload
INFO:     Started server process [8]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

🌐 백엔드 헬스체크:
{"status":"healthy","version":"1.0.0"}

📖 API 문서 확인:
<title>UVIS - Swagger UI</title>
```

---

## 🎯 Step 6: 프론트엔드 확인

```bash
cd /root/uvis

echo "🔄 프론트엔드 재시작..."
docker-compose restart frontend

sleep 10

echo "📊 프론트엔드 상태:"
docker-compose ps frontend
```

**브라우저 테스트:**
1. 브라우저에서 `http://YOUR_SERVER_IP` 접속
2. 로그인 (기존 계정 사용)
3. 사이드바에서 **"IoT 센서 모니터링"** 메뉴 클릭
4. 센서 대시보드 페이지 확인

---

## 🔧 문제 해결 (Troubleshooting)

### 문제 1: 백엔드가 시작되지 않음

**증상:**
```
docker-compose ps backend
# Status: Restarting 또는 Exit
```

**해결:**
```bash
cd /root/uvis

# 로그 확인
docker-compose logs --tail=100 backend

# 컨테이너 재시작
docker-compose down backend
docker-compose up -d backend
```

---

### 문제 2: Import 오류 발생

**증상:**
```
ImportError: cannot import name 'Base' from 'app.core.database'
ModuleNotFoundError: No module named 'twilio'
```

**해결:**
이 오류들은 이미 수정되었습니다. 최신 코드를 다시 가져오세요:
```bash
cd /root/uvis
git fetch origin main
git reset --hard origin/main
docker-compose build backend
docker-compose up -d backend
```

---

### 문제 3: Nginx가 unhealthy 상태

**증상:**
```
docker-compose ps nginx
# Status: Up (unhealthy)
```

**해결:**
```bash
cd /root/uvis

# Nginx 재시작
docker-compose restart nginx

# 설정 확인
docker exec coldchain-nginx nginx -t

# 로그 확인
docker-compose logs --tail=50 nginx
```

---

## 📊 전체 시스템 상태 확인

```bash
cd /root/uvis

echo "🔍 전체 컨테이너 상태:"
docker-compose ps

echo ""
echo "🌐 헬스체크:"
echo "Backend: $(curl -s http://localhost:8000/health | jq -r .status 2>/dev/null || echo 'N/A')"
echo "Frontend: $(curl -s http://localhost:5173 -o /dev/null -w '%{http_code}' 2>/dev/null)"
echo "Nginx: $(curl -s http://localhost -o /dev/null -w '%{http_code}' 2>/dev/null)"
```

---

## 🎉 성공 확인 체크리스트

- [ ] `docker-compose ps` 에서 모든 컨테이너가 `Up` 상태
- [ ] `curl http://localhost:8000/health` 가 `{"status":"healthy"}` 반환
- [ ] 백엔드 로그에 `Uvicorn running on http://0.0.0.0:8000` 표시
- [ ] `http://YOUR_SERVER_IP:8000/docs` 에서 Swagger UI 접근 가능
- [ ] 프론트엔드에서 "IoT 센서 모니터링" 메뉴 표시
- [ ] `/iot/sensors` 페이지가 로딩됨

---

## 📞 추가 도움이 필요한 경우

1. **백엔드 로그 전체 보기:**
   ```bash
   docker-compose logs -f backend
   ```

2. **데이터베이스 연결 확인:**
   ```bash
   docker exec -it coldchain-postgres psql -U uvis_user -d uvis_db -c "\dt"
   ```

3. **전체 재시작 (최후의 수단):**
   ```bash
   cd /root/uvis
   docker-compose down
   docker-compose up -d
   sleep 30
   docker-compose ps
   ```

---

## 🔗 관련 링크

- **Pull Request**: https://github.com/rpaakdi1-spec/3-/pull/4
- **Repository**: https://github.com/rpaakdi1-spec/3-

---

**이 가이드를 따라 실행하고, 결과를 공유해주세요!** 🚀
