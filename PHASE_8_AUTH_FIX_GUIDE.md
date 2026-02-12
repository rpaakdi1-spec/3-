# Phase 8 인증 오류 해결 가이드

**발견 시각**: 2026-02-07  
**오류 코드**: 401 Unauthorized  
**위치**: 재무 대시보드 페이지  
**심각도**: 🟡 Medium (사용자 재로그인으로 해결 가능)

---

## 🔍 오류 분석

### 발견된 오류
```javascript
GET http://139.150.11.99/api/v1/billing/enhanced/dashboard/financial 
401 (Unauthorized)

Failed to load dashboard data: 
AxiosError: Request failed with status code 401
```

### 원인
- JWT 토큰이 만료되었거나
- 로컬 스토리지에 토큰이 없거나
- 토큰 형식이 잘못됨

### 백엔드 검증 결과
✅ 백엔드는 정상 작동 중
- ✅ 로그인 API: 200 OK
- ✅ 토큰 발급: 정상
- ✅ Financial Dashboard API: 200 OK
- ✅ 응답 데이터: 정상

**결론**: 프론트엔드 토큰 관리 문제

---

## ✅ 즉시 해결 방법 (사용자용)

### 방법 1: 재로그인 (권장)
```
1. 현재 페이지 새로고침: F5
2. 로그아웃 버튼 클릭 (우측 상단)
3. 로그인 페이지로 이동
4. admin / admin123 입력
5. 로그인 후 재무 대시보드 재접속
```

### 방법 2: 강력 새로고침
```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

### 방법 3: 브라우저 캐시 삭제
```
Chrome:
1. F12 → Application 탭
2. Storage → Clear site data
3. 페이지 새로고침

Firefox:
1. F12 → Storage 탭
2. Local Storage 우클릭 → Delete All
3. 페이지 새로고침
```

### 방법 4: 시크릿 모드 테스트
```
Chrome: Ctrl + Shift + N
Firefox: Ctrl + Shift + P
Edge: Ctrl + Shift + N

시크릿 창에서 http://139.150.11.99/ 접속
admin / admin123로 로그인
재무 대시보드 테스트
```

---

## 🔧 개발자 디버깅 단계

### 1. 로컬 스토리지 확인
```javascript
// F12 Console에서 실행
localStorage.getItem('token')
localStorage.getItem('access_token')
localStorage.getItem('auth_token')

// 모든 스토리지 확인
console.log('LocalStorage:', localStorage)
console.log('SessionStorage:', sessionStorage)
```

### 2. Axios 인터셉터 확인
```javascript
// F12 Console에서 실행
// 토큰이 요청 헤더에 포함되는지 확인
axios.interceptors.request.use(
  config => {
    console.log('Request Headers:', config.headers);
    return config;
  }
);
```

### 3. 네트워크 탭 확인
```
F12 → Network 탭
financial 요청 선택
Headers → Request Headers → Authorization 확인
```

**예상 헤더**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**문제 시나리오**:
```
Authorization: (없음)
또는
Authorization: Bearer null
또는
Authorization: Bearer undefined
```

---

## 🛠️ 프론트엔드 수정 (개발자용)

### 이슈 위치
```
파일: frontend/src/pages/billing/FinancialDashboardPage.tsx
      frontend/src/services/api.ts
      frontend/src/store/authStore.ts
```

### 수정 1: API 클라이언트에 토큰 추가

#### frontend/src/services/api.ts
```typescript
import axios from 'axios';

// API 클라이언트 생성
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://139.150.11.99:8000',
});

// 요청 인터셉터: 모든 요청에 토큰 추가
api.interceptors.request.use(
  (config) => {
    // 로컬 스토리지에서 토큰 가져오기
    const token = localStorage.getItem('access_token') 
                || localStorage.getItem('token')
                || sessionStorage.getItem('access_token');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 401 오류 시 로그인 페이지로 리다이렉트
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 또는 인증 실패
      localStorage.removeItem('access_token');
      localStorage.removeItem('token');
      sessionStorage.removeItem('access_token');
      
      // 로그인 페이지로 리다이렉트
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 수정 2: 로그인 시 토큰 저장 확인

#### frontend/src/store/authStore.ts
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  user: any | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      
      login: async (username: string, password: string) => {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch('http://139.150.11.99:8000/api/v1/auth/login', {
          method: 'POST',
          body: formData,
        });
        
        if (!response.ok) {
          throw new Error('Login failed');
        }
        
        const data = await response.json();
        
        // 토큰과 사용자 정보 저장
        set({ token: data.access_token, user: data.user });
        
        // 로컬 스토리지에도 저장
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
      },
      
      logout: () => {
        set({ token: null, user: null });
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

### 수정 3: 대시보드 페이지에서 토큰 확인

#### frontend/src/pages/billing/FinancialDashboardPage.tsx
```typescript
import { useEffect, useState } from 'react';
import { useAuthStore } from '../../store/authStore';
import api from '../../services/api';

export const FinancialDashboardPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { token } = useAuthStore();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 토큰 확인
        if (!token) {
          console.error('No token found');
          window.location.href = '/login';
          return;
        }

        setLoading(true);
        
        // API 호출 (인터셉터가 자동으로 토큰 추가)
        const response = await api.get('/api/v1/billing/enhanced/dashboard/financial', {
          params: {
            start_date: '2025-11-07',
            end_date: '2026-02-07',
          },
        });
        
        setData(response.data);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
        setError(err.message);
        
        // 401 오류 시 로그인 페이지로
        if (err.response?.status === 401) {
          window.location.href = '/login';
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {/* 대시보드 컨텐츠 */}
    </div>
  );
};
```

---

## 🧪 프로덕션 서버에서 테스트

### 백엔드 테스트 (이미 확인됨 ✅)
```bash
# 프로덕션 서버에서 실행
cd /root/uvis

# 테스트 스크립트 실행
curl -s -X POST "http://139.150.11.99:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 결과: ✅ 200 OK, 토큰 발급 성공
```

### 프론트엔드 빌드 및 배포
```bash
cd /root/uvis/frontend

# 수정 후 빌드
npm run build

# Docker 재빌드
cd /root/uvis
docker-compose build --no-cache frontend
docker-compose up -d frontend

# 확인
docker logs uvis-frontend --tail 50
```

---

## 📊 근본 원인 분석

### 가능한 원인

1. **토큰 스토리지 키 불일치**
   ```
   백엔드: access_token
   프론트엔드: token (불일치)
   ```

2. **토큰 만료 처리 미흡**
   ```
   토큰 만료 시 자동 로그아웃 누락
   401 응답 시 리다이렉트 누락
   ```

3. **Axios 인터셉터 미설정**
   ```
   Authorization 헤더 자동 추가 누락
   ```

4. **로그인 후 토큰 저장 누락**
   ```
   localStorage.setItem 누락
   Zustand persist 미설정
   ```

---

## ✅ 임시 해결책 (Quick Fix)

### 브라우저 콘솔에서 수동 토큰 설정

```javascript
// F12 Console에서 실행

// 1. 로그인하여 토큰 받기
fetch('http://139.150.11.99:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=admin&password=admin123'
})
.then(res => res.json())
.then(data => {
  console.log('Token:', data.access_token);
  
  // 2. 로컬 스토리지에 저장
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  
  console.log('✅ Token saved!');
  
  // 3. 페이지 새로고침
  location.reload();
});
```

---

## 📝 체크리스트

### 사용자 확인 사항
- [ ] 재로그인 시도
- [ ] 강력 새로고침 (Ctrl+Shift+R)
- [ ] 시크릿 모드에서 테스트
- [ ] 다른 브라우저에서 테스트

### 개발자 확인 사항
- [ ] 로컬 스토리지에 토큰 존재 여부
- [ ] Authorization 헤더 포함 여부
- [ ] API 인터셉터 설정 확인
- [ ] 로그인 후 토큰 저장 로직 확인
- [ ] 401 응답 처리 로직 확인

### 프로덕션 확인 사항
- [ ] 백엔드 로그인 API 정상
- [ ] 백엔드 대시보드 API 정상
- [ ] 프론트엔드 빌드 최신 버전
- [ ] Docker 컨테이너 정상 실행

---

## 🎯 권장 조치

### 즉시 (사용자)
1. **재로그인**: admin / admin123
2. **강력 새로고침**: Ctrl+Shift+R
3. **다시 테스트**: 재무 대시보드 접속

### 단기 (개발자)
1. **토큰 인터셉터 추가**: api.ts 수정
2. **401 리다이렉트 구현**: 자동 로그아웃
3. **토큰 저장 확인**: localStorage 설정
4. **빌드 및 배포**: 프로덕션 업데이트

### 중기 (개선)
1. **토큰 갱신 로직**: Refresh Token 구현
2. **토큰 만료 알림**: 사용자에게 사전 알림
3. **자동 재로그인**: 토큰 만료 시 자동 갱신
4. **에러 처리 개선**: 사용자 친화적 메시지

---

## 📞 지원

### 즉시 해결이 필요한 경우
```bash
# 프로덕션 서버에서 백엔드 재시작
cd /root/uvis
docker-compose restart backend

# 프론트엔드 재시작
docker-compose restart frontend

# 로그 확인
docker logs uvis-frontend --tail 100
docker logs uvis-backend --tail 100
```

### 문제 지속 시
1. 스크린샷 촬영 (F12 Console + Network 탭)
2. 오류 메시지 복사
3. GitHub Issue 생성: https://github.com/rpaakdi1-spec/3-/issues

---

## 🎯 최종 상태

### 현재 상황
- ✅ 백엔드: 정상 (로그인 API, 대시보드 API 모두 200 OK)
- ⚠️ 프론트엔드: 토큰 관리 이슈 (401 Unauthorized)

### 예상 해결 시간
- 사용자 재로그인: 즉시 (1분)
- 코드 수정 및 배포: 30분
- 완전 해결: 1시간 이내

### 우선순위
🟡 **Medium** - 사용자가 재로그인으로 우회 가능

---

**작성일**: 2026-02-07  
**최종 업데이트**: 2026-02-07 06:30 UTC  
**상태**: 해결 중 (임시 해결책 제공, 영구 수정 권장)
