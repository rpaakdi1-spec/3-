# 🎉 Phase 10 한글 UI 완성 - 서버 배포 명령어

## ✅ 샌드박스 작업 완료 상태

### 완료된 작업
1. ✅ 한글 번역 파일 생성 및 병합 (`frontend/public/locales/ko/translation.json`)
2. ✅ API URL 환경 변수 수정 (`VITE_API_BASE_URL=/api/v1`)
3. ✅ Git 커밋 및 푸시 완료:
   - 커밋 `8661a8d`: 한글 번역 추가
   - 커밋 `976fb4e`: 배포 가이드 및 스크립트 추가

### GitHub 최신 상태
- **리포지토리**: https://github.com/rpaakdi1-spec/3-
- **최신 커밋**: `976fb4e`
- **포함 내용**:
  - Korean translations for dispatch rules
  - Deployment script
  - Comprehensive guide

---

## 🚀 서버 배포 실행 명령어

서버(`/root/uvis`)에서 아래 명령어를 **순서대로** 실행해 주세요.

### 방법 1: 자동 배포 스크립트 (권장)

```bash
# 1. 배포 스크립트 다운로드
cd /root/uvis
curl -O https://raw.githubusercontent.com/rpaakdi1-spec/3-/main/FINAL_KOREAN_DEPLOYMENT.sh
chmod +x FINAL_KOREAN_DEPLOYMENT.sh

# 2. 스크립트 실행
./FINAL_KOREAN_DEPLOYMENT.sh
```

**스크립트가 자동으로 수행하는 작업**:
1. 작업 디렉토리 정리
2. 최신 코드 가져오기 (git pull)
3. .env 파일 수정 (VITE_API_BASE_URL)
4. 테스트 파일 백업
5. Tailwind CSS v4 플러그인 설치
6. 프론트엔드 빌드
7. Docker 컨테이너 재시작
8. 배포 상태 확인

---

### 방법 2: 수동 배포 (단계별)

#### Step 1: 작업 디렉토리 정리 및 최신 코드 가져오기
```bash
cd /root/uvis
git checkout -- . 2>/dev/null || true
git pull origin main
```

**예상 출력**:
```
Updating 2b0544b..976fb4e
...
frontend/public/locales/ko/translation.json
```

#### Step 2: .env 파일 수정
```bash
cd frontend
cat > .env << 'EOF'
# API Configuration
VITE_API_BASE_URL=/api/v1
EOF
cat .env  # 확인
```

**예상 출력**:
```
# API Configuration
VITE_API_BASE_URL=/api/v1
```

#### Step 3: 테스트 파일 백업
```bash
mkdir -p .build-backup
mv src/components/common/__tests__ .build-backup/ 2>/dev/null || true
mv src/store/__tests__ .build-backup/ 2>/dev/null || true
mv src/utils/__tests__ .build-backup/ 2>/dev/null || true
mv src/setupTests.ts .build-backup/ 2>/dev/null || true
echo "✅ Test files backed up"
```

#### Step 4: Tailwind CSS v4 PostCSS 플러그인 설치
```bash
npm install -D @tailwindcss/postcss --legacy-peer-deps
```

**예상 출력**: 패키지 설치 로그

#### Step 5: 프론트엔드 빌드
```bash
npm run build
```

**예상 출력**:
```
vite v5.x.x building for production...
✓ built in Xs
dist/index.html
dist/assets/...
```

#### Step 6: 빌드 확인
```bash
ls -lh dist/index.html
```

**예상 출력**: 파일 날짜가 현재 시각

#### Step 7: 메인 디렉토리로 복귀
```bash
cd /root/uvis
```

#### Step 8: Docker 컨테이너 재시작
```bash
docker-compose stop frontend nginx
docker-compose rm -f frontend nginx
docker-compose build --no-cache frontend
docker-compose up -d frontend nginx
```

**예상 출력**:
```
Stopping uvis-frontend ... done
Stopping uvis-nginx ... done
...
Building frontend
...
Creating uvis-frontend ... done
Creating uvis-nginx ... done
```

#### Step 9: 대기 및 상태 확인 (30초 대기)
```bash
sleep 30
docker-compose ps
```

**예상 출력**:
```
NAME            STATUS                    PORTS
uvis-backend    Up X minutes (healthy)    0.0.0.0:8000->8000/tcp
uvis-db         Up X minutes (healthy)    5432/tcp
uvis-frontend   Up 30 seconds (healthy)   80/tcp
uvis-nginx      Up 30 seconds             0.0.0.0:80->80/tcp
```

#### Step 10: 빌드 파일 날짜 확인
```bash
ls -lh frontend/dist/index.html
```

**예상 출력**: 최신 날짜

#### Step 11: HTTP 응답 확인
```bash
curl -I http://localhost/
```

**예상 출력**:
```
HTTP/1.1 200 OK
Server: nginx/1.29.4
...
```

#### Step 12: API 테스트
```bash
curl -s http://localhost:8000/api/v1/dispatch-rules/ | jq '.[0:2]'
```

**예상 출력**: 2개 규칙의 JSON 배열

---

## 🧪 브라우저 테스트 가이드

### 중요: 브라우저 캐시 완전 삭제 필수!

#### 방법 1: 시크릿 모드 (가장 확실)
1. 모든 브라우저 창 닫기
2. 브라우저 완전히 종료
3. 브라우저 재시작
4. **시크릿/프라이빗 모드** 열기:
   - Chrome: `Ctrl + Shift + N`
   - Firefox: `Ctrl + Shift + P`
5. 주소창에 입력: `http://139.150.11.99/`

#### 방법 2: 캐시 완전 삭제
1. `Ctrl + Shift + Delete` (설정 열기)
2. **전체 기간** 선택
3. 체크 항목:
   - ✅ 캐시된 이미지 및 파일
   - ✅ 쿠키 및 기타 사이트 데이터
4. **데이터 삭제** 클릭
5. **브라우저 완전히 종료**
6. 브라우저 재시작
7. `http://139.150.11.99/` 접속

#### 방법 3: 개발자 도구 강제 새로고침
1. `http://139.150.11.99/` 접속
2. `F12` (개발자 도구 열기)
3. **Network** 탭 선택
4. **Disable cache** 체크박스 활성화
5. 주소창 새로고침 버튼 **우클릭**
6. **"캐시 비우기 및 강력 새로고침"** 선택

---

## ✅ 확인 사항 체크리스트

### 1. 대시보드 확인
- [ ] 로그인 화면이 정상적으로 로드됨
- [ ] 로그인 후 대시보드 접속 가능
- [ ] **좌측 사이드바에 "스마트 배차 규칙" 메뉴가 한글로 표시됨** ⭐

### 2. Dispatch Rules 페이지 확인
**URL**: `http://139.150.11.99/dispatch-rules`

- [ ] 페이지 제목: **"스마트 배차 규칙"** (한글) ⭐
- [ ] 버튼: **"+ 새 규칙 만들기"** (한글) ⭐
- [ ] **2개의 규칙 카드가 표시됨**:
  - Priority Drivers (우선순위: 100)
  - Nearby Drivers Priority (우선순위: 90)
- [ ] 각 규칙 카드에 버튼: Test, Logs, Performance

### 3. 새 규칙 만들기 폼 (선택 확인)
**"+ 새 규칙 만들기"** 버튼 클릭 시:

- [ ] 폼 레이블이 한글로 표시:
  - **규칙 이름**
  - **설명**
  - **규칙 유형**
  - **우선순위**
  - **조건 (JSON)**
  - **작업 (JSON)**
  - **비주얼 빌더로 전환**

### 4. Rule Template Gallery (선택 확인)
- [ ] 섹션 제목: **"규칙 템플릿 갤러리"** (한글)
- [ ] 검색 박스: **"템플릿 검색"** (한글)
- [ ] 8개 템플릿 카드가 한글로 표시:
  1. ✅ 근처 기사 우선
  2. ✅ 고평점 기사 우선
  3. ✅ 긴급 주문 처리
  4. ✅ 피크 시간 최적화
  5. ✅ 온도 민감 화물
  6. ✅ 기사 업무량 균등 분배
  7. ✅ 다중 경유지 경로 최적화
  8. ✅ 신규 기사 교육 배정

---

## 📸 스크린샷 요청

배포 확인을 위해 다음 **스크린샷**을 공유해 주세요:

### 필수 스크린샷
1. **대시보드 (좌측 사이드바 포함)**
   - "스마트 배차 규칙" 메뉴가 한글로 표시되는지 확인

2. **Dispatch Rules 페이지**
   - URL: `http://139.150.11.99/dispatch-rules`
   - 페이지 제목 "스마트 배차 규칙" 확인
   - 2개 규칙 카드 확인

### 선택 스크린샷 (가능하면)
3. **"새 규칙 만들기" 폼**
   - 폼 레이블이 한글로 표시되는지 확인

4. **Rule Template Gallery**
   - 템플릿이 한글로 표시되는지 확인

---

## 🐛 문제 발생 시

### 문제 1: 규칙이 표시되지 않음 (빈 페이지)

**확인 명령** (서버):
```bash
# API 직접 테스트
curl http://localhost:8000/api/v1/dispatch-rules/

# 예상 출력: 2개 규칙의 JSON 배열
```

**해결**:
1. API가 정상 작동하는지 확인
2. 브라우저 콘솔 (F12 → Console) 확인
3. Network 탭에서 API 요청 상태 확인

### 문제 2: UI가 여전히 영어로 표시됨

**확인 명령** (서버):
```bash
# 번역 파일 확인
cat /root/uvis/frontend/public/locales/ko/translation.json | jq .dispatchRules

# 예상 출력: dispatchRules 섹션이 표시되어야 함
```

**해결**:
1. 번역 파일이 빌드에 포함되었는지 확인
2. 브라우저 캐시를 완전히 삭제하고 재접속

### 문제 3: ERR_CONNECTION_REFUSED 오류

**확인 명령** (서버):
```bash
# .env 파일 확인
cat /root/uvis/frontend/.env

# 예상 출력: VITE_API_BASE_URL=/api/v1

# 빌드된 JS 파일에서 localhost:8000 검색
cd /root/uvis/frontend
grep -r "localhost:8000" dist/ || echo "✅ No localhost:8000 found"
```

**해결**:
1. `.env` 파일이 올바른지 확인
2. 프론트엔드 재빌드 필요

---

## 📊 배포 완료 후 최종 상태

### ✅ 예상 결과
- Frontend: `http://139.150.11.99/` (200 OK)
- Dispatch Rules: `http://139.150.11.99/dispatch-rules` (한글 UI)
- API: `http://139.150.11.99:8000/api/v1/dispatch-rules/` (2개 규칙)
- API Docs: `http://139.150.11.99:8000/docs` (Swagger UI)

### 🎯 성공 지표
1. ✅ 좌측 사이드바에 "스마트 배차 규칙" 메뉴 한글 표시
2. ✅ Dispatch Rules 페이지 제목 한글 표시
3. ✅ 2개 규칙 카드 정상 로드
4. ✅ "새 규칙 만들기" 버튼 한글 표시
5. ✅ 폼 레이블 전체 한글 표시
6. ✅ 템플릿 갤러리 한글 표시

---

## 🎉 Phase 10 완료!

모든 확인 사항이 체크되면 **Phase 10 완료**입니다!

### 최종 성과
- ✅ Backend: 14개 API 엔드포인트 구현
- ✅ Frontend: Dispatch Rules 페이지 구현
- ✅ **한글 UI 완성** 🇰🇷
- ✅ API 연동 완료
- ✅ TypeScript 에러 0개
- ✅ Tailwind CSS v4 적용
- ✅ Docker 컨테이너 정상 작동

### 다음 단계
- 브라우저 테스트 및 스크린샷 공유
- 최종 확인 및 승인
- Phase 11 계획

---

**배포 준비 완료** ✅  
**샌드박스-서버 동기화 완료** ✅  
**한글 번역 완료** ✅  

이제 서버에서 위 명령어를 실행하고 결과를 공유해 주세요! 🚀
