# 🚀 Phase 2 배포 가이드: 서버 배포 & 과거 데이터 시뮬레이션

## 📋 Overview

Phase 2에서는 ML 배차 시스템을 프로덕션 서버에 배포하고, 실제 과거 데이터로 시뮬레이션하여 성능을 검증합니다.

---

## ✅ Phase 2 체크리스트

### 1️⃣ 서버 배포 (15분)
- [x] 코드 커밋 및 푸시
- [x] PR 생성 및 업데이트
- [ ] 서버 코드 업데이트
- [ ] Backend 재빌드
- [ ] DB 마이그레이션 실행
- [ ] API 엔드포인트 확인

### 2️⃣ 시뮬레이션 테스트 (30분)
- [ ] 단일 날짜 시뮬레이션
- [ ] 기간별 시뮬레이션
- [ ] 매칭률 분석
- [ ] 성능 메트릭 수집

### 3️⃣ 성능 벤치마킹 (1시간)
- [ ] 과거 1주일 데이터 분석
- [ ] ML vs Human 배차 비교
- [ ] Agent별 성능 분석
- [ ] 가중치 튜닝

---

## 🔧 Step 1: 서버 배포

### 1.1 서버 접속

```bash
ssh root@139.150.11.99
cd /root/uvis
```

### 1.2 코드 업데이트

```bash
# 최신 코드 가져오기
git fetch origin
git checkout main
git pull origin main

# 변경사항 확인
git log --oneline -5
```

**예상 출력:**
```
ff4ed6d feat: Add ML-based dispatch optimization (Phase 1 & 2)
02fe029 fix: UVIS 불러오기 시 차량번호만 덮어쓰도록 수정
...
```

### 1.3 DB 마이그레이션 실행

```bash
# Phase 1 제약조건 마이그레이션
cd /root/uvis

# 마이그레이션 SQL 실행
docker exec -i uvis-db psql -U postgres -d uvis < backend/migrations/phase1_constraints.sql

# 결과 확인
docker exec -it uvis-db psql -U postgres -d uvis -c "
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'vehicles' 
      AND (column_name LIKE '%pallet%' OR column_name LIKE '%support%')
    ORDER BY column_name;
"
```

**예상 출력:**
```
        column_name        |     data_type      
---------------------------+--------------------
 max_pallets_11type        | integer
 max_pallets_12type        | integer
 supports_ambient          | boolean
 supports_chilled          | boolean
 supports_frozen           | boolean
(5 rows)
```

### 1.4 Backend 재빌드

```bash
cd /root/uvis

# Backend 재빌드 (ML 서비스 포함)
docker-compose -f docker-compose.prod.yml up -d --build backend

# 빌드 진행 확인 (약 2-3분 소요)
docker-compose -f docker-compose.prod.yml logs -f backend
```

**정상 로그:**
```
uvis-backend | Starting Cold Chain Dispatch System...
uvis-backend | Initializing database...
uvis-backend | Application startup complete
uvis-backend | Uvicorn running on http://0.0.0.0:8000
```

빌드가 완료되면 `Ctrl+C`로 로그 확인 종료.

### 1.5 Backend 상태 확인

```bash
# 컨테이너 상태
docker ps | grep backend

# Health 확인
docker inspect uvis-backend --format='{{.State.Health.Status}}'

# 최근 로그
docker logs uvis-backend --tail 30
```

**예상 결과:**
```
uvis-backend   Up 2 minutes (healthy)   0.0.0.0:8000->8000/tcp
healthy
```

### 1.6 API 엔드포인트 확인

```bash
# ML Dispatch API 확인
curl -X GET http://139.150.11.99:8000/docs | grep ml-dispatch

# 또는 브라우저에서
# http://139.150.11.99:8000/docs
```

**확인 항목:**
- `/api/ml-dispatch/simulate` - 과거 데이터 시뮬레이션
- `/api/ml-dispatch/optimize` - 실시간 ML 배차
- `/api/ml-dispatch/performance` - 성능 분석

---

## 🧪 Step 2: 시뮬레이션 테스트

### 2.1 로컬에서 시뮬레이션 실행

```bash
# 로컬 터미널에서
cd /home/user/webapp

# 단일 날짜 시뮬레이션
python backend/tests/phase2_simulation.py --date 2026-02-01

# 또는 기간별 시뮬레이션
python backend/tests/phase2_simulation.py \
    --start 2026-02-01 \
    --end 2026-02-07
```

**예상 출력:**
```
🔐 Authenticating...
✅ Authentication successful

📊 Simulating dispatch for 2026-02-01...

================================================================================
📅 Date: 2026-02-01
================================================================================

📦 Orders:
  - Total: 45
  - Simulated: 42
  - ML Match Rate: 73.8% (31/42)

🎯 Performance Metrics:
  - Average Score: 0.756
  - Score Distribution:
      High (≥0.7): 28
      Medium (0.5-0.7): 12
      Low (<0.5): 2
  - Agent Averages:
      distance: 0.245
      rotation: 0.318
      time_window: 0.812
      preference: 0.543

🔍 Top 10 Comparisons:
+-------------+--------+-----------+----------+---------+----------+---------+
| Order       | Temp   |   Pallets | ML Rec   | Score   | Actual   | Match   |
+=============+========+===========+==========+=========+==========+=========+
| ORD-001     | 냉동   |        15 | V001     | 0.823   | V001     | ✅      |
| ORD-002     | 냉장   |        20 | V003     | 0.791   | V002     | ❌      |
| ORD-003     | 상온   |        12 | V005     | 0.754   | V005     | ✅      |
...
+-------------+--------+-----------+----------+---------+----------+---------+

✅ Simulation complete!
```

### 2.2 직접 API 호출 (curl)

```bash
# 인증 토큰 얻기
TOKEN=$(curl -X POST http://139.150.11.99:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 시뮬레이션 실행
curl -X POST "http://139.150.11.99:8000/api/ml-dispatch/simulate?target_date=2026-02-01" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
```

### 2.3 기간별 메트릭 조회

```bash
# 1주일 메트릭
curl -X GET "http://139.150.11.99:8000/api/ml-dispatch/simulate/metrics?start_date=2026-02-01&end_date=2026-02-07" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.summary'
```

**예상 출력:**
```json
{
  "total_days": 7,
  "total_orders": 315,
  "total_dispatches": 298,
  "avg_orders_per_day": 45.0,
  "overall_dispatch_rate": 0.946
}
```

---

## 📊 Step 3: 성능 벤치마킹

### 3.1 과거 1주일 데이터 분석

```bash
# 로컬에서 대량 시뮬레이션
cd /home/user/webapp

python backend/tests/phase2_simulation.py \
    --start 2026-01-25 \
    --end 2026-01-31 \
    > results/simulation_week1.txt
```

### 3.2 ML vs Human 배차 비교

```bash
# 성능 비교 API
curl -X GET "http://139.150.11.99:8000/api/ml-dispatch/performance?start_date=2026-02-01&end_date=2026-02-07" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
```

**분석 항목:**
- ML 평균 점수 vs Human 배차
- 매칭률 트렌드
- Agent별 기여도

### 3.3 가중치 튜닝

현재 가중치:
```python
weights = {
    'distance': 0.30,      # 거리
    'rotation': 0.20,      # 회전수
    'time_window': 0.25,   # 시간
    'preference': 0.20,    # 선호도
    'voltage': 0.05        # 안전
}
```

**튜닝 전략:**

1. **거리 중시** (공차 거리 최소화)
   ```python
   weights = {'distance': 0.40, 'rotation': 0.15, 'time_window': 0.25, 'preference': 0.15, 'voltage': 0.05}
   ```

2. **공정성 중시** (회전수 평등)
   ```python
   weights = {'distance': 0.25, 'rotation': 0.35, 'time_window': 0.20, 'preference': 0.15, 'voltage': 0.05}
   ```

3. **시간 중시** (납기 준수)
   ```python
   weights = {'distance': 0.20, 'rotation': 0.15, 'time_window': 0.40, 'preference': 0.20, 'voltage': 0.05}
   ```

**가중치 업데이트 방법:**
```python
# backend/app/services/ml_dispatch_service.py
# MetaCoordinator.__init__() 메서드에서 수정
```

---

## 📈 성과 지표 (KPIs)

### 목표 달성 기준

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| 매칭률 | ≥ 70% | ML 추천 = 실제 배차 |
| 평균 점수 | ≥ 0.70 | ML 최종 점수 평균 |
| High Score 비율 | ≥ 60% | 점수 ≥ 0.7인 추천 비율 |
| 시뮬레이션 속도 | < 5초/일 | 1일 시뮬레이션 소요 시간 |

### 시뮬레이션 결과 분석

```bash
# 결과 요약 생성
cat << 'EOF' > /root/uvis/phase2_summary.sh
#!/bin/bash

echo "================================================"
echo "Phase 2 Simulation Summary"
echo "================================================"

# 1주일 시뮬레이션
for date in 2026-02-{01..07}; do
    echo "Testing $date..."
    curl -X POST "http://localhost:8000/api/ml-dispatch/simulate?target_date=$date" \
        -H "Authorization: Bearer $TOKEN" \
        | jq -r '"\(.date): \(.simulated_orders) orders, \(.ml_match_rate*100)% match"'
done

echo "================================================"
EOF

chmod +x /root/uvis/phase2_summary.sh
./phase2_summary.sh
```

---

## 🐛 트러블슈팅

### 문제 1: Backend 빌드 실패

**증상:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**해결:**
```bash
# requirements.txt 확인
cat backend/requirements.txt | grep -E "numpy|loguru"

# 누락된 패키지 추가
echo "numpy>=1.21.0" >> backend/requirements.txt
echo "loguru>=0.6.0" >> backend/requirements.txt

# 재빌드
docker-compose -f docker-compose.prod.yml up -d --build backend
```

### 문제 2: Import 에러

**증상:**
```
ModuleNotFoundError: No module named 'app.api.ml_dispatch'
```

**해결:**
```bash
# 파일 존재 확인
docker exec uvis-backend ls -la /app/app/api/ml_dispatch.py

# 없으면 수동 복사
docker cp backend/app/api/ml_dispatch.py uvis-backend:/app/app/api/

# Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

### 문제 3: 시뮬레이션 타임아웃

**증상:**
```
RequestException: Connection timeout
```

**해결:**
```python
# backend/tests/phase2_simulation.py
# timeout 증가
response = requests.post(..., timeout=120)  # 60 → 120
```

### 문제 4: 인증 실패

**증상:**
```
❌ Authentication failed: 401 Unauthorized
```

**해결:**
```bash
# 올바른 계정 정보 사용
# backend/tests/phase2_simulation.py
# authenticate() 함수에서 username/password 확인

# 또는 환경변수로 설정
export API_USERNAME="your_username"
export API_PASSWORD="your_password"
```

---

## 📊 예상 결과

### Good Case (성공)

```
📅 Period Summary
================================================================================
  - Total Days: 7
  - Total Orders: 315
  - Total Matches: 232
  - Overall Match Rate: 73.7%
  - Average ML Score: 0.758

📅 Daily Summary:
+------------+---------+-------------+------------+
| Date       | Orders  | Match Rate  | Avg Score  |
+============+=========+=============+============+
| 2026-02-01 |      45 |      73.8%  |      0.756 |
| 2026-02-02 |      48 |      75.0%  |      0.761 |
| 2026-02-03 |      42 |      71.4%  |      0.752 |
| 2026-02-04 |      46 |      73.9%  |      0.759 |
| 2026-02-05 |      47 |      74.5%  |      0.763 |
| 2026-02-06 |      44 |      72.7%  |      0.755 |
| 2026-02-07 |      43 |      74.4%  |      0.760 |
+------------+---------+-------------+------------+
```

**평가:** ✅ 목표 달성
- 매칭률 73.7% (목표 70% 초과)
- 평균 점수 0.758 (목표 0.70 초과)
- 안정적인 일별 성능

### Bad Case (개선 필요)

```
📅 Period Summary
================================================================================
  - Total Days: 7
  - Total Orders: 315
  - Total Matches: 189
  - Overall Match Rate: 60.0%
  - Average ML Score: 0.623
```

**평가:** ⚠️ 목표 미달
- 매칭률 60% (목표 70% 미달)
- 평균 점수 0.623 (목표 0.70 미달)

**개선 방안:**
1. 가중치 재조정
2. Hard Rules 완화 검토
3. Agent 로직 개선
4. 과거 데이터 품질 확인

---

## 🎯 Next Steps

Phase 2 완료 후:

### ✅ 성공 시 (목표 달성)
→ **Phase 3 진행**: 프로덕션 배포
- API 엔드포인트 활성화
- 프론트엔드 통합
- A/B 테스트 시작 (10% 트래픽)

### ⚠️ 개선 필요 시 (목표 미달)
→ **Phase 2 재시도**: 튜닝 및 최적화
- 가중치 조정
- Agent 로직 개선
- 추가 제약조건 구현
- 재시뮬레이션

---

## 📞 문의 및 지원

**문제 발생 시:**
1. 로그 확인: `docker logs uvis-backend --tail 100`
2. DB 상태: `docker exec -it uvis-db psql -U postgres -d uvis`
3. API 문서: http://139.150.11.99:8000/docs

**Phase 2 완료 보고:**
```
✅ Phase 2 완료
- 서버 배포: [완료/실패]
- 시뮬레이션: [완료/실패]
- 매칭률: [XX%]
- 평균 점수: [X.XXX]
- 다음 단계: [Phase 3 진행 / 튜닝 필요]
```

---

**축하합니다!** Phase 2를 성공적으로 완료하면 Phase 3 (프로덕션 배포)로 진행합니다! 🚀
