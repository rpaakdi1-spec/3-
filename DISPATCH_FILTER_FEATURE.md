# 배차 관리 필터링 기능

## 📋 개요

배차 관리 페이지에 다양한 필터링 기능을 추가하여 사용자가 원하는 배차를 쉽게 찾을 수 있도록 개선했습니다.

## ✨ 추가된 기능

### 1. 🔍 통합 검색
- **검색 대상**: 배차번호, 차량번호, 운전자명
- **동작**: 실시간 검색 (입력하는 즉시 필터링)
- **대소문자**: 구분 없이 검색
- **예시**: "DISP", "전남87", "김운전" 등

### 2. 📊 상태 필터
- **옵션**:
  - 전체 (기본값)
  - 임시저장 (DRAFT)
  - 확정 (CONFIRMED)
  - 진행중 (IN_PROGRESS)
  - 완료 (COMPLETED)
  - 취소 (CANCELLED)

### 3. 🚛 차량 필터
- **자동 생성**: 현재 배차 목록에 있는 차량만 표시
- **정렬**: 차량번호순으로 자동 정렬
- **동작**: 선택한 차량의 배차만 표시

### 4. 📅 날짜 필터
- **형식**: YYYY-MM-DD (예: 2026-02-19)
- **동작**: 선택한 날짜의 배차만 표시
- **UI**: 캘린더 아이콘과 함께 날짜 선택기

### 5. 📈 결과 카운트
- **표시**: "총 X건 중 Y건 표시"
- **동작**: 필터 적용 시 실시간 업데이트
- **위치**: 필터 영역 바로 아래

## 🎯 사용 방법

### 단일 필터 사용
```
1. 검색창에 "DISP-2026" 입력
   → 해당 배차번호를 포함한 배차만 표시

2. 상태 드롭다운에서 "진행중" 선택
   → 진행 중인 배차만 표시

3. 차량 드롭다운에서 "V전남87바1336" 선택
   → 해당 차량의 배차만 표시

4. 날짜 선택기에서 "2026-02-19" 선택
   → 해당 날짜의 배차만 표시
```

### 복합 필터 사용
```
1. 상태: "진행중" 선택
2. 날짜: "2026-02-19" 선택
3. 검색: "V전남87" 입력
   → 2026-02-19의 진행 중인 전남87 차량 배차만 표시
```

### 필터 초기화
```
- 검색창: 텍스트 삭제 또는 X 버튼 클릭
- 상태: "전체" 선택
- 차량: "전체 차량" 선택
- 날짜: 날짜 선택 해제 또는 빈칸으로 변경
```

## 💻 기술 구현

### 프론트엔드 (React + TypeScript)

#### 상태 관리
```typescript
const [searchText, setSearchText] = useState<string>('');
const [filterStatus, setFilterStatus] = useState<string>('전체');
const [filterVehicle, setFilterVehicle] = useState<string>('전체');
const [filterDate, setFilterDate] = useState<string>('');
```

#### 필터링 로직
```typescript
const filteredDispatches = dispatches.filter((dispatch) => {
  // 검색 필터
  if (searchText) {
    const search = searchText.toLowerCase();
    const matchesSearch = 
      dispatch.dispatch_number?.toLowerCase().includes(search) ||
      dispatch.vehicle_plate?.toLowerCase().includes(search) ||
      dispatch.driver_name?.toLowerCase().includes(search);
    if (!matchesSearch) return false;
  }

  // 상태 필터
  if (filterStatus !== '전체' && dispatch.status !== filterStatus) {
    return false;
  }

  // 차량 필터
  if (filterVehicle !== '전체' && dispatch.vehicle_plate !== filterVehicle) {
    return false;
  }

  // 날짜 필터
  if (filterDate && dispatch.dispatch_date !== filterDate) {
    return false;
  }

  return true;
});
```

#### UI 컴포넌트
```tsx
{/* 검색 필터 */}
<div className="relative">
  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
  <input
    type="text"
    value={searchText}
    onChange={(e) => setSearchText(e.target.value)}
    placeholder="배차번호, 차량, 운전자 검색..."
    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg"
  />
</div>

{/* 상태 필터 */}
<select
  value={filterStatus}
  onChange={(e) => setFilterStatus(e.target.value)}
  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg"
>
  <option value="전체">전체 상태</option>
  <option value="DRAFT">임시저장</option>
  <option value="CONFIRMED">확정</option>
  <option value="IN_PROGRESS">진행중</option>
  <option value="COMPLETED">완료</option>
  <option value="CANCELLED">취소</option>
</select>

{/* 차량 필터 */}
<select
  value={filterVehicle}
  onChange={(e) => setFilterVehicle(e.target.value)}
  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg"
>
  <option value="전체">전체 차량</option>
  {Array.from(vehicles).sort().map((vehicle) => (
    <option key={vehicle} value={vehicle}>{vehicle}</option>
  ))}
</select>

{/* 날짜 필터 */}
<div className="relative">
  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
  <input
    type="date"
    value={filterDate}
    onChange={(e) => setFilterDate(e.target.value)}
    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg"
  />
</div>
```

## 🚀 배포 방법

### 자동 배포 (권장)
```bash
# 서버에 SSH 접속
ssh root@139.150.11.99

# 배포 스크립트 실행
bash /root/uvis/backend/deploy_dispatch_filter.sh
```

### 수동 배포
```bash
# 1. 프론트엔드 디렉토리로 이동
cd /root/uvis/frontend

# 2. 최신 코드 가져오기
git fetch origin main
git reset --hard origin/main

# 3. 변경사항 확인
grep -A 5 "searchText" src/pages/DispatchesPage.tsx

# 4. 빌드
npm run build

# 5. 컨테이너에 복사
docker cp dist/. uvis-frontend:/usr/share/nginx/html/

# 6. 캐시 클리어
docker exec uvis-nginx rm -rf /var/cache/nginx/*

# 7. 재시작
docker restart uvis-frontend
docker restart uvis-nginx

# 8. 대기 및 확인
sleep 10
docker logs uvis-frontend --tail 20
```

## ✅ 테스트 방법

### 1. 브라우저 캐시 완전 삭제
```
Chrome/Edge:
1. Ctrl + Shift + Delete
2. "전체 기간" 선택
3. "쿠키 및 기타 사이트 데이터" 체크
4. "캐시된 이미지 및 파일" 체크
5. "데이터 삭제" 클릭
6. Ctrl + Shift + R 로 새로고침
```

### 2. InPrivate/Incognito 모드 (권장)
```
1. Ctrl + Shift + N (Chrome) 또는 Ctrl + Shift + P (Edge)
2. http://139.150.11.99 접속
3. 로그인
4. 배차 관리 페이지로 이동
```

### 3. 기능 테스트

#### 검색 필터 테스트
```
1. 검색창에 "DISP" 입력
   → 배차번호에 DISP가 포함된 배차만 표시

2. 검색창에 "전남87" 입력
   → 차량번호에 전남87이 포함된 배차만 표시

3. 검색창 비우기
   → 모든 배차 다시 표시
```

#### 상태 필터 테스트
```
1. 상태 드롭다운에서 "진행중" 선택
   → 진행 중인 배차만 표시

2. "완료" 선택
   → 완료된 배차만 표시

3. "전체" 선택
   → 모든 배차 다시 표시
```

#### 차량 필터 테스트
```
1. 차량 드롭다운에서 특정 차량 선택
   → 해당 차량의 배차만 표시

2. "전체 차량" 선택
   → 모든 배차 다시 표시
```

#### 날짜 필터 테스트
```
1. 날짜 선택기에서 오늘 날짜 선택
   → 오늘 날짜의 배차만 표시

2. 다른 날짜 선택
   → 해당 날짜의 배차만 표시

3. 날짜 비우기
   → 모든 배차 다시 표시
```

#### 복합 필터 테스트
```
1. 상태: "진행중"
2. 날짜: 오늘
3. 검색: 특정 차량번호
   → 오늘 진행 중인 특정 차량의 배차만 표시
```

### 4. 성능 테스트
```
1. 100개 이상의 배차가 있을 때
2. 각 필터를 빠르게 변경
3. 검색창에 빠르게 입력
   → 지연 없이 부드럽게 동작해야 함
```

## 🐛 트러블슈팅

### 문제 1: 필터가 동작하지 않음
**원인**: 브라우저 캐시에 오래된 파일이 남아있음

**해결**:
```bash
# 1. 브라우저 캐시 완전 삭제
Ctrl + Shift + Delete → 전체 기간 → 삭제

# 2. InPrivate 모드 테스트
Ctrl + Shift + N

# 3. 서버 캐시 확인
ssh root@139.150.11.99
docker exec uvis-nginx rm -rf /var/cache/nginx/*
docker restart uvis-nginx
```

### 문제 2: 검색 시 아무것도 표시되지 않음
**원인**: 대소문자 또는 공백 문제

**해결**:
```typescript
// 이미 구현되어 있음: toLowerCase()로 대소문자 무시
const search = searchText.toLowerCase();
const matchesSearch = 
  dispatch.dispatch_number?.toLowerCase().includes(search) ||
  dispatch.vehicle_plate?.toLowerCase().includes(search) ||
  dispatch.driver_name?.toLowerCase().includes(search);
```

### 문제 3: 드롭다운에 차량이 표시되지 않음
**원인**: 배차 데이터에 vehicle_plate가 없음

**해결**:
```bash
# 백엔드 API 확인
curl http://localhost:8000/api/v1/dispatches | jq '.[] | {id, vehicle_plate}'

# vehicle_plate 필드가 없으면 백엔드 수정 필요
```

### 문제 4: 필터링 후 카운트가 잘못됨
**원인**: 필터링 로직 순서 문제

**해결**:
```typescript
// 이미 구현되어 있음: 정확한 카운트
<p className="text-sm text-gray-600">
  총 {dispatches.length}건 중 {filteredDispatches.length}건 표시
</p>
```

## 📊 성능 최적화

### 1. useMemo 적용
```typescript
// 차량 목록 메모이제이션
const vehicles = useMemo(() => {
  return new Set(dispatches.map(d => d.vehicle_plate).filter(Boolean));
}, [dispatches]);

// 필터링된 배차 메모이제이션
const filteredDispatches = useMemo(() => {
  return dispatches.filter((dispatch) => {
    // 필터 로직
  });
}, [dispatches, searchText, filterStatus, filterVehicle, filterDate]);
```

### 2. 디바운싱 (선택적)
```typescript
// 검색 입력에 디바운스 적용
import { useMemo, useState, useCallback } from 'react';
import debounce from 'lodash/debounce';

const debouncedSearch = useCallback(
  debounce((value: string) => setSearchText(value), 300),
  []
);
```

## 📈 향후 개선 사항

### 1. 고급 필터
- [ ] 거리 범위 필터 (0-50km, 50-100km 등)
- [ ] 주문 수 범위 필터
- [ ] 긴급 배차 필터
- [ ] 예약 배차 필터

### 2. 저장된 필터
- [ ] 사용자가 자주 사용하는 필터 조합 저장
- [ ] 빠른 필터 버튼 (오늘, 진행중, 내 차량 등)

### 3. 정렬 기능
- [ ] 날짜순, 차량순, 상태순 정렬
- [ ] 오름차순/내림차순 전환

### 4. 엑스포트 기능
- [ ] 필터링된 결과를 Excel/CSV로 다운로드
- [ ] PDF 보고서 생성

## 🔗 관련 파일

- `frontend/src/pages/DispatchesPage.tsx`: 필터링 기능 구현
- `deploy_dispatch_filter.sh`: 자동 배포 스크립트
- `DISPATCH_FILTER_FEATURE.md`: 이 문서

## 📝 변경 이력

| 날짜 | 버전 | 변경 내용 | 커밋 |
|------|------|-----------|------|
| 2026-02-19 | 1.0.0 | 초기 필터링 기능 추가 | 3cfdfb6 |
| 2026-02-19 | 1.0.1 | 배포 스크립트 추가 | ceecaaa |

## 👥 문의

문제가 발생하거나 개선 사항이 있으면 개발팀에 문의해주세요.

---
**최종 업데이트**: 2026-02-19  
**작성자**: AI Assistant  
**문서 버전**: 1.0
