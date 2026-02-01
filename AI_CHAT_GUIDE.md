# 🤖 AI 채팅 기반 주문 등록/수정 시스템

## 📋 개요

자연어 채팅으로 주문을 등록하고 수정할 수 있는 AI 어시스턴트 시스템입니다.

---

## ✨ 주요 기능

### 1. **자연어 주문 입력**
```
사용자: "서울에서 부산으로 냉동 10팔레트 500kg 보내줘"
AI: "다음 정보로 주문을 등록하시겠습니까?
     • 온도대: 냉동
     • 상차지: 서울
     • 하차지: 부산
     • 팔레트: 10개
     • 중량: 500kg
     
     등록하시려면 '네' 또는 '확인'을 입력해주세요."
```

### 2. **시간 정보 자동 파싱**
```
사용자: "내일 오전 9시 상차, 오후 2시 하차"
AI: (상차시간: 09:00, 하차시간: 14:00으로 자동 변환)
```

### 3. **주문 수정** (개발 중)
```
사용자: "주문번호 ORD-12345 중량 600kg로 변경"
AI: "주문 ORD-12345가 수정되었습니다!"
```

---

## 🚀 배포 방법

### 1. **코드 업데이트**
```bash
cd /root/uvis
git pull origin genspark_ai_developer
```

### 2. **환경변수 설정 (선택사항)**

OpenAI API를 사용하려면 `.env` 파일에 추가:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

**주의**: API 키가 없어도 시뮬레이션 모드로 작동합니다!

### 3. **백엔드 재빌드**
```bash
docker-compose -f docker-compose.prod.yml stop backend
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml up -d backend
```

### 4. **프론트엔드 재빌드**
```bash
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

### 5. **상태 확인**
```bash
docker-compose -f docker-compose.prod.yml ps
docker logs uvis-backend --tail 50
```

---

## 📱 사용 방법

### **1단계: AI 주문 어시스턴트 접속**
1. 브라우저에서 `http://139.150.11.99` 접속
2. 로그인
3. 사이드바에서 **"💬 AI 주문 어시스턴트"** 클릭

### **2단계: 자연어로 주문 입력**

#### **예시 1: 기본 주문**
```
서울에서 부산으로 냉동 10팔레트 500kg 보내줘
```

#### **예시 2: 시간 포함**
```
인천에서 대전으로 냉장 5팔레트 300kg, 내일 오전 9시 상차, 오후 3시 하차
```

#### **예시 3: 상세 정보**
```
경기도 성남시에서 서울 강남구로 상온 15팔레트 800kg 2.5cbm 보내줘
```

### **3단계: 주문 확인**
AI가 추출한 정보를 확인하고:
- **등록하기** 버튼 클릭 → 주문 등록
- **취소** 버튼 클릭 → 다시 입력

### **4단계: 완료**
```
✅ 주문 ORD-1737418234567이(가) 등록되었습니다!
```

---

## 🎯 지원되는 입력 패턴

### **온도대**
- "냉동" → 냉동
- "냉장" → 냉장
- "상온" → 상온

### **위치**
- "서울에서 부산으로" → 상차지: 서울, 하차지: 부산
- "경기도 성남시" → 주소 자동 저장

### **수량**
- "10팔레트" → pallet_count: 10
- "500kg" → weight_kg: 500
- "2.5cbm" → volume_cbm: 2.5

### **시간**
- "오전 9시" → 09:00
- "오후 2시" → 14:00
- "14시 30분" → 14:30
- "상차 09:00, 하차 14:00" → pickup: 09:00, delivery: 14:00

### **날짜**
- "오늘" → 오늘 날짜
- "내일" → 내일 날짜
- "2024-02-05" → 2024-02-05

---

## 🧪 테스트 시나리오

### **테스트 1: 기본 주문**
```
입력: "서울에서 부산으로 냉동 10팔레트 500kg"

예상 결과:
✅ 온도대: 냉동
✅ 상차지: 서울
✅ 하차지: 부산
✅ 팔레트: 10개
✅ 중량: 500kg
```

### **테스트 2: 시간 포함**
```
입력: "인천에서 대전으로 냉장 5팔레트, 내일 오전 9시 상차, 오후 2시 하차"

예상 결과:
✅ 온도대: 냉장
✅ 상차지: 인천
✅ 하차지: 대전
✅ 팔레트: 5개
✅ 상차시간: 09:00
✅ 하차시간: 14:00
✅ 주문일자: 내일 날짜
```

### **테스트 3: 상세 정보**
```
입력: "경기도 성남시에서 서울 강남구로 상온 15팔레트 800kg 2.5cbm"

예상 결과:
✅ 온도대: 상온
✅ 상차지: 경기도 성남시
✅ 하차지: 서울 강남구
✅ 팔레트: 15개
✅ 중량: 800kg
✅ 부피: 2.5cbm
```

---

## 🔧 기술 스택

### **프론트엔드**
- React + TypeScript
- Tailwind CSS
- Lucide React Icons
- React Hot Toast

### **백엔드**
- FastAPI
- Python 3.11
- SQLAlchemy
- OpenAI API (선택사항)

### **AI 처리**
- **모드 1**: OpenAI GPT-4 (API 키 설정 시)
- **모드 2**: 시뮬레이션 (정규식 기반 패턴 매칭)

---

## 📊 시스템 구조

```
사용자 입력
    ↓
Frontend (AIChatPage.tsx)
    ↓
API (/api/v1/ai-chat/process)
    ↓
AIChatService
    ├─→ OpenAI GPT-4 (API 키 있음)
    └─→ Simulation Mode (API 키 없음)
    ↓
주문 정보 추출
    ↓
검증 및 확인 요청
    ↓
주문 생성 (Order 테이블)
```

---

## ⚙️ 환경변수

| 변수 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `OPENAI_API_KEY` | ❌ | None | OpenAI API 키 (선택사항) |

**주의**: API 키 없이도 시뮬레이션 모드로 동작합니다!

---

## 🐛 트러블슈팅

### **문제 1: AI 응답이 느림**
```bash
# 로그 확인
docker logs uvis-backend --tail 100 | grep "AI"

# OpenAI API 호출 시간 확인
# 예상: 1-3초 (GPT-4)
```

### **문제 2: 주문 정보 추출 실패**
- **시뮬레이션 모드**: 더 명확한 패턴으로 입력
  ```
  예: "서울에서 부산으로 냉동 10팔레트 500kg"
  ```
- **OpenAI 모드**: API 키 확인 및 로그 체크

### **문제 3: 채팅 UI가 표시되지 않음**
```bash
# 프론트엔드 재빌드
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml up -d frontend

# 브라우저 캐시 삭제 (Ctrl + Shift + R)
```

---

## 📈 향후 개선 계획

### **Phase 4: 고급 기능** (예정)
- [ ] 음성 입력 지원 (Speech-to-Text)
- [ ] 주문 조회 기능
- [ ] 대화 기록 저장
- [ ] 거래처 자동 매칭
- [ ] 다국어 지원

### **Phase 5: AI 개선** (예정)
- [ ] Fine-tuning 모델
- [ ] 더 정확한 주소 파싱
- [ ] 자동 견적 계산
- [ ] 배차 제안

---

## 📝 커밋 정보

- **커밋**: `c798dee`
- **브랜치**: `genspark_ai_developer`
- **PR**: https://github.com/rpaakdi1-spec/3-/pull/3

---

## 🎉 완성된 기능 체크리스트

- [x] 채팅 UI 구현
- [x] 자연어 파싱 (시뮬레이션 모드)
- [x] OpenAI GPT-4 연동 (선택사항)
- [x] 주문 정보 추출
- [x] 주문 확인 프로세스
- [x] 주문 생성 (DB 저장)
- [x] 오류 처리
- [x] 사이드바 메뉴 추가
- [x] 라우트 설정
- [x] API 엔드포인트

---

## 💡 사용 팁

1. **간단한 문장으로 시작**: "서울에서 부산으로 냉동 10팔레트"
2. **단계별 입력**: 먼저 기본 정보 → 시간 정보 추가
3. **확인 후 수정**: AI가 잘못 이해했다면 취소 후 다시 입력
4. **구체적인 표현**: "서울" 보다는 "서울시 강남구"가 더 정확

---

## 🆘 지원

문제 발생 시:
1. 백엔드 로그 확인: `docker logs uvis-backend --tail 100`
2. 프론트엔드 콘솔 확인: 브라우저 F12 → Console
3. GitHub Issue 등록 또는 문의

---

**즐거운 주문 등록 되세요! 🚀**
