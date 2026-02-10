"""
Simulation Engine for Rule Testing
규칙 시뮬레이션 실행 엔진
"""
import time
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.condition_parser import ConditionParser, validate_conditions
from app.models.simulation import RuleSimulation
from app.models.dispatch_rule import DispatchRule


class SimulationEngine:
    """시뮬레이션 엔진"""
    
    def __init__(self, db: Session):
        self.db = db
        self.parser = ConditionParser()
    
    async def run_simulation(
        self,
        simulation_id: int,
        rule_config: Dict[str, Any],
        scenario_data: Dict[str, Any],
        iterations: int = 1,
        randomize: bool = False
    ) -> Dict[str, Any]:
        """
        시뮬레이션 실행
        
        Args:
            simulation_id: 시뮬레이션 ID
            rule_config: 규칙 설정
            scenario_data: 시나리오 데이터
            iterations: 반복 횟수
            randomize: 데이터 랜덤화 여부
            
        Returns:
            실행 결과
        """
        
        # 시뮬레이션 조회
        simulation = self.db.query(RuleSimulation).filter(
            RuleSimulation.id == simulation_id
        ).first()
        
        if not simulation:
            raise ValueError(f"Simulation {simulation_id} not found")
        
        # 상태 업데이트
        simulation.status = "running"
        simulation.started_at = datetime.utcnow()
        self.db.commit()
        
        try:
            # 규칙 조건 검증
            conditions = rule_config.get("conditions", {})
            validation_errors = validate_conditions(conditions)
            
            if validation_errors:
                raise ValueError(f"Invalid conditions: {', '.join(validation_errors)}")
            
            # 시뮬레이션 실행
            results = []
            response_times = []
            successful_matches = 0
            failed_matches = 0
            
            for iteration in range(iterations):
                # 시나리오 데이터 준비
                test_data = self._prepare_scenario_data(scenario_data, randomize, iteration)
                
                # 각 주문에 대해 매칭 시도
                orders = test_data.get("orders", [])
                drivers = test_data.get("drivers", [])
                
                for order in orders:
                    start_time = time.time()
                    
                    # 규칙 적용하여 최적 기사 찾기
                    matched_driver = self._find_best_match(
                        order, 
                        drivers, 
                        conditions,
                        rule_config.get("actions", {})
                    )
                    
                    end_time = time.time()
                    response_time_ms = (end_time - start_time) * 1000
                    response_times.append(response_time_ms)
                    
                    # 결과 기록
                    if matched_driver:
                        successful_matches += 1
                        results.append({
                            "iteration": iteration + 1,
                            "order_id": order.get("id"),
                            "matched_driver_id": matched_driver.get("id"),
                            "success": True,
                            "response_time_ms": response_time_ms,
                            "distance_km": order.get("distance_km"),
                            "estimated_cost": self._calculate_cost(order, matched_driver)
                        })
                    else:
                        failed_matches += 1
                        results.append({
                            "iteration": iteration + 1,
                            "order_id": order.get("id"),
                            "success": False,
                            "response_time_ms": response_time_ms,
                            "reason": "No matching driver found"
                        })
            
            # 통계 계산
            total_matches = len(results)
            match_rate = (successful_matches / total_matches * 100) if total_matches > 0 else 0
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            
            estimated_distance = sum(r.get("distance_km", 0) for r in results if r.get("success"))
            estimated_cost = sum(r.get("estimated_cost", 0) for r in results if r.get("success"))
            estimated_time = estimated_distance / 40 * 60 if estimated_distance > 0 else 0  # 평균 40km/h 가정
            
            # 결과 업데이트
            simulation.status = "completed"
            simulation.completed_at = datetime.utcnow()
            simulation.duration_seconds = (simulation.completed_at - simulation.started_at).total_seconds()
            
            simulation.total_matches = total_matches
            simulation.successful_matches = successful_matches
            simulation.failed_matches = failed_matches
            simulation.match_rate = match_rate
            
            simulation.avg_response_time_ms = avg_response_time
            simulation.min_response_time_ms = min_response_time
            simulation.max_response_time_ms = max_response_time
            
            simulation.estimated_cost = estimated_cost
            simulation.estimated_distance_km = estimated_distance
            simulation.estimated_time_minutes = estimated_time
            
            simulation.results = results
            
            self.db.commit()
            
            return {
                "simulation_id": simulation_id,
                "status": "completed",
                "statistics": {
                    "total_matches": total_matches,
                    "successful_matches": successful_matches,
                    "failed_matches": failed_matches,
                    "match_rate": round(match_rate, 2),
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "min_response_time_ms": round(min_response_time, 2),
                    "max_response_time_ms": round(max_response_time, 2),
                    "estimated_cost": round(estimated_cost, 2),
                    "estimated_distance_km": round(estimated_distance, 2),
                    "estimated_time_minutes": round(estimated_time, 2)
                },
                "results": results
            }
            
        except Exception as e:
            # 오류 처리
            simulation.status = "failed"
            simulation.completed_at = datetime.utcnow()
            simulation.errors = [{"error": str(e), "timestamp": datetime.utcnow().isoformat()}]
            self.db.commit()
            
            raise
    
    def _prepare_scenario_data(
        self, 
        scenario_data: Dict[str, Any], 
        randomize: bool, 
        iteration: int
    ) -> Dict[str, Any]:
        """시나리오 데이터 준비 (랜덤화 옵션)"""
        
        if not randomize:
            return scenario_data
        
        # 랜덤 시드 설정 (재현 가능성)
        random.seed(iteration)
        
        # 데이터 복사 및 랜덤화
        test_data = scenario_data.copy()
        
        # 주문 데이터 랜덤화
        if "orders" in test_data:
            orders = []
            for order in test_data["orders"]:
                randomized_order = order.copy()
                # 거리 ±20% 랜덤
                if "distance_km" in randomized_order:
                    base_distance = randomized_order["distance_km"]
                    randomized_order["distance_km"] = base_distance * random.uniform(0.8, 1.2)
                orders.append(randomized_order)
            test_data["orders"] = orders
        
        # 기사 데이터 랜덤화
        if "drivers" in test_data:
            drivers = []
            for driver in test_data["drivers"]:
                randomized_driver = driver.copy()
                # 평점 ±0.3 랜덤
                if "rating" in randomized_driver:
                    base_rating = randomized_driver["rating"]
                    randomized_driver["rating"] = max(1.0, min(5.0, base_rating + random.uniform(-0.3, 0.3)))
                drivers.append(randomized_driver)
            test_data["drivers"] = drivers
        
        return test_data
    
    def _find_best_match(
        self,
        order: Dict[str, Any],
        drivers: List[Dict[str, Any]],
        conditions: Dict[str, Any],
        actions: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """최적 기사 찾기"""
        
        matched_drivers = []
        
        for driver in drivers:
            # 컨텍스트 구성
            context = {
                **order,
                **driver,
                "order": order,
                "driver": driver
            }
            
            # 조건 평가
            if self.parser.evaluate(conditions, context):
                matched_drivers.append(driver)
        
        if not matched_drivers:
            return None
        
        # 우선순위에 따라 정렬 (평점 높은 순)
        matched_drivers.sort(
            key=lambda d: d.get("rating", 0), 
            reverse=True
        )
        
        return matched_drivers[0]
    
    def _calculate_cost(self, order: Dict[str, Any], driver: Dict[str, Any]) -> float:
        """비용 계산 (간단한 모델)"""
        base_cost = 10000  # 기본 비용
        distance_cost = order.get("distance_km", 0) * 1500  # km당 1500원
        priority_cost = 5000 if order.get("priority") == "high" else 0
        
        return base_cost + distance_cost + priority_cost


async def compare_simulations(
    db: Session,
    simulation_a_id: int,
    simulation_b_id: int
) -> Dict[str, Any]:
    """
    두 시뮬레이션 결과 비교
    
    Returns:
        비교 결과 및 추천
    """
    
    sim_a = db.query(RuleSimulation).filter(RuleSimulation.id == simulation_a_id).first()
    sim_b = db.query(RuleSimulation).filter(RuleSimulation.id == simulation_b_id).first()
    
    if not sim_a or not sim_b:
        raise ValueError("One or both simulations not found")
    
    # 지표 비교
    metrics = {
        "match_rate": {
            "a": sim_a.match_rate or 0,
            "b": sim_b.match_rate or 0,
            "winner": "A" if (sim_a.match_rate or 0) > (sim_b.match_rate or 0) else "B"
        },
        "avg_response_time_ms": {
            "a": sim_a.avg_response_time_ms or 0,
            "b": sim_b.avg_response_time_ms or 0,
            "winner": "A" if (sim_a.avg_response_time_ms or float('inf')) < (sim_b.avg_response_time_ms or float('inf')) else "B"
        },
        "estimated_cost": {
            "a": sim_a.estimated_cost or 0,
            "b": sim_b.estimated_cost or 0,
            "winner": "A" if (sim_a.estimated_cost or float('inf')) < (sim_b.estimated_cost or float('inf')) else "B"
        }
    }
    
    # 전체 승자 결정
    a_wins = sum(1 for m in metrics.values() if m["winner"] == "A")
    b_wins = sum(1 for m in metrics.values() if m["winner"] == "B")
    
    overall_winner = "A" if a_wins > b_wins else ("B" if b_wins > a_wins else "tie")
    
    # AI 추천 생성
    recommendation = _generate_recommendation(sim_a, sim_b, metrics, overall_winner)
    
    return {
        "simulation_a": {
            "id": sim_a.id,
            "name": sim_a.name,
            "match_rate": sim_a.match_rate,
            "avg_response_time_ms": sim_a.avg_response_time_ms,
            "estimated_cost": sim_a.estimated_cost
        },
        "simulation_b": {
            "id": sim_b.id,
            "name": sim_b.name,
            "match_rate": sim_b.match_rate,
            "avg_response_time_ms": sim_b.avg_response_time_ms,
            "estimated_cost": sim_b.estimated_cost
        },
        "metrics": metrics,
        "overall_winner": overall_winner,
        "recommendation": recommendation,
        "confidence_score": 0.85 if overall_winner != "tie" else 0.5
    }


def _generate_recommendation(
    sim_a: RuleSimulation,
    sim_b: RuleSimulation,
    metrics: Dict,
    winner: str
) -> str:
    """AI 추천 생성"""
    
    if winner == "tie":
        return "두 규칙의 성능이 비슷합니다. 더 많은 시나리오로 테스트해보세요."
    
    winner_sim = sim_a if winner == "A" else sim_b
    loser_sim = sim_b if winner == "A" else sim_a
    
    recommendation = f"규칙 {winner} ({winner_sim.name})를 추천합니다.\n\n"
    
    # 장점 나열
    advantages = []
    if metrics["match_rate"]["winner"] == winner:
        diff = abs(metrics["match_rate"]["a"] - metrics["match_rate"]["b"])
        advantages.append(f"매칭 성공률이 {diff:.1f}% 더 높습니다")
    
    if metrics["avg_response_time_ms"]["winner"] == winner:
        diff = abs(metrics["avg_response_time_ms"]["a"] - metrics["avg_response_time_ms"]["b"])
        advantages.append(f"응답 시간이 {diff:.1f}ms 더 빠릅니다")
    
    if metrics["estimated_cost"]["winner"] == winner:
        diff = abs(metrics["estimated_cost"]["a"] - metrics["estimated_cost"]["b"])
        advantages.append(f"예상 비용이 {diff:,.0f}원 더 저렴합니다")
    
    recommendation += "장점:\n" + "\n".join(f"• {adv}" for adv in advantages)
    
    return recommendation
