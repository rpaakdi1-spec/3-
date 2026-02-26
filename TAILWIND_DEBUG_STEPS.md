# Tailwind CSS 스타일이 적용되지 않는 문제 디버깅

## 현재 상황
- 네트워크: CSS/JS 파일들이 모두 200 OK로 정상 로딩됨
- 파일 크기도 정상 (index-BjMybcaV.css: 15.3 kB, index-BIw4OMTJ.js: 247 kB)
- 하지만 화면이 "흐터러져 있음" (스타일이 적용되지 않음)

## 원인 가능성
1. **Tailwind CSS가 빌드에 포함되지 않았을 수 있음** (가장 유력)
2. CSS 파싱 오류
3. JavaScript 오류로 인한 렌더링 문제
4. Content Security Policy 문제

---

## 🔍 1단계: 브라우저 개발자 도구로 확인해야 할 것들

### A. Console 탭 확인
**F12 → Console 탭**
```
다음과 같은 오류가 있는지 확인:
- Uncaught SyntaxError
- Uncaught TypeError
- Failed to load module
- CORS error
```
➡️ **모든 오류 메시지를 복사해주세요**

---

### B. Elements 탭 확인
**F12 → Elements 탭**
1. `<div id="root">` 를 찾아서 확장
2. 안에 무엇이 렌더링되어 있는지 확인
3. 스크린샷 또는 HTML 구조 복사

---

### C. Network 탭 세부 확인
**F12 → Network 탭**
1. `index-BjMybcaV.css` 클릭
2. **Response 탭**으로 이동
3. CSS 내용의 **처음 50줄**을 복사해주세요

예상되는 내용:
```css
:root{
  ...
}
.bg-gradient-to-b{
  background-image:linear-gradient(to bottom,var(--tw-gradient-stops))
}
.from-blue-400{
  --tw-gradient-from:#60a5fa;
  --tw-gradient-to:#60a5fa00;
  --tw-gradient-stops:var(--tw-gradient-from),var(--tw-gradient-to)
}
```

만약 위와 같은 Tailwind 클래스가 **없다면**, Tailwind가 빌드되지 않은 것입니다.

---

### D. Computed Styles 확인
**F12 → Elements 탭**
1. 로그인 카드 부분의 `<div>` 중 하나를 선택
2. 오른쪽 **Computed** 탭 확인
3. `background-color`, `padding`, `border-radius` 등이 적용되어 있는지 확인
4. 스크린샷 또는 주요 스타일 값 복사

---

## 🖥️ 2단계: 서버에서 실행해야 할 명령어

다음 명령어들을 **서버에서** 실행하고 결과를 알려주세요:

```bash
# 서버로 이동
cd /root/uvis/frontend

# 1. Tailwind 설정 확인
echo "=== tailwind.config.js ==="
cat tailwind.config.js

# 2. PostCSS 설정 확인
echo ""
echo "=== postcss.config.js ==="
cat postcss.config.js

# 3. src/index.css 확인
echo ""
echo "=== src/index.css (처음 20줄) ==="
head -20 src/index.css

# 4. 빌드된 CSS 파일 확인
echo ""
echo "=== 빌드된 CSS 파일 내용 (처음 50줄) ==="
head -50 dist/assets/index-BjMybcaV.css

# 5. Tailwind 클래스가 빌드에 포함되었는지 확인
echo ""
echo "=== Tailwind 클래스 검색 ==="
grep -o "\.bg-gradient-to-b\|\.from-blue-400\|\.to-blue-600" dist/assets/index-BjMybcaV.css | head -10

# 6. package.json 확인
echo ""
echo "=== Tailwind CSS 패키지 설치 여부 ==="
grep -A 2 "tailwindcss\|postcss\|autoprefixer" package.json

# 7. LoginPage 소스 확인
echo ""
echo "=== LoginPage className 사용 ==="
grep -n "className=" src/pages/LoginPage.tsx | head -15
```

---

## 🔧 3단계: 예상되는 문제와 해결방법

### 문제 A: Tailwind CSS가 빌드에 포함되지 않음
**증상**: 빌드된 CSS에 `.bg-gradient-to-b` 같은 Tailwind 클래스가 없음

**해결방법**:
```bash
cd /root/uvis/frontend

# 1. tailwind.config.js 확인 및 수정
cat > tailwind.config.js << 'TAILWIND_EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
TAILWIND_EOF

# 2. postcss.config.js 확인
cat > postcss.config.js << 'POSTCSS_EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
POSTCSS_EOF

# 3. src/index.css 맨 위에 Tailwind 지시어 확인
head -5 src/index.css
# 다음과 같아야 함:
# @tailwind base;
# @tailwind components;
# @tailwind utilities;

# 만약 없다면:
cat > src/index.css << 'CSS_EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 기존 스타일 유지 */
CSS_EOF

# 4. 클린 빌드
rm -rf node_modules/.vite dist
npm run build

# 5. Docker 재배포
cd /root/uvis
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker exec uvis-frontend nginx -s reload
```

---

### 문제 B: CSS 파일이 로드되지만 적용되지 않음
**증상**: Network에서 CSS 파일이 200 OK지만 스타일이 적용되지 않음

**해결방법**:
```bash
# Docker 컨테이너 내부에서 직접 확인
docker exec uvis-frontend cat /usr/share/nginx/html/assets/index-BjMybcaV.css | head -50

# CSS 파일의 MIME 타입 확인
curl -I http://139.150.11.99/assets/index-BjMybcaV.css

# 기대값: Content-Type: text/css
```

---

### 문제 C: React 렌더링 오류
**증상**: Console에 JavaScript 오류가 있음

**해결방법**:
```bash
cd /root/uvis/frontend

# 1. LoginPage.tsx 문법 확인
npx eslint src/pages/LoginPage.tsx

# 2. TypeScript 컴파일 체크
npx tsc --noEmit
```

---

## 📋 체크리스트

브라우저에서 확인:
- [ ] Console에 오류 없음
- [ ] Elements에서 `<div id="root">` 안에 로그인 폼이 렌더링됨
- [ ] Network에서 `index-BjMybcaV.css` Response에 Tailwind 클래스가 있음
- [ ] Elements에서 선택한 요소의 Computed 스타일에 값이 있음

서버에서 확인:
- [ ] `tailwind.config.js`에 `content: ["./src/**/*.{js,ts,jsx,tsx}"]` 설정됨
- [ ] `postcss.config.js`에 `tailwindcss` 플러그인 있음
- [ ] `src/index.css`에 `@tailwind` 지시어 3개 있음
- [ ] 빌드된 CSS에 `.bg-gradient-to-b` 같은 Tailwind 클래스가 존재함

---

## 🆘 긴급 수정 방법

만약 위의 모든 확인이 복잡하다면, 다음 명령어를 **서버에서** 실행:

```bash
cd /root/uvis/frontend

# 전체 재빌드
rm -rf node_modules/.vite dist
npm install
npm run build

# dist 폴더 내용 확인
ls -lh dist/assets/*.css

# Docker 재배포
cd /root/uvis
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/ | head -5
docker exec uvis-frontend nginx -s reload

# 브라우저에서 Ctrl+Shift+F5 (완전 새로고침)
```

---

## 다음 단계

위의 진단 결과를 알려주시면:
1. **Console 오류 메시지**
2. **Elements 탭의 `<div id="root">` 내용**
3. **Network Response 탭의 CSS 내용 (처음 50줄)**
4. **서버 명령어 실행 결과**

이 정보를 바탕으로 정확한 해결 방법을 제시하겠습니다!
