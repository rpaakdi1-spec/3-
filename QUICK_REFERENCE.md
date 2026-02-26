# 🎯 UVIS Layout Fix - Quick Reference

## ⚡ 빠른 실행

```bash
# 파일 복사
cp /home/user/webapp/{complete_layout_fix.sh,batch_remove_layout.sh,verify_layout_fix.sh} /root/uvis/

# 실행
cd /root/uvis
chmod +x *.sh
./complete_layout_fix.sh
```

**소요 시간**: 약 5-7분

---

## 📋 문제 & 해결

### 문제
- ❌ 일부 페이지에서 메뉴/사이드바 사라짐
- ❌ 44개 페이지가 개별 Layout 사용

### 해결
- ✅ 모든 페이지에서 Layout 제거
- ✅ App.tsx의 단일 Layout만 사용

---

## 🔧 3가지 실행 옵션

### 1️⃣ 원클릭 (추천)
```bash
./complete_layout_fix.sh
```

### 2️⃣ 단계별
```bash
./batch_remove_layout.sh    # Layout 제거
./verify_layout_fix.sh       # 검증
cd frontend && npm run build # 빌드
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### 3️⃣ 수동 (비추천)
```bash
# 각 페이지마다
sed -i '/import.*Layout/d' Page.tsx
sed -i '/<Layout>/d' Page.tsx
sed -i '/<\/Layout>/d' Page.tsx
```

---

## ✅ 테스트

### 브라우저
1. **캐시 삭제** (Ctrl+Shift+Delete, 전체 기간)
2. **Chrome 재시작**
3. http://139.150.11.99/login
4. admin / admin123
5. **모든 페이지 확인**
   - [ ] 사이드바 표시
   - [ ] 메뉴 동작
   - [ ] 페이지 전환 정상

### 콘솔 확인
```javascript
// 브라우저 콘솔 (F12)
console.log('Path:', window.location.pathname);
console.log('Nav count:', document.querySelectorAll('nav').length); // 1이어야 함
```

---

## 🐛 문제 해결

| 문제 | 해결 |
|------|------|
| Permission denied | `chmod +x /root/uvis/*.sh` |
| 빌드 실패 | 백업 복구 후 재시도 |
| 컨테이너 안 됨 | `docker logs uvis-frontend` 확인 |
| 이전 버전 로드 | 캐시 재삭제, 시크릿 모드 |

### 백업 복구
```bash
cd /root/uvis/frontend/src/pages
BACKUP=$(ls -dt layout_removal_backup_* | head -1)
cp "$BACKUP"/*.tsx ./
```

---

## 📊 예상 결과

### Before
```
📊 Layout을 사용하는 페이지: 44 개
❌ UI 일관성 없음
```

### After
```
✅ 성공: 44 개
✅ Layout이 남아있는 페이지: 0 개
✅ 모든 페이지에서 사이드바 표시
```

---

## 📦 파일 목록

| 파일 | 크기 | 용도 |
|------|------|------|
| complete_layout_fix.sh | 5.3K | 전체 자동화 |
| batch_remove_layout.sh | 3.9K | Layout 일괄 제거 |
| verify_layout_fix.sh | 5.2K | 검증 |
| LAYOUT_BATCH_REMOVAL_GUIDE.md | 7.7K | 상세 가이드 |
| UVIS_UI_FIX_COMPLETE_GUIDE.md | 7.2K | 완전 가이드 |

---

## 💡 핵심 원칙

### ✅ DO
- Layout은 **App.tsx에만**
- 페이지는 **순수 컴포넌트**
- 캐시 **완전 삭제**

### ❌ DON'T
- 개별 페이지에서 Layout import 금지
- 부분 캐시 삭제 금지
- 백업 없이 수정 금지

---

**TL;DR**
```bash
cp /home/user/webapp/*.sh /root/uvis/
cd /root/uvis && chmod +x *.sh && ./complete_layout_fix.sh
# 브라우저 캐시 삭제 → 테스트
```
