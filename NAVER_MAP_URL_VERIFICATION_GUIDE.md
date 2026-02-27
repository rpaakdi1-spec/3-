# 네이버 지도 API URL 등록 확인 가이드

## 📋 현재 상태

### ✅ 확인 완료 사항
- **Client ID**: `oimsa0yj4k`
- **API 스크립트**: 정상 다운로드 (HTTP 200)
- **환경 변수**: `.env` 및 `.env.production`에 설정 완료

### 🔍 확인 결과
```bash
✅ API 스크립트 다운로드 성공 (HTTP 200)
✅ Client ID가 유효함
⚠️  브라우저 테스트로 URL 등록 여부 최종 확인 필요
```

---

## 🌐 브라우저 테스트 방법

### Step 1: 테스트 파일 배포

서버(`/root/uvis`)에서 실행:

```bash
cd /root/uvis
git pull origin main

# 방법 1: frontend public 디렉토리에 복사
cp test_naver_map.html frontend/public/

# 방법 2: Docker 컨테이너에 직접 복사
docker cp test_naver_map.html uvis-frontend:/usr/share/nginx/html/

# 방법 3: 프론트엔드 재빌드 (권장)
docker-compose down frontend
docker-compose up -d --build frontend
```

### Step 2: 브라우저에서 테스트

1. 브라우저에서 다음 URL 열기:
   ```
   http://139.150.11.99/test_naver_map.html
   ```

2. 페이지 로딩 확인

### Step 3: 결과 해석

#### ✅ **URL 등록됨** (성공)
- 화면에 지도가 정상적으로 표시됨
- 초록색 메시지: "✅ 네이버 지도 API 정상 작동"
- 서울 지역 지도 표시

**조치**: 아무것도 할 필요 없음. 정상 운영 중.

---

#### ❌ **URL 미등록** (실패)
- 화면에 지도가 표시되지 않음
- 빨간색 메시지: "❌ 네이버 지도 API 로드 실패"
- 에러 메시지: "Client ID가 유효하지 않거나 URL이 등록되지 않았습니다"

**조치**: 아래 "Naver Cloud Console 설정" 섹션 참조

---

## ⚙️ Naver Cloud Console 설정

### URL이 등록되지 않은 경우:

#### 1. 로그인
- https://www.ncloud.com/ 접속
- 네이버 클라우드 계정으로 로그인

#### 2. Maps API 서비스 이동
1. 상단 **Console** 클릭
2. 좌측 메뉴에서 **Services** 선택
3. **AI·NAVER API** → **Maps** 선택

#### 3. Application 선택
- Client ID: **oimsa0yj4k** 인 애플리케이션 찾기
- 해당 애플리케이션 클릭

#### 4. Web Service URL 추가
**Web Service URL** 섹션에 다음 URL들을 **모두** 추가:

```
http://139.150.11.99
http://139.150.11.99/vehicles
http://139.150.11.99/*
```

**추가 방법**:
- 입력 필드에 URL 입력
- 엔터 또는 "추가" 버튼 클릭
- 각 URL마다 반복

#### 5. 저장
- **저장** 또는 **확인** 버튼 클릭
- ⏱️ **5-10분 대기** (DNS 전파 시간)

#### 6. 테스트
```bash
# 브라우저 캐시 삭제
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)

# 또는 시크릿 모드로 테스트
Ctrl + Shift + N (Chrome)
```

- http://139.150.11.99/test_naver_map.html 재확인
- 지도가 보이면 성공 ✅

---

## 🔧 CLI에서 확인

### 방법 1: 스크립트 실행
```bash
cd /home/user/webapp
bash CHECK_NAVER_MAP_REGISTRATION.sh
```

### 방법 2: 수동 확인
```bash
# API 스크립트 다운로드 확인
curl -s "https://oapi.map.naver.com/openapi/v3/maps.js?ncpClientId=oimsa0yj4k" | head -20

# HTTP 상태 코드 확인
curl -I -s "https://oapi.map.naver.com/openapi/v3/maps.js?ncpClientId=oimsa0yj4k" | grep HTTP
```

**예상 결과**:
```
HTTP/2 200
```

---

## 📝 등록해야 할 URL 전체 목록

| URL | 목적 |
|-----|------|
| `http://139.150.11.99` | 메인 도메인 |
| `http://139.150.11.99/vehicles` | 차량 관리 페이지 |
| `http://139.150.11.99/*` | 와일드카드 (모든 하위 경로) |
| `http://localhost` | 로컬 개발용 (선택) |
| `http://127.0.0.1` | 로컬 개발용 (선택) |

---

## 🐛 문제 해결

### 문제 1: 지도가 안 보임
**증상**: 빈 화면 또는 에러 메시지

**해결**:
1. Naver Cloud Console에서 URL 등록 재확인
2. 5-10분 대기 (DNS 전파)
3. 브라우저 캐시 완전 삭제:
   ```javascript
   // 브라우저 콘솔에서 실행
   localStorage.clear();
   sessionStorage.clear();
   location.reload();
   ```
4. 시크릿 모드로 재테스트

### 문제 2: Console 에러 메시지
**증상**: F12 개발자 도구에서 에러 표시

**확인**:
```javascript
// 브라우저 콘솔에서 확인
console.log(typeof naver);  // "undefined"면 API 로드 실패
console.log(typeof naver.maps);  // "undefined"면 API 로드 실패
```

**해결**:
- Client ID 재확인
- URL 등록 상태 재확인
- 네트워크 탭에서 script 로딩 확인

### 문제 3: Error Code 표시
**증상**: "Error Code: 200" 등의 메시지

**의미**:
- Error Code 200: URL 미등록
- Error Code 400: 잘못된 Client ID
- Error Code 500: 서버 오류

**해결**:
- Error Code 200 → Naver Cloud에서 URL 추가
- Error Code 400 → Client ID 재확인
- Error Code 500 → 잠시 후 재시도

---

## 📊 시스템에서 네이버 지도를 사용하는 페이지

| 페이지 | URL | 지도 기능 |
|--------|-----|-----------|
| 차량 관리 | `/vehicles` | 차량 위치 표시 |
| 실시간 모니터링 | `/monitoring` | 실시간 차량 추적 |
| 배차 최적화 | `/dispatch-optimization` | 경로 시각화 |

---

## ✅ 확인 체크리스트

### 배포 전
- [ ] `.env.production`에 `VITE_NAVER_MAP_CLIENT_ID=oimsa0yj4k` 설정
- [ ] Client ID 유효성 확인
- [ ] Naver Cloud Console 접근 권한 확인

### Naver Cloud Console
- [ ] https://www.ncloud.com/ 로그인
- [ ] Maps API 서비스 접근
- [ ] Application (oimsa0yj4k) 선택
- [ ] Web Service URL 추가:
  - [ ] `http://139.150.11.99`
  - [ ] `http://139.150.11.99/vehicles`
  - [ ] `http://139.150.11.99/*`
- [ ] 저장 완료
- [ ] 5-10분 대기

### 테스트
- [ ] `test_naver_map.html` 서버 배포
- [ ] 브라우저에서 테스트 페이지 열기
- [ ] 지도 정상 표시 확인
- [ ] `/vehicles` 페이지에서 지도 확인
- [ ] 브라우저 캐시 삭제 후 재확인

---

## 🎯 다음 단계

URL 등록 완료 후:

1. **시스템 전체 테스트**
   ```bash
   # 서버에서 실행
   cd /root/uvis
   docker-compose ps  # 모든 컨테이너 실행 확인
   docker-compose logs frontend --tail=50  # 로그 확인
   ```

2. **차량 관리 페이지 테스트**
   - http://139.150.11.99/vehicles 접속
   - 로그인: admin / admin123
   - 지도에 차량 마커 표시 확인

3. **실제 데이터 입력**
   - 고객 데이터 입력
   - 차량 GPS 데이터 입력
   - 실시간 위치 추적 테스트

---

## 📞 참고 링크

- **Naver Cloud Platform**: https://www.ncloud.com/
- **Naver Maps API 문서**: https://navermaps.github.io/maps.js.ncp/docs/
- **문의하기**: https://www.ncloud.com/support/question

---

## 📄 관련 문서

- `CURRENT_SYSTEM_STATUS.md` - 전체 시스템 현황
- `NAVER_MAP_SETUP_GUIDE.md` - 네이버 지도 초기 설정
- `QUICK_REFERENCE.md` - 빠른 참조 가이드
- `DEPLOY_NAVER_MAP.sh` - 자동 배포 스크립트

---

**작성일**: 2026-02-27  
**Client ID**: oimsa0yj4k  
**Status**: URL 등록 확인 필요 ⚠️
