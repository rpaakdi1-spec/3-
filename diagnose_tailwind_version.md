# 🔍 Tailwind v3 → v4로 자동 변경되는 원인 진단

## 가능한 원인들:

### 1. package.json에 v4 의존성이 남아있음
```bash
cd /root/uvis/frontend
cat package.json | grep -i tailwind
```

**확인할 것**:
- `"tailwindcss": "^4.x.x"` ← 이게 있으면 문제
- `"@tailwindcss/postcss": "^4.x.x"` ← 이것도 제거 필요
- `"dependencies"` 섹션에 tailwind 있는지
- `"devDependencies"` 섹션에 tailwind 있는지

---

### 2. package-lock.json이 v4를 캐싱하고 있음
```bash
cd /root/uvis/frontend

# package-lock.json 확인
cat package-lock.json | grep -A5 '"tailwindcss"'

# 해결: package-lock.json 삭제 후 재설치
rm -f package-lock.json
rm -rf node_modules
npm install --legacy-peer-deps
```

---

### 3. 다른 패키지가 Tailwind v4를 의존성으로 가지고 있음
```bash
cd /root/uvis/frontend

# 어떤 패키지가 tailwindcss를 필요로 하는지 확인
npm ls tailwindcss

# 또는
npm list @tailwindcss/postcss
```

---

### 4. npm install 시 최신 버전으로 자동 업데이트됨
```bash
# package.json에서 버전 범위 확인
cat package.json | grep tailwind

# ^ 기호는 마이너 버전 자동 업데이트를 의미
# "tailwindcss": "^3.4.17"  ← 이건 3.4.x 범위 내에서만 업데이트
# "tailwindcss": "3.4.17"   ← 이건 정확히 3.4.17로 고정
```

---

### 5. Vite 또는 다른 빌드 도구가 v4를 강제함
```bash
cd /root/uvis/frontend

# vite.config.ts 확인
cat vite.config.ts | grep -i tailwind

# postcss.config.js 확인
cat postcss.config.js
```

---

## 🚀 완전한 해결 방법

### Step 1: 모든 Tailwind 관련 패키지 완전 제거
```bash
cd /root/uvis/frontend

# 1. 모든 Tailwind 패키지 제거
npm uninstall tailwindcss @tailwindcss/postcss @tailwindcss/vite postcss-import

# 2. 캐시 삭제
rm -rf node_modules
rm -f package-lock.json
npm cache clean --force
```

### Step 2: package.json에서 Tailwind 의존성 수동 확인/제거
```bash
# package.json 열기
nano package.json  # 또는 vim package.json

# 확인할 섹션:
# "dependencies": { ... }
# "devDependencies": { ... }

# tailwind 관련 항목 모두 삭제:
# - "tailwindcss": "..."
# - "@tailwindcss/postcss": "..."
# - "@tailwindcss/vite": "..."
```

### Step 3: Tailwind v3 정확한 버전으로 설치
```bash
cd /root/uvis/frontend

# 정확한 버전 지정 (^ 없이!)
npm install -D tailwindcss@3.4.17 postcss@8.4.38 autoprefixer@10.4.18 --save-exact --legacy-peer-deps

# --save-exact: package.json에 정확한 버전만 저장 (^ 제거)
```

### Step 4: package.json 최종 확인
```bash
cat package.json | grep -A10 "devDependencies"

# 다음과 같이 나와야 함:
# "tailwindcss": "3.4.17"  ← ^ 기호 없음!
# "postcss": "8.4.38"
# "autoprefixer": "10.4.18"
```

### Step 5: PostCSS 설정 (v3 전용)
```bash
cat > postcss.config.js << 'POSTCSS_EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
POSTCSS_EOF
```

### Step 6: Tailwind 설정 (v3 전용)
```bash
cat > tailwind.config.js << 'TW_EOF'
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
TW_EOF
```

### Step 7: CSS import 확인 (v3 스타일)
```bash
# src/index.css 또는 src/App.css 확인
cat src/index.css 2>/dev/null || cat src/main.css 2>/dev/null

# 다음과 같아야 함 (v3 스타일):
# @tailwind base;
# @tailwind components;
# @tailwind utilities;

# v4 스타일이면 수정 필요:
# @import "tailwindcss";  ← 이건 v4 스타일
```

v4 스타일이면 v3로 수정:
```bash
cat > src/index.css << 'CSS_EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
CSS_EOF
```

### Step 8: 재빌드 및 버전 확인
```bash
cd /root/uvis/frontend

# 빌드
npm run build

# CSS 파일에서 Tailwind 버전 확인
grep -o "tailwindcss v[0-9.]*" dist/assets/*.css | head -1

# 예상 출력: "tailwindcss v3.4.17"
# v4가 나오면 여전히 문제가 있는 것
```

### Step 9: node_modules에서 실제 설치된 버전 확인
```bash
cat node_modules/tailwindcss/package.json | grep '"version"'

# 예상 출력: "version": "3.4.17"
```

---

## 🔍 원인 찾기 스크립트

```bash
cd /root/uvis/frontend

echo "=== 1. package.json의 Tailwind 의존성 ==="
cat package.json | grep -A2 -B2 tailwind

echo -e "\n=== 2. node_modules의 실제 버전 ==="
cat node_modules/tailwindcss/package.json 2>/dev/null | grep '"version"' || echo "tailwindcss not installed"

echo -e "\n=== 3. package-lock.json의 버전 ==="
cat package-lock.json 2>/dev/null | grep -A2 '"tailwindcss"' | head -10 || echo "no package-lock.json"

echo -e "\n=== 4. 어떤 패키지가 tailwindcss를 의존하는지 ==="
npm ls tailwindcss 2>&1 | head -20

echo -e "\n=== 5. PostCSS 설정 ==="
cat postcss.config.js 2>/dev/null || echo "no postcss.config.js"

echo -e "\n=== 6. Tailwind 설정 ==="
cat tailwind.config.js 2>/dev/null || cat tailwind.config.ts 2>/dev/null || echo "no tailwind config"

echo -e "\n=== 7. CSS import 스타일 ==="
find src -name "*.css" -exec echo "=== {} ===" \; -exec head -10 {} \; 2>/dev/null

echo -e "\n=== 8. 빌드된 CSS의 Tailwind 버전 ==="
grep -o "tailwindcss v[0-9.]*" dist/assets/*.css 2>/dev/null | head -1 || echo "no dist files"
```

---

## 💡 핵심 포인트

### v3로 고정하려면:
1. ✅ `--save-exact` 플래그 사용 (^ 제거)
2. ✅ `package-lock.json` 삭제 후 재설치
3. ✅ `@tailwindcss/postcss` 완전 제거 (v4 전용 패키지)
4. ✅ CSS import를 `@tailwind` 지시문으로 변경 (v3 스타일)

### 확인 방법:
```bash
# package.json에서
"tailwindcss": "3.4.17"  ← ^ 없어야 함!

# CSS 파일에서
/*! tailwindcss v3.4.17 | ... */  ← v3.x.x여야 함!
```

