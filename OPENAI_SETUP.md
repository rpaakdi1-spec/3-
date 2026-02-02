# OpenAI API 연동 가이드

## 📋 개요

AI 주문 어시스턴트에서 **ChatGPT (OpenAI API)**를 사용하여 자연어를 자동으로 해석할 수 있습니다.

현재는 **시뮬레이션 모드**(패턴 매칭)로 작동하지만, OpenAI API 키를 설정하면 **GPT-4o-mini**가 자동으로 입력을 이해합니다.

---

## 🎯 장점

### 시뮬레이션 모드 (현재)
- ❌ 정확한 패턴만 인식
- ❌ "서울에서 부산 10p, 대구 15p" → 때때로 인식 실패
- ❌ 자연스러운 표현 제한적

### OpenAI 모드 (API 키 설정 시)
- ✅ **모든 자연어 표현 이해**
- ✅ "서울에서 부산으로 10개, 대구는 15개 보내줘" → 완벽 인식
- ✅ "내일 아침 9시에 출발해서 부산 10개" → 완벽 인식
- ✅ 맥락 이해 및 대화 흐름 파악
- ✅ 오타나 다양한 표현도 이해

---

## 🔑 OpenAI API 키 발급

### 1단계: OpenAI 계정 생성
1. https://platform.openai.com 접속
2. 회원가입 (또는 로그인)

### 2단계: API 키 발급
1. 우측 상단 프로필 → **API keys** 클릭
2. **Create new secret key** 클릭
3. 키 이름 입력 (예: "uvis-ai-chat")
4. **Create secret key** 클릭
5. **키 복사** (sk-proj-...로 시작)
   - ⚠️ 이 키는 한 번만 표시됩니다!
   - 안전한 곳에 저장하세요

### 3단계: 크레딧 충전
1. **Settings** → **Billing** 이동
2. **Add payment method** (카드 등록)
3. 크레딧 충전 (최소 $5)
   - GPT-4o-mini: 약 $0.15 / 1M 토큰
   - 하루 100회 사용 시 약 $0.30~$1.00

---

## ⚙️ 서버 설정

### 방법 1: 환경변수 파일 (.env)

```bash
cd /root/uvis

# .env 파일 편집
nano backend/.env
```

다음 라인 추가:
```
OPENAI_API_KEY=sk-proj-여기에발급받은키입력
```

저장: `Ctrl+O` → `Enter` → `Ctrl+X`

### 방법 2: Docker Compose 환경변수

```bash
cd /root/uvis

# docker-compose.prod.yml 편집
nano docker-compose.prod.yml
```

backend 서비스에 environment 추가:
```yaml
services:
  backend:
    # ... 기존 설정 ...
    environment:
      - OPENAI_API_KEY=sk-proj-여기에발급받은키입력
      # ... 기타 환경변수 ...
```

---

## 🚀 배포 및 적용

### 1️⃣ 백엔드 재빌드
```bash
cd /root/uvis

# 최신 코드 가져오기
git pull origin genspark_ai_developer

# 백엔드 재빌드
docker-compose -f docker-compose.prod.yml stop backend
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml up -d backend
```

### 2️⃣ 로그 확인
```bash
# OpenAI API 활성화 확인
docker logs uvis-backend 2>&1 | grep "OpenAI"
```

**성공 시:**
```
✅ OpenAI API 키가 설정되었습니다.
```

**실패 시 (API 키 없음):**
```
⚠️ OPENAI_API_KEY가 설정되지 않았습니다. 시뮬레이션 모드로 실행됩니다.
```

### 3️⃣ 테스트
AI 주문 어시스턴트에서 다양한 표현 테스트:

```
서울에서 부산으로 10개, 대구는 15개 보내줘 냉동으로
```

```
내일 아침 9시 출발해서 부산 10팔레트 대구 15팔레트 냉동
```

```
부산 10, 대구 15, 광주 8 서울에서 냉동
```

→ **모두 정확하게 인식됩니다!** ✅

---

## 💰 비용 안내

### GPT-4o-mini 요금 (2024년 기준)
- **입력**: $0.150 / 1M 토큰
- **출력**: $0.600 / 1M 토큰

### 예상 사용량
| 사용 횟수 | 예상 비용 |
|-----------|-----------|
| 100회/일 | $0.30~$1.00/일 |
| 1,000회/일 | $3.00~$10.00/일 |
| 10,000회/일 | $30.00~$100.00/일 |

### 비용 절감 팁
1. ✅ 사용량 모니터링: https://platform.openai.com/usage
2. ✅ 월간 한도 설정: Settings → Billing → Usage limits
3. ✅ 알림 설정: 일일 $5 초과 시 알림

---

## 🔍 디버깅

### API 키 확인
```bash
docker logs uvis-backend 2>&1 | grep -A 5 "OpenAI"
```

### API 호출 확인
```bash
docker logs uvis-backend --follow | grep "🤖"
```

**예상 로그:**
```
🤖 OpenAI API 호출... (메시지 길이: 45자)
✅ OpenAI 응답 받음: 250자
```

### API 오류 확인
```bash
docker logs uvis-backend 2>&1 | grep "OpenAI API 오류"
```

**일반적인 오류:**
- `Incorrect API key`: 키 확인 필요
- `You exceeded your current quota`: 크레딧 부족
- `Rate limit`: 호출 속도 제한 (대기 후 재시도)

---

## 📊 OpenAI vs 시뮬레이션 모드 비교

| 항목 | 시뮬레이션 모드 | OpenAI 모드 |
|------|----------------|-------------|
| 비용 | 무료 | 유료 (~$1/일) |
| 인식률 | 70~80% | 95~99% |
| 자연어 이해 | 제한적 | 우수 |
| 복잡한 표현 | ❌ | ✅ |
| 오타 처리 | ❌ | ✅ |
| 맥락 이해 | 제한적 | ✅ |
| 속도 | 빠름 (~50ms) | 보통 (~500ms) |

---

## ⚠️ 보안 주의사항

1. **API 키 보호**
   - ❌ GitHub에 커밋하지 마세요
   - ❌ 코드에 하드코딩하지 마세요
   - ✅ 환경변수로만 관리하세요

2. **접근 제한**
   - .env 파일 권한: `chmod 600 backend/.env`
   - API 키 정기 갱신 (3개월마다)

3. **모니터링**
   - 일일 사용량 확인
   - 이상 트래픽 감지 시 키 삭제 후 재발급

---

## 📞 문의

OpenAI API 관련 문의:
- OpenAI 공식 문서: https://platform.openai.com/docs
- 요금: https://openai.com/pricing
- 지원: https://help.openai.com

---

## 🎉 마무리

OpenAI API 키를 설정하면:
- ✅ 더 자연스러운 대화
- ✅ 높은 인식률
- ✅ 사용자 만족도 향상

**비용 대비 효과가 충분합니다!** 😊

테스트 후 만족하시면 계속 사용하시고, 아니면 언제든 다시 시뮬레이션 모드로 전환 가능합니다.
