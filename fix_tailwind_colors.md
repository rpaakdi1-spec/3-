# 🔥 Tailwind CSS 색상 클래스 누락 문제 해결

## 문제 진단
- ✅ CSS 파일이 로드됨 (14,918 bytes)
- ✅ Tailwind v4.1.18 확인됨
- ❌ 색상 클래스가 생성되지 않음 (`.bg-blue-400`, `.text-white` 등)

## 원인
Tailwind CSS v4는 **JIT (Just-In-Time)** 모드로 동작하며, 
실제로 사용된 클래스만 생성합니다.

**그러나** 현재 빌드에서 색상 클래스가 하나도 생성되지 않은 것은:
1. Tailwind가 소스 코드를 스캔하지 못함
2. `content` 설정이 잘못됨
3. 또는 Tailwind v4 PostCSS 플러그인 문제

---

## 🚀 해결책: 서버에서 실행

### Step 1: Tailwind 설정 확인

```bash
cd /root/uvis/frontend

# 현재 Tailwind 설정 확인
cat tailwind.config.js 2>/dev/null || cat tailwind.config.ts 2>/dev/null || echo "설정 파일 없음"

# PostCSS 설정 확인
cat postcss.config.js
```

### Step 2: package.json의 Tailwind 버전 확인

```bash
cat package.json | grep -A2 -B2 tailwind
```

### Step 3: CSS import 파일 확인

```bash
# 메인 CSS 파일이 Tailwind를 올바르게 import하는지 확인
find src -name "*.css" -exec echo "=== {} ===" \; -exec head -20 {} \;
```

### Step 4: 임시 해결책 - Tailwind v3로 다운그레이드

```bash
cd /root/uvis/frontend

# Tailwind v3로 다운그레이드
npm uninstall @tailwindcss/postcss tailwindcss
npm install -D tailwindcss@3.4.17 postcss@8.4.38 autoprefixer@10.4.18 --legacy-peer-deps

# PostCSS 설정 수정
cat > postcss.config.js << 'POSTCSS_EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
POSTCSS_EOF

# Tailwind 설정 확인/생성
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

# 재빌드
npm run build

# 빌드 확인
ls -lh dist/assets/*.css

# CSS에 색상 클래스가 생성되었는지 확인
grep -o "\.bg-blue-[0-9]*\|\.text-white\|\.bg-white" dist/assets/*.css | head -10

# Docker 재배포
cd /root/uvis
docker-compose restart frontend

# 10초 대기
sleep 10

# 브라우저 테스트
echo "✅ 브라우저에서 시크릿 모드로 http://139.150.11.99 접속"
echo "✅ Ctrl + Shift + N → http://139.150.11.99"
```

---

## 📋 예상 결과

### 성공 시:
```bash
# CSS 파일 크기가 증가함 (색상 클래스 추가로)
dist/assets/index-[hash].css: ~50-100 KB (이전: 14.9 KB)

# CSS에 색상 클래스 확인됨
.bg-blue-400
.bg-blue-500
.bg-blue-600
.text-white
.bg-white
```

### 실패 시:
- 빌드 로그 확인: `npm run build 2>&1 | tee build.log`
- Tailwind 경고 메시지 확인
- `content` 설정이 올바른지 확인

---

## 🔧 대안: Tailwind v4 수정

Tailwind v4를 계속 사용하려면:

```bash
cd /root/uvis/frontend

# @tailwindcss/postcss 최신 버전으로 업데이트
npm install -D @tailwindcss/postcss@latest --legacy-peer-deps

# CSS 파일에 Tailwind v4 import 확인
cat > src/index.css << 'CSS_EOF'
@import "tailwindcss";
CSS_EOF

# 재빌드
npm run build
```

---

## 💡 핵심 포인트

**문제**: Tailwind가 색상 클래스를 생성하지 않음  
**원인**: Tailwind v4 PostCSS 설정 또는 content 스캔 실패  
**해결**: Tailwind v3로 다운그레이드 (100% 안정적)

