# 배차 최적화 진단 기능 개선

**날짜**: 2026-02-19  
**버전**: v1.1.0  
**목적**: 배차 최적화 실패 시 정확한 원인 파악 및 사용자 알림

---

## 🎯 문제 상황

### 현재 증상
- 대시보드에서 `total_orders=1`, `pending_orders=1`이지만 배차 생성 안 됨
- API 호출 시 `success: false, error: "주문을 찾을 수 없습니다"` 또는 `success: true, total_dispatches: 0`
- **실패 원인을 알 수 없음** - 로그에 상세 정보 부족

### 근본 원인
1. **GPS 좌표 누락**: 상차지/하차지 위도·경도 없음
2. **거래처 연결 오류**: `pickup_client_id` 또는 `delivery_client_id`가 유효하지 않음
3. **용량 초과**: 팔레트 또는 중량이 차량 용량을 초과
4. **온도대 불일치**: 주문의 온도대와 호환되는 차량 없음
5. **시간 제약**: 타이트한 time window로 인해 솔루션 불가능

---

## 📦 개선 사항

### 1. 진단 정보 수집 (Diagnostics Collection)

```python
diagnostics = {
    'orders_count': len(orders),
    'vehicles_count': len(vehicles),
    'issues': [],
    'total_pallet_demand': 0,
    'total_weight_demand': 0,
    'total_vehicle_pallet_capacity': 0,
    'total_vehicle_weight_capacity': 0
}
```

**수집 항목**:
- 주문 수 / 차량 수
- 위치 수 (depot + pickup + delivery)
- GPS 좌표 누락 개수
- 팔레트 수요 vs 차량 팔레트 용량
- 중량 수요 vs 차량 중량 용량
- 온도대별 호환 차량 수

### 2. GPS 좌표 검증

```python
missing_coords_count = 0
for loc in locations:
    if loc.location_type != 'depot':
        if loc.latitude == depot_lat and loc.longitude == depot_lon:
            missing_coords_count += 1

if missing_coords_count > 0:
    diagnostics['issues'].append(
        f"⚠️  {missing_coords_count}개 위치에 좌표가 없어 기본 좌표 사용"
    )
```

**기능**:
- 각 주문의 pickup/delivery 위치 검사
- 기본 좌표(서울 시청) 사용 시 경고
- 누락 개수 카운트 및 로깅

### 3. 용량 제약 검증

```python
total_pallet_demand = sum(order.pallet_count for order in orders)
total_weight_demand = sum(order.weight_kg for order in orders)
total_vehicle_pallet_capacity = sum(v.max_pallets for v in vehicle_infos)
total_vehicle_weight_capacity = sum(v.max_weight_kg for v in vehicle_infos)

if total_pallet_demand > total_vehicle_pallet_capacity:
    issue = f"⚠️  팔레트 초과: 주문 {total_pallet_demand}개 > 차량 용량 {total_vehicle_pallet_capacity}개"
    diagnostics['issues'].append(issue)
    logger.warning(issue)
```

**검증 항목**:
- 팔레트 수요 < 차량 팔레트 용량
- 중량 수요 < 차량 중량 용량
- 초과 시 구체적인 수치와 함께 경고

### 4. 온도대 호환성 검증

```python
compatible_types = self._convert_temp_zone_to_vehicle_types(temp_zone)
compatible_vehicles = [v for v in vehicles if v.vehicle_type in compatible_types]

if not compatible_vehicles:
    issue = f"온도대 [{temp_zone.value}]에 호환 차량 없음 " \
            f"(필요: {[t.value for t in compatible_types]}, " \
            f"보유: {[v.vehicle_type.value for v in vehicles]})"
    logger.warning(issue)
    failed_zones.append({
        'temp_zone': temp_zone.value,
        'orders_count': len(zone_orders),
        'reason': issue
    })
```

**매칭 규칙**:
- `냉동(-18℃)` → `냉동` 또는 `듀얼` 차량
- `냉장(0~10℃)` → `냉장` 또는 `듀얼` 차량
- `상온(10~25℃)` → `상온` 또는 `듀얼` 차량

### 5. 상세 실패 로깅

```python
if not solution:
    logger.error("❌ 배차 최적화 실패 - 솔루션을 찾지 못했습니다")
    logger.error(f"📊 진단 정보:")
    logger.error(f"   - 주문 수: {diagnostics['orders_count']}건")
    logger.error(f"   - 차량 수: {diagnostics['vehicles_count']}대")
    logger.error(f"   - 위치 수: {len(locations)}개")
    logger.error(f"   - 팔레트 수요: {diagnostics['total_pallet_demand']}개")
    logger.error(f"   - 팔레트 용량: {diagnostics['total_vehicle_pallet_capacity']}개")
    logger.error(f"   - 중량 수요: {diagnostics['total_weight_demand']:.1f}kg")
    logger.error(f"   - 중량 용량: {diagnostics['total_vehicle_weight_capacity']:.1f}kg")
    
    if diagnostics['issues']:
        logger.error(f"\n🔍 발견된 문제:")
        for issue in diagnostics['issues']:
            logger.error(f"   {issue}")
```

**로그 출력**:
- Docker logs에서 쉽게 확인 가능
- 각 항목별 수치 명시
- 문제 목록 bullet point 형식

### 6. 구조화된 오류 응답

**실패 시 응답 구조**:
```json
{
  "success": false,
  "error": "배차 최적화 실패",
  "reasons": [
    "GPS 좌표 누락 (3개 위치)",
    "팔레트 용량 부족 (수요 50 > 용량 40)",
    "중량 용량 부족 (수요 5000kg > 용량 4500kg)"
  ],
  "diagnostics": {
    "orders_count": 10,
    "vehicles_count": 5,
    "total_pallet_demand": 50,
    "total_vehicle_pallet_capacity": 40,
    "total_weight_demand": 5000.0,
    "total_vehicle_weight_capacity": 4500.0,
    "issues": [...]
  }
}
```

**부분 성공 시 응답 구조**:
```json
{
  "success": true,
  "total_orders": 15,
  "total_dispatches": 8,
  "temperature_zones": [...],
  "dispatches": [...],
  "failed_zones": [
    {
      "temp_zone": "냉동(-18℃)",
      "orders_count": 5,
      "reason": "온도대에 호환 차량 없음",
      "details": ["냉동 차량 필요, 현재 냉장/상온만 보유"]
    }
  ],
  "warnings": [
    "냉동(-18℃): 온도대에 호환 차량 없음"
  ]
}
```

---

## 📂 수정 파일

### `/root/uvis/backend/app/services/cvrptw_service.py`

**함수**: `_optimize_temperature_zone()`

**라인**: 505-687

**주요 변경**:
1. 진단 정보 수집 초기화 (line 516-520)
2. GPS 좌표 검증 추가 (line 632-641)
3. 용량 제약 검증 추가 (line 647-663)
4. 실패 시 상세 로깅 (line 668-706)
5. 구조화된 오류 응답 반환 (line 707-712)

**함수**: `optimize_dispatch_cvrptw()`

**라인**: 448-497

**주요 변경**:
1. `failed_zones` 배열 초기화 (line 449)
2. 온도대별 실패 정보 수집 (line 460-477)
3. 완전 실패 시 오류 응답 (line 493-503)
4. 부분 성공 시 경고 포함 응답 (line 506-525)

---

## 🚀 배포 방법

### 방법 1: 자동 배포 스크립트 (권장)

```bash
# 로컬에서 서버로 복사
scp /home/user/webapp/backend/app/services/cvrptw_service.py root@139.150.11.99:/root/uvis/backend/app/services/

# 서버에서 Docker 재시작
ssh root@139.150.11.99 "cd /root/uvis && docker restart uvis-backend"

# 대기 및 상태 확인
ssh root@139.150.11.99 "sleep 15 && docker ps | grep uvis-backend"
```

### 방법 2: 서버 직접 접속

```bash
ssh root@139.150.11.99

# 백업
cp /root/uvis/backend/app/services/cvrptw_service.py \
   /root/uvis/backend/app/services/cvrptw_service.py.backup_$(date +%Y%m%d_%H%M%S)

# 로컬에서 새 파일 가져오기
# (git pull 또는 scp 이용)

# Docker 재시작
cd /root/uvis
docker restart uvis-backend
sleep 15

# 상태 확인
docker ps
docker logs uvis-backend --tail 50
```

---

## 🧪 테스트 방법

### 1. API 직접 호출

```bash
curl -X POST 'http://139.150.11.99:8000/api/v1/dispatches/optimize' \
  -H 'Content-Type: application/json' \
  -d '{
    "order_ids": [],
    "vehicle_ids": [],
    "dispatch_date": "2026-02-19"
  }' | jq .
```

**기대 결과 (실패 시)**:
```json
{
  "success": false,
  "error": "모든 온도대에서 배차 최적화 실패",
  "total_orders": 10,
  "failed_zones": [
    {
      "temp_zone": "냉장(0~10℃)",
      "orders_count": 10,
      "reason": "솔루션을 찾지 못했습니다",
      "details": [
        "GPS 좌표 누락 (8개 위치)",
        "팔레트 용량 부족 (수요 45 > 용량 40)"
      ],
      "diagnostics": {...}
    }
  ],
  "message": "배차 최적화에 실패했습니다. 다음을 확인하세요:\n- 냉장(0~10℃): GPS 좌표 누락 (8개 위치), 팔레트 용량 부족 (수요 45 > 용량 40)"
}
```

### 2. 로그 실시간 모니터링

```bash
ssh root@139.150.11.99
docker logs -f uvis-backend
```

**API 호출 후 로그 확인**:
```
INFO     | === CVRPTW 배차 최적화 시작 ===
INFO     | 주문: 10건, 시간 제한: 15초
INFO     | 
온도대 [냉장(0~10℃)] 최적화: 10건
INFO     | 위치: 21개 (차고지 1 + 주문 위치 20)
WARNING  | ⚠️  8개 위치에 좌표가 없어 기본 좌표(서울) 사용
INFO     | 차량: 5대
WARNING  | ⚠️  팔레트 초과: 주문 45개 > 차량 용량 40개
INFO     | 📐 Haversine 거리 사용
INFO     | OR-Tools 검색 시작...
ERROR    | ❌ 배차 최적화 실패 - 솔루션을 찾지 못했습니다
ERROR    | 📊 진단 정보:
ERROR    |    - 주문 수: 10건
ERROR    |    - 차량 수: 5대
ERROR    |    - 위치 수: 21개
ERROR    |    - 팔레트 수요: 45개
ERROR    |    - 팔레트 용량: 40개
ERROR    |    - 중량 수요: 4200.0kg
ERROR    |    - 중량 용량: 5000.0kg
ERROR    | 
🔍 발견된 문제:
ERROR    |    ⚠️  8개 위치에 좌표가 없어 기본 좌표 사용
ERROR    |    ⚠️  팔레트 초과: 주문 45개 > 차량 용량 40개
ERROR    | 
💡 실패 추정 원인:
ERROR    |    1. GPS 좌표 누락 (8개 위치)
ERROR    |    2. 팔레트 용량 부족 (수요 45 > 용량 40)
```

### 3. 통합 테스트

```bash
cd /home/user/webapp
python3 test_dispatch_flow.py
```

**기대 출력**:
- 기존: `✅ 기본 배차 최적화: 최적화 완료: 차량 0대 배차, 미배차 0건`
- 개선: API 응답에 `failed_zones`, `warnings` 포함
- 로그에 구체적인 실패 원인 출력

---

## 📋 해결 가이드

### 문제 1: GPS 좌표 누락

**증상**:
```
⚠️  8개 위치에 좌표가 없어 기본 좌표(서울) 사용
```

**해결 방법**:

1. **거래처 GPS 업데이트**:
   ```sql
   -- 거래처 좌표 확인
   SELECT id, name, latitude, longitude 
   FROM clients 
   WHERE latitude IS NULL OR longitude IS NULL;
   
   -- Naver Geocoding으로 좌표 획득 후 업데이트
   UPDATE clients 
   SET latitude = 37.5012, longitude = 127.0396 
   WHERE id = 123;
   ```

2. **주문 GPS 직접 입력**:
   - 프론트엔드에서 주소 입력 시 자동 geocoding
   - 또는 관리자가 수동으로 좌표 입력

3. **일괄 Geocoding 실행**:
   ```bash
   # 모든 거래처 주소 → GPS 변환
   curl -X POST 'http://localhost:8000/api/v1/utils/geocode-all-clients'
   ```

### 문제 2: 팔레트 용량 부족

**증상**:
```
⚠️  팔레트 초과: 주문 45개 > 차량 용량 40개
```

**해결 방법**:

1. **차량 추가**:
   - 더 많은 차량 등록
   - 또는 대형 차량으로 교체

2. **주문 분할**:
   - 한 번에 처리할 주문 수 줄이기
   - 여러 배치로 나누어 최적화

3. **차량 용량 증대**:
   ```sql
   UPDATE vehicles 
   SET max_pallets = 15 
   WHERE max_pallets < 15 AND vehicle_type IN ('1톤', '1.4톤');
   ```

### 문제 3: 온도대 불일치

**증상**:
```
온도대 [냉동(-18℃)]에 호환 차량 없음 (필요: ['냉동', '듀얼'], 보유: ['냉장', '상온'])
```

**해결 방법**:

1. **냉동 차량 추가**:
   - 차량 타입을 '냉동' 또는 '듀얼'로 등록

2. **기존 차량 타입 변경**:
   ```sql
   UPDATE vehicles 
   SET vehicle_type = '듀얼' 
   WHERE id IN (1, 2, 3);
   ```

3. **주문 온도대 조정** (필요 시):
   ```sql
   UPDATE orders 
   SET temperature_zone = '냉장(0~10℃)' 
   WHERE temperature_zone = '냉동(-18℃)' 
     AND product_name LIKE '%냉장%';
   ```

### 문제 4: 시간 제약

**증상**:
```
솔루션을 찾지 못했습니다
(진단 정보상 GPS, 용량 모두 정상)
```

**해결 방법**:

1. **시간 제약 완화**:
   ```python
   # API 호출 시
   {
     "order_ids": [...],
     "time_limit_seconds": 60,  # 15 → 60초로 증가
     "use_time_windows": false  # 시간창 비활성화
   }
   ```

2. **Time Window 조정**:
   ```sql
   -- 거래처 작업 시간 확대
   UPDATE clients 
   SET pickup_start_time = '06:00', 
       pickup_end_time = '20:00';
   ```

3. **Haversine → Naver API**:
   ```python
   {
     "use_real_routing": true  # 실제 경로 사용
   }
   ```

---

## ✅ 체크리스트

배포 전:
- [ ] 로컬에서 테스트 통과 확인
- [ ] `cvrptw_service.py` 수정 완료
- [ ] Git commit 및 push 완료

배포 시:
- [ ] 서버 접속 확인
- [ ] 기존 파일 백업
- [ ] 새 파일 복사
- [ ] Docker 재시작
- [ ] 컨테이너 상태 확인 (healthy)

배포 후:
- [ ] API 테스트 실행
- [ ] 로그 확인 (진단 정보 출력 여부)
- [ ] 실패 시 reasons 배열에 원인 포함 확인
- [ ] 프론트엔드에서 오류 메시지 확인

---

## 📞 문제 발생 시

1. **로그 확인**:
   ```bash
   docker logs uvis-backend --tail 100 | grep -B 5 -A 20 "ERROR"
   ```

2. **백업 복원**:
   ```bash
   cp /root/uvis_backup_*/cvrptw_service.py /root/uvis/backend/app/services/
   docker restart uvis-backend
   ```

3. **Git 되돌리기**:
   ```bash
   git revert HEAD
   git push
   # 서버에서 git pull 후 재배포
   ```

---

**작성자**: Claude Code Assistant  
**문서 버전**: 1.0  
**최종 수정**: 2026-02-19
