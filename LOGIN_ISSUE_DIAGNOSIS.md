# 로그인 화면 UI 깨짐 문제 진단 및 해결

## 🔍 문제 상황
- 로그인 화면이 깨져 보임 (distorted layout)
- "데이터를 불러오는 중입니다" 메시지만 표시되거나 스타일이 적용되지 않음
- Tailwind CSS가 제대로 적용되지 않는 것으로 보임

## 🎯 원인 분석

### 1. 이전 배포의 문제점
서버에서 여러 차례 `OrdersPage.tsx` 파일을 수정하는 과정에서:
- Layout 태그 제거 시도 중 구문 오류 발생
- 괄호/중괄호 불일치
- JSX 구조 손상

### 2. 가능한 원인들
1. **손상된 OrdersPage.tsx가 빌드에 영향**
   - 구문 오류로 인해 번들 파일이 손상됨
   - 이로 인해 전체 앱의 로딩/렌더링에 문제 발생

2. **CSS 빌드 문제**
   - Tailwind CSS가 제대로 빌드되지 않음
   - CSS 파일은 생성되었으나 내용이 비어있거나 불완전함

3. **브라우저 캐시**
   - 이전의 손상된 빌드가 캐시되어 있음
   - 강제 새로고침(Ctrl+F5)이 필요함

4. **Service Worker 간섭**
   - PWA Service Worker가 오래된 캐시를 서빙
   - Service Worker 제거 필요

## ✅ 해결 방법

### 방법 1: 자동 수정 스크립트 실행 (권장)

서버에서 다음 명령어를 실행하세요:

```bash
cd /root/uvis/frontend

# 수정 스크립트 다운로드 (sandbox에서 생성한 스크립트)
# 또는 아래 내용을 복사하여 FIX_UI_ISSUES.sh 파일로 저장

# 실행 권한 부여
chmod +x FIX_UI_ISSUES.sh

# 스크립트 실행
bash FIX_UI_ISSUES.sh
```

이 스크립트는 자동으로:
1. 현재 파일 백업
2. OrdersPage.tsx를 git에서 클린 버전으로 복원
3. Layout import 및 태그 제거
4. App.tsx에서 /orders 라우트 수정
5. navigation.ts 설정 확인
6. 빌드 및 검증

### 방법 2: 수동 수정

```bash
cd /root/uvis/frontend

# 1. 백업
cp src/pages/OrdersPage.tsx src/pages/OrdersPage.tsx.backup_manual
cp src/App.tsx src/App.tsx.backup_manual

# 2. Git에서 클린 버전 복원
git checkout HEAD -- src/pages/OrdersPage.tsx

# 3. Layout import 제거
sed -i '/^import Layout from/d' src/pages/OrdersPage.tsx

# 4. Layout 태그 제거 (Python 스크립트)
python3 << 'EOF'
with open("src/pages/OrdersPage.tsx", "r") as f:
    lines = f.readlines()

filtered = [line for line in lines if line.strip() not in ["<Layout>", "</Layout>"]]

with open("src/pages/OrdersPage.tsx", "w") as f:
    f.writelines(filtered)
EOF

# 5. 검증
grep "import Layout" src/pages/OrdersPage.tsx  # 결과 없어야 함
grep -c "<Layout>" src/pages/OrdersPage.tsx    # 0이어야 함

# 6. 빌드
npm run build
```

### 방법 3: 완전 클린 빌드

문제가 계속되면 완전히 새로 빌드:

```bash
cd /root/uvis/frontend

# 1. node_modules와 dist 제거
rm -rf node_modules dist

# 2. 소스 파일 복원
git checkout HEAD -- src/pages/OrdersPage.tsx src/App.tsx

# 3. 의존성 재설치
npm install

# 4. 빌드
npm run build
```

## 🚀 Docker 재배포

빌드가 성공하면:

```bash
cd /root/uvis

# 1. 컨테이너 중지 및 제거
docker-compose stop frontend
docker-compose rm -f frontend

# 2. 이미지 제거
docker rmi uvis-frontend

# 3. 새로 빌드 (캐시 없이)
docker-compose build --no-cache frontend

# 4. 시작
docker-compose up -d frontend

# 5. 로그 확인
docker logs uvis-frontend --tail 20

# 6. 상태 확인
docker ps | grep frontend
```

## 🌐 브라우저에서 확인

1. **캐시 완전 초기화:**
   - Chrome/Edge: Ctrl + Shift + Delete → "전체 기간" 선택 → "캐시된 이미지 및 파일" 체크 → 삭제
   - Firefox: Ctrl + Shift + Delete → "전체" 선택 → "캐시" 체크 → 지금 지우기

2. **Service Worker 제거:**
   - F12 (개발자 도구)
   - Application/애플리케이션 탭
   - Service Workers 섹션
   - "Unregister" 클릭

3. **강제 새로고침:**
   - Ctrl + F5 (또는 Ctrl + Shift + R)

4. **시크릿 모드로 테스트:**
   - Ctrl + Shift + N (Chrome/Edge)
   - Ctrl + Shift + P (Firefox)

## 🔍 추가 진단

### 서버에서 현재 상태 확인

```bash
cd /root/uvis/frontend

# 1. 빌드 파일 확인
echo "=== CSS 파일 ==="
ls -lh dist/assets/*.css

echo -e "\n=== JS 파일 (처음 10개) ==="
ls -lh dist/assets/*.js | head -10

# 2. 소스 파일 상태
echo -e "\n=== OrdersPage Layout import ==="
grep "import Layout" src/pages/OrdersPage.tsx || echo "✅ Layout import 없음"

echo -e "\n=== OrdersPage Layout 태그 ==="
grep -c "<Layout>" src/pages/OrdersPage.tsx || echo "✅ Layout 태그 없음"

echo -e "\n=== App.tsx /orders 라우트 ==="
grep -A3 'path="/orders"' src/App.tsx

# 3. Git 상태
echo -e "\n=== Git 상태 ==="
git status --short

echo -e "\n=== 최근 커밋 ==="
git log --oneline -5
```

### 브라우저 콘솔 확인

F12를 누르고 다음을 확인:

1. **Console 탭:**
   - JavaScript 에러가 있는지 확인
   - 특히 "Unexpected token", "SyntaxError" 등

2. **Network 탭:**
   - index-*.css 파일이 200 OK로 로드되는지
   - 파일 크기가 적절한지 (13KB 이상)
   - index-*.js 파일들이 제대로 로드되는지

3. **Elements 탭:**
   - `<head>` 섹션에 `<link rel="stylesheet">` 태그가 있는지
   - `<body>` 내부의 HTML 구조가 정상인지

## 📊 정상 상태 체크리스트

빌드 및 배포 후 다음을 확인:

- [ ] `npm run build` 성공
- [ ] dist/assets/ 폴더에 CSS 파일 3개 존재 (~13-15KB)
- [ ] dist/assets/ 폴더에 JS 파일 90개 이상 존재
- [ ] OrdersPage.tsx에 Layout import 없음
- [ ] OrdersPage.tsx에 <Layout> 태그 없음
- [ ] App.tsx의 /orders 라우트가 <ProtectedRoute>만 사용
- [ ] Docker 컨테이너 정상 실행 (docker ps)
- [ ] 브라우저 캐시 초기화 완료
- [ ] Service Worker 제거 완료
- [ ] 로그인 페이지에 파란색 gradient 배경 표시
- [ ] 로그인 폼 정상 표시
- [ ] 로그인 성공 후 대시보드로 이동
- [ ] 사이드바 메뉴 정상 표시
- [ ] /orders 페이지에서 Layout 중복 없음

## 🆘 문제가 계속되면

스크린샷을 공유해주세요:
1. 로그인 페이지 화면
2. F12 Console 탭
3. F12 Network 탭 (CSS 파일 로드 상태)
4. 서버 터미널의 `npm run build` 출력

그리고 다음 명령어 출력:
```bash
cd /root/uvis/frontend
git status
git diff src/pages/OrdersPage.tsx
grep -A5 'path="/orders"' src/App.tsx
```

## 📝 변경 사항 요약

수정된 내용:
1. **OrdersPage.tsx**: Layout import 및 태그 완전 제거
2. **App.tsx**: /orders 라우트에서 LayoutWrapper 제거, ProtectedRoute만 사용
3. **navigation.ts**: 중앙 집중식 메뉴 설정 (src/config/navigation.ts)

결과:
- ✅ Layout 중복 문제 해결
- ✅ UI 깨짐 현상 수정
- ✅ 메뉴 관리 중앙화 (2곳 → 1곳)
- ✅ 코드 중복 -88줄
- ✅ 유지보수성 향상
