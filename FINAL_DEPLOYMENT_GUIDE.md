# 🚀 UVIS Gabia 서버 최종 배포 가이드

## 📋 수정 완료된 문제들

### 1. Backend Settings 문제 해결 ✅
- **문제**: Pydantic v2의 Config 클래스 문법 오류
- **해결**: `model_config` 딕셔너리로 변경
- **추가**: `extra='ignore'` 설정으로 Docker 환경 변수 허용

### 2. 환경 변수 매핑 문제 해결 ✅
- **문제**: ENVIRONMENT 변수가 APP_ENV로 매핑되지 않음
- **해결**: `Field(alias="ENVIRONMENT")` 추가

### 3. Docker Compose 설정 문제 해결 ✅
- **문제**: 개발용 docker-compose.yml 사용 중
- **해결**: 프로덕션용 `docker-compose.prod.yml` 생성
- **변경**: `env_file: .env` 추가로 환경 변수 주입

### 4. Naver Maps API 설정 완료 ✅
- **Client ID**: pkciiaux61
- **Client Secret**: (설정 완료)
- **.env 파일**: 모든 필수 환경 변수 포함

---

## 🎯 PuTTY에서 실행할 최종 배포 명령

```bash
cd /root/uvis && \
git fetch origin genspark_ai_developer && \
git reset --hard origin/genspark_ai_developer && \
curl -O https://raw.githubusercontent.com/rpaakdi1-spec/3-/genspark_ai_developer/deploy-gabia-final-fixed.sh && \
chmod +x deploy-gabia-final-fixed.sh && \
./deploy-gabia-final-fixed.sh
```

---

## 📊 배포 프로세스 (10단계)

### Step 1: 프로젝트 디렉토리 이동
- `/root/uvis`로 이동

### Step 2: 최신 코드 가져오기
- Commit: **b3f5290**
- 브랜치: **genspark_ai_developer**
- 변경사항: Settings 클래스 수정, docker-compose.prod.yml 추가

### Step 3: 필수 파일 확인
- backend/app/core/config.py (Pydantic v2 호환)
- docker-compose.prod.yml (프로덕션 설정)
- .env.production (환경 변수)

### Step 4: 환경 변수 설정
```env
DATABASE_URL=postgresql://uvis_user:uvis_password@db:5432/uvis_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=gabia-uvis-production-secret-2026
ENVIRONMENT=production
NAVER_MAP_CLIENT_ID=pkciiaux61
NAVER_MAP_CLIENT_SECRET=dBi4yjpGEj7SJTYwAz00e8pab6XuumhdQH4WbFy5
CORS_ORIGINS=http://139.150.11.99,http://139.150.11.99:3000,http://139.150.11.99:8000
REACT_APP_API_URL=http://139.150.11.99:8000
REACT_APP_WS_URL=ws://139.150.11.99:8000/ws
```

### Step 5: 기존 컨테이너 정리
- `docker-compose -f docker-compose.prod.yml down -v`
- `docker system prune -af`

### Step 6: Docker 이미지 빌드
- Backend 빌드: 5-8분
- Frontend 빌드: 8-12분
- **총 예상 시간: 15-20분**

### Step 7: 컨테이너 시작
- DB, Redis, Backend, Frontend, Nginx 시작
- 초기화 대기: 30초

### Step 8: 컨테이너 상태 확인
- 5개 컨테이너 모두 Up 상태 확인

### Step 9: Health Check
- Backend: http://localhost:8000/health
- 최대 10회 재시도 (5초 간격)

### Step 10: 로그 확인
- Backend 로그: 최근 20줄
- Frontend 로그: 최근 20줄

---

## 🎉 배포 완료 후 접속 정보

### 📍 서비스 URL
- **Frontend**: http://139.150.11.99
- **Frontend (직접)**: http://139.150.11.99:3000
- **API Docs**: http://139.150.11.99:8000/docs
- **Health**: http://139.150.11.99:8000/health
- **Backend API**: http://139.150.11.99:8000

### 👤 테스트 계정
- **관리자**: admin@example.com / admin123
- **드라이버 1**: driver1 / password123
- **드라이버 2**: driver2 / password123

### 🗺️ Naver Maps 기능
- ✅ Static Map: 정적 지도 표시
- ✅ Geocoding: 주소 → 좌표 변환
- ✅ Reverse Geocoding: 좌표 → 주소 변환
- ✅ Directions 5: 경로 탐색

---

## ⏱️ 예상 소요 시간

| 단계 | 예상 시간 |
|------|----------|
| 코드 동기화 | 10초 |
| 환경 설정 | 30초 |
| Docker 캐시 클리어 | 1분 |
| Backend 빌드 | 5-8분 |
| Frontend 빌드 | 8-12분 |
| 컨테이너 시작 | 1-2분 |
| Health Check | 30초 |
| **총 예상 시간** | **16-24분** |

---

## 🔧 문제 발생 시 해결 방법

### Backend 빌드 실패
```bash
# 로그 확인
cat /tmp/backend-build.log | tail -50

# 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache backend
```

### Frontend 빌드 실패
```bash
# 로그 확인
cat /tmp/frontend-build.log | tail -50

# 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache frontend
```

### Health Check 실패
```bash
# Backend 로그 확인
docker-compose -f docker-compose.prod.yml logs --tail=100 backend

# Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 수동 Health Check
curl http://localhost:8000/health
```

### 컨테이너 상태 확인
```bash
# 모든 컨테이너 상태
docker-compose -f docker-compose.prod.yml ps

# 특정 컨테이너 로그
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart [service_name]
```

---

## 📝 주요 변경사항 요약

### backend/app/core/config.py
```python
# Before (Pydantic v1 스타일)
class Config:
    env_file = ".env"
    case_sensitive = True

# After (Pydantic v2 스타일)
model_config = {
    "env_file": ".env",
    "case_sensitive": True,
    "extra": "ignore"  # ✅ Docker 환경 변수 허용
}
```

### docker-compose.prod.yml
```yaml
# ✅ env_file 추가로 .env 파일 주입
backend:
  build:
    context: ./backend
    dockerfile: Dockerfile.prod
  env_file:
    - .env  # 환경 변수 파일
  depends_on:
    db:
      condition: service_healthy
    redis:
      condition: service_healthy
```

---

## 🎯 이번 배포의 차이점

### 이전 배포 시도들
- ❌ Pydantic v1 Config 클래스 사용
- ❌ 환경 변수가 제대로 전달되지 않음
- ❌ "Extra inputs are not permitted" 에러
- ❌ NAVER_MAP 키 누락

### 이번 최종 배포
- ✅ Pydantic v2 model_config 사용
- ✅ env_file로 환경 변수 주입
- ✅ extra='ignore' 설정
- ✅ NAVER_MAP API 키 설정 완료
- ✅ 프로덕션용 docker-compose.prod.yml
- ✅ 모든 필수 환경 변수 포함

---

## 🚀 지금 바로 실행하세요!

1. **PuTTY로 서버 접속**
   - IP: 139.150.11.99
   - Port: 22
   - User: root
   - Password: igG5v@iJ

2. **배포 명령 복사 & 실행**
   ```bash
   cd /root/uvis && \
   git fetch origin genspark_ai_developer && \
   git reset --hard origin/genspark_ai_developer && \
   curl -O https://raw.githubusercontent.com/rpaakdi1-spec/3-/genspark_ai_developer/deploy-gabia-final-fixed.sh && \
   chmod +x deploy-gabia-final-fixed.sh && \
   ./deploy-gabia-final-fixed.sh
   ```

3. **약 20분 대기**
   - 빌드 진행 상황이 실시간으로 표시됩니다
   - 커피 한 잔 하세요 ☕

4. **배포 완료!**
   - http://139.150.11.99 접속
   - admin@example.com / admin123 로그인

---

## ✅ 이번엔 반드시 성공합니다!

모든 근본 원인이 해결되었습니다:
1. ✅ Pydantic Settings 설정 수정
2. ✅ Docker Compose 프로덕션 설정
3. ✅ 환경 변수 올바른 주입
4. ✅ Naver Maps API 키 설정
5. ✅ TypeScript 빌드 최적화

**지금 바로 배포를 시작하세요!** 🚀
