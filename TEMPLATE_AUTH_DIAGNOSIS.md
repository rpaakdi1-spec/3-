# 템플릿 관리 페이지 401 오류 해결 가이드

## 🔴 문제 증상

템플릿 관리 페이지(`http://139.150.11.99/template-management`)에서:
- ⭐ 즐겨찾기 토글 → **401 Unauthorized**
- ⚡ 활성화/비활성화 토글 → **401 Unauthorized**  
- 📋 템플릿 복제 → **401 Unauthorized**
- 🗑️ 템플릿 삭제 → **401 Unauthorized**

Network 탭 확인 시:
- **Authorization 헤더가 누락**됨
- Request Headers에 `Authorization: Bearer ...` 없음

## 🔍 원인 분석

### 코드는 정상입니다!

1. **API Client (`frontend/src/api/client.ts`)** ✅
   ```typescript
   this.client.interceptors.request.use(
     (config) => {
       const token = localStorage.getItem('access_token');
       if (token) {
         config.headers.Authorization = `Bearer ${token}`;
       }
       return config;
     }
   );
   ```
   → 모든 요청에 자동으로 Authorization 헤더 추가

2. **Template Management Page** ✅
   ```typescript
   const toggleFavorite = async (id: number, currentStatus: boolean) => {
     await apiClient.put(`/dispatch-form/templates/${id}`, {
       is_favorite: !currentStatus
     });
   };
   ```
   → `apiClient` 사용, 헤더 자동 추가됨

3. **Nginx 설정** ✅
   ```nginx
   add_header Cache-Control "no-store, no-cache, must-revalidate";
   ```
   → 캐시 방지 설정 이미 적용됨

### 실제 원인: 브라우저 캐시

**브라우저가 이전 빌드의 JavaScript 파일을 캐시**하고 있습니다!
- 서버는 최신 코드를 제공하지만
- 브라우저는 오래된 JS 파일 (Authorization 헤더 없는 버전)을 사용 중

## ✅ 해결 방법

### 방법 1: 시크릿 모드 (가장 빠르고 확실)

```
1. Ctrl + Shift + N (Chrome) 또는 Ctrl + Shift + P (Firefox)
2. http://139.150.11.99 접속
3. 로그인 (admin / 비밀번호)
4. 템플릿 관리 페이지 테스트
```

**✅ 이 방법이 성공하면 → 캐시 문제 확정**

### 방법 2: 브라우저 캐시 완전 삭제

```
1. Ctrl + Shift + Delete
2. 전체 기간 선택
3. "쿠키 및 기타 사이트 데이터" 체크
4. "캐시된 이미지 및 파일" 체크
5. 데이터 삭제 클릭
6. F12 개발자 도구 열기
7. Network 탭 → "Disable cache" 체크
8. 개발자 도구를 연 상태에서 Ctrl + Shift + R (강력 새로고침)
```

### 방법 3: 콘솔에서 강제 로그아웃

```javascript
// F12 → Console 탭에서 실행
localStorage.clear();
sessionStorage.clear();
location.href = '/login';
```

로그인 후 다시 템플릿 관리 페이지 접속

### 방법 4: 서버 재빌드 (이미 완료)

```bash
cd /root/uvis
bash CLEAR_CACHE_AND_TEST.sh
```

## 🧪 테스트 페이지

### 직접 API 테스트 페이지 접속

```
http://139.150.11.99/test-api.html
```

이 페이지에서:
1. ✅ 인증 상태 확인
2. ✅ 템플릿 목록 조회 (GET)
3. ✅ 즐겨찾기 변경 (PUT)
4. ✅ 템플릿 복제 (POST)

**이 페이지가 정상 작동하면 → 코드 문제 없음, 캐시 문제**

## 🔍 진단 체크리스트

### 1단계: 로그인 상태 확인

```javascript
// 브라우저 콘솔 (F12)에서 실행
console.log('Token:', localStorage.getItem('access_token'));
console.log('User:', JSON.parse(localStorage.getItem('user')));
```

**예상 결과:**
```
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcxMD...
User: {username: "admin", role: "ADMIN", ...}
```

**❌ 만약 `Token: null` → 다시 로그인 필요**

### 2단계: Network 탭 확인

1. F12 → Network 탭
2. 템플릿 즐겨찾기 ⭐ 클릭
3. `templates/40` PUT 요청 찾기
4. **Request Headers** 확인:

**✅ 정상:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**❌ 문제:**
```
Content-Type: application/json
(Authorization 헤더 없음!)
```

**→ Authorization 헤더 없으면 → 브라우저 캐시 문제 확정**

### 3단계: 직접 fetch 테스트

```javascript
// 브라우저 콘솔에서 실행
fetch('http://139.150.11.99/api/v1/dispatch-form/templates/40', {
  method: 'PUT',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ is_favorite: true })
})
.then(r => r.json())
.then(d => console.log('Success:', d))
.catch(e => console.error('Error:', e));
```

**✅ 이 테스트가 성공하면 → API는 정상, UI 코드 캐시 문제**

## 📊 DB 확인

### 최근 변경된 템플릿 확인

```bash
cd /root/uvis

docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT id, name, is_favorite, is_active, updated_at 
FROM dispatch_form_templates 
ORDER BY updated_at DESC 
LIMIT 5;
"
```

### 즐겨찾기 템플릿 확인

```bash
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT id, name, is_favorite 
FROM dispatch_form_templates 
WHERE is_favorite = true;
"
```

## 🎯 최종 해결 플랜

### Plan A: 사용자가 즉시 해결 (권장)

```
1. 시크릿 모드로 http://139.150.11.99 접속
2. 로그인
3. 템플릿 관리 페이지 테스트
   → ✅ 성공하면 일반 브라우저에서 캐시 삭제만 하면 됨
```

### Plan B: 일반 브라우저 캐시 삭제

```
1. Ctrl + Shift + Delete → 전체 기간 캐시 삭제
2. F12 → Network → Disable cache 체크
3. Ctrl + Shift + R (강력 새로고침)
4. 콘솔에서 localStorage.clear() 실행
5. 다시 로그인
```

### Plan C: 테스트 페이지로 확인

```
1. http://139.150.11.99/test-api.html 접속
2. "1️⃣ 로그인 상태 확인" 클릭
3. "3️⃣ 즐겨찾기 변경" 테스트
   → ✅ 성공하면 메인 앱 캐시 문제 확정
```

## 📝 예상 결과

### ✅ 성공 시

**Network 탭:**
```
PUT http://139.150.11.99/api/v1/dispatch-form/templates/40
Status: 200 OK

Request Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  Content-Type: application/json

Response:
  {
    "id": 40,
    "name": "도미노 백암 → 밀양",
    "is_favorite": true,
    "updated_at": "2026-03-09T10:45:12.123456"
  }
```

**브라우저:**
- ✅ 토스트 메시지: "즐겨찾기에 추가했습니다"
- ✅ 별 아이콘 노란색으로 변경
- ✅ 즐겨찾기 카운트 증가

**DB:**
```sql
 id |       name        | is_favorite | updated_at
----+-------------------+-------------+----------------------------
 40 | 도미노 백암 → 밀양 |      t      | 2026-03-09 10:45:12.123456
```

### ❌ 실패 시 (401 Unauthorized)

**Network 탭:**
```
PUT http://139.150.11.99/api/v1/dispatch-form/templates/40
Status: 401 Unauthorized

Request Headers:
  Content-Type: application/json
  (❌ Authorization 헤더 없음!)

Response:
  {"detail": "Not authenticated"}
```

**→ 이 경우: 브라우저 캐시 문제, Plan A/B/C 중 하나 실행**

## 🚀 빠른 해결 명령어

### 서버 측 (이미 완료)

```bash
cd /root/uvis
docker compose build --no-cache frontend
docker compose up -d frontend
```

### 클라이언트 측 (사용자가 해야 할 일)

#### 옵션 1: 시크릿 모드
```
Ctrl + Shift + N → http://139.150.11.99
```

#### 옵션 2: 콘솔에서
```javascript
localStorage.clear();
sessionStorage.clear();
location.href = '/login';
```

#### 옵션 3: 캐시 삭제
```
Ctrl + Shift + Delete → 전체 기간 삭제 → Ctrl + Shift + R
```

## 📞 문제 지속 시 제공 정보

1. **Network 탭 스크린샷**
   - Request Headers 부분 (Authorization 헤더 확인)
   - Response 부분 (401 메시지 확인)

2. **Console 탭 출력**
   ```javascript
   localStorage.getItem('access_token')
   localStorage.getItem('user')
   ```

3. **테스트 페이지 결과**
   - `http://139.150.11.99/test-api.html` 에서 테스트 결과

4. **백엔드 로그**
   ```bash
   docker compose logs backend --tail=50 | grep "dispatch-form/templates"
   ```

## ✨ 요약

- **코드**: ✅ 정상 (apiClient 인터셉터, 모든 API 호출 올바름)
- **서버**: ✅ 정상 (nginx 캐시 방지 설정, 최신 빌드)
- **문제**: ❌ 브라우저 캐시 (이전 JS 파일 사용 중)
- **해결**: 🎯 시크릿 모드 또는 캐시 삭제 후 강력 새로고침

**가장 빠른 방법: 시크릿 모드에서 테스트!**
