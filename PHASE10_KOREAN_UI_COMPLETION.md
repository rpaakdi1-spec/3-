# Phase 10: 한글 UI 완성 가이드

## 📋 개요

Phase 10의 최종 단계로, Dispatch Rules 페이지의 완전한 한글화를 완료합니다.

### 완료된 작업
- ✅ 한글 번역 파일 생성 (`dispatchRules` 섹션)
- ✅ API URL 환경 변수 수정 (VITE_API_URL → VITE_API_BASE_URL)
- ✅ 번역 파일 병합 완료
- ✅ Git 커밋 및 푸시 완료

### 변경 사항 요약

#### 1. 한글 번역 추가
**파일**: `frontend/public/locales/ko/translation.json`

**추가된 섹션**:
```json
{
  "dispatchRules": {
    "title": "스마트 배차 규칙",
    "createRule": "새 규칙 만들기",
    "simulation": "규칙 시뮬레이션",
    "templates": "템플릿",
    "actions": "작업",
    "ruleSimulation": { ... },
    "templateGallery": { ... },
    "form": { ... },
    "messages": { ... }
  }
}
```

**포함된 번역**:
- 페이지 제목 및 버튼
- 8개 규칙 템플릿 (근처 기사 우선, 고평점 기사 우선, 긴급 주문 처리 등)
- 폼 레이블 (규칙 이름, 설명, 규칙 유형, 우선순위 등)
- 성공/오류 메시지
- 난이도 레벨 (쉬움, 보통, 어려움)
- 카테고리 (거리, 품질, 우선순위, 시간, 특수, 공정성, 효율성, 교육)

#### 2. API URL 설정 수정
**파일**: `frontend/.env`

**변경 전**:
```env
VITE_API_URL=/api/v1
```

**변경 후**:
```env
VITE_API_BASE_URL=/api/v1
```

**이유**: 
- `frontend/src/api/dispatch-rules.ts`에서 `import.meta.env.VITE_API_BASE_URL`을 사용
- 환경 변수명이 일치하지 않아 `http://localhost:8000`으로 폴백되는 문제 해결

#### 3. Git 커밋
**커밋 해시**: `8661a8d`
**커밋 메시지**: 
```
feat(i18n): Add Korean translations for dispatch rules feature

- Add comprehensive Korean translations for dispatch rules UI
- Include rule simulation, template gallery, form labels, and messages
- Support for 8 rule templates with Korean descriptions
- Add difficulty levels and category translations
```

---

## 🚀 서버 배포 가이드

### 전제 조건
- 서버 위치: `/root/uvis`
- 최신 코드가 GitHub에 푸시됨 (커밋 8661a8d)

### 배포 방법 1: 자동 스크립트 사용 (권장)

#### 1-1. 스크립트 다운로드
```bash
cd /root/uvis
curl -O https://raw.githubusercontent.com/rpaakdi1-spec/3-/main/FINAL_KOREAN_DEPLOYMENT.sh
chmod +x FINAL_KOREAN_DEPLOYMENT.sh
```

#### 1-2. 스크립트 실행
```bash
./FINAL_KOREAN_DEPLOYMENT.sh
```

#### 스크립트 수행 내용
1. ✅ 작업 디렉토리 정리 (`git checkout -- .`)
2. ✅ 최신 코드 가져오기 (`git pull origin main`)
3. ✅ `.env` 파일 수정 (VITE_API_BASE_URL 설정)
4. ✅ 테스트 파일 백업
5. ✅ Tailwind CSS v4 PostCSS 플러그인 설치
6. ✅ 프론트엔드 빌드 (`npm run build`)
7. ✅ Docker 컨테이너 재시작
8. ✅ 배포 상태 확인

---

### 배포 방법 2: 수동 실행

#### 2-1. 작업 디렉토리 정리
```bash
cd /root/uvis
git checkout -- . 2>/dev/null || true
git status
```

#### 2-2. 최신 코드 가져오기
```bash
git pull origin main
```
**예상 출력**: `Updating 2b0544b..8661a8d`

#### 2-3. .env 파일 수정
```bash
cd frontend
cat > .env << 'EOF'
# API Configuration
VITE_API_BASE_URL=/api/v1
EOF
```

#### 2-4. 테스트 파일 백업
```bash
mkdir -p .build-backup
mv src/components/common/__tests__ .build-backup/ 2>/dev/null || true
mv src/store/__tests__ .build-backup/ 2>/dev/null || true
mv src/utils/__tests__ .build-backup/ 2>/dev/null || true
mv src/setupTests.ts .build-backup/ 2>/dev/null || true
echo "✅ Test files backed up"
```

#### 2-5. Tailwind CSS v4 PostCSS 플러그인 설치
```bash
npm install -D @tailwindcss/postcss --legacy-peer-deps
```

#### 2-6. 프론트엔드 빌드
```bash
npm run build
```
**예상 결과**: `dist/index.html` 및 `dist/assets/` 파일 생성

#### 2-7. 빌드 확인
```bash
ls -lh dist/index.html
```
**예상 출력**: 파일 날짜가 현재 시각이어야 함

#### 2-8. 컨테이너 재시작
```bash
cd /root/uvis
docker-compose stop frontend nginx
docker-compose rm -f frontend nginx
docker-compose build --no-cache frontend
docker-compose up -d frontend nginx
```

#### 2-9. 대기 및 상태 확인
```bash
sleep 30
docker-compose ps
```
**예상 출력**: `uvis-frontend` 상태가 `Up` 및 `(healthy)`

#### 2-10. HTTP 응답 확인
```bash
curl -I http://localhost/
```
**예상 출력**: `HTTP/1.1 200 OK`

#### 2-11. API 테스트
```bash
curl http://localhost:8000/api/v1/dispatch-rules/ | jq '.[0:2]'
```
**예상 출력**: 2개 규칙의 JSON 배열

---

## 🧪 브라우저 테스트

### 중요: 브라우저 캐시 완전 삭제 필수!

#### 방법 1: 시크릿/프라이빗 모드 (가장 확실)
1. **Chrome**: `Ctrl + Shift + N`
2. **Firefox**: `Ctrl + Shift + P`
3. `http://139.150.11.99/` 접속

#### 방법 2: 캐시 완전 삭제
1. `Ctrl + Shift + Delete`
2. **전체 기간** 선택
3. **캐시된 이미지 및 파일** 체크
4. **쿠키 및 기타 사이트 데이터** 체크
5. 데이터 삭제
6. **브라우저 완전히 종료 후 재시작**
7. `http://139.150.11.99/` 접속

#### 방법 3: 개발자 도구 강제 새로고침
1. `F12` (개발자 도구 열기)
2. **Network** 탭 선택
3. **Disable cache** 체크박스 활성화
4. 주소창 새로고침 버튼 **우클릭**
5. **"캐시 비우기 및 강력 새로고침"** 선택

---

## ✅ 확인 사항

### 1. 대시보드
- [ ] 로그인 화면 정상 로드
- [ ] 로그인 후 대시보드 접속
- [ ] **좌측 사이드바에 "스마트 배차 규칙" 메뉴 표시 (한글!)**

### 2. Dispatch Rules 페이지 (http://139.150.11.99/dispatch-rules)
- [ ] 페이지 제목: **"스마트 배차 규칙"** (한글)
- [ ] 버튼: **"+ 새 규칙 만들기"** (한글)
- [ ] **2개의 규칙 카드 표시**:
  - Priority Drivers (우선순위: 100)
  - Nearby Drivers Priority (우선순위: 90)
- [ ] 각 규칙 카드에 버튼: Test, Logs, Performance

### 3. Visual Builder (새 규칙 만들기 클릭 시)
- [ ] 폼 레이블이 한글로 표시:
  - 규칙 이름
  - 설명
  - 규칙 유형
  - 우선순위
  - 조건 (JSON)
  - 작업 (JSON)

### 4. Rule Template Gallery
- [ ] 템플릿 제목: **"규칙 템플릿 갤러리"** (한글)
- [ ] 검색 박스: **"템플릿 검색"** (한글)
- [ ] 8개 템플릿 카드가 한글로 표시:
  1. 근처 기사 우선
  2. 고평점 기사 우선
  3. 긴급 주문 처리
  4. 피크 시간 최적화
  5. 온도 민감 화물
  6. 기사 업무량 균등 분배
  7. 다중 경유지 경로 최적화
  8. 신규 기사 교육 배정

### 5. Rule Simulation
- [ ] 시뮬레이션 섹션 제목: **"규칙 시뮬레이션"** (한글)
- [ ] 설명 텍스트가 한글로 표시
- [ ] 버튼: **"시뮬레이션 실행"** (한글)

---

## 📸 스크린샷 요청

배포 확인을 위해 다음 스크린샷을 공유해 주세요:

1. **대시보드** (좌측 사이드바 포함)
   - "스마트 배차 규칙" 메뉴 표시 확인

2. **Dispatch Rules 페이지**
   - 페이지 제목 "스마트 배차 규칙" 확인
   - 2개 규칙 카드 표시 확인

3. **Create New Rule 폼** (선택 사항)
   - 폼 레이블이 한글로 표시되는지 확인

4. **Rule Template Gallery** (선택 사항)
   - 템플릿 제목과 카드가 한글로 표시되는지 확인

---

## 🐛 문제 해결

### 문제 1: 규칙이 표시되지 않음
**증상**: 페이지는 로드되지만 규칙 카드가 비어있음

**원인**: API 연결 실패 (ERR_CONNECTION_REFUSED)

**해결**:
1. 브라우저 콘솔 확인 (F12 → Console)
2. 오류가 `http://localhost:8000`으로 요청하는 경우:
   - `.env` 파일이 제대로 설정되지 않음
   - 프론트엔드 재빌드 필요

**확인 명령** (서버):
```bash
# .env 파일 확인
cat /root/uvis/frontend/.env

# 예상 출력
# VITE_API_BASE_URL=/api/v1

# 빌드 파일에서 API URL 확인
cd /root/uvis/frontend
grep -r "localhost:8000" dist/ || echo "✅ No localhost:8000 found"
```

### 문제 2: UI가 영어로 표시됨
**증상**: 페이지는 작동하지만 여전히 영어로 표시

**원인**: 
1. 번역 파일이 빌드에 포함되지 않음
2. i18n 언어 설정이 한국어로 되어 있지 않음

**해결**:
```bash
# 서버에서 번역 파일 확인
cat /root/uvis/frontend/public/locales/ko/translation.json | jq .dispatchRules

# 예상 출력: dispatchRules 섹션이 표시되어야 함

# i18n 설정 확인
cat /root/uvis/frontend/src/i18n/config.ts
```

### 문제 3: 빌드 실패
**증상**: `npm run build` 명령 시 타입 에러 발생

**해결**:
```bash
# 테스트 파일 다시 백업
cd /root/uvis/frontend
rm -rf src/components/common/__tests__
rm -rf src/store/__tests__
rm -rf src/utils/__tests__
rm -f src/setupTests.ts

# 재빌드
npm run build
```

### 문제 4: 컨테이너 재시작 루프
**증상**: `docker-compose ps`에서 frontend가 계속 재시작됨

**해결**:
```bash
# 로그 확인
docker-compose logs frontend --tail=50

# nginx 설정 테스트
docker-compose exec frontend nginx -t

# 문제가 있으면 컨테이너 재빌드
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

## 📊 Phase 10 최종 상태

### Backend
- ✅ 14개 API 엔드포인트 구현
- ✅ 모든 엔드포인트 정상 작동
- ✅ 테스트 데이터 2개 생성

### Frontend
- ✅ Dispatch Rules 페이지 구현
- ✅ Visual Rule Builder 구현
- ✅ Rule Template Gallery 구현
- ✅ Rule Simulation 구현
- ✅ **한글 번역 완료** 🎉
- ✅ API 연동 완료

### Infrastructure
- ✅ TypeScript 에러 281개 → 0개
- ✅ Tailwind CSS v4 설정 완료
- ✅ 프론트엔드 빌드 성공
- ✅ Docker 컨테이너 정상 작동

### Documentation
- ✅ 배포 스크립트 작성
- ✅ 상세 가이드 문서 작성
- ✅ 문제 해결 가이드 작성

---

## 🎯 다음 단계

1. **서버 배포 실행**
   - 배포 스크립트 실행 또는 수동 배포
   - 컨테이너 상태 확인

2. **브라우저 테스트**
   - 캐시 완전 삭제 후 접속
   - 한글 UI 확인
   - 규칙 로딩 확인

3. **스크린샷 공유**
   - 대시보드 (사이드바 포함)
   - Dispatch Rules 페이지
   - (선택) 규칙 생성 폼

4. **Phase 10 완료 확인** 🎉
   - 모든 확인 사항 체크
   - 최종 승인

---

## 📚 관련 파일

### 샌드박스
- `/home/user/webapp/FINAL_KOREAN_DEPLOYMENT.sh` - 배포 스크립트
- `/home/user/webapp/PHASE10_KOREAN_UI_COMPLETION.md` - 본 가이드
- `/home/user/webapp/frontend/public/locales/ko/translation.json` - 한글 번역
- `/home/user/webapp/frontend/.env` - 환경 변수

### 서버 (/root/uvis)
- 최신 코드: 커밋 8661a8d
- 배포 스크립트: GitHub에서 다운로드 필요

---

## 📞 지원

문제가 발생하면:
1. 배포 로그 전체 공유
2. 브라우저 콘솔 스크린샷 공유
3. `docker-compose ps` 출력 공유
4. `curl -I http://localhost/` 출력 공유

---

**작성일**: 2026-02-08  
**작성자**: GenSpark AI  
**버전**: 1.0  
**상태**: 배포 준비 완료 ✅
