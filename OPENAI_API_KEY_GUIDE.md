# 🔑 OpenAI API 키 발급 완벽 가이드

## 📋 목차
1. [회원가입 및 로그인](#1-회원가입-및-로그인)
2. [API 키 생성](#2-api-키-생성)
3. [결제 방법 설정](#3-결제-방법-설정)
4. [사용량 제한 설정](#4-사용량-제한-설정-권장)
5. [API 키 확인 및 테스트](#5-api-키-확인-및-테스트)

---

## 1. 회원가입 및 로그인

### 단계 1-1: OpenAI 플랫폼 접속
```
https://platform.openai.com
```

![OpenAI Platform](https://platform.openai.com)

### 단계 1-2: 계정 생성
- **신규 사용자**: "Sign up" 클릭
- **기존 사용자**: "Log in" 클릭

#### 가입 방법 (3가지)
1. **Google 계정으로 가입** (권장 - 가장 빠름)
   - "Continue with Google" 클릭
   - Google 계정 선택
   
2. **Microsoft 계정으로 가입**
   - "Continue with Microsoft" 클릭
   - Microsoft 계정 로그인
   
3. **이메일로 가입**
   - 이메일 주소 입력
   - 비밀번호 생성 (8자 이상)
   - 이메일 인증 완료

### 단계 1-3: 전화번호 인증
- 전화번호 입력 (한국: +82)
- SMS로 받은 인증 코드 입력
- ⚠️ **중요**: 한 전화번호당 하나의 계정만 가능

---

## 2. API 키 생성

### 단계 2-1: API Keys 페이지 이동
```
https://platform.openai.com/api-keys
```

또는:
1. 로그인 후 좌측 메뉴에서 **"API keys"** 클릭
2. 대시보드 우측 상단 프로필 → **"View API keys"**

### 단계 2-2: 새 API 키 생성

#### 방법 A: 기본 키 생성 (간단)
1. **"Create new secret key"** 버튼 클릭
2. 키 이름 입력 (예: "UVIS Production")
3. **"Create secret key"** 클릭

#### 방법 B: 프로젝트별 키 생성 (권장)
1. **"Create new secret key"** 클릭
2. **Key name**: `UVIS-Production-Key` (알아보기 쉬운 이름)
3. **Permissions**: 
   - ✅ `All` (모든 권한)
   - 또는 `Restricted` 선택 후:
     - ✅ `Model capabilities` (필수)
     - ✅ `Models` → `gpt-4`, `gpt-3.5-turbo`
4. **Projects** (선택사항):
   - 프로젝트가 있으면 선택
   - 없으면 **"Default project"** 그대로
5. **"Create secret key"** 클릭

### 단계 2-3: API 키 복사 및 보관

⚠️ **매우 중요!**
```
생성 즉시 나타나는 API 키는 딱 한 번만 보입니다!
반드시 안전한 곳에 저장하세요.
```

**API 키 형식:**
```
sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 안전한 보관 방법:

**방법 1: 비밀번호 관리자 사용 (최고 권장)**
- 1Password
- LastPass
- Bitwarden

**방법 2: 암호화된 메모**
- 컴퓨터 메모장에 저장 금지 ❌
- 클라우드 암호화 저장소 사용 ✅

**방법 3: 환경변수 파일**
```bash
# .env.prod (서버에서만 보관)
OPENAI_API_KEY=sk-proj-your-key-here
```

---

## 3. 결제 방법 설정

### ⚠️ 중요: 무료 크레딧 확인

OpenAI는 신규 가입 시 **$5 무료 크레딧**을 제공합니다.
- 유효기간: 가입 후 3개월
- 확인: https://platform.openai.com/account/billing/overview

### 단계 3-1: 결제 페이지 이동
```
https://platform.openai.com/account/billing/overview
```

### 단계 3-2: 결제 방법 추가

1. **"Add payment method"** 클릭

2. **결제 방법 선택:**

#### 옵션 A: 신용카드/체크카드 (가장 일반적)
```
✅ Visa
✅ Mastercard
✅ American Express
✅ 국내 체크카드 (Visa/Master 로고 있는 것)
```

**입력 정보:**
- 카드 번호 (16자리)
- 만료일 (MM/YY)
- CVC (뒷면 3자리)
- 카드 소유자 이름 (영문)
- 청구 주소 (영문)

#### 옵션 B: PayPal
- PayPal 계정 연결

#### 옵션 C: 기업용 - 송금
- 최소 $1,000부터 가능

### 단계 3-3: 자동 충전 설정 (선택)

**"Auto-recharge"** 설정:
- 잔액이 특정 금액 이하로 떨어지면 자동 충전
- 권장 설정:
  ```
  잔액 $5 이하 → $10 자동 충전
  ```

### 단계 3-4: 초기 충전 (선택)

무료 크레딧이 없거나 더 필요하면:
1. **"Add credits"** 클릭
2. 금액 선택 (최소 $5)
3. 결제 완료

**권장 초기 충전:**
- 테스트용: $10 (약 14,000원)
- 실제 운영: $50 (약 70,000원)

---

## 4. 사용량 제한 설정 (권장)

### 왜 필요한가?
```
예기치 않은 과금을 방지하기 위해 반드시 설정하세요!
```

### 단계 4-1: 사용량 제한 페이지
```
https://platform.openai.com/account/billing/limits
```

### 단계 4-2: 월간 한도 설정

**"Usage limits"** 섹션:

1. **Monthly budget cap** 설정:
   ```
   권장: $50/month (월 약 70,000원)
   테스트: $10/month (월 약 14,000원)
   ```

2. **Email notification** 설정:
   ```
   ✅ 80% 도달 시 알림
   ✅ 100% 도달 시 알림
   ```

### 단계 4-3: 하드 리밋 설정 (강력 권장)

**"Hard limit"** 활성화:
```
✅ Stop usage when limit is reached
```

이렇게 하면:
- 한도 초과 시 API 자동 차단
- 추가 과금 없음
- 안심하고 사용 가능

---

## 5. API 키 확인 및 테스트

### 단계 5-1: 키 목록 확인

```
https://platform.openai.com/api-keys
```

생성된 키 목록에서:
- ✅ 키 이름
- ✅ 생성 날짜
- ✅ 마지막 사용 날짜
- ✅ 권한

### 단계 5-2: 테스트 (옵션 1 - 간단)

**curl로 테스트:**

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-proj-your-key-here" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**예상 응답:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      }
    }
  ]
}
```

### 단계 5-3: 테스트 (옵션 2 - Python)

```python
from openai import OpenAI

client = OpenAI(api_key="sk-proj-your-key-here")

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

### 단계 5-4: 사용량 모니터링

```
https://platform.openai.com/account/usage
```

확인 항목:
- 📊 일별 사용량
- 💰 예상 비용
- 📈 사용 추이

---

## 🔒 보안 주의사항

### ✅ 해야 할 것

1. **API 키를 안전하게 보관**
   - 환경변수로 저장
   - 코드에 직접 입력 금지
   - Git에 커밋 금지

2. **정기적으로 키 교체**
   - 3-6개월마다 새 키 생성
   - 구 키 삭제

3. **사용량 모니터링**
   - 주간 사용량 확인
   - 이상 활동 감지

### ❌ 하면 안 되는 것

1. **공개 저장소에 키 업로드**
   ```bash
   # 절대 이렇게 하지 마세요!
   git add .env
   git commit -m "add api key"  # ❌❌❌
   ```

2. **브라우저/클라이언트에서 사용**
   ```javascript
   // 프런트엔드에서 절대 사용 금지! ❌
   const apiKey = "sk-proj-...";
   ```

3. **여러 사람과 키 공유**
   - 각자 별도 계정/키 사용
   - 팀용은 Organization 기능 사용

---

## 💡 자주 묻는 질문 (FAQ)

### Q1: API 키를 잃어버렸어요
**A:** 다시 볼 수 없습니다. 새 키를 만들어야 합니다.
1. 기존 키 삭제 (Revoke)
2. 새 키 생성
3. 서버 환경변수 업데이트

### Q2: 무료로 사용할 수 있나요?
**A:** 신규 가입 시 $5 무료 크레딧 제공 (3개월 유효)
- GPT-3.5: 약 7,000건 주문 처리 가능
- GPT-4: 약 500건 주문 처리 가능

### Q3: 결제 카드가 필요한가요?
**A:** API 사용을 위해서는 결제 방법 등록 필수
- 무료 크레딧만 쓰더라도 카드 등록 필요
- 충전 없이 카드만 등록도 가능

### Q4: 한도를 초과하면 어떻게 되나요?
**A:** Hard limit 설정 여부에 따라:
- Hard limit ON: API 차단, 추가 과금 없음 ✅
- Hard limit OFF: 계속 사용, 과금 계속 ⚠️

### Q5: 여러 프로젝트에 같은 키를 써도 되나요?
**A:** 가능하지만 권장하지 않습니다.
- 프로젝트별 키 생성 권장
- 보안 및 사용량 추적에 유리

### Q6: 키가 유출되었어요!
**A:** 즉시 조치:
1. https://platform.openai.com/api-keys 접속
2. 해당 키 옆 "Revoke" 클릭
3. 새 키 생성
4. 서버 환경변수 업데이트
5. 사용량 확인 (이상 과금 체크)

### Q7: Organization vs Personal 계정?
**A:** 
- **Personal**: 개인 사용 (시작하기 좋음)
- **Organization**: 팀 사용 (권한 관리, 더 높은 한도)

### Q8: GPT-4와 GPT-3.5 중 어떤 걸 쓸까요?
**A:**
- **테스트/개발**: GPT-3.5 (저렴, 빠름)
- **실제 운영**: GPT-4 (정확, 자연스러움)
- 비용 차이: GPT-4가 약 14배 비쌈

---

## 📊 비용 계산기

### GPT-3.5 Turbo

| 항목 | 가격 | 주문 1건 | 월 100건 | 월 1,000건 |
|------|------|---------|---------|-----------|
| 입력 | $0.0005/1K tokens | - | - | - |
| 출력 | $0.0015/1K tokens | - | - | - |
| **총** | - | **$0.0005** | **$0.05** | **$0.50** |
| **한화** | - | **약 0.7원** | **약 70원** | **약 700원** |

### GPT-4 Turbo

| 항목 | 가격 | 주문 1건 | 월 100건 | 월 1,000건 |
|------|------|---------|---------|-----------|
| 입력 | $0.01/1K tokens | - | - | - |
| 출력 | $0.03/1K tokens | - | - | - |
| **총** | - | **$0.007** | **$0.70** | **$7.00** |
| **한화** | - | **약 10원** | **약 1,000원** | **약 10,000원** |

### 무료 크레딧으로 얼마나 쓸 수 있나?

**$5 무료 크레딧으로:**
- GPT-3.5: 약 **10,000건** 주문 처리
- GPT-4: 약 **700건** 주문 처리

---

## 🎯 다음 단계

API 키 발급 완료! 이제:

1. ✅ **서버 설정**: `OPENAI_SETUP.md` 참고
2. ✅ **환경변수 추가**: `.env.prod` 파일
3. ✅ **재배포**: Docker Compose 재시작
4. ✅ **테스트**: AI 채팅 사용

---

## 📞 도움이 필요하면

- **OpenAI 공식 문서**: https://platform.openai.com/docs
- **API 상태**: https://status.openai.com
- **커뮤니티**: https://community.openai.com
- **지원팀**: https://help.openai.com

---

**이제 ChatGPT의 강력한 자연어 이해 능력을 사용할 준비가 되었습니다!** 🎉
