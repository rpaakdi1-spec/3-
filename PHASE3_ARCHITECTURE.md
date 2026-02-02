# 🚀 Phase 3: 프로덕션 통합 아키텍처

## 📋 Overview

Phase 3는 ML 배차 시스템을 실제 프로덕션 환경에 안전하게 통합하는 단계입니다.

**목표:**
- ✅ 프론트엔드 UI 통합
- ✅ A/B 테스트 프레임워크
- ✅ 점진적 롤아웃 (10% → 30% → 100%)
- ✅ 실시간 모니터링
- ✅ 자동 롤백 메커니즘

---

## 🏗️ 전체 아키텍처

```
┌────────────────────────────────────────────────────────────────┐
│                         Frontend UI                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DispatchPage.tsx (기존)                                 │  │
│  │    ├── 수동 배차 (기존 플로우)                           │  │
│  │    └── 🆕 ML 추천 패널 (신규)                           │  │
│  │         ├── Top 3 차량 추천                              │  │
│  │         ├── 상세 점수 표시                               │  │
│  │         └── 1-Click 배차 버튼                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│                      A/B Test Controller                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Traffic Split (Redis Cache)                             │  │
│  │    ├── Group A (Control): Legacy Dispatch (90% → 70%)   │  │
│  │    ├── Group B (Treatment): ML Dispatch (10% → 30%)     │  │
│  │    └── Gradual Rollout Logic                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                     ↓                      ↓
         ┌───────────────────┐   ┌──────────────────────┐
         │  Legacy Dispatch  │   │   ML Dispatch        │
         │  (기존 시스템)     │   │   (Phase 2)          │
         └───────────────────┘   └──────────────────────┘
                     ↓                      ↓
┌────────────────────────────────────────────────────────────────┐
│                   Performance Monitoring                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Real-time Metrics Dashboard                             │  │
│  │    ├── ML Success Rate (목표: ≥ 95%)                    │  │
│  │    ├── Average Score (목표: ≥ 0.70)                     │  │
│  │    ├── Response Time (목표: < 2s)                       │  │
│  │    ├── Error Rate (목표: < 1%)                          │  │
│  │    └── User Satisfaction (목표: ≥ 4.0/5.0)             │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│                    Auto Rollback System                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Alert & Rollback Triggers                               │  │
│  │    ├── Error Rate > 5% → Auto Rollback                  │  │
│  │    ├── ML Score < 0.60 → Alert                          │  │
│  │    ├── Response Time > 5s → Alert                       │  │
│  │    └── Manual Rollback Button                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Phase 3 로드맵

### Week 1-2: 프론트엔드 통합
- [ ] ML 추천 UI 컴포넌트
- [ ] 1-Click 배차 기능
- [ ] 실시간 점수 업데이트

### Week 3-4: A/B 테스트 프레임워크
- [ ] Traffic Split 로직
- [ ] 실험 그룹 관리
- [ ] 메트릭 수집

### Week 5-6: 점진적 롤아웃
- [ ] 10% 트래픽 (파일럿)
- [ ] 30% 트래픽 (확대)
- [ ] 100% 트래픽 (전면 배포)

### Week 7-8: 모니터링 & 최적화
- [ ] 실시간 대시보드
- [ ] 자동 경고 시스템
- [ ] 온라인 학습 파이프라인

---

## 🎨 1. 프론트엔드 UI 설계

### 1.1 ML 추천 패널 (MLRecommendationPanel.tsx)

```typescript
interface MLRecommendation {
  rank: number;
  vehicleId: number;
  vehicleCode: string;
  score: number;
  reason: string;
  details: {
    distance: number;
    rotation: number;
    timeWindow: number;
    preference: number;
    voltage: boolean;
  };
}

interface MLRecommendationPanelProps {
  orderId: number;
  recommendations: MLRecommendation[];
  onSelect: (vehicleId: number) => void;
  loading: boolean;
}

const MLRecommendationPanel: React.FC<MLRecommendationPanelProps> = ({
  orderId,
  recommendations,
  onSelect,
  loading
}) => {
  if (loading) {
    return <Skeleton count={3} height={120} />;
  }

  return (
    <div className="ml-recommendation-panel">
      <div className="panel-header">
        <RobotIcon />
        <h3>🤖 AI 추천 배차</h3>
        <Badge>Beta</Badge>
      </div>

      {recommendations.map((rec) => (
        <VehicleRecommendationCard
          key={rec.vehicleId}
          rank={rec.rank}
          vehicleCode={rec.vehicleCode}
          score={rec.score}
          reason={rec.reason}
          details={rec.details}
          onSelect={() => onSelect(rec.vehicleId)}
        />
      ))}

      <div className="panel-footer">
        <InfoIcon />
        <span>AI가 과거 배차 데이터를 학습하여 추천합니다</span>
      </div>
    </div>
  );
};
```

### 1.2 차량 추천 카드 (VehicleRecommendationCard.tsx)

```typescript
const VehicleRecommendationCard: React.FC<VehicleRecommendationCardProps> = ({
  rank,
  vehicleCode,
  score,
  reason,
  details,
  onSelect
}) => {
  const scoreColor = score >= 0.7 ? 'green' : score >= 0.5 ? 'yellow' : 'red';

  return (
    <div className={`vehicle-card rank-${rank}`}>
      {/* Rank Badge */}
      <div className="rank-badge">
        {rank === 1 && <TrophyIcon />}
        #{rank}
      </div>

      {/* Vehicle Info */}
      <div className="vehicle-info">
        <h4>{vehicleCode}</h4>
        <ScoreBadge score={score} color={scoreColor} />
      </div>

      {/* Reason */}
      <div className="reason">
        <TagIcon />
        {reason}
      </div>

      {/* Detailed Scores */}
      <Collapsible title="상세 점수">
        <ScoreBreakdown>
          <ScoreBar label="거리" value={1 - details.distance} max={1} />
          <ScoreBar label="회전수" value={1 - details.rotation} max={1} />
          <ScoreBar label="시간여유" value={details.timeWindow} max={1} />
          <ScoreBar label="선호도" value={details.preference} max={1} />
          <ScoreIndicator label="전압" value={details.voltage} />
        </ScoreBreakdown>
      </Collapsible>

      {/* Action Button */}
      <Button
        variant={rank === 1 ? 'primary' : 'secondary'}
        onClick={onSelect}
        fullWidth
      >
        {rank === 1 ? '🚀 이 차량으로 배차' : '선택'}
      </Button>
    </div>
  );
};
```

### 1.3 배차 페이지 통합 (DispatchPage.tsx)

```typescript
const DispatchPage: React.FC = () => {
  const [selectedOrders, setSelectedOrders] = useState<number[]>([]);
  const [mlRecommendations, setMlRecommendations] = useState<MLRecommendation[][]>([]);
  const [showMLPanel, setShowMLPanel] = useState(false);
  const [mlEnabled, setMlEnabled] = useState(false); // A/B Test Flag

  // Fetch ML recommendations
  const fetchMLRecommendations = async (orderIds: number[]) => {
    try {
      const response = await api.post('/api/ml-dispatch/optimize', {
        order_ids: orderIds,
        mode: 'recommend'
      });

      setMlRecommendations(response.data.results.map(r => r.top_3));
      setShowMLPanel(true);
    } catch (error) {
      console.error('ML recommendation failed:', error);
      // Fallback to legacy
    }
  };

  // Handle ML-assisted dispatch
  const handleMLDispatch = async (orderId: number, vehicleId: number) => {
    try {
      // Create dispatch with ML assignment
      await api.post('/api/dispatches', {
        order_id: orderId,
        vehicle_id: vehicleId,
        assigned_by: 'ml_assisted' // Track ML usage
      });

      toast.success('AI 추천으로 배차 완료!');
      
      // Track success
      trackEvent('ml_dispatch_success', { orderId, vehicleId });
    } catch (error) {
      console.error('Dispatch failed:', error);
      toast.error('배차 실패');
    }
  };

  return (
    <div className="dispatch-page">
      {/* Existing UI */}
      <OrderSelectionPanel
        orders={orders}
        onSelect={setSelectedOrders}
      />

      {/* ML Toggle (A/B Test controlled) */}
      {mlEnabled && (
        <div className="ml-controls">
          <Switch
            label="🤖 AI 추천 사용"
            checked={showMLPanel}
            onChange={(checked) => {
              if (checked && selectedOrders.length > 0) {
                fetchMLRecommendations(selectedOrders);
              } else {
                setShowMLPanel(false);
              }
            }}
          />
        </div>
      )}

      <div className="dispatch-content">
        {/* Legacy Dispatch Panel (기존) */}
        <LegacyDispatchPanel
          selectedOrders={selectedOrders}
          onDispatch={handleLegacyDispatch}
        />

        {/* ML Recommendation Panel (신규) */}
        {showMLPanel && (
          <MLRecommendationPanel
            recommendations={mlRecommendations}
            onSelect={handleMLDispatch}
          />
        )}
      </div>
    </div>
  );
};
```

---

## 🧪 2. A/B 테스트 프레임워크

### 2.1 Traffic Split Controller (Backend)

```python
# backend/app/services/ab_test_service.py

import random
from typing import Optional
from redis import Redis
from loguru import logger

class ABTestService:
    """A/B 테스트 트래픽 분배 서비스"""
    
    def __init__(self, redis: Redis):
        self.redis = redis
        self.experiment_key = "ml_dispatch:experiment:v1"
    
    def assign_user_to_group(self, user_id: int) -> str:
        """
        사용자를 실험 그룹에 할당
        
        Returns:
            'control' or 'treatment'
        """
        # 기존 할당 확인
        existing_group = self.redis.hget(
            self.experiment_key,
            f"user:{user_id}"
        )
        
        if existing_group:
            return existing_group.decode()
        
        # 새 할당
        rollout_percentage = self._get_rollout_percentage()
        
        # 사용자 ID 기반 일관된 해싱
        hash_value = hash(f"ml_dispatch_v1_{user_id}") % 100
        
        if hash_value < rollout_percentage:
            group = "treatment"  # ML Dispatch
        else:
            group = "control"    # Legacy Dispatch
        
        # Redis에 저장
        self.redis.hset(
            self.experiment_key,
            f"user:{user_id}",
            group
        )
        
        logger.info(f"User {user_id} assigned to group: {group}")
        
        return group
    
    def _get_rollout_percentage(self) -> int:
        """현재 롤아웃 비율 가져오기"""
        percentage = self.redis.get("ml_dispatch:rollout_percentage")
        if percentage:
            return int(percentage)
        return 10  # 기본 10%
    
    def set_rollout_percentage(self, percentage: int):
        """롤아웃 비율 설정 (0-100)"""
        if not 0 <= percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        
        self.redis.set("ml_dispatch:rollout_percentage", percentage)
        logger.info(f"Rollout percentage set to {percentage}%")
    
    def get_experiment_stats(self) -> dict:
        """실험 통계 조회"""
        all_users = self.redis.hgetall(self.experiment_key)
        
        control_count = sum(1 for v in all_users.values() if v == b'control')
        treatment_count = sum(1 for v in all_users.values() if v == b'treatment')
        
        return {
            "total_users": len(all_users),
            "control_count": control_count,
            "treatment_count": treatment_count,
            "treatment_percentage": (
                treatment_count / len(all_users) * 100
                if all_users else 0
            ),
            "rollout_percentage": self._get_rollout_percentage()
        }
```

### 2.2 API 엔드포인트

```python
# backend/app/api/ml_dispatch.py (추가)

@router.get("/ab-test/assignment")
async def get_ab_test_assignment(
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """
    현재 사용자의 A/B 테스트 그룹 조회
    
    Returns:
        {
            "group": "treatment" | "control",
            "ml_enabled": true | false
        }
    """
    ab_service = ABTestService(redis)
    group = ab_service.assign_user_to_group(current_user.id)
    
    return {
        "group": group,
        "ml_enabled": (group == "treatment")
    }


@router.post("/ab-test/rollout")
async def update_rollout_percentage(
    percentage: int,
    current_user: User = Depends(get_current_admin),  # Admin only
    redis: Redis = Depends(get_redis)
):
    """
    롤아웃 비율 업데이트 (관리자 전용)
    
    Args:
        percentage: 0-100 (treatment 그룹 비율)
    """
    ab_service = ABTestService(redis)
    ab_service.set_rollout_percentage(percentage)
    
    stats = ab_service.get_experiment_stats()
    
    return {
        "success": True,
        "rollout_percentage": percentage,
        "stats": stats
    }


@router.get("/ab-test/stats")
async def get_ab_test_stats(
    current_user: User = Depends(get_current_admin),
    redis: Redis = Depends(get_redis)
):
    """A/B 테스트 통계 조회"""
    ab_service = ABTestService(redis)
    stats = ab_service.get_experiment_stats()
    
    return stats
```

### 2.3 프론트엔드 통합

```typescript
// frontend/src/hooks/useABTest.ts

import { useEffect, useState } from 'react';
import { api } from '@/services/api';

interface ABTestAssignment {
  group: 'control' | 'treatment';
  mlEnabled: boolean;
}

export const useABTest = () => {
  const [assignment, setAssignment] = useState<ABTestAssignment | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAssignment = async () => {
      try {
        const response = await api.get('/api/ml-dispatch/ab-test/assignment');
        setAssignment(response.data);
        
        // Track assignment
        analytics.track('ab_test_assigned', {
          group: response.data.group,
          experiment: 'ml_dispatch_v1'
        });
      } catch (error) {
        console.error('Failed to fetch A/B test assignment:', error);
        // Fallback to control
        setAssignment({ group: 'control', mlEnabled: false });
      } finally {
        setLoading(false);
      }
    };

    fetchAssignment();
  }, []);

  return { assignment, loading };
};


// 사용 예시
const DispatchPage: React.FC = () => {
  const { assignment, loading } = useABTest();

  if (loading) {
    return <LoadingSpinner />;
  }

  const mlEnabled = assignment?.mlEnabled ?? false;

  return (
    <div>
      {/* ML 기능은 treatment 그룹에만 표시 */}
      {mlEnabled && (
        <MLRecommendationPanel ... />
      )}
    </div>
  );
};
```

---

## 📊 3. 실시간 모니터링 대시보드

### 3.1 메트릭 수집

```python
# backend/app/services/metrics_service.py

from prometheus_client import Counter, Histogram, Gauge
from typing import Dict

# Prometheus Metrics
ml_dispatch_total = Counter(
    'ml_dispatch_total',
    'Total ML dispatch requests',
    ['status', 'group']  # status: success/failure, group: control/treatment
)

ml_dispatch_score = Histogram(
    'ml_dispatch_score',
    'ML dispatch score distribution',
    buckets=[0.3, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

ml_dispatch_response_time = Histogram(
    'ml_dispatch_response_time_seconds',
    'ML dispatch response time',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

ml_dispatch_error_rate = Gauge(
    'ml_dispatch_error_rate',
    'ML dispatch error rate (last 5 min)'
)


class MetricsService:
    """메트릭 수집 및 집계 서비스"""
    
    @staticmethod
    def track_ml_dispatch(
        status: str,
        group: str,
        score: float,
        response_time: float
    ):
        """ML 배차 메트릭 기록"""
        ml_dispatch_total.labels(status=status, group=group).inc()
        
        if status == 'success':
            ml_dispatch_score.observe(score)
        
        ml_dispatch_response_time.observe(response_time)
    
    @staticmethod
    async def calculate_error_rate(
        db: Session,
        window_minutes: int = 5
    ) -> float:
        """최근 N분간 에러율 계산"""
        from datetime import datetime, timedelta
        
        start_time = datetime.now() - timedelta(minutes=window_minutes)
        
        total = (
            db.query(Dispatch)
            .filter(Dispatch.created_at >= start_time)
            .filter(Dispatch.assigned_by.like('%ml%'))
            .count()
        )
        
        errors = (
            db.query(Dispatch)
            .filter(Dispatch.created_at >= start_time)
            .filter(Dispatch.assigned_by.like('%ml%'))
            .filter(Dispatch.status == DispatchStatus.CANCELLED)
            .count()
        )
        
        error_rate = errors / total if total > 0 else 0.0
        ml_dispatch_error_rate.set(error_rate)
        
        return error_rate
```

### 3.2 대시보드 API

```python
@router.get("/monitoring/metrics")
async def get_monitoring_metrics(
    window_minutes: int = 60,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    실시간 모니터링 메트릭 조회
    
    Returns:
        {
            "success_rate": 0.97,
            "avg_score": 0.756,
            "avg_response_time": 1.23,
            "error_rate": 0.03,
            "total_dispatches": 1250,
            "timeseries": [...]
        }
    """
    from datetime import datetime, timedelta
    
    start_time = datetime.now() - timedelta(minutes=window_minutes)
    
    # ML 배차 조회
    ml_dispatches = (
        db.query(Dispatch)
        .filter(Dispatch.created_at >= start_time)
        .filter(Dispatch.assigned_by.like('%ml%'))
        .all()
    )
    
    if not ml_dispatches:
        return {
            "success_rate": 0.0,
            "avg_score": 0.0,
            "avg_response_time": 0.0,
            "error_rate": 0.0,
            "total_dispatches": 0
        }
    
    # 성공률
    success_count = sum(
        1 for d in ml_dispatches
        if d.status not in [DispatchStatus.CANCELLED, DispatchStatus.FAILED]
    )
    success_rate = success_count / len(ml_dispatches)
    
    # 평균 점수
    scores = [d.optimization_score for d in ml_dispatches if d.optimization_score]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    # 에러율
    error_rate = await MetricsService.calculate_error_rate(db, window_minutes)
    
    return {
        "success_rate": round(success_rate, 3),
        "avg_score": round(avg_score, 3),
        "error_rate": round(error_rate, 3),
        "total_dispatches": len(ml_dispatches),
        "window_minutes": window_minutes
    }
```

---

## 🔄 4. 점진적 롤아웃 전략

### Stage 1: 파일럿 (10% - Week 1-2)
```bash
# 10% 트래픽으로 시작
curl -X POST http://139.150.11.99:8000/api/ml-dispatch/ab-test/rollout \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"percentage": 10}'

# 모니터링
watch -n 10 'curl -s http://139.150.11.99:8000/api/ml-dispatch/monitoring/metrics | jq .'
```

**성공 기준:**
- Success Rate ≥ 95%
- Error Rate < 5%
- 사용자 컴플레인 없음

### Stage 2: 확대 (30% - Week 3-4)
```bash
# 30%로 증가
curl -X POST .../rollout -d '{"percentage": 30}'
```

**성공 기준:**
- Success Rate ≥ 97%
- Avg Score ≥ 0.70
- Response Time < 2s

### Stage 3: 전면 배포 (100% - Week 5-6)
```bash
# 100% 배포
curl -X POST .../rollout -d '{"percentage": 100}'
```

---

## 🚨 5. 자동 롤백 시스템

```python
# backend/app/services/auto_rollback_service.py

class AutoRollbackService:
    """자동 롤백 서비스"""
    
    def __init__(self, redis: Redis, db: Session):
        self.redis = redis
        self.db = db
        self.ab_service = ABTestService(redis)
    
    async def check_health(self) -> Dict[str, Any]:
        """시스템 헬스 체크"""
        metrics_service = MetricsService()
        
        # 메트릭 수집
        error_rate = await metrics_service.calculate_error_rate(self.db, 5)
        
        # 최근 평균 점수
        recent_dispatches = (
            self.db.query(Dispatch)
            .filter(Dispatch.assigned_by.like('%ml%'))
            .order_by(Dispatch.created_at.desc())
            .limit(50)
            .all()
        )
        
        scores = [d.optimization_score for d in recent_dispatches if d.optimization_score]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # 임계값 체크
        triggers = []
        
        if error_rate > 0.05:  # 5% 초과
            triggers.append({
                "type": "error_rate",
                "value": error_rate,
                "threshold": 0.05,
                "severity": "critical"
            })
        
        if avg_score < 0.60:  # 0.60 미만
            triggers.append({
                "type": "low_score",
                "value": avg_score,
                "threshold": 0.60,
                "severity": "warning"
            })
        
        return {
            "healthy": len([t for t in triggers if t['severity'] == 'critical']) == 0,
            "error_rate": error_rate,
            "avg_score": avg_score,
            "triggers": triggers
        }
    
    async def execute_rollback(self, reason: str):
        """롤백 실행"""
        logger.warning(f"Executing rollback: {reason}")
        
        # 0%로 롤백
        self.ab_service.set_rollout_percentage(0)
        
        # 알림 전송
        await self._send_alert(
            "🚨 ML Dispatch Auto Rollback",
            f"Reason: {reason}\nRollout percentage set to 0%"
        )
    
    async def _send_alert(self, title: str, message: str):
        """관리자 알림"""
        # Slack/Email/SMS 등으로 알림
        logger.critical(f"{title}: {message}")
```

---

## 📈 6. 성공 지표 (Success Metrics)

### 기술적 지표
| Metric | Target | Critical Threshold |
|--------|--------|--------------------|
| Success Rate | ≥ 97% | < 95% (Rollback) |
| Error Rate | < 3% | > 5% (Rollback) |
| Avg Score | ≥ 0.70 | < 0.60 (Alert) |
| Response Time | < 2s | > 5s (Alert) |

### 비즈니스 지표
| Metric | Target | Measurement |
|--------|--------|-------------|
| 사용자 만족도 | ≥ 4.0/5.0 | 설문조사 |
| 배차 효율 | +20% | 공차 거리 감소 |
| 작업 시간 | -30% | 배차 소요 시간 |

---

## 📚 다음 문서

다음으로 생성할 파일:
1. `frontend/src/components/MLRecommendationPanel.tsx` - UI 컴포넌트
2. `backend/app/services/ab_test_service.py` - A/B 테스트 서비스
3. `PHASE3_DEPLOYMENT_GUIDE.md` - 배포 가이드

---

**Phase 3 시작 준비 완료!** 🚀
