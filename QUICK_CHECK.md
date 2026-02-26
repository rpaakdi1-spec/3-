# 🚀 빠른 진단 - Tailwind CSS 미적용 문제

## ⚡ 30초 체크 (브라우저에서)

### 1. F12 → Console 탭
오류 메시지가 있나요?
- ❌ 있다면 → 메시지 복사해서 알려주세요
- ✅ 없다면 → 다음 단계로

### 2. F12 → Network 탭
`index-BjMybcaV.css` 클릭 → Response 탭
처음 몇 줄에 이런 내용이 있나요?
```css
.bg-gradient-to-b{background-image:linear-gradient(to bottom,var(--tw-gradient-stops))}
.from-blue-400{--tw-gradient-from:#60a5fa}
```

- ✅ 있다면 → **문제 B** (CSS는 있지만 적용 안됨)
- ❌ 없다면 → **문제 A** (Tailwind가 빌드 안됨) ⬅️ **가장 유력!**

---

## 🔧 해결 방법

### 문제 A: Tailwind CSS가 빌드 안됨 (90% 확률)

**서버에서 다음 명령어 실행:**

```bash
cd /root/uvis/frontend

# 1단계: Tailwind 설정 확인
echo "=== 현재 빌드된 CSS 확인 ==="
head -30 dist/assets/index-BjMybcaV.css

echo ""
echo "=== Tailwind 클래스 검색 ==="
grep -c "\.bg-gradient-to-b" dist/assets/index-BjMybcaV.css || echo "Tailwind 클래스 없음! 재빌드 필요"

echo ""
echo "=== src/index.css 확인 ==="
head -5 src/index.css
```

**만약 "Tailwind 클래스 없음!" 이 나오면:**

```bash
cd /root/uvis/frontend

# 클린 빌드
rm -rf dist node_modules/.vite
npm run build

# 빌드 확인
head -30 dist/assets/index-*.css
grep -c "bg-gradient" dist/assets/index-*.css

# Docker 재배포
cd /root/uvis
docker exec uvis-frontend rm -rf /usr/share/nginx/html/*
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker exec uvis-frontend nginx -s reload

# 브라우저: Ctrl+Shift+F5
```

---

### 문제 B: CSS 파일은 있지만 적용 안됨 (10% 확률)

**서버에서:**
```bash
# React가 제대로 렌더링되는지 확인
docker logs uvis-frontend --tail 30

# JS 오류 확인
curl http://139.150.11.99/ | grep "script\|link"
```

**브라우저에서:**
- F12 → Elements → `<div id="root">` 안에 무엇이 있는지 확인
- 빈 화면이면: JavaScript 오류
- 내용은 있는데 스타일 없으면: CSS 경로 오류

---

## 📋 진단 결과 공유 양식

다음 정보를 복사해서 붙여넣어 주세요:

```
=== 브라우저 Console (F12) ===
(오류 메시지 복사 - 없으면 "없음")

=== Network Response (index-BjMybcaV.css) ===
(처음 5줄 복사)

=== 서버 명령어 결과 ===
$ cd /root/uvis/frontend && head -30 dist/assets/index-BjMybcaV.css
(결과 복사)
```

이 정보를 주시면 정확한 해결책을 드리겠습니다!
