# 🔑 AI API 키 설정 가이드

**날짜**: 2026-02-02  
**소요 시간**: 15분  
**난이도**: ⭐ 쉬움

---

## 📋 준비 사항

### 필요한 것
- [ ] OpenAI API 키 (필수)
- [ ] Gemini API 키 (선택)
- [ ] 서버 SSH 접속 권한 (root@139.150.11.99)

### API 키 발급 링크
1. **OpenAI**: https://platform.openai.com/api-keys
2. **Gemini**: https://makersuite.google.com/app/apikey

---

## 🚀 Step 1: OpenAI API 키 발급 (5분)

### 1.1 OpenAI 플랫폼 접속
1. https://platform.openai.com/ 접속
2. 로그인 (계정이 없으면 Sign up)
3. 좌측 메뉴에서 **API keys** 클릭

### 1.2 API 키 생성
1. **"Create new secret key"** 버튼 클릭
2. 키 이름 입력 (예: `UVIS-Production`)
3. **"Create secret key"** 클릭
4. ⚠️ **중요**: 생성된 키를 즉시 복사! (다시 볼 수 없음)
   ```
   sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 1.3 API 키 형식 확인
```
✅ 올바른 형식: sk-proj-... (최신)
✅ 올바른 형식: sk-... (구형)
❌ 잘못된 형식: API_KEY_HERE
```

### 1.4 사용량 및 요금 설정 (선택)
1. **Usage** 메뉴에서 사용량 확인
2. **Billing** → **Usage limits** 설정 (예: $10/월)
3. 결제 방법 등록 (신용카드)

**💡 팁**: 무료 크레딧이 있다면 먼저 사용됩니다!

---

## 🔧 Step 2: 서버에 API 키 설정 (5분)

### 2.1 서버 접속
```bash
# SSH로 서버 접속
ssh root@139.150.11.99

# 작업 디렉토리 이동
cd /root/uvis

# 현재 위치 확인
pwd
# 출력: /root/uvis
```

### 2.2 .env 파일 백업
```bash
# 백업 생성 (날짜 포함)
cp .env .env.backup_$(date +%Y%m%d_%H%M%S)

# 백업 확인
ls -lh .env*
```

### 2.3 .env 파일 편집
```bash
# nano 에디터로 열기 (추천)
nano .env

# 또는 vi 에디터
vi .env
```

### 2.4 API 키 추가
**파일 하단에 다음 내용 추가**:

```env
# ==========================================
# AI API Configuration (Added: 2026-02-02)
# ==========================================

# OpenAI API Key (필수)
OPENAI_API_KEY=sk-proj-your-actual-api-key-here

# Gemini API Key (선택 - Google AI)
# GEMINI_API_KEY=your-gemini-api-key-here

# AI 기능 활성화
ENABLE_AI_FEATURES=true

# AI 모델 설정
AI_MODEL=gpt-4
AI_MODEL_TEMPERATURE=0.7

# AI 비용 제한 (선택)
AI_MAX_COST_PER_REQUEST=0.5
AI_DAILY_BUDGET=10.0
```

**⚠️ 주의사항**:
- `sk-proj-your-actual-api-key-here` 부분을 실제 API 키로 교체
- 키 앞뒤에 공백이나 따옴표 없이 입력
- 줄바꿈 없이 한 줄로 입력

### 2.5 파일 저장 및 종료
**nano 에디터**:
- `Ctrl + O` (저장)
- `Enter` (확인)
- `Ctrl + X` (종료)

**vi 에디터**:
- `ESC` 키 누르기
- `:wq` 입력 후 `Enter` (저장 및 종료)

### 2.6 설정 확인
```bash
# API 키가 제대로 설정되었는지 확인
grep OPENAI_API_KEY .env

# 출력 예시:
# OPENAI_API_KEY=sk-proj-abc123...

# AI 기능 설정 확인
grep "ENABLE_AI_FEATURES\|AI_MODEL" .env
```

---

## 🔄 Step 3: Backend 재시작 (3분)

### 3.1 Backend 컨테이너 재시작
```bash
cd /root/uvis

# Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 재시작 확인
docker ps | grep uvis-backend
```

### 3.2 재시작 대기
```bash
# 30초 대기 (Backend 초기화 시간)
sleep 30

# 또는 로그를 실시간으로 확인
docker logs -f uvis-backend
# (Ctrl+C로 종료)
```

### 3.3 Backend 로그 확인
```bash
# 최근 로그 확인
docker logs uvis-backend --tail 50

# AI 관련 로그 필터링
docker logs uvis-backend --tail 100 | grep -i "openai\|ai\|api_key"

# 에러 확인
docker logs uvis-backend --tail 50 | grep -i error
```

**✅ 정상 출력 예시**:
```
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

**❌ 에러 발생 시**:
```
ERROR: Invalid API key
ERROR: OpenAI API key not configured
```
→ `.env` 파일의 API 키를 다시 확인하세요!

---

## ✅ Step 4: 기능 테스트 (2분)

### 4.1 Health Check
```bash
# Backend 상태 확인
curl -s http://localhost:8000/health | jq '.'

# 예상 출력:
# {
#   "status": "healthy",
#   "app_name": "Cold Chain Dispatch System",
#   "environment": "production"
# }
```

### 4.2 AI 사용 통계 확인
```bash
# AI 사용 통계 API 테스트
curl -s http://localhost:8000/api/v1/ai-usage/stats | jq '.'

# 예상 출력:
# {
#   "total_requests": 0,
#   "total_cost": 0.0,
#   "success_rate": 0.0,
#   "models": []
# }
```

### 4.3 AI 채팅 테스트 (선택)
```bash
# AI 채팅 API 테스트
curl -s -X POST http://localhost:8000/api/v1/ai-chat/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕하세요! 테스트 메시지입니다."
  }' | jq '.'

# 예상 출력:
# {
#   "response": "안녕하세요! 무엇을 도와드릴까요?",
#   "model": "gpt-4",
#   "cost": 0.002,
#   "tokens_used": 25
# }
```

### 4.4 브라우저에서 확인
1. http://139.150.11.99 접속
2. 로그인
3. **AI 채팅** 메뉴 클릭
4. 테스트 메시지 전송
5. **AI 비용 대시보드** 메뉴 클릭
6. 실시간 비용 데이터 확인

---

## 🎯 성공 기준

### ✅ 다음 항목이 모두 확인되면 성공!

- [ ] `.env` 파일에 OPENAI_API_KEY 추가됨
- [ ] Backend 컨테이너가 정상 재시작됨
- [ ] Health Check API가 정상 응답함
- [ ] AI 사용 통계 API가 응답함 (에러 없음)
- [ ] AI 채팅에서 응답을 받음
- [ ] AI 비용 대시보드에 데이터가 표시됨

---

## 🔧 문제 해결

### 문제 1: "Invalid API key" 에러
**원인**: API 키가 잘못되었거나 유효하지 않음

**해결**:
```bash
# .env 파일 확인
cat .env | grep OPENAI_API_KEY

# API 키 형식 확인 (sk-proj-... 또는 sk-...)
# 앞뒤 공백 제거
# OpenAI 플랫폼에서 키 재생성
```

---

### 문제 2: Backend 재시작 실패
**원인**: .env 파일 문법 오류 또는 Docker 문제

**해결**:
```bash
# 백업에서 복원
cp .env.backup_20260202_* .env

# Docker 전체 재시작
cd /root/uvis
docker-compose -f docker-compose.prod.yml down
sleep 10
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker logs uvis-backend --tail 100
```

---

### 문제 3: AI API 응답 없음
**원인**: OpenAI 서버 문제 또는 네트워크 문제

**해결**:
```bash
# OpenAI API 직접 테스트
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.'

# Backend에서 외부 연결 확인
docker exec uvis-backend ping -c 3 api.openai.com

# 방화벽 확인
iptables -L | grep -i openai
```

---

### 문제 4: 비용 폭탄 방지
**원인**: AI 사용량이 예상보다 많을 수 있음

**예방**:
```bash
# .env에 비용 제한 설정 추가
nano .env

# 추가할 내용:
AI_MAX_COST_PER_REQUEST=0.5
AI_DAILY_BUDGET=10.0
AI_MONTHLY_BUDGET=100.0

# OpenAI 플랫폼에서도 사용 한도 설정
# https://platform.openai.com/account/billing/limits
```

---

## 📊 모니터링

### 일일 비용 체크 (매일 확인 권장)
```bash
cd /root/uvis

# 오늘의 AI 비용 확인
curl -s "http://localhost:8000/api/v1/ai-usage/cost-summary?period=1d" | jq '.'

# 이번 주 비용
curl -s "http://localhost:8000/api/v1/ai-usage/cost-summary?period=7d" | jq '.'

# 이번 달 비용
curl -s "http://localhost:8000/api/v1/ai-usage/cost-summary?period=30d" | jq '.'
```

### 모델별 사용량 확인
```bash
# 모델별 통계
curl -s http://localhost:8000/api/v1/ai-usage/stats | jq '.models'

# 최근 사용 로그
curl -s "http://localhost:8000/api/v1/ai-usage/logs?limit=10" | jq '.items[]'
```

---

## 💡 권장 설정

### GPT-4 vs GPT-3.5-turbo
```env
# 고품질 응답 (비용 높음)
AI_MODEL=gpt-4
AI_MODEL_TEMPERATURE=0.7

# 빠른 응답 (비용 낮음)
AI_MODEL=gpt-3.5-turbo
AI_MODEL_TEMPERATURE=0.7

# 가장 저렴 (기본 응답)
AI_MODEL=gpt-3.5-turbo
AI_MODEL_TEMPERATURE=0.3
```

### 비용 최적화 팁
```env
# 1. 토큰 제한 설정
AI_MAX_TOKENS=500

# 2. 응답 캐싱 활성화
AI_ENABLE_CACHE=true
AI_CACHE_TTL=3600

# 3. Rate Limiting 설정
AI_RATE_LIMIT=10
AI_RATE_LIMIT_PERIOD=60
```

---

## 🎓 다음 단계

### ✅ AI 기능 활성화 완료 후:
1. **AB Test UI 활성화** (30분)
2. **Frontend 페이지 검증** (1시간)
3. **ML Dispatch 모니터링** (계속)

### 📚 참고 문서:
- `QUICK_START_NEXT_STEPS.md` - 다음 작업 가이드
- `NEXT_STEPS_PRIORITY.md` - 전체 로드맵
- `FINAL_SYSTEM_SUMMARY.md` - 시스템 요약

---

## 📞 지원

### OpenAI 관련
- **문서**: https://platform.openai.com/docs
- **API 참조**: https://platform.openai.com/docs/api-reference
- **커뮤니티**: https://community.openai.com/

### 프로젝트 관련
- **GitHub**: https://github.com/rpaakdi1-spec/3-
- **API 문서**: http://139.150.11.99:8000/docs

---

## ✅ 완료 체크리스트

**설정 완료 후 체크**:
- [ ] OpenAI API 키 발급 완료
- [ ] 서버 `.env` 파일에 키 추가
- [ ] Backend 재시작 성공
- [ ] Health Check 정상
- [ ] AI 채팅 테스트 성공
- [ ] AI 비용 대시보드 확인
- [ ] 비용 제한 설정 (선택)
- [ ] 모니터링 스크립트 확인

**모든 항목 체크 완료** → 🎉 **AI 기능 활성화 완료!**

---

## 🎯 예상 결과

### Before (API 키 설정 전)
```
❌ AI 채팅: "API key not configured"
❌ AI 비용: 데이터 없음
❌ AI 사용 통계: 모두 0
```

### After (API 키 설정 후)
```
✅ AI 채팅: 정상 응답
✅ AI 비용: 실시간 추적
✅ AI 사용 통계: 실시간 업데이트
```

---

**설정을 시작하시겠습니까?**

**추천 실행 순서**:
1. OpenAI API 키 발급 (5분)
2. 서버 `.env` 파일 수정 (3분)
3. Backend 재시작 (2분)
4. 기능 테스트 (5분)

**총 소요 시간**: 약 15분

---

**생성일**: 2026-02-02  
**버전**: 1.0

**프로젝트 성공을 응원합니다! 🚀**
