# 프론트엔드 진단 로그 배포 가이드

## 📋 개요

**문제**: 배차 최적화 후 `⚠️ 차량을 찾을 수 없음: undefined` 오류로 차량 배정 0건 생성

**원인 분석**: 백엔드 API 응답의 `vehicle_id` 필드가 프론트엔드에서 정상적으로 읽히지 않음

**해결 방법**: 진단 로그 추가 → API 응답 구조 확인 → 필드명 또는 타입 불일치 해결

## 🚀 배포 단계

### 1️⃣ 서버 접속
```bash
ssh root@139.150.11.99
```

### 2️⃣ 프론트엔드 디렉터리 이동
```bash
cd /root/uvis/frontend
```

### 3️⃣ 최신 코드 가져오기
```bash
git fetch origin main
git pull origin main
```

### 4️⃣ 프론트엔드 빌드
```bash
npm run build
```
**예상 시간**: 약 15-20초

### 5️⃣ 빌드 결과 확인
```bash
ls -lh dist/
```
**확인 사항**: `dist/index.html` 및 `dist/assets/` 존재

### 6️⃣ Nginx 재시작 (필요시)
```bash
# Nginx 설정 테스트
nginx -t

# Nginx 재시작
systemctl restart nginx

# 또는 Docker를 사용하는 경우
docker restart uvis-frontend
```

## 🧪 테스트 방법

### 1️⃣ 브라우저 캐시 삭제
- Windows/Linux: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

### 2️⃣ 개발자 도구 열기
- Windows/Linux: `F12`
- Mac: `Cmd + Option + I`

### 3️⃣ Console 탭 이동
- Console 탭 클릭
- 로그 필터를 "All" 또는 "Verbose"로 설정

### 4️⃣ 배차 최적화 실행
1. 배차 최적화 페이지 이동
2. 주문 선택 (예: 27, 28, 30번)
3. "배차 최적화" 버튼 클릭

### 5️⃣ Console 로그 확인
다음 로그들을 찾아서 확인:

```
🔍 dispatch 데이터: { ... }
🔍 찾는 vehicle_id: <숫자 또는 undefined>
🔍 사용 가능한 vehicles: [{ id: ..., code: ... }, ...]
```

## 🔍 진단 시나리오

### 시나리오 1: vehicle_id가 undefined
```javascript
🔍 dispatch 데이터: { vehicle: 5, ... }  // vehicle_id가 아닌 vehicle
🔍 찾는 vehicle_id: undefined
```
**해결**: 백엔드 API 응답 필드명 확인 필요 (`vehicle` vs `vehicle_id`)

### 시나리오 2: vehicle_id는 있지만 vehicles 배열에 없음
```javascript
🔍 dispatch 데이터: { vehicle_id: 5, ... }
🔍 찾는 vehicle_id: 5
🔍 사용 가능한 vehicles: [{ id: 6, code: ... }, { id: 7, code: ... }]
```
**해결**: 
- 차량 목록 로딩 로직 확인
- 차량 상태 필터 확인 (active=true 등)

### 시나리오 3: 타입 불일치
```javascript
🔍 dispatch 데이터: { vehicle_id: "5", ... }  // 문자열
🔍 찾는 vehicle_id: "5"
🔍 사용 가능한 vehicles: [{ id: 5, code: ... }]  // 숫자
```
**해결**: 타입 변환 필요 (`parseInt()` 또는 `String()`)

## 📤 진단 결과 보고

다음 정보를 캡처해서 공유:

1. **Console 로그 전체**
   ```
   🔍 dispatch 데이터: ...
   🔍 찾는 vehicle_id: ...
   🔍 사용 가능한 vehicles: ...
   ⚠️ 차량을 찾을 수 없음: ...
   ```

2. **Network 탭에서 API 응답**
   - `/api/v1/dispatches/optimize` 요청
   - Response 탭의 JSON 데이터
   - 특히 `dispatches` 배열의 첫 번째 항목

3. **Backend 로그**
   ```bash
   docker logs uvis-backend --tail 100
   ```

## 🔧 백업 및 롤백

### 배포 전 백업
```bash
cd /root/uvis/frontend
cp -r dist dist.backup_$(date +%Y%m%d_%H%M%S)
```

### 롤백 (문제 발생 시)
```bash
cd /root/uvis/frontend
rm -rf dist
mv dist.backup_YYYYMMDD_HHMMSS dist
systemctl restart nginx  # 또는 docker restart uvis-frontend
```

## 📞 문제 해결

### 빌드 실패
```bash
# Node.js 버전 확인
node --version  # v18 이상 권장

# 의존성 재설치
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Nginx 설정 오류
```bash
# Nginx 설정 파일 확인
cat /etc/nginx/sites-available/default

# Nginx 에러 로그
tail -100 /var/log/nginx/error.log
```

### Docker 컨테이너 문제
```bash
# 컨테이너 상태 확인
docker ps -a | grep uvis-frontend

# 컨테이너 로그 확인
docker logs uvis-frontend --tail 100

# 컨테이너 재시작
docker restart uvis-frontend
```

## 📝 다음 단계

진단 로그를 통해 원인을 파악한 후:

1. **필드명 불일치 해결**
   - 백엔드 스키마 수정 (`vehicle` → `vehicle_id`)
   - 또는 프론트엔드 코드 수정 (`dispatch.vehicle_id` → `dispatch.vehicle`)

2. **타입 불일치 해결**
   - 프론트엔드에서 타입 변환 추가
   - 백엔드 API 응답 타입 통일

3. **차량 목록 필터 수정**
   - 활성 차량만 로딩하도록 확인
   - 배차에 사용된 차량이 목록에 포함되는지 확인

## 📚 관련 파일

- **프론트엔드 소스**: `frontend/src/pages/OptimizationPage.tsx` (라인 177-185)
- **백엔드 스키마**: `backend/app/schemas/dispatch.py`
- **백엔드 서비스**: `backend/app/services/cvrptw_service.py` (라인 705)
- **배포 스크립트**: `deploy_frontend_fix.sh`

## 🎯 성공 기준

✅ Console에 진단 로그가 정상적으로 출력됨  
✅ `vehicle_id` 값이 명확하게 확인됨  
✅ 사용 가능한 vehicles 목록이 표시됨  
✅ 원인 파악 → 수정 방향 결정

---

**작성일**: 2026-02-19  
**작성자**: Claude AI Assistant  
**버전**: 1.0
