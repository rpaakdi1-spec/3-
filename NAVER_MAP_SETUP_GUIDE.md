# 🗺️ 네이버 지도 API 설정 가이드

**Client ID**: `oimsa0yj4k`  
**현재 URL**: `http://139.150.11.99`  
**에러**: Authentication Failed (200)

---

## 🔍 문제 원인

네이버 클라우드 플랫폼에서 해당 서비스 URL(`http://139.150.11.99`)이 등록되지 않아 인증 실패

---

## ✅ 해결 방법

### 1단계: 네이버 클라우드 플랫폼 접속

1. **웹사이트**: https://www.ncloud.com/
2. **로그인**: 네이버 계정으로 로그인
3. **Console 이동**: 우측 상단 "Console" 버튼 클릭

### 2단계: AI·NAVER API 서비스 이동

1. **Services** 메뉴 클릭
2. **AI·NAVER API** 선택
3. **Maps** 클릭

### 3단계: Application 찾기

1. **Application 목록**에서 Client ID가 `oimsa0yj4k`인 애플리케이션 찾기
2. 해당 Application 이름 클릭하여 상세 페이지 이동

### 4단계: Web 서비스 URL 등록

**"Web 서비스 URL" 섹션**에서 다음 URL들을 추가:

```
http://139.150.11.99
http://139.150.11.99/vehicles
http://localhost:5173
```

**또는 와일드카드 사용**:
```
http://139.150.11.99*
http://localhost:5173*
```

> 💡 **팁**: 와일드카드(`*`)를 사용하면 모든 하위 경로가 자동으로 허용됩니다.

### 5단계: 저장 및 대기

1. **저장** 버튼 클릭
2. 약 **5-10분** 대기 (DNS 전파 시간)
3. 브라우저 캐시 클리어

---

## 🚀 배포 (설정 적용)

### 서버에서 실행:

```bash
cd /root/uvis
git pull origin main

# Frontend 재빌드 (환경변수 적용)
docker-compose stop frontend
docker-compose rm -f frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

## 🧪 테스트 방법

### 1. 브라우저 캐시 클리어
```javascript
// F12 → Console
localStorage.clear();
sessionStorage.clear();
location.reload();
```

### 2. 차량 관리 페이지 접속
```
http://139.150.11.99/vehicles
```

### 3. 지도 탭 클릭

**정상 동작 시**:
- ✅ 지도가 로드됨
- ✅ 차량 마커가 표시됨
- ✅ Console에 에러 없음

**여전히 에러 시**:
- ⏳ 5-10분 더 대기 (DNS 전파)
- 🔄 브라우저 캐시 강제 새로고침: `Ctrl+Shift+R`
- 🕵️ 시크릿 모드에서 테스트

---

## 📋 등록된 환경변수

### `.env.production`
```env
VITE_NAVER_MAP_CLIENT_ID=oimsa0yj4k
```

### `.env`
```env
VITE_NAVER_MAP_CLIENT_ID=oimsa0yj4k
```

### 코드에서 사용
```typescript
// frontend/src/components/map/NaverMap.tsx (line 64-66)
script.src = `https://openapi.map.naver.com/openapi/v3/maps.js?ncpClientId=${
  import.meta.env.VITE_NAVER_MAP_CLIENT_ID || 'oimsa0yj4k'
}`;
```

---

## 🔧 네이버 클라우드 플랫폼 상세 설정

### Application 정보
- **Client ID**: `oimsa0yj4k`
- **API**: Maps (JavaScript API v3)

### 필수 등록 URL
| 용도 | URL |
|------|-----|
| Production | `http://139.150.11.99` |
| Vehicles 페이지 | `http://139.150.11.99/vehicles` |
| Development | `http://localhost:5173` |

### 권장 등록 URL (와일드카드)
```
http://139.150.11.99*
http://localhost:5173*
```

---

## 🐛 문제 해결 (Troubleshooting)

### Q1: 여전히 "Authentication Failed" 에러
```
원인: URL이 아직 등록되지 않았거나 전파 중
해결:
1. 네이버 클라우드에서 URL 등록 재확인
2. 5-10분 더 대기
3. 브라우저 캐시 완전 삭제
4. 시크릿 모드에서 테스트
```

### Q2: "Service Workers are not supported" 경고
```
원인: PWA 기능이 HTTPS가 아닌 HTTP에서 작동하지 않음
해결: 이 경고는 무시해도 됩니다 (지도 작동에 영향 없음)
      또는 HTTPS 설정 (SSL 인증서 적용)
```

### Q3: 지도가 로드되지 않음 (흰 화면)
```
원인: 스크립트 로딩 실패 또는 네트워크 문제
해결:
1. F12 → Network 탭에서 maps.js 로딩 확인
2. Console 에러 메시지 확인
3. Frontend 재시작:
   docker-compose restart frontend
```

### Q4: 차량 마커가 표시되지 않음
```
원인: 차량 데이터가 없거나 GPS 좌표 문제
해결:
1. Backend API 확인:
   curl http://localhost:8000/api/v1/vehicles
2. 차량에 latitude/longitude 데이터 있는지 확인
3. 테스트 데이터 추가 필요
```

---

## 📊 지도 기능

### 현재 구현된 기능
- ✅ 차량 실시간 위치 표시
- ✅ 차량 상태별 색상 마커 (가용/운행중/오프라인)
- ✅ 클릭 시 차량 정보 표시
- ✅ 자동 줌/중심 조정 (모든 차량이 보이도록)
- ✅ 경로 Polyline 표시
- ✅ 범례 및 통계 표시

### 지원하는 기능
- 🗺️ 지도 확대/축소/이동
- 📍 차량 마커 커스터마이징
- 🛣️ 경로 표시 (Polyline)
- 📊 실시간 차량 현황
- 🔍 InfoWindow (차량 상세 정보)

---

## 🎨 마커 색상 구분

| 상태 | 색상 | 의미 |
|------|------|------|
| available | 🟢 녹색 | 배차 가능 |
| busy | 🟠 주황색 | 운행 중 |
| offline | ⚫ 회색 | 오프라인 |

---

## 📝 Git 변경사항

### 수정된 파일:
- `frontend/.env` - VITE_NAVER_MAP_CLIENT_ID 추가
- `frontend/.env.production` - VITE_NAVER_MAP_CLIENT_ID 추가

### 커밋 메시지:
```
fix: Add Naver Maps API client ID to environment variables
```

---

## 🔒 보안 고려사항

### Client ID 노출
- ✅ **괜찮음**: Client ID는 공개되어도 문제없음
- 🔒 **중요**: URL 등록으로만 접근 제한
- ⚠️ **주의**: Secret Key가 있다면 절대 노출 금지

### URL 제한
- ✅ 등록된 URL에서만 API 사용 가능
- 🔒 다른 도메인에서 접근 불가
- 📌 개발/운영 URL을 모두 등록

---

## 📚 참고 자료

- **네이버 Maps API 문서**: https://navermaps.github.io/maps.js.ncp/
- **네이버 클라우드 가이드**: https://guide.ncloud-docs.com/docs/maps-overview
- **API 사용량 확인**: 네이버 클라우드 Console → AI·NAVER API → Maps → 사용량

---

## 🎯 다음 단계

### 네이버 클라우드에서 URL 등록 후:

1. ✅ URL 등록 확인
2. ⏳ 5-10분 대기
3. 🚀 Frontend 재배포
4. 🧪 테스트 실행
5. ✅ 정상 작동 확인

### 추가 개선 사항:

- [ ] HTTPS 적용 (SSL 인증서)
- [ ] 실시간 차량 위치 업데이트 (WebSocket)
- [ ] 클러스터링 (차량이 많을 때)
- [ ] 경로 최적화 표시
- [ ] 지도 스타일 커스터마이징

---

**생성일**: 2026-02-27  
**최종 수정**: 2026-02-27  
**상태**: ✅ 설정 완료 - 네이버 클라우드 URL 등록 필요
