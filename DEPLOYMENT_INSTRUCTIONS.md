# 차량-운전자 배정 관리 배포 가이드

**배포일**: 2026-02-27  
**커밋**: dab42fd  
**대상**: 프로덕션 서버 (139.150.11.99)

---

## 🚀 빠른 배포

### 1단계: 서버 접속
```bash
ssh root@139.150.11.99
```

### 2단계: 코드 업데이트
```bash
cd /root/uvis
git pull origin main
```

### 3단계: Frontend 재배포
```bash
# Frontend 컨테이너 재시작 (빌드 포함)
docker-compose down frontend
docker-compose up -d --build frontend

# 또는 전체 재시작
docker-compose restart
```

### 4단계: 배포 확인
```bash
# 컨테이너 상태
docker-compose ps

# Frontend 로그 확인
docker-compose logs -f frontend
```

### 5단계: 웹 접속 테스트
- URL: http://139.150.11.99/vehicle-driver-management
- 로그인: admin / admin123

---

## ✅ 배포 후 테스트

### 필수 테스트 항목

#### 1. 페이지 로드
```
✓ 페이지가 정상적으로 로드되는가?
✓ 운전자 풀이 좌측에 표시되는가?
✓ 차량 목록이 우측에 표시되는가?
```

#### 2. 드래그앤드롭 (핵심 수정 사항!)
```
✓ 운전자를 차량에 드래그하면 배정되는가?
✓ 차량 A의 운전자를 차량 B로 드래그하면 MOVE(이동)되는가?
  ❌ 이전: 복사됨 (버그)
  ✅ 현재: 이동됨 (수정됨)
✓ 차량의 운전자를 운전자 풀로 드래그하면 해제되는가?
```

#### 3. 필터 기능 (신규 추가!)
```
✓ 상태 필터가 작동하는가? (운행가능, 운행중, 정비중, 운행불가)
✓ 차량유형 필터가 작동하는가? (냉동, 냉장, 겸용, 상온)
✓ 면허 필터가 작동하는가? (1종 대형, 1종 보통, 2종)
✓ 검색창이 작동하는가? (차량번호, 운전자명, 차량유형)
✓ 필터 초기화 버튼이 나타나고 작동하는가?
```

#### 4. UI/UX
```
✓ 드래그 시 반투명 효과
✓ 드롭 영역 하이라이트
✓ Toast 메시지 표시
✓ 모바일 반응형
```

---

## 🔍 문제 해결

### 문제 1: 페이지가 로드되지 않음
```bash
# Frontend 로그 확인
docker-compose logs frontend

# Frontend 재빌드
docker-compose up -d --build frontend
```

### 문제 2: 드래그앤드롭이 작동하지 않음
```bash
# 브라우저 콘솔 확인 (F12)
# react-dnd 라이브러리 로드 확인

# 캐시 클리어
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

### 문제 3: API 요청 실패
```bash
# Backend 로그 확인
docker-compose logs backend

# Backend 재시작
docker-compose restart backend
```

### 문제 4: 여전히 복사되는 현상
```bash
# 코드 버전 확인
cd /root/uvis
git log --oneline -5

# 최신 커밋이 79ec1b9 또는 dab42fd인지 확인
# 아니면 다시 pull
git pull origin main
docker-compose up -d --build frontend
```

---

## 📊 변경 사항 요약

### 수정된 버그
1. **운전자 복사 문제** → ✅ 이동으로 수정
   - 이전: 차량 A → 차량 B로 드래그 시 복사됨
   - 현재: 정확하게 이동됨 (차량 A에서 자동 해제)

### 추가된 기능
1. **상태 필터**: 차량 상태별 필터링
2. **차량유형 필터**: 냉동/냉장/겸용/상온 필터링
3. **면허 필터**: 운전자 면허별 필터링
4. **필터 초기화**: 원클릭 초기화 버튼
5. **확장된 검색**: 차량유형 포함 검색

---

## 🎯 핵심 기술 변경

### Before (버그)
```typescript
// VehicleCard의 onDrop
drop: (item) => {
  if (item.vehicleId !== vehicle.id) {
    onDropDriver(vehicle.id, item.driver);  // ❌ sourceVehicleId 없음
  }
}
```

### After (수정)
```typescript
// VehicleCard의 onDrop
drop: (item) => {
  if (item.vehicleId !== vehicle.id) {
    onDropDriver(vehicle.id, item.driver, item.vehicleId);  // ✅ sourceVehicleId 전달
  }
}

// handleDropDriver에서 처리
if (sourceVehicleId) {
  // 1. 이전 차량에서 제거
  await vehiclesAPI.update(sourceVehicleId, { driver_name: null, driver_phone: null });
}
// 2. 새 차량에 배정
await vehiclesAPI.update(vehicleId, { driver_name: driver.name, driver_phone: driver.phone });
```

---

## 📱 사용자 가이드

### 신규 배정
1. 좌측 "운전자 풀"에서 운전자 카드를 선택
2. 우측 차량의 배정 영역으로 드래그
3. 드롭하면 배정 완료
4. "OOO님이 차량에 배정되었습니다" 메시지 확인

### 운전자 이동 (🆕 수정됨!)
1. 차량 A의 운전자 카드를 선택
2. 차량 B의 배정 영역으로 드래그
3. 드롭하면 자동으로:
   - 차량 A에서 해제
   - 차량 B에 배정
4. "OOO님이 다른 차량으로 이동되었습니다" 메시지 확인

### 배정 해제
1. 차량의 운전자 카드를 선택
2. 좌측 "운전자 풀"로 드래그
3. 드롭하면 배정 해제
4. "OOO님의 배정이 해제되었습니다" 메시지 확인

### 필터 사용 (🆕 신규!)
1. **빠른 찾기**: 검색창에 차량번호, 운전자명, 차량유형 입력
2. **상태로 찾기**: 상태 드롭다운에서 선택
3. **유형으로 찾기**: 차량유형 드롭다운에서 선택
4. **면허로 찾기**: 운전자 면허 드롭다운에서 선택
5. **초기화**: "필터 초기화" 버튼 클릭

---

## 🔐 보안 체크리스트

```
✓ 인증 확인 (로그인 필요)
✓ 권한 확인 (관리자만 접근)
✓ API 인증 토큰
✓ CORS 설정
```

---

## 📈 성능 모니터링

### 배포 후 확인 사항
```bash
# CPU 사용률
docker stats

# 메모리 사용량
docker-compose ps

# 로그 확인
docker-compose logs -f frontend backend
```

---

## 🎉 완료 체크리스트

배포 완료 후 다음 항목을 확인하세요:

- [ ] Git pull 완료
- [ ] Frontend 컨테이너 재빌드 완료
- [ ] 페이지 정상 로드 확인
- [ ] 운전자 → 차량 드래그 테스트 (신규 배정)
- [ ] 차량 → 차량 드래그 테스트 (이동, 복사 아님!)
- [ ] 차량 → 운전자 풀 드래그 테스트 (배정 해제)
- [ ] 상태 필터 테스트
- [ ] 차량유형 필터 테스트
- [ ] 면허 필터 테스트
- [ ] 검색 기능 테스트
- [ ] 필터 초기화 버튼 테스트
- [ ] Toast 메시지 표시 확인
- [ ] 모바일 반응형 확인

---

## 📞 지원

문제 발생 시:
1. 로그 확인: `docker-compose logs -f frontend backend`
2. 브라우저 콘솔 확인 (F12)
3. 커밋 해시 확인: `git log --oneline -1`

**예상 커밋**: `79ec1b9` (버그 수정) 또는 `dab42fd` (문서 추가)

---

**배포 준비 완료!** 🚀
