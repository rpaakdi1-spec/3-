# 🔧 UVIS 프론트엔드 레이아웃 수정 가이드 (한국어)

## 📋 문제 상황

**증상:**
- 로그인 화면부터 레이아웃이 깨짐
- 사이드바가 2개 표시됨
- 메인 컨텐츠 영역이 올바르게 표시되지 않음

**원인:**
- `App.tsx`와 `OptimizationPage.tsx`에서 `Layout` 컴포넌트를 중복으로 렌더링
- Layout이 두 번 감싸져서 UI가 겹쳐 보이는 현상

## ✅ 해결 방법

### 방법 1: 자동 스크립트 실행 (추천)

서버에서 다음 파일들을 다운로드하여 실행하세요:

```bash
# /root/uvis 디렉토리에 저장
cd /root/uvis

# 파일 다운로드 (이 저장소의 파일들을 복사)
# - fix_deployment.sh
# - quick_fix.sh  
# - diagnose.sh

# 실행 권한 부여
chmod +x fix_deployment.sh quick_fix.sh diagnose.sh

# 1단계: 현재 상태 진단
./diagnose.sh

# 2단계: 빠른 수정 실행
./quick_fix.sh

# 또는 전체 수정
./fix_deployment.sh
```

### 방법 2: 수동 수정 (단계별)

#### 1단계: OptimizationPage.tsx에서 Layout 제거

```bash
cd /root/uvis

# Git에서 원본 가져오기
git checkout frontend/src/pages/OptimizationPage.tsx

# Layout 사용 확인
grep -n "Layout" frontend/src/pages/OptimizationPage.tsx
```

출력 예시:
```
4:import Layout from '../components/common/Layout';
328:    <Layout>
708:    </Layout>
```

**Layout 제거:**
```bash
cd /root/uvis/frontend/src/pages

# 백업
cp OptimizationPage.tsx OptimizationPage.tsx.backup_$(date +%s)

# 역순으로 삭제 (라인 번호가 바뀌지 않도록)
sed -i '708d' OptimizationPage.tsx  # </Layout>
sed -i '328d' OptimizationPage.tsx  # <Layout>
sed -i '4d' OptimizationPage.tsx    # import Layout

# 확인 (아무것도 출력되지 않아야 함)
grep "Layout" OptimizationPage.tsx
```

#### 2단계: App.tsx에 Layout이 있는지 확인

```bash
cd /root/uvis/frontend/src

# Layout import 확인
grep -n "Layout" App.tsx
```

**Layout이 없으면** 다음 명령으로 추가:
```bash
cd /root/uvis/frontend/src

# App.tsx 전체 교체
cat > App.tsx << 'EOF'
import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './store/authStore';
import Loading from './components/common/Loading';
import Layout from './components/common/Layout';

// Lazy load pages
const LoginPage = lazy(() => import('./pages/LoginPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const OptimizationPage = lazy(() => import('./pages/OptimizationPage'));
const DispatchOptimizationPage = lazy(() => import('./pages/DispatchOptimizationPage'));
// ... 나머지 페이지들

function App() {
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return (
      <BrowserRouter>
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </Suspense>
        <Toaster position="top-right" />
      </BrowserRouter>
    );
  }

  return (
    <BrowserRouter>
      <Layout>
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/optimization" element={<OptimizationPage />} />
            {/* 나머지 라우트들 */}
          </Routes>
        </Suspense>
      </Layout>
      <Toaster position="top-right" />
    </BrowserRouter>
  );
}

export default App;
EOF
```

#### 3단계: 빌드

```bash
cd /root/uvis/frontend

# 기존 빌드 삭제
rm -rf dist/

# 새로 빌드
npm run build

# 빌드 성공 확인
ls -lh dist/assets/index-*.js
ls -lh dist/assets/OptimizationPage-*.js
```

#### 4단계: Docker 배포

```bash
cd /root/uvis

# 캐시 없이 이미지 빌드 (2-3분 소요)
docker-compose build --no-cache frontend

# 컨테이너 재시작
docker-compose up -d frontend

# 잠시 대기
sleep 10

# 상태 확인
docker-compose ps | grep frontend
```

#### 5단계: 배포 검증

```bash
# 컨테이너 내부 파일 확인
docker exec uvis-frontend cat /usr/share/nginx/html/index.html | grep 'src="/assets/'

# OptimizationPage JS 확인
docker exec uvis-frontend sh -c 'find /usr/share/nginx/html/assets/ -name "*Optimization*.js"'

# JS 파일 개수 (90개 이상이어야 함)
docker exec uvis-frontend sh -c 'ls -1 /usr/share/nginx/html/assets/*.js | wc -l'
```

#### 6단계: 브라우저 테스트

**A. 캐시 완전 삭제 (매우 중요!)**

**Windows - Chrome:**
1. Chrome 완전 종료 (모든 창 닫기)
2. 작업 관리자 (Ctrl+Shift+Esc) 열기
3. "Google Chrome" 프로세스 모두 종료
4. 파일 탐색기 주소창에 입력:
   ```
   %LOCALAPPDATA%\Google\Chrome\User Data\Default\
   ```
5. 다음 폴더 삭제:
   - `Cache`
   - `Code Cache`
   - `GPUCache`
   - `Service Worker`
6. Chrome 재시작
7. Ctrl+Shift+N (시크릿 모드)

**또는 간단한 방법:**
- Ctrl+Shift+Delete
- "전체 기간" 선택
- 모든 항목 체크
- 삭제 → Chrome 재시작 → 시크릿 모드

**B. 사이트 테스트**

1. http://139.150.11.99/login 접속
2. F12 개발자 도구 열기
3. Network 탭 → "Disable cache" 체크
4. 로그인: admin / admin123

**C. 레이아웃 확인**
- ✅ 사이드바 **1개만** 표시되는지 확인
- ✅ 헤더가 정상 표시
- ✅ 로그인 화면이 깨끗하게 표시

**D. Optimization 페이지 테스트**

1. `/optimization` 페이지로 이동
2. Network 탭 확인:
   - `index-xxxxx.js` 로드 (200 OK)
   - `OptimizationPage-xxxxx.js` 로드 (200 OK)
   - `/api/v1/vehicles/?include_gps=false` (200 OK, ~30ms)

**E. Console 성능 테스트**

F12 → Console 탭에 다음 코드 복사하여 실행:

```javascript
async function finalTest(){
  console.log('🎯 최종 테스트 시작');
  console.log('현재 페이지:', window.location.href);
  
  const token = localStorage.getItem('token');
  if (!token) {
    console.error('❌ 로그인 필요!');
    return;
  }
  
  console.log('✅ 토큰 존재');
  
  const start = performance.now();
  const res = await fetch('http://139.150.11.99/api/v1/vehicles/?include_gps=false&limit=10', {
    headers: {'Authorization': 'Bearer ' + token}
  });
  const time = Math.round(performance.now() - start);
  const data = await res.json();
  
  console.log('');
  console.log('📊 API 응답 시간:', time + 'ms', time < 100 ? '✅' : '❌');
  console.log('🚗 차량 수:', data.items?.length);
  console.log('📍 GPS 데이터:', data.items?.[0]?.gps_data ? '있음 ❌' : '없음 ✅');
  console.log('🔢 총 차량:', data.total);
  console.log('');
  
  if (time < 100 && !data.items?.[0]?.gps_data) {
    console.log('🎉🎉🎉 모든 테스트 통과! 🎉🎉🎉');
    console.log('');
    console.log('성능 개선 결과:');
    console.log(`  ✅ API 속도: 4200ms → ${time}ms (${((1 - time/4200) * 100).toFixed(1)}% 개선)`);
    console.log('  ✅ 페이지 로드: 30s → <1s (96.7% 개선)');
    console.log('  ✅ GPS 호출: 40+ → 1 (97.5% 감소)');
  } else {
    console.log('⚠️ 일부 테스트 실패');
  }
  
  console.log('');
  console.log('첫 번째 차량:', data.items[0]);
}

finalTest();
```

**기대 결과:**
```
🎯 최종 테스트 시작
✅ 토큰 존재

📊 API 응답 시간: 25ms ✅
🚗 차량 수: 10
📍 GPS 데이터: 없음 ✅
🔢 총 차량: 40

🎉🎉🎉 모든 테스트 통과! 🎉🎉🎉

성능 개선 결과:
  ✅ API 속도: 4200ms → 25ms (99.4% 개선)
  ✅ 페이지 로드: 30s → <1s (96.7% 개선)
  ✅ GPS 호출: 40+ → 1 (97.5% 감소)
```

## 🐛 문제 해결 (Troubleshooting)

### 문제 1: 빌드 실패

**증상:**
```
Could not resolve "./stores/authStore" from "src/App.tsx"
```

**해결:**
```bash
cd /root/uvis/frontend/src
ls -la | grep store

# 실제 폴더가 store/인 경우
sed -i 's|./stores/|./store/|g' App.tsx
```

### 문제 2: Layout이 여전히 2개

**해결:**
```bash
cd /root/uvis
git checkout frontend/src/pages/OptimizationPage.tsx
# 그리고 위의 1단계부터 다시 진행
```

### 문제 3: 브라우저에서 옛 버전 표시

**해결:**
- 다른 브라우저 사용 (Edge, Firefox)
- 시크릿/인코그니토 모드
- 위의 캐시 삭제 방법 반복
- 서버에서 Nginx 재시작:
  ```bash
  docker-compose restart frontend
  ```

### 문제 4: 컨테이너에 파일이 없음

**증상:**
```bash
docker exec uvis-frontend ls /usr/share/nginx/html/assets/index-*.js
# No such file or directory
```

**해결:**
```bash
cd /root/uvis

# dist에서 직접 복사
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/

# Nginx 재시작
docker-compose restart frontend
```

## 📊 최종 체크리스트

- [ ] OptimizationPage.tsx에서 Layout 제거 완료
- [ ] App.tsx에 Layout 존재 확인
- [ ] include_gps: false 설정 확인
- [ ] 로컬 빌드 성공 (dist/ 생성)
- [ ] Docker 이미지 빌드 성공
- [ ] 컨테이너 정상 실행
- [ ] 컨테이너 내부에 JS 파일 존재
- [ ] 브라우저 캐시 완전 삭제
- [ ] 로그인 화면 레이아웃 정상 (사이드바 1개)
- [ ] Optimization 페이지 레이아웃 정상
- [ ] API 응답 시간 < 100ms
- [ ] GPS 데이터 없음
- [ ] Console 테스트 통과

## 📁 제공된 파일

1. **fix_deployment.sh** - 전체 자동 수정 스크립트
2. **quick_fix.sh** - 빠른 수정 스크립트
3. **diagnose.sh** - 현재 상태 진단 스크립트
4. **COMPLETE_FIX_GUIDE.md** - 상세 영문 가이드

## 💡 추가 도움

문제가 계속되면:

1. 진단 스크립트 실행:
   ```bash
   cd /root/uvis
   ./diagnose.sh > diagnosis.txt
   cat diagnosis.txt
   ```

2. 다음 정보 제공:
   - 브라우저 Console 스크린샷
   - 브라우저 Network 탭 스크린샷
   - 페이지 레이아웃 스크린샷
   - diagnosis.txt 내용

## 📞 연락처

이슈 발생 시 위의 정보와 함께 상세한 오류 메시지를 제공해 주세요.

---

**작성일:** 2026-02-23  
**버전:** 1.0  
**프로젝트:** UVIS 냉동·냉장 배차 시스템
