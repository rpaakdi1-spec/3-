"""
ML-based Rule Suggestion Service

Analyzes historical dispatch data to suggest optimal dispatch rules automatically.
Phase 3: Auto-Learning from past performance data.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.dispatch import Dispatch, DispatchStatus, DispatchRoute
from app.models.order import Order, TemperatureZone
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.dispatch_rule import DispatchRule

logger = logging.getLogger(__name__)


@dataclass
class RuleSuggestion:
    """ML이 제안하는 배차 규칙"""
    rule_type: str  # assignment, constraint, optimization
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    confidence: float  # 신뢰도 (0-1)
    support: int  # 지지도 (발생 횟수)
    expected_improvement: Dict[str, float]  # 예상 개선 효과
    priority: int


class MLRuleSuggestionService:
    """ML 기반 규칙 제안 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.min_support = 5  # 최소 발생 횟수
        self.min_confidence = 0.7  # 최소 신뢰도
    
    async def analyze_and_suggest_rules(
        self,
        days_back: int = 30,
        limit: int = 10
    ) -> List[RuleSuggestion]:
        """
        과거 배차 데이터를 분석하여 규칙 제안
        
        Args:
            days_back: 분석할 과거 일수
            limit: 최대 제안 규칙 수
            
        Returns:
            제안 규칙 리스트
        """
        logger.info(f"Starting rule suggestion analysis for past {days_back} days...")
        
        # 1. 온도대별 차량 할당 패턴 분석
        temp_rules = await self._analyze_temperature_patterns(days_back)
        
        # 2. 거리 기반 차량 선택 패턴 분석
        distance_rules = await self._analyze_distance_patterns(days_back)
        
        # 3. 시간대별 배차 패턴 분석
        time_rules = await self._analyze_time_patterns(days_back)
        
        # 4. 적재율 최적화 패턴 분석
        capacity_rules = await self._analyze_capacity_patterns(days_back)
        
        # 5. 고객별 선호 차량 패턴 분석
        client_rules = await self._analyze_client_preferences(days_back)
        
        # 모든 제안 통합
        all_suggestions = []
        all_suggestions.extend(temp_rules)
        all_suggestions.extend(distance_rules)
        all_suggestions.extend(time_rules)
        all_suggestions.extend(capacity_rules)
        all_suggestions.extend(client_rules)
        
        # 신뢰도와 지지도로 정렬
        all_suggestions.sort(
            key=lambda x: (x.confidence * x.support, x.confidence),
            reverse=True
        )
        
        logger.info(f"Generated {len(all_suggestions)} rule suggestions")
        return all_suggestions[:limit]
    
    async def _analyze_temperature_patterns(self, days_back: int) -> List[RuleSuggestion]:
        """온도대별 차량 할당 패턴 분석"""
        logger.info("Analyzing temperature zone patterns...")
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # 온도대별 성공적인 배차 데이터 수집
        query = self.db.query(
            Order.temperature_zone,
            Vehicle.vehicle_type,
            func.count(Dispatch.id).label('count'),
            func.avg(DispatchRoute.actual_distance_km).label('avg_distance'),
            func.avg(
                func.extract('epoch', Dispatch.completed_at - Dispatch.actual_start_time) / 3600
            ).label('avg_hours')
        ).join(
            DispatchRoute, DispatchRoute.order_id == Order.id
        ).join(
            Dispatch, Dispatch.id == DispatchRoute.dispatch_id
        ).join(
            Vehicle, Vehicle.id == Dispatch.vehicle_id
        ).filter(
            and_(
                Dispatch.status == DispatchStatus.COMPLETED,
                Dispatch.created_at >= cutoff_date
            )
        ).group_by(
            Order.temperature_zone,
            Vehicle.vehicle_type
        ).all()
        
        suggestions = []
        temp_vehicle_map = defaultdict(lambda: {'count': 0, 'total': 0})
        
        for temp_zone, vehicle_type, count, avg_dist, avg_hours in query:
            if temp_zone and vehicle_type:
                temp_vehicle_map[temp_zone]['count'] += count
                temp_vehicle_map[temp_zone]['total'] += count
                
                # 가장 많이 사용된 차량 타입 추적
                if count >= self.min_support:
                    suggestions.append(RuleSuggestion(
                        rule_type="assignment",
                        name=f"{temp_zone.value} 주문 → {vehicle_type.value} 차량 우선 배정",
                        description=f"{temp_zone.value} 온도대 주문은 {vehicle_type.value} 차량에 우선 배정하는 규칙입니다. 과거 {count}건의 성공 사례 기반.",
                        conditions={
                            "order.temperature_zone": temp_zone.value
                        },
                        actions={
                            "prefer_vehicle_type": vehicle_type.value,
                            "priority_weight": 1.5
                        },
                        confidence=min(count / temp_vehicle_map[temp_zone]['total'], 1.0) if temp_vehicle_map[temp_zone]['total'] > 0 else 0.0,
                        support=count,
                        expected_improvement={
                            "avg_distance_km": round(avg_dist or 0, 2),
                            "avg_time_hours": round(avg_hours or 0, 2)
                        },
                        priority=90
                    ))
        
        logger.info(f"Found {len(suggestions)} temperature-based rule suggestions")
        return suggestions
    
    async def _analyze_distance_patterns(self, days_back: int) -> List[RuleSuggestion]:
        """거리 기반 차량 선택 패턴 분석"""
        logger.info("Analyzing distance patterns...")
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # 거리별 차량 크기 분석
        query = self.db.query(
            func.floor(DispatchRoute.planned_distance_km / 50).label('distance_bucket'),
            Vehicle.max_weight_kg,
            func.count(Dispatch.id).label('count'),
            func.avg(DispatchRoute.actual_distance_km).label('avg_distance')
        ).join(
            DispatchRoute, DispatchRoute.dispatch_id == Dispatch.id
        ).join(
            Vehicle, Vehicle.id == Dispatch.vehicle_id
        ).filter(
            and_(
                Dispatch.status == DispatchStatus.COMPLETED,
                Dispatch.created_at >= cutoff_date,
                DispatchRoute.planned_distance_km.isnot(None)
            )
        ).group_by(
            'distance_bucket',
            Vehicle.max_weight_kg
        ).having(
            func.count(Dispatch.id) >= self.min_support
        ).all()
        
        suggestions = []
        
        for distance_bucket, max_weight, count, avg_dist in query:
            if distance_bucket is not None and max_weight:
                distance_km = distance_bucket * 50
                
                suggestions.append(RuleSuggestion(
                    rule_type="constraint",
                    name=f"{distance_km}km 이상 배송 시 {max_weight}kg 차량 권장",
                    description=f"장거리 배송({distance_km}km 이상)은 {max_weight}kg 차량이 적합합니다. 과거 {count}건의 성공 사례 기반.",
                    conditions={
                        "order.estimated_distance_km": {"$gte": distance_km}
                    },
                    actions={
                        "prefer_vehicle_weight": max_weight,
                        "min_vehicle_weight": max(max_weight * 0.8, 1000)
                    },
                    confidence=0.75,
                    support=count,
                    expected_improvement={
                        "avg_distance_km": round(avg_dist or 0, 2)
                    },
                    priority=70
                ))
        
        logger.info(f"Found {len(suggestions)} distance-based rule suggestions")
        return suggestions[:5]  # 상위 5개만
    
    async def _analyze_time_patterns(self, days_back: int) -> List[RuleSuggestion]:
        """시간대별 배차 패턴 분석"""
        logger.info("Analyzing time patterns...")
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # 시간대별 배차 성공률 분석
        query = self.db.query(
            func.extract('hour', Dispatch.planned_start_time).label('hour'),
            func.count(Dispatch.id).label('total'),
            func.sum(
                func.case(
                    (Dispatch.status == DispatchStatus.COMPLETED, 1),
                    else_=0
                )
            ).label('completed')
        ).filter(
            Dispatch.created_at >= cutoff_date
        ).group_by(
            'hour'
        ).having(
            func.count(Dispatch.id) >= self.min_support
        ).all()
        
        suggestions = []
        
        for hour, total, completed in query:
            if hour is not None and total > 0:
                success_rate = (completed or 0) / total
                
                if success_rate >= 0.9:  # 90% 이상 성공률
                    suggestions.append(RuleSuggestion(
                        rule_type="optimization",
                        name=f"{int(hour)}시대 배차 우선 처리",
                        description=f"{int(hour)}시대 배차는 {success_rate*100:.1f}% 성공률을 보입니다. 우선 처리를 권장합니다.",
                        conditions={
                            "dispatch.planned_hour": int(hour)
                        },
                        actions={
                            "priority_boost": 1.2,
                            "recommend_slot": True
                        },
                        confidence=success_rate,
                        support=total,
                        expected_improvement={
                            "success_rate": round(success_rate * 100, 1)
                        },
                        priority=60
                    ))
        
        logger.info(f"Found {len(suggestions)} time-based rule suggestions")
        return suggestions[:3]  # 상위 3개만
    
    async def _analyze_capacity_patterns(self, days_back: int) -> List[RuleSuggestion]:
        """적재율 최적화 패턴 분석"""
        logger.info("Analyzing capacity patterns...")
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # 적재율 80% 이상인 성공 배차 분석
        query = self.db.query(
            Vehicle.max_pallets,
            func.avg(Order.pallet_count).label('avg_pallets'),
            func.count(Dispatch.id).label('count')
        ).join(
            DispatchRoute, DispatchRoute.dispatch_id == Dispatch.id
        ).join(
            Order, Order.id == DispatchRoute.order_id
        ).join(
            Vehicle, Vehicle.id == Dispatch.vehicle_id
        ).filter(
            and_(
                Dispatch.status == DispatchStatus.COMPLETED,
                Dispatch.created_at >= cutoff_date,
                Vehicle.max_pallets.isnot(None)
            )
        ).group_by(
            Vehicle.max_pallets
        ).having(
            func.count(Dispatch.id) >= self.min_support
        ).all()
        
        suggestions = []
        
        for max_pallets, avg_pallets, count in query:
            if max_pallets and avg_pallets:
                utilization_rate = avg_pallets / max_pallets
                
                if 0.7 <= utilization_rate <= 0.95:  # 최적 적재율
                    suggestions.append(RuleSuggestion(
                        rule_type="optimization",
                        name=f"{int(max_pallets)}팔레트 차량 적재율 최적화",
                        description=f"{int(max_pallets)}팔레트 차량은 평균 {avg_pallets:.1f}팔레트({utilization_rate*100:.1f}% 적재율)로 운영됩니다.",
                        conditions={
                            "vehicle.max_pallets": int(max_pallets)
                        },
                        actions={
                            "target_utilization_min": 0.7,
                            "target_utilization_max": 0.95,
                            "consolidate_orders": True
                        },
                        confidence=0.8,
                        support=count,
                        expected_improvement={
                            "utilization_rate": round(utilization_rate * 100, 1)
                        },
                        priority=75
                    ))
        
        logger.info(f"Found {len(suggestions)} capacity-based rule suggestions")
        return suggestions[:3]
    
    async def _analyze_client_preferences(self, days_back: int) -> List[RuleSuggestion]:
        """고객별 선호 차량 패턴 분석"""
        logger.info("Analyzing client preferences...")
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # 고객별 자주 사용하는 차량 분석
        query = self.db.query(
            Order.pickup_client_id,
            Vehicle.vehicle_code,
            func.count(Dispatch.id).label('count')
        ).join(
            DispatchRoute, DispatchRoute.order_id == Order.id
        ).join(
            Dispatch, Dispatch.id == DispatchRoute.dispatch_id
        ).join(
            Vehicle, Vehicle.id == Dispatch.vehicle_id
        ).filter(
            and_(
                Dispatch.status == DispatchStatus.COMPLETED,
                Dispatch.created_at >= cutoff_date,
                Order.pickup_client_id.isnot(None)
            )
        ).group_by(
            Order.pickup_client_id,
            Vehicle.vehicle_code
        ).having(
            func.count(Dispatch.id) >= self.min_support
        ).all()
        
        suggestions = []
        client_vehicle_count = {}
        
        for client_id, vehicle_code, count in query:
            if client_id not in client_vehicle_count:
                client_vehicle_count[client_id] = []
            client_vehicle_count[client_id].append((vehicle_code, count))
        
        # 각 고객별로 가장 많이 사용한 차량 찾기
        for client_id, vehicle_list in client_vehicle_count.items():
            vehicle_list.sort(key=lambda x: x[1], reverse=True)
            top_vehicle, top_count = vehicle_list[0]
            total_count = sum(v[1] for v in vehicle_list)
            
            if top_count / total_count >= 0.6:  # 60% 이상 사용
                suggestions.append(RuleSuggestion(
                    rule_type="assignment",
                    name=f"고객 {client_id} → 차량 {top_vehicle} 우선 배정",
                    description=f"고객 {client_id}는 차량 {top_vehicle}를 {top_count}회({top_count/total_count*100:.1f}%) 사용했습니다.",
                    conditions={
                        "order.pickup_client_id": client_id
                    },
                    actions={
                        "prefer_vehicle_code": top_vehicle,
                        "priority_weight": 1.3
                    },
                    confidence=top_count / total_count,
                    support=top_count,
                    expected_improvement={},
                    priority=50
                ))
        
        logger.info(f"Found {len(suggestions)} client preference rule suggestions")
        return suggestions[:5]  # 상위 5개만
    
    async def create_rules_from_suggestions(
        self,
        suggestions: List[RuleSuggestion],
        auto_activate: bool = False
    ) -> List[DispatchRule]:
        """
        제안된 규칙들을 실제 DispatchRule로 생성
        
        Args:
            suggestions: 제안 규칙 리스트
            auto_activate: 자동 활성화 여부
            
        Returns:
            생성된 DispatchRule 리스트
        """
        logger.info(f"Creating {len(suggestions)} rules from suggestions...")
        
        created_rules = []
        
        for suggestion in suggestions:
            # 중복 규칙 체크
            existing = self.db.query(DispatchRule).filter(
                DispatchRule.name == suggestion.name
            ).first()
            
            if existing:
                logger.warning(f"Rule '{suggestion.name}' already exists, skipping...")
                continue
            
            # 새 규칙 생성
            rule = DispatchRule(
                name=suggestion.name,
                description=suggestion.description,
                rule_type=suggestion.rule_type,
                priority=suggestion.priority,
                is_active=auto_activate,
                conditions=suggestion.conditions,
                actions=suggestion.actions,
                version=1
            )
            
            self.db.add(rule)
            created_rules.append(rule)
        
        self.db.commit()
        
        logger.info(f"Created {len(created_rules)} new rules")
        return created_rules
    
    async def get_rule_performance_report(self, rule_id: int) -> Dict[str, Any]:
        """
        특정 규칙의 성능 리포트 생성
        
        Args:
            rule_id: 규칙 ID
            
        Returns:
            성능 리포트 딕셔너리
        """
        from app.models.dispatch_rule import RuleExecutionLog
        
        rule = self.db.query(DispatchRule).filter(DispatchRule.id == rule_id).first()
        if not rule:
            return {"error": "Rule not found"}
        
        # 실행 로그 통계
        logs = self.db.query(RuleExecutionLog).filter(
            RuleExecutionLog.rule_id == rule_id
        ).all()
        
        total_executions = len(logs)
        successful_executions = sum(1 for log in logs if log.success)
        
        total_distance_saved = sum(log.distance_saved_km or 0 for log in logs)
        total_cost_saved = sum(log.cost_saved or 0 for log in logs)
        total_time_saved = sum(log.time_saved_minutes or 0 for log in logs)
        
        avg_execution_time = (
            sum(log.execution_time_ms or 0 for log in logs) / total_executions
        ) if total_executions > 0 else 0
        
        return {
            "rule_id": rule_id,
            "rule_name": rule.name,
            "rule_type": rule.rule_type,
            "priority": rule.priority,
            "is_active": rule.is_active,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": (successful_executions / total_executions * 100) if total_executions > 0 else 0,
            "avg_execution_time_ms": round(avg_execution_time, 2),
            "total_distance_saved_km": round(total_distance_saved, 2),
            "total_cost_saved": round(total_cost_saved, 2),
            "total_time_saved_minutes": round(total_time_saved, 2),
            "created_at": rule.created_at.isoformat(),
            "updated_at": rule.updated_at.isoformat()
        }
