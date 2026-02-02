# 🤖 UVIS ML 배차 시스템 구현 완료 및 배포 가이드

## 📦 생성된 파일

```
/home/user/webapp/
├── ML_DISPATCH_ARCHITECTURE.md          # 전체 아키텍처 설계 문서
├── backend/
│   ├── app/
│   │   └── services/
│   │       └── ml_dispatch_service.py   # ML 배차 서비스 (핵심)
│   └── tests/
│       └── test_ml_dispatch.py          # 단위 테스트
└── ML_DEPLOYMENT_GUIDE.md               # 이 문서
```

---

## 🎯 핵심 개념 요약

### Multi-Agent 아키텍처

```
┌────────────────────┐
│   Hard Rules       │  ← 필수 제약조건 (온도대, 용량, 기피차량 등)
└─────────┬──────────┘
          ↓
┌────────────────────┐
│   ML Agents        │  ← 5개 전문 Agent
│                    │
│  1. Distance       │  공차 거리 최소화
│  2. Rotation       │  회전수 평등
│  3. Time Window    │  하차시간 준수
│  4. Preference     │  고정배차/선호지
│  5. Voltage        │  저전압 배제
└─────────┬──────────┘
          ↓
┌────────────────────┐
│ Meta Coordinator   │  ← 최종 점수 통합
└─────────┬──────────┘
          ↓
     [최적 차량]
```

### 점수 계산 방식

각 Agent가 0~1 점수를 계산 → 가중치 적용 → 최종 점수:

```python
최종점수 = (
    거리 * 0.30 +
    회전수 * 0.20 +
    시간 * 0.25 +
    선호도 * 0.20 +
    전압 * 0.05
)
```

---

## 🚀 Quick Start (로컬 테스트)

### 1️⃣ 환경 확인

```bash
cd /home/user/webapp

# Python 환경 확인
python --version  # Python 3.8+

# 필수 패키지 설치
pip install numpy loguru
```

### 2️⃣ 테스트 실행

```bash
# 테스트 스크립트 실행
cd /home/user/webapp
python backend/tests/test_ml_dispatch.py
```

**예상 출력:**
```
🚀 ML Dispatch Service 테스트 시작

============================================================
ML Dispatch Service 테스트
============================================================

1️⃣  테스트 데이터 생성 중...
   ✅ 주문: TEST_ORDER_001
   ✅ 차량: 3대

2️⃣  ML Dispatch 서비스 초기화...
   ✅ 서비스 초기화 완료

3️⃣  배차 최적화 실행 중...
   ✅ 3대 차량 순위 결정 완료

4️⃣  배차 순위 결과:
------------------------------------------------------------

순위 1: TEST_V001 (12가3456)
  🎯 최종 점수: 0.823
  📊 세부 점수:
     - 거리: 0.127 (낮을수록 좋음)
     - 회전수: 0.000 (낮을수록 좋음)
     - 시간여유: 0.800 (높을수록 좋음)
     - 선호도: 0.500 (높을수록 좋음)
     - 전압안전: 1.000 (1.0=안전)
  💡 선택 이유: 근거리, 회전수적음, 시간여유 (점수: 0.823)

순위 2: TEST_V002 (34나5678)
  🎯 최종 점수: 0.756
  ...

============================================================
✨ 추천 차량: TEST_V001 (근거리, 회전수적음, 시간여유)
============================================================
```

---

## 🔧 기존 시스템 통합

### 방법 1: 기존 서비스와 병행 (권장)

기존 `DispatchOptimizationService`와 함께 사용:

```python
# backend/app/api/dispatches.py

from app.services.dispatch_optimization_service import DispatchOptimizationService
from app.services.ml_dispatch_service import MLDispatchService

@router.post("/optimize-ml")
async def optimize_dispatch_ml(
    order_ids: List[int],
    db: Session = Depends(get_db)
):
    """ML 기반 배차 최적화 (신규)"""
    
    # 주문 및 차량 조회
    orders = db.query(Order).filter(Order.id.in_(order_ids)).all()
    vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.AVAILABLE).all()
    
    # ML 서비스 실행
    ml_service = MLDispatchService(db)
    results = await ml_service.optimize_dispatch(orders, vehicles)
    
    # 결과 반환
    return {
        "success": True,
        "results": [
            {
                "order_id": result['order'].id,
                "order_number": result['order'].order_number,
                "recommended_vehicles": [
                    {
                        "vehicle_id": rank.vehicle.id,
                        "vehicle_code": rank.vehicle.code,
                        "score": rank.total_score,
                        "reason": rank.reason
                    }
                    for rank in result['rankings'][:3]  # Top 3
                ]
            }
            for result in results
        ]
    }
```

### 방법 2: A/B 테스트

일부 주문만 ML로 배차:

```python
import random

@router.post("/optimize")
async def optimize_dispatch(
    order_ids: List[int],
    db: Session = Depends(get_db)
):
    """배차 최적화 (A/B 테스트)"""
    
    # 30% 확률로 ML 사용
    use_ml = random.random() < 0.3
    
    if use_ml:
        logger.info("Using ML Dispatch Service")
        ml_service = MLDispatchService(db)
        results = await ml_service.optimize_dispatch(orders, vehicles)
        # ML 결과 변환
        ...
    else:
        logger.info("Using Legacy Dispatch Service")
        legacy_service = DispatchOptimizationService(db)
        results = await legacy_service.optimize_with_google_or_tools(orders, vehicles)
    
    return results
```

---

## 📊 실전 배포 단계

### Phase 1: 테스트 환경 (Week 1-2)

```bash
# 1. 코드 커밋
cd /home/user/webapp
git add backend/app/services/ml_dispatch_service.py
git add backend/tests/test_ml_dispatch.py
git add ML_DISPATCH_ARCHITECTURE.md
git add ML_DEPLOYMENT_GUIDE.md

git commit -m "feat: Add ML-based dispatch optimization service

- Multi-Agent architecture (5 agents)
- Distance, rotation, time, preference, voltage optimization
- Meta coordinator for final decision
- Unit tests included"

git push origin main
```

```bash
# 2. 서버 배포
ssh root@139.150.11.99
cd /root/uvis
git pull origin main

# Backend 재빌드
docker-compose -f docker-compose.prod.yml up -d --build backend

# 상태 확인
docker logs uvis-backend --tail 50
```

```bash
# 3. 테스트 실행 (서버에서)
docker exec -it uvis-backend python backend/tests/test_ml_dispatch.py
```

### Phase 2: 파일럿 런 (Week 3-4)

**목표:** 실제 데이터로 시뮬레이션

```python
# backend/app/api/dispatches.py

@router.post("/simulate-ml")
async def simulate_ml_dispatch(
    date: str,  # "2026-02-02"
    db: Session = Depends(get_db)
):
    """과거 데이터로 ML 배차 시뮬레이션"""
    
    # 해당 날짜 주문 조회
    target_date = datetime.strptime(date, "%Y-%m-%d").date()
    orders = db.query(Order).filter(Order.order_date == target_date).all()
    vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).all()
    
    # ML 배차 실행
    ml_service = MLDispatchService(db)
    results = await ml_service.optimize_dispatch(orders, vehicles)
    
    # 기존 배차와 비교
    comparison = []
    for result in results:
        order = result['order']
        ml_top = result['rankings'][0] if result['rankings'] else None
        
        # 실제로 배차된 차량 (historical)
        actual_dispatch = db.query(Dispatch).filter(Dispatch.order_id == order.id).first()
        
        comparison.append({
            "order": order.order_number,
            "ml_recommendation": ml_top.vehicle.code if ml_top else None,
            "ml_score": ml_top.total_score if ml_top else 0,
            "actual_vehicle": actual_dispatch.vehicle.code if actual_dispatch else None,
            "match": ml_top.vehicle.id == actual_dispatch.vehicle_id if (ml_top and actual_dispatch) else False
        })
    
    # 매칭률 계산
    match_rate = sum(1 for c in comparison if c['match']) / len(comparison)
    
    return {
        "date": date,
        "total_orders": len(orders),
        "match_rate": match_rate,
        "comparison": comparison
    }
```

**실행:**
```bash
curl -X POST http://139.150.11.99:8000/api/dispatches/simulate-ml \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-02-01"}'
```

### Phase 3: 프로덕션 배포 (Week 5-6)

**API 엔드포인트 추가:**

```python
@router.post("/optimize-with-ml")
async def optimize_with_ml_production(
    order_ids: List[int],
    mode: str = "recommend",  # "recommend" or "auto"
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ML 배차 최적화 (프로덕션)
    
    mode:
      - recommend: 추천만 (사람이 최종 선택)
      - auto: 자동 배차 (1순위로 자동 배정)
    """
    
    orders = db.query(Order).filter(Order.id.in_(order_ids)).all()
    vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.AVAILABLE).all()
    
    ml_service = MLDispatchService(db)
    results = await ml_service.optimize_dispatch(orders, vehicles)
    
    dispatches = []
    
    for result in results:
        order = result['order']
        rankings = result['rankings']
        
        if not rankings:
            logger.warning(f"No vehicles for order {order.order_number}")
            continue
        
        if mode == "auto":
            # 자동 배차: 1순위로 즉시 배정
            best = rankings[0]
            dispatch = Dispatch(
                order_id=order.id,
                vehicle_id=best.vehicle.id,
                optimization_score=best.total_score,
                assigned_by='ml_auto',
                assigned_user_id=current_user.id,
                status=DispatchStatus.ASSIGNED
            )
            db.add(dispatch)
            dispatches.append(dispatch)
            
            logger.info(f"Auto-assigned: {order.order_number} → {best.vehicle.code}")
        
        else:
            # 추천만: 프론트엔드에서 선택
            pass
    
    if mode == "auto":
        db.commit()
    
    return {
        "mode": mode,
        "results": [
            {
                "order_id": result['order'].id,
                "order_number": result['order'].order_number,
                "top_3": [
                    {
                        "rank": i + 1,
                        "vehicle_id": rank.vehicle.id,
                        "vehicle_code": rank.vehicle.code,
                        "score": rank.total_score,
                        "reason": rank.reason,
                        "details": {
                            "distance_score": rank.agent_scores.distance,
                            "rotation_score": rank.agent_scores.rotation,
                            "time_score": rank.agent_scores.time_window,
                            "preference_score": rank.agent_scores.preference,
                            "voltage_ok": rank.agent_scores.voltage == 1.0
                        }
                    }
                    for i, rank in enumerate(result['rankings'][:3])
                ]
            }
            for result in results
        ]
    }
```

---

## 🎨 프론트엔드 통합

### 배차 화면에 ML 추천 표시

```typescript
// frontend/src/pages/DispatchPage.tsx

const handleMLOptimize = async (orderIds: number[]) => {
  try {
    const response = await fetch('/api/dispatches/optimize-with-ml', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_ids: orderIds, mode: 'recommend' })
    });
    
    const data = await response.json();
    
    // 결과 표시
    setMLRecommendations(data.results);
    setShowMLPanel(true);
  } catch (error) {
    console.error('ML 최적화 실패:', error);
  }
};

// UI 렌더링
<div className="ml-recommendations">
  <h3>🤖 AI 추천 배차</h3>
  {mlRecommendations.map(result => (
    <div key={result.order_id} className="order-recommendation">
      <h4>주문: {result.order_number}</h4>
      
      {result.top_3.map(vehicle => (
        <div 
          key={vehicle.vehicle_id} 
          className={`vehicle-card rank-${vehicle.rank}`}
        >
          <div className="rank-badge">#{vehicle.rank}</div>
          <div className="vehicle-info">
            <strong>{vehicle.vehicle_code}</strong>
            <span className="score">점수: {vehicle.score.toFixed(3)}</span>
          </div>
          <div className="reason">{vehicle.reason}</div>
          
          {/* 상세 점수 */}
          <details>
            <summary>상세</summary>
            <ul>
              <li>거리: {vehicle.details.distance_score.toFixed(2)}</li>
              <li>회전수: {vehicle.details.rotation_score.toFixed(2)}</li>
              <li>시간: {vehicle.details.time_score.toFixed(2)}</li>
              <li>선호도: {vehicle.details.preference_score.toFixed(2)}</li>
              <li>전압: {vehicle.details.voltage_ok ? '✅' : '❌'}</li>
            </ul>
          </details>
          
          <button onClick={() => assignVehicle(result.order_id, vehicle.vehicle_id)}>
            이 차량으로 배차
          </button>
        </div>
      ))}
    </div>
  ))}
</div>
```

---

## 📈 성능 모니터링

### KPI 추적

```sql
-- 일별 ML 배차 성과
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_dispatches,
    AVG(optimization_score) as avg_score,
    AVG(actual_total_distance_km) as avg_distance,
    SUM(CASE WHEN was_delayed THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as delay_rate
FROM dispatch_training_data
WHERE assigned_by = 'ml_auto'
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### 대시보드 메트릭

```python
@router.get("/ml-metrics")
async def get_ml_metrics(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """ML 배차 성과 메트릭"""
    
    # 데이터 조회
    ml_dispatches = db.query(Dispatch).filter(
        Dispatch.assigned_by.like('ml%'),
        Dispatch.created_at.between(start_date, end_date)
    ).all()
    
    legacy_dispatches = db.query(Dispatch).filter(
        Dispatch.assigned_by == 'human',
        Dispatch.created_at.between(start_date, end_date)
    ).all()
    
    # 메트릭 계산
    metrics = {
        "ml": calculate_metrics(ml_dispatches),
        "legacy": calculate_metrics(legacy_dispatches),
        "improvement": {}
    }
    
    # 개선율 계산
    metrics["improvement"] = {
        "distance": (metrics["legacy"]["avg_distance"] - metrics["ml"]["avg_distance"]) / metrics["legacy"]["avg_distance"],
        "on_time": metrics["ml"]["on_time_rate"] - metrics["legacy"]["on_time_rate"],
        "fairness": metrics["ml"]["rotation_variance"] < metrics["legacy"]["rotation_variance"]
    }
    
    return metrics
```

---

## 🔄 지속 개선

### 온라인 학습 준비

```python
# backend/app/services/ml_training_service.py

class MLTrainingService:
    """ML 모델 지속 학습"""
    
    def collect_feedback(self, dispatch_id: int):
        """배차 결과 피드백 수집"""
        dispatch = self.db.query(Dispatch).get(dispatch_id)
        
        # 실제 결과 데이터 수집
        training_data = {
            'dispatch_id': dispatch.id,
            'features': extract_features(dispatch.order, dispatch.vehicle),
            'actual_distance': dispatch.actual_total_distance_km,
            'was_delayed': dispatch.was_delayed,
            'driver_satisfaction': dispatch.driver_satisfaction
        }
        
        # 학습 데이터베이스에 저장
        self.db.execute(
            "INSERT INTO dispatch_training_data (...) VALUES (...)",
            training_data
        )
        self.db.commit()
    
    def retrain_models(self):
        """주기적 모델 재학습 (주 1회)"""
        # 최근 데이터 로드
        recent_data = self.load_recent_training_data(days=30)
        
        # 모델 재학습
        # (향후 구현: LightGBM 모델 fine-tuning)
        
        logger.info("Models retrained successfully!")
```

---

## ✅ 배포 체크리스트

### 코드 준비
- [x] `ml_dispatch_service.py` 작성 완료
- [x] `test_ml_dispatch.py` 작성 완료
- [x] 아키텍처 문서 작성 완료
- [x] 배포 가이드 작성 완료

### 서버 배포
- [ ] 코드 커밋 및 푸시
- [ ] 서버 코드 업데이트 (git pull)
- [ ] Backend 재빌드
- [ ] 테스트 실행 확인
- [ ] 로그 확인 (에러 없음)

### API 통합
- [ ] `/optimize-with-ml` 엔드포인트 추가
- [ ] `/simulate-ml` 엔드포인트 추가 (선택)
- [ ] `/ml-metrics` 엔드포인트 추가 (선택)

### 프론트엔드
- [ ] ML 추천 패널 UI 추가
- [ ] 배차 화면 통합
- [ ] 점수 시각화

### 모니터링
- [ ] ML 배차 로그 수집
- [ ] 성과 메트릭 추적
- [ ] A/B 테스트 결과 분석

---

## 🎓 학습 리소스

### 추천 자료
- **Google OR-Tools:** https://developers.google.com/optimization
- **Vehicle Routing Problem:** https://en.wikipedia.org/wiki/Vehicle_routing_problem
- **Multi-Agent Systems:** https://www.coursera.org/learn/multi-agent-systems

### 다음 단계
1. **강화학습 도입:** Deep Q-Network (DQN)로 동적 배차 학습
2. **실시간 재배차:** 운행 중 돌발 상황 대응
3. **예측 모델:** 수요 예측 및 선제적 차량 배치

---

## 📞 지원

문제 발생 시:
1. 로그 확인: `docker logs uvis-backend --tail 100`
2. 테스트 재실행: `python backend/tests/test_ml_dispatch.py`
3. 이슈 리포트: GitHub Issues

---

**축하합니다! ML 기반 배차 시스템 구현 완료!** 🎉

이제 점진적으로 배포하고 실제 데이터로 성능을 검증하세요!
