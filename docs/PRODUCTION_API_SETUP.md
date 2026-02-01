# 🚀 프로덕션 서버 API 키 설정 및 배포 가이드

이 가이드는 **실제 서버 (139.150.11.99 / /root/uvis)**에서 OpenAI API 키를 설정하는 방법입니다.

---

## 📋 사전 준비

✅ API 키 확인:
- OPENAI_API_KEY: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (본인의 API 키 사용)
- GEMINI_API_KEY: `AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (본인의 API 키 사용)

⚠️ **주의**: 위의 API 키는 예시입니다. 실제로는 OpenAI 및 Gemini 대시보드에서 발급받은 본인의 API 키를 사용해야 합니다.

---

## 1️⃣ 서버 접속

```bash
# SSH로 서버 접속
ssh root@139.150.11.99

# 또는 접속되어 있다면 작업 디렉토리로 이동
cd /root/uvis
pwd  # /root/uvis 확인
```

---

## 2️⃣ 최신 코드 가져오기

```bash
cd /root/uvis

# 현재 브랜치 확인
git branch

# genspark_ai_developer 브랜치로 전환 (이미 있다면 skip)
git checkout genspark_ai_developer

# 최신 코드 가져오기
git pull origin genspark_ai_developer

# 최신 커밋 확인
git log --oneline -5
```

**예상 출력:**
```
1c67b10 docs: OpenAI API 설정 가이드 추가
2464de2 feat: AI 비용 모니터링 대시보드 추가
9701d77 feat: GPT-4를 기본 AI 모델로 설정
70a9db9 feat: AI 모델 선택 기능 추가
ab29fac fix: OptimizationPage 차량 상태 필터링 오류 수정
```

---

## 3️⃣ `.env.prod` 파일 편집

```bash
cd /root/uvis

# .env.prod 파일 열기
nano .env.prod
```

**추가할 내용 (파일 끝에 추가):**
```bash
# OpenAI API (ChatGPT-4)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Gemini API (선택 사항)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ **중요**: 위의 `xxxxx...`를 본인의 실제 API 키로 교체하세요!

**저장 및 종료:**
- `Ctrl + O` (저장)
- `Enter` (확인)
- `Ctrl + X` (종료)

**확인:**
```bash
cat .env.prod | grep -E "OPENAI|GEMINI"
```

**예상 출력:**
```
OPENAI_API_KEY=sk-proj-KtlsKSAiq_VeH...
GEMINI_API_KEY=AIzaSyD4G2uus...
```

---

## 4️⃣ Docker Compose 파일 확인

```bash
cd /root/uvis

# docker-compose.prod.yml 확인
cat docker-compose.prod.yml | grep -A 3 "env_file:"
```

**확인 사항:**
```yaml
services:
  backend:
    env_file:
      - .env.prod  # ← 이 설정이 있어야 함
```

**만약 없다면 추가:**
```bash
nano docker-compose.prod.yml
```

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file:
      - .env.prod  # ← 추가
    # ... 나머지 설정
```

---

## 5️⃣ 백엔드 재배포

```bash
cd /root/uvis

# 1. 백엔드 컨테이너 중지
docker-compose -f docker-compose.prod.yml stop backend

# 2. 백엔드 컨테이너 제거 (환경변수 새로고침 위해)
docker-compose -f docker-compose.prod.yml rm -f backend

# 3. 백엔드 이미지 재빌드 (새 의존성 포함)
docker-compose -f docker-compose.prod.yml build backend

# 4. 백엔드 컨테이너 시작
docker-compose -f docker-compose.prod.yml up -d backend

# 5. 컨테이너 상태 확인
docker ps | grep backend
```

**예상 출력:**
```
CONTAINER ID   IMAGE               STATUS         PORTS
a1b2c3d4e5f6   uvis-backend        Up 10 seconds  0.0.0.0:8000->8000/tcp
```

---

## 6️⃣ 로그 확인 (중요!)

```bash
cd /root/uvis

# 백엔드 로그 실시간 확인 (30초 동안)
docker logs uvis-backend --tail 100 -f
```

**확인 포인트 (성공 시):**
```
✅ OpenAI API Key configured
✅ Using model: gpt-4o
✅ AIChatService initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**⚠️ 경고 메시지 (실패 시):**
```
❌ OpenAI API 키가 설정되지 않았습니다
⚠️ AI 모델이 설정되지 않았습니다. 시뮬레이션 모드로 실행됩니다.
```

**문제 해결:**
```bash
# 1. 환경변수 확인
docker exec -it uvis-backend env | grep -E "OPENAI|GEMINI"

# 2. API 키가 없다면 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 3. 여전히 안 되면 .env.prod 파일 다시 확인
cat /root/uvis/.env.prod | grep OPENAI
```

---

## 7️⃣ 프론트엔드 재배포 (선택)

```bash
cd /root/uvis

# 프론트엔드 재빌드 (새로운 라이브러리 recharts 포함)
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml up -d frontend

# 상태 확인
docker ps | grep frontend
```

---

## 8️⃣ AI 채팅 테스트

### **방법 1: 웹 UI로 테스트 (추천)**

```
1️⃣ 브라우저에서 접속:
   http://139.150.11.99

2️⃣ 로그인:
   - ID: admin
   - 비밀번호: 관리자 비밀번호

3️⃣ 사이드바 → "💬 AI 주문 어시스턴트" 클릭

4️⃣ 테스트 메시지 입력:
```

**테스트 입력:**
```
서울 강남구에서 부산 해운대구로 냉동 10팔레트 500kg 보내줘
```

**기대 결과:**
- ✅ AI 응답 즉시 표시 (2-5초)
- ✅ "추출된 주문 정보" 카드 표시
- ✅ 온도대: 냉동
- ✅ 상차지: 서울 강남구
- ✅ 하차지: 부산 해운대구
- ✅ 팔레트: 10개
- ✅ 중량: 500kg

### **방법 2: API로 직접 테스트**

```bash
# 서버에서 실행
cd /root/uvis

# 1. 로그인 토큰 획득
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=YOUR_PASSWORD" | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. AI 채팅 API 호출
curl -X POST http://localhost:8000/api/v1/ai-chat/process \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "서울에서 부산으로 냉동 10팔레트 보내줘",
    "context": {},
    "model": "gpt-4"
  }' | jq .
```

**예상 응답:**
```json
{
  "intent": "create_order",
  "message": "주문 정보를 확인해주세요...",
  "parsed_order": {
    "pickup_address": "서울",
    "delivery_address": "부산",
    "temperature_zone": "냉동",
    "pallet_count": 10
  },
  "model_used": "gpt-4"
}
```

---

## 9️⃣ 비용 모니터링 대시보드 확인

```
1️⃣ 접속:
   http://139.150.11.99/ai-cost

2️⃣ 로그인 (ADMIN 계정만 접근 가능)

3️⃣ 확인 항목:
   - 총 비용 카드
   - 오늘 비용 카드
   - 총 요청 수
   - 총 토큰 수
   - 날짜별 비용 추이 차트
   - 모델별 비용 분포 차트
```

---

## 🔧 문제 해결

### **문제 1: "⚠️ OpenAI API 키가 설정되지 않았습니다"**

**해결:**
```bash
# 1. .env.prod 파일 확인
cat /root/uvis/.env.prod | grep OPENAI

# 2. Docker 컨테이너 내부 환경변수 확인
docker exec -it uvis-backend env | grep OPENAI

# 3. 환경변수가 없다면 컨테이너 재생성
docker-compose -f docker-compose.prod.yml down backend
docker-compose -f docker-compose.prod.yml up -d backend

# 4. 로그 다시 확인
docker logs uvis-backend --tail 50
```

---

### **문제 2: "❌ 401 Unauthorized"**

**원인:**
- API 키가 잘못됨
- API 키가 만료됨

**해결:**
```bash
# 1. OpenAI 대시보드에서 API 키 재확인
# https://platform.openai.com/api-keys

# 2. 새 API 키 생성
# 기존 키 삭제 → 새 키 생성

# 3. .env.prod 파일 업데이트
nano /root/uvis/.env.prod

# 4. 백엔드 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

---

### **문제 3: 응답이 느림 (10초+)**

**원인:**
- GPT-4 모델의 긴 응답 시간
- 네트워크 지연

**해결:**
```
1. AI 채팅 UI에서 모델 선택
2. "GPT-3.5 Turbo" 선택 (2-3초 응답)
3. 또는 "Gemini Pro" 선택 (무료, 1-2초)
```

---

### **문제 4: 비용 모니터링 페이지 404**

**원인:**
- 프론트엔드가 재빌드되지 않음
- Nginx 캐시

**해결:**
```bash
# 1. 프론트엔드 재빌드
cd /root/uvis
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml up -d frontend

# 2. Nginx 캐시 클리어
docker exec -it uvis-nginx sh -c "rm -rf /var/cache/nginx/*"
docker restart uvis-nginx

# 3. 브라우저 캐시 클리어 (Ctrl+Shift+R)
```

---

## ✅ 성공 확인 체크리스트

- [ ] 서버 접속 완료 (ssh root@139.150.11.99)
- [ ] 최신 코드 가져오기 완료 (git pull)
- [ ] `.env.prod` 파일에 API 키 추가 완료
- [ ] 백엔드 컨테이너 재시작 완료
- [ ] 로그에서 "✅ OpenAI API Key configured" 확인
- [ ] AI 채팅 UI로 주문 입력 테스트 성공
- [ ] 주문 정보 파싱 성공
- [ ] 비용 모니터링 대시보드 (/ai-cost) 접속 성공
- [ ] OpenAI 대시보드에서 사용량 확인

---

## 🎯 테스트 시나리오

### **시나리오 1: 단순 주문**
```
입력: "서울에서 부산으로 냉동 10팔레트 보내줘"

예상 결과:
- 온도대: 냉동
- 상차지: 서울
- 하차지: 부산
- 팔레트: 10개
```

### **시나리오 2: 복잡한 1:N 주문**
```
입력: "서울 강남구에서 부산 해운대구로 냉동 20팔레트 1000kg,
대구 수성구로 냉장 15팔레트 700kg,
대전 유성구로 상온 10팔레트 500kg 보내줘.
상차는 내일 오전 9시부터 11시, 
부산은 오후 2시까지, 대구는 오후 3시까지, 대전은 오후 4시까지."

예상 결과:
- 3개 주문으로 자동 분리
- 각 온도대, 주소, 팔레트, 시간 정확히 파싱
```

---

## 💰 비용 확인

### **OpenAI 대시보드**
```
접속: https://platform.openai.com/usage

확인:
- 오늘 사용량
- 모델별 요청 수
- 총 비용
```

### **시스템 대시보드**
```
접속: http://139.150.11.99/ai-cost (ADMIN 전용)

확인:
- 총 비용 (7일/30일)
- 모델별 비용 분포
- 날짜별 비용 추이
- Intent별 비용
```

---

## 📞 완료 후 보고

테스트 완료 후 다음 정보를 공유해주세요:

1. **테스트 결과**
   - AI 채팅 응답 시간: ___ 초
   - 주문 파싱 정확도: ✅ 또는 ❌
   - 스크린샷 (선택)

2. **비용 정보**
   - 첫 주문 비용: $___
   - 오늘 총 비용: $___

3. **문제 사항** (있다면)
   - 오류 메시지
   - 로그 내용

---

**작성일**: 2026-02-01
**작성자**: AI Assistant
**문서 버전**: 1.0
