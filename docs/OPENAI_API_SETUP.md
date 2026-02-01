# 🔑 ChatGPT-4 (OpenAI) API 설정 가이드

이 가이드는 Cold Chain Dispatch System에서 ChatGPT-4 (OpenAI API)를 설정하는 방법을 안내합니다.

---

## 📋 목차

1. [OpenAI API 키 발급](#1-openai-api-키-발급)
2. [로컬 개발 환경 설정](#2-로컬-개발-환경-설정)
3. [프로덕션 서버 설정](#3-프로덕션-서버-설정)
4. [API 키 테스트](#4-api-키-테스트)
5. [비용 관리](#5-비용-관리)
6. [문제 해결](#6-문제-해결)

---

## 1️⃣ OpenAI API 키 발급

### **Step 1: OpenAI 계정 생성**

1. **접속**: [https://platform.openai.com/signup](https://platform.openai.com/signup)
2. **가입**: 이메일 또는 Google 계정으로 가입
3. **인증**: 이메일 인증 완료

### **Step 2: API 키 생성**

1. **로그인 후 접속**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. **키 생성**: "Create new secret key" 버튼 클릭
3. **이름 입력**: 키 이름 입력 (예: "Cold Chain Dispatch System")
4. **생성**: "Create secret key" 클릭
5. **⚠️ API 키 복사**: 한 번만 표시됩니다!

**생성된 API 키 형식:**
```
sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ 중요 사항:**
- API 키는 **한 번만** 표시됩니다
- 즉시 안전한 곳에 저장하세요
- **절대 GitHub에 커밋하지 마세요**
- `.env` 파일은 `.gitignore`에 포함되어 있습니다

### **Step 3: 결제 정보 등록**

1. **접속**: [https://platform.openai.com/account/billing/overview](https://platform.openai.com/account/billing/overview)
2. **결제 등록**: "Add payment details" 클릭
3. **카드 정보**: 신용카드 정보 입력
4. **한도 설정**: 사용량 한도 설정 (권장: **$50/월**)

**💰 비용 예상:**

| 사용량 | 모델 | 비용 (USD) | 비용 (KRW) |
|--------|------|-----------|-----------|
| 주문 1건 | GPT-4o | $0.005-0.010 | ₩6-13 |
| 일 100건 | GPT-4o | $0.50-1.00 | ₩650-1,300 |
| 월 1,000건 | GPT-4o | $5-10 | ₩6,500-13,000 |
| 월 3,000건 | GPT-4o | $15-30 | ₩19,500-39,000 |

**가격표 (per 1M tokens):**
- **GPT-4o**: $5 (입력) + $15 (출력)
- **GPT-3.5 Turbo**: $0.5 (입력) + $1.5 (출력) ← 10배 저렴!
- **Gemini Pro**: 무료 (일일 제한 있음)

---

## 2️⃣ 로컬 개발 환경 설정

### **Step 1: `.env` 파일 수정**

```bash
cd /home/user/webapp/backend
nano .env
```

**또는 직접 편집:**

```bash
# OpenAI API (ChatGPT-4)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Gemini API (선택 사항 - 무료 테스트용)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ 주의:**
- `your_openai_api_key_here`를 실제 API 키로 교체
- 따옴표 없이 직접 입력
- 앞뒤 공백 없이 입력

### **Step 2: 백엔드 재시작**

```bash
cd /home/user/webapp

# FastAPI 개발 서버 재시작
# (이미 실행 중이면 Ctrl+C로 종료 후)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**성공 로그:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ OpenAI API Key configured
✅ Using model: gpt-4o
✅ AIChatService initialized successfully
```

### **Step 3: 환경변수 확인**

```bash
cd /home/user/webapp/backend
python3 << EOF
import os
from dotenv import load_dotenv
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
print(f"OpenAI API Key: {openai_key[:20]}..." if openai_key else "❌ API Key not found")
EOF
```

**예상 출력:**
```
OpenAI API Key: sk-proj-xxxxxxxxxxxxx...
```

---

## 3️⃣ 프로덕션 서버 설정

### **환경: /root/uvis 서버**

### **Step 1: `.env.prod` 파일 생성/수정**

```bash
cd /root/uvis
nano .env.prod
```

**추가 내용:**
```bash
# OpenAI API (ChatGPT-4)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Gemini API (선택 사항)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**전체 `.env.prod` 예시:**
```bash
# Application
APP_ENV=production
APP_NAME=Cold Chain Dispatch System
SECRET_KEY=your_production_secret_key_here

# Database (PostgreSQL)
DATABASE_URL=postgresql://postgres:your_password@postgres:5432/cold_chain

# OpenAI API
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Gemini API (선택 사항)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Naver Map API
NAVER_MAP_CLIENT_ID=your_naver_map_client_id
NAVER_MAP_CLIENT_SECRET=your_naver_map_client_secret

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# CORS
CORS_ORIGINS=http://139.150.11.99,https://yourdomain.com

# API Settings
API_PREFIX=/api/v1
```

### **Step 2: Docker Compose 확인**

```bash
cd /root/uvis
cat docker-compose.prod.yml | grep -A 5 "environment:"
```

**확인 사항:**
- `env_file: .env.prod` 설정 확인
- 또는 `environment:` 섹션에 직접 설정

**방법 A: env_file 사용 (권장)**
```yaml
services:
  backend:
    env_file:
      - .env.prod
```

**방법 B: environment 직접 설정**
```yaml
services:
  backend:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
```

### **Step 3: 백엔드 재배포**

```bash
cd /root/uvis

# 백엔드 컨테이너 재시작 (환경변수 반영)
docker-compose -f docker-compose.prod.yml down backend
docker-compose -f docker-compose.prod.yml up -d backend

# 로그 확인
docker logs uvis-backend --tail 50
```

**성공 로그 확인:**
```
✅ OpenAI API Key configured
✅ Using model: gpt-4o
✅ AIChatService initialized successfully
```

### **Step 4: 컨테이너 내부 환경변수 확인**

```bash
# 백엔드 컨테이너 접속
docker exec -it uvis-backend bash

# 환경변수 확인
echo $OPENAI_API_KEY

# Python에서 확인
python3 << EOF
import os
print(f"OpenAI Key: {os.getenv('OPENAI_API_KEY')[:20]}...")
EOF

# 종료
exit
```

---

## 4️⃣ API 키 테스트

### **방법 1: 직접 API 테스트 (추천)**

```bash
cd /home/user/webapp/backend

# Python 스크립트로 테스트
python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    print("🧪 OpenAI API 테스트 중...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "Hello! 간단히 응답해줘."}
        ],
        max_tokens=50
    )
    
    print("✅ API 연결 성공!")
    print(f"응답: {response.choices[0].message.content}")
    print(f"사용 토큰: {response.usage.total_tokens}")
    print(f"예상 비용: ${response.usage.total_tokens * 0.00002:.6f}")
    
except Exception as e:
    print(f"❌ 오류: {e}")
EOF
```

**예상 출력:**
```
🧪 OpenAI API 테스트 중...
✅ API 연결 성공!
응답: 안녕하세요! 무엇을 도와드릴까요?
사용 토큰: 45
예상 비용: $0.000900
```

### **방법 2: AI 채팅 UI로 테스트**

```
1️⃣ 접속: http://localhost:3000 (개발) 또는 http://139.150.11.99 (프로덕션)
2️⃣ 로그인
3️⃣ 사이드바 → "💬 AI 주문 어시스턴트"
4️⃣ 테스트 메시지 입력:
```

**테스트 메시지:**
```
서울에서 부산으로 냉동 10팔레트 보내줘
```

**기대 결과:**
- ✅ AI 응답 즉시 표시
- ✅ 주문 정보 파싱
- ✅ "추출된 주문 정보" 카드 표시

**실패 시:**
- ❌ "죄송합니다. 처리 중 오류가 발생했습니다"
- → 백엔드 로그 확인 필요

### **방법 3: API 엔드포인트 직접 호출**

```bash
# 로그인 토큰 획득 (먼저)
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password" | jq -r '.access_token')

# AI 채팅 API 호출
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

## 5️⃣ 비용 관리

### **1. OpenAI 대시보드에서 모니터링**

```
접속: https://platform.openai.com/usage
```

**확인 항목:**
- 일별 사용량 (USD)
- 모델별 요청 수
- 토큰 사용량
- 남은 크레딧

### **2. 시스템 내장 비용 모니터링**

```
접속: http://139.150.11.99/ai-cost (ADMIN 전용)
```

**확인 가능한 정보:**
- 실시간 비용 추적
- 모델별 비용 분포
- 날짜별 비용 추이
- Intent별 비용

### **3. 사용량 한도 설정 (권장)**

```
1. 접속: https://platform.openai.com/account/limits
2. "Usage limits" 섹션
3. Monthly budget 설정 (예: $50)
4. 임계값 알림 설정 (예: $40에서 이메일)
```

### **4. 비용 절감 팁**

#### **자동 모델 선택 (향후 구현 예정)**

```python
# 주문 복잡도에 따라 모델 자동 선택
if order_count == 1 and pallet_count < 10:
    model = "gpt-3.5-turbo"  # 10배 저렴
elif order_count >= 3:
    model = "gpt-4o"  # 정확도 우선
else:
    model = "gemini-pro"  # 무료
```

#### **개발/테스트 환경 분리**

```bash
# 개발 환경: Gemini 사용 (무료)
APP_ENV=development
GEMINI_API_KEY=your_gemini_key

# 프로덕션: GPT-4 사용
APP_ENV=production
OPENAI_API_KEY=your_openai_key
```

#### **캐싱 활용**

```python
# 동일한 질문 반복 시 캐시된 응답 사용
# (향후 Redis 캐싱 구현 예정)
```

---

## 6️⃣ 문제 해결

### **문제 1: API 키가 인식되지 않음**

**증상:**
```
⚠️ OpenAI API 키가 설정되지 않았습니다
⚠️ AI 모델이 설정되지 않았습니다. 시뮬레이션 모드로 실행됩니다.
```

**해결:**

```bash
# 1. 환경변수 확인
cd /home/user/webapp/backend
cat .env | grep OPENAI

# 2. 환경변수 형식 확인 (따옴표 없어야 함)
# ✅ 올바름: OPENAI_API_KEY=sk-proj-xxx
# ❌ 잘못됨: OPENAI_API_KEY="sk-proj-xxx"

# 3. 백엔드 재시작
# Ctrl+C로 종료 후
uvicorn main:app --reload
```

---

### **문제 2: 401 Unauthorized**

**증상:**
```
❌ OpenAI API 오류: 401 Unauthorized
```

**원인:**
- API 키가 잘못됨
- API 키가 만료됨
- 결제 정보 미등록

**해결:**

```bash
# 1. API 키 재확인
# https://platform.openai.com/api-keys

# 2. 새 API 키 생성
# 기존 키 삭제 → 새 키 생성

# 3. .env 파일 업데이트
nano /home/user/webapp/backend/.env

# 4. 결제 정보 확인
# https://platform.openai.com/account/billing/overview
```

---

### **문제 3: 429 Too Many Requests**

**증상:**
```
❌ OpenAI API 오류: 429 Too Many Requests
```

**원인:**
- Rate limit 초과
- 무료 플랜의 일일 한도 초과

**해결:**

```bash
# 1. OpenAI 대시보드 확인
# https://platform.openai.com/account/limits

# 2. Tier 업그레이드
# Tier 1 → Tier 2로 업그레이드 (사용량 증가 시 자동)

# 3. 임시 대안: Gemini 사용
# .env 파일에 GEMINI_API_KEY 추가
```

**Rate Limits (Tier 1):**
- GPT-4o: 500 requests/day
- GPT-3.5: 3,500 requests/day

---

### **문제 4: 500 Internal Server Error**

**증상:**
```
❌ OpenAI API 오류: 500 Internal Server Error
```

**원인:**
- OpenAI 서비스 장애
- 네트워크 문제

**해결:**

```bash
# 1. OpenAI 상태 확인
# https://status.openai.com

# 2. 자동 폴백 확인
# 시스템이 자동으로 시뮬레이션 모드로 전환해야 함

# 3. 로그 확인
docker logs uvis-backend --tail 100 | grep "OpenAI"
```

---

### **문제 5: 응답이 느림 (10초+)**

**증상:**
- AI 응답 시간이 10초 이상 소요

**원인:**
- GPT-4 모델의 긴 응답 시간
- 네트워크 지연

**해결:**

```python
# 1. GPT-3.5 Turbo로 전환 (2-3초)
# AI 채팅 UI에서 모델 선택 → "GPT-3.5 Turbo"

# 2. max_tokens 줄이기 (응답 시간 단축)
response = client.chat.completions.create(
    model="gpt-4o",
    max_tokens=1000,  # 기본 2000 → 1000
    temperature=0.3
)

# 3. 타임아웃 설정 확인
# frontend/src/api/client.ts
timeout: 30000,  # 30초
```

---

## 📚 추가 리소스

### **공식 문서**
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI Pricing](https://openai.com/pricing)
- [OpenAI Rate Limits](https://platform.openai.com/docs/guides/rate-limits)

### **모범 사례**
- [Best Practices for API Key Safety](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)

### **비용 최적화**
- [Optimizing LLM Applications](https://platform.openai.com/docs/guides/production-best-practices)
- [Token Counting Guide](https://platform.openai.com/tokenizer)

---

## ✅ 설정 완료 체크리스트

- [ ] OpenAI 계정 생성 완료
- [ ] API 키 발급 및 안전하게 저장
- [ ] 결제 정보 등록 및 한도 설정 ($50/월 권장)
- [ ] `.env` 파일에 API 키 추가
- [ ] 백엔드 재시작 및 로그 확인
- [ ] AI 채팅 UI로 테스트 성공
- [ ] 비용 모니터링 대시보드 확인 (/ai-cost)
- [ ] OpenAI 대시보드에서 사용량 모니터링 설정

---

## 🎯 다음 단계

1. **프로덕션 서버에 배포**
   ```bash
   cd /root/uvis
   # .env.prod 파일 수정
   # 백엔드 재배포
   ```

2. **비용 모니터링 설정**
   - OpenAI 대시보드에서 알림 설정
   - 시스템 대시보드 (/ai-cost) 정기 확인

3. **비용 최적화**
   - 단순 주문 → GPT-3.5 전환 검토
   - 개발 환경 → Gemini 사용 검토

---

## ❓ 문의

문제가 계속되면:
1. 백엔드 로그 확인: `docker logs uvis-backend --tail 100`
2. OpenAI 상태 페이지 확인: https://status.openai.com
3. API 키 재발급 시도

---

**마지막 업데이트**: 2026-02-01
