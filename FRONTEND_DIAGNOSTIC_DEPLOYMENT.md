# 🔍 프론트엔드 진단 로그 배포 완료

## 📋 현재 상황

**문제**: 배차 최적화 후 차량 배정 실패  
**증상**:
```
⚠️ 차량을 찾을 수 없음: undefined
🚛 변환된 차량 배정: 0 건
❌ vehicleAssignments가 비어있음
```

**원인 추정**: 백엔드 API 응답의 `vehicle_id` 필드를 프론트엔드에서 읽지 못함

## ✅ 완료된 작업

### 1. 진단 로그 추가 ✅
**파일**: `frontend/src/pages/OptimizationPage.tsx` (라인 177-185)

**추가된 로그**:
```javascript
console.log('🔍 dispatch 데이터:', dispatch);
console.log('🔍 찾는 vehicle_id:', dispatch.vehicle_id);
console.log('🔍 사용 가능한 vehicles:', vehicles.map(v => ({ id: v.id, code: v.code })));
```

**목적**: 
- API 응답 구조 확인
- vehicle_id 필드명 검증
- 타입 불일치 감지 (string vs number)

### 2. 프론트엔드 빌드 완료 ✅
```bash
✓ 3846 modules transformed
✓ built in 15.91s
```
**빌드 위치**: `/home/user/webapp/frontend/dist/`

### 3. 배포 자료 생성 ✅
| 파일 | 용도 |
|------|------|
| `FRONTEND_DEPLOYMENT_INSTRUCTIONS.md` | 상세 배포 가이드 (3.6 KB) |
| `QUICK_DEPLOY_GUIDE.md` | 빠른 명령어 참고 (1.8 KB) |
| `SERVER_DEPLOYMENT_COMMANDS.sh` | 자동 배포 스크립트 (2.7 KB) |
| `deploy_frontend_fix.sh` | 원격 배포 스크립트 (1.1 KB) |

### 4. Git 커밋 및 푸시 ✅
```bash
✅ 21bbec8 feat(frontend): Add diagnostic logging for vehicle assignment debugging
✅ d4da32b docs: Add comprehensive frontend deployment and diagnostic guide
✅ e3d3285 feat: Add automated deployment script and quick guide
✅ Pushed to origin/main
✅ Pushed to origin/feature/dispatch-diagnostics
```

## 🚀 다음 단계: 서버 배포

### 방법 1: 간단 명령어 (추천)

서버에 SSH 접속 후 다음 명령어를 **순서대로** 실행:

```bash
# 1. 서버 접속
ssh root@139.150.11.99

# 2. 프론트엔드 디렉터리로 이동
cd /root/uvis/frontend

# 3. 최신 코드 가져오기
git fetch origin main
git pull origin main

# 4. 프론트엔드 빌드
npm run build

# 5. 웹서버 재시작 (Docker 사용 시)
docker restart uvis-frontend

# 또는 Nginx 사용 시
nginx -t && systemctl restart nginx
```

**예상 시간**: 약 20-30초

### 방법 2: 자동화 스크립트

```bash
ssh root@139.150.11.99
cd /root/uvis/frontend
bash SERVER_DEPLOYMENT_COMMANDS.sh
```

## 🧪 테스트 절차

### 1️⃣ 브라우저 준비
1. **캐시 삭제 새로고침**:
   - Windows/Linux: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **개발자 도구 열기**:
   - Windows/Linux: `F12`
   - Mac: `Cmd + Option + I`

3. **Console 탭 선택**

### 2️⃣ 배차 최적화 실행
1. 배차 최적화 페이지 이동
2. 주문 선택 (예: 27, 28, 30번)
3. "배차 최적화" 버튼 클릭

### 3️⃣ Console 로그 확인
다음 로그들이 표시됩니다:

```javascript
🔍 dispatch 데이터: { ... }
🔍 찾는 vehicle_id: <값>
🔍 사용 가능한 vehicles: [{ id: ..., code: ... }, ...]
```

### 4️⃣ 스크린샷 캡처
**Console 탭 전체**를 스크린샷으로 캡처해서 공유해주세요!

특히 다음 정보가 중요합니다:
- `dispatch 데이터` 전체 객체
- `vehicle_id` 값 (undefined인지, 숫자인지, 문자열인지)
- `vehicles` 배열의 첫 3-5개 항목

## 🔍 예상 시나리오

### ✅ 시나리오 1: 필드명 불일치
```javascript
🔍 dispatch 데이터: { 
  vehicle: 5,        // ← vehicle_id가 아닌 vehicle
  driver_id: null,
  ...
}
🔍 찾는 vehicle_id: undefined
```
**해결 방법**: 백엔드 스키마 수정 또는 프론트엔드 필드명 변경

### ✅ 시나리오 2: 차량 미포함
```javascript
🔍 dispatch 데이터: { vehicle_id: 5, ... }
🔍 찾는 vehicle_id: 5
🔍 사용 가능한 vehicles: [
  { id: 6, code: "V전남87바4401" },
  { id: 7, code: "V전남87바4156" }
]
```
**해결 방법**: 차량 목록 로딩 로직 확인 (활성 차량 필터 등)

### ✅ 시나리오 3: 타입 불일치
```javascript
🔍 dispatch 데이터: { vehicle_id: "5", ... }  // ← 문자열
🔍 찾는 vehicle_id: "5"
🔍 사용 가능한 vehicles: [
  { id: 5, code: "V전남87바4158" }  // ← 숫자
]
```
**해결 방법**: 타입 변환 (`Number()` 또는 `===` → `==`)

## 📊 추가 진단 정보 (필요시)

### Network 탭 확인
1. F12 → Network 탭
2. 배차 최적화 실행
3. `/api/v1/dispatches/optimize` 요청 찾기
4. Response 탭 → JSON 데이터 확인
5. `dispatches[0].vehicle_id` 값 확인

### Backend 로그 확인
```bash
ssh root@139.150.11.99
docker logs uvis-backend --tail 100 | grep -E "배차|dispatch|vehicle"
```

## 🔧 문제 해결

### 빌드 실패 시
```bash
cd /root/uvis/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### 롤백 필요 시
```bash
cd /root/uvis/frontend
rm -rf dist
mv dist.backup_YYYYMMDD_HHMMSS dist  # 최근 백업 사용
docker restart uvis-frontend  # 또는 systemctl restart nginx
```

## 📁 관련 파일

| 파일 | 경로 | 설명 |
|------|------|------|
| OptimizationPage.tsx | `frontend/src/pages/OptimizationPage.tsx` | 진단 로그 추가된 컴포넌트 |
| dispatch.py | `backend/app/schemas/dispatch.py` | 백엔드 스키마 정의 |
| cvrptw_service.py | `backend/app/services/cvrptw_service.py:705` | 배차 생성 로직 |
| 배포 가이드 | `FRONTEND_DEPLOYMENT_INSTRUCTIONS.md` | 상세 배포 절차 |
| 간단 가이드 | `QUICK_DEPLOY_GUIDE.md` | 빠른 참조 |
| 배포 스크립트 | `SERVER_DEPLOYMENT_COMMANDS.sh` | 자동화 스크립트 |

## 🎯 성공 기준

✅ Console에 진단 로그 3줄 출력됨  
✅ `vehicle_id` 값이 명확하게 확인됨 (undefined, 숫자, 또는 문자열)  
✅ `vehicles` 배열에 차량 목록이 표시됨  
✅ 문제 원인 파악 → 수정 방향 결정

## 📞 지원 정보

**서버**: root@139.150.11.99  
**프론트엔드 경로**: /root/uvis/frontend  
**컨테이너**: uvis-frontend (Docker) 또는 Nginx  
**백엔드 API**: http://localhost:8000/api/v1/dispatches/optimize

## 📝 다음 작업 (진단 후)

1. **원인 파악**: Console 로그 분석
2. **수정 방향 결정**: 백엔드 vs 프론트엔드
3. **코드 수정**: 필드명 또는 타입 변환
4. **재테스트**: 차량 배정 정상 생성 확인
5. **PR 업데이트**: 수정 사항 반영

---

**작성일**: 2026-02-19 12:30 KST  
**작성자**: Claude AI Assistant  
**상태**: 🟢 배포 준비 완료 - 서버 실행 대기 중

