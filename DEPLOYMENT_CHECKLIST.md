# 🚀 Phase 10 배포 체크리스트

## ✅ 샌드박스 작업 완료 사항

- [x] 한글 번역 파일 생성 (`/tmp/dispatch-rules-ko.json`)
- [x] 기존 번역과 병합 (`frontend/public/locales/ko/translation.json`)
- [x] API URL 환경 변수 수정 (`VITE_API_BASE_URL=/api/v1`)
- [x] 배포 스크립트 작성 (`FINAL_KOREAN_DEPLOYMENT.sh`)
- [x] 상세 가이드 문서 작성
- [x] Git 커밋 및 푸시 완료 (커밋 a16e2a3)

---

## 📦 서버 배포 체크리스트

### 배포 전 확인
- [ ] 서버 접속: `ssh root@139.150.11.99`
- [ ] 작업 디렉토리 이동: `cd /root/uvis`
- [ ] 현재 상태 확인: `git status`

### 배포 실행 (자동 방법)
- [ ] 스크립트 다운로드: `curl -O https://raw.githubusercontent.com/rpaakdi1-spec/3-/main/FINAL_KOREAN_DEPLOYMENT.sh`
- [ ] 실행 권한 부여: `chmod +x FINAL_KOREAN_DEPLOYMENT.sh`
- [ ] 스크립트 실행: `./FINAL_KOREAN_DEPLOYMENT.sh`

### 배포 완료 확인
- [ ] 스크립트 정상 완료 (오류 없음)
- [ ] 최신 코드 pull 완료 (커밋 a16e2a3)
- [ ] `.env` 파일 수정 확인
- [ ] npm 패키지 설치 완료
- [ ] 프론트엔드 빌드 성공
- [ ] Docker 컨테이너 재시작 완료

### 서버 상태 확인
- [ ] `docker-compose ps` - 모든 컨테이너 `Up` 및 `healthy`
- [ ] `curl -I http://localhost/` - HTTP 200 OK
- [ ] `curl http://localhost:8000/api/v1/dispatch-rules/` - 2개 규칙 JSON 응답

---

## 🌐 브라우저 테스트 체크리스트

### 캐시 삭제
- [ ] 시크릿/프라이빗 모드로 접속
  - Chrome: `Ctrl + Shift + N`
  - Firefox: `Ctrl + Shift + P`
- [ ] 또는 캐시 완전 삭제:
  - [ ] `Ctrl + Shift + Delete`
  - [ ] 전체 기간 선택
  - [ ] 캐시 및 쿠키 삭제
  - [ ] 브라우저 재시작

### 페이지 접속
- [ ] `http://139.150.11.99/` 접속
- [ ] 로그인 화면 정상 표시
- [ ] 로그인 성공

### 대시보드 확인
- [ ] 대시보드 정상 로드
- [ ] 좌측 사이드바 표시
- [ ] **"스마트 배차 규칙"** 메뉴 한글 표시 ⭐

### Dispatch Rules 페이지 (`/dispatch-rules`)
- [ ] 페이지 정상 로드
- [ ] 페이지 제목: **"스마트 배차 규칙"** (한글) ⭐
- [ ] 버튼: **"+ 새 규칙 만들기"** (한글) ⭐
- [ ] 2개 규칙 카드 표시:
  - [ ] Priority Drivers (우선순위: 100)
  - [ ] Nearby Drivers Priority (우선순위: 90)
- [ ] 각 카드에 버튼: Test, Logs, Performance

### 새 규칙 만들기 폼 (선택)
- [ ] "새 규칙 만들기" 버튼 클릭
- [ ] 폼 표시
- [ ] 폼 레이블 한글 표시:
  - [ ] 규칙 이름
  - [ ] 설명
  - [ ] 규칙 유형
  - [ ] 우선순위
  - [ ] 조건 (JSON)
  - [ ] 작업 (JSON)

### Rule Template Gallery (선택)
- [ ] 템플릿 섹션 표시
- [ ] 섹션 제목: **"규칙 템플릿 갤러리"** (한글)
- [ ] 검색 박스: **"템플릿 검색"** (한글)
- [ ] 8개 템플릿 카드 한글 표시:
  - [ ] 근처 기사 우선
  - [ ] 고평점 기사 우선
  - [ ] 긴급 주문 처리
  - [ ] 피크 시간 최적화
  - [ ] 온도 민감 화물
  - [ ] 기사 업무량 균등 분배
  - [ ] 다중 경유지 경로 최적화
  - [ ] 신규 기사 교육 배정

---

## 📸 스크린샷 체크리스트

### 필수 스크린샷
- [ ] 1. 대시보드 (좌측 사이드바 포함)
  - "스마트 배차 규칙" 메뉴 표시 확인
- [ ] 2. Dispatch Rules 페이지
  - 페이지 제목 및 2개 규칙 카드 확인

### 선택 스크린샷
- [ ] 3. 새 규칙 만들기 폼
  - 폼 레이블 한글 표시 확인
- [ ] 4. Rule Template Gallery
  - 템플릿 한글 표시 확인

---

## 🐛 문제 해결 체크리스트

### 문제 1: 규칙이 표시되지 않음
- [ ] API 직접 테스트: `curl http://localhost:8000/api/v1/dispatch-rules/`
- [ ] 브라우저 콘솔 확인 (F12 → Console)
- [ ] Network 탭 확인 (F12 → Network)
- [ ] 에러 메시지 확인

### 문제 2: UI가 영어로 표시됨
- [ ] 번역 파일 확인: `cat /root/uvis/frontend/public/locales/ko/translation.json | jq .dispatchRules`
- [ ] 브라우저 캐시 완전 삭제
- [ ] 시크릿 모드로 재접속

### 문제 3: ERR_CONNECTION_REFUSED
- [ ] `.env` 파일 확인: `cat /root/uvis/frontend/.env`
- [ ] 빌드 파일에서 localhost:8000 검색: `grep -r "localhost:8000" /root/uvis/frontend/dist/`
- [ ] 프론트엔드 재빌드 필요

### 문제 4: 컨테이너 재시작 루프
- [ ] 로그 확인: `docker-compose logs frontend --tail=50`
- [ ] nginx 설정 테스트: `docker-compose exec frontend nginx -t`
- [ ] 컨테이너 재빌드: `docker-compose build --no-cache frontend`

---

## ✅ 최종 승인 체크리스트

### Phase 10 완료 조건
- [ ] 서버 배포 성공
- [ ] 모든 컨테이너 정상 작동
- [ ] HTTP 응답 200 OK
- [ ] API 응답 정상
- [ ] 대시보드 한글 메뉴 표시
- [ ] Dispatch Rules 페이지 한글 표시
- [ ] 2개 규칙 카드 로드
- [ ] 스크린샷 2개 이상 촬영 및 공유

### 최종 승인
- [ ] 모든 확인 사항 통과
- [ ] 스크린샷 공유 완료
- [ ] **Phase 10 완료!** 🎉

---

**체크리스트 완료 시**: Phase 10 완료 및 다음 단계로 진행 가능

**문제 발생 시**: 문제 해결 체크리스트 참고 또는 추가 지원 요청
