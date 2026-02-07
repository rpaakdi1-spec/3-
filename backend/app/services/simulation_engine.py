"""
Advanced Simulation Engine for Rule Testing and What-If Analysis
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from loguru import logger

from app.models.dispatch_rule import DispatchRule
from app.models.dispatches import Dispatch
from app.models.orders import Order
from app.services.rule_engine import RuleEngine


class SimulationEngine:
    """
    Advanced simulation engine for testing dispatch rules
    - Historical data replay
    - What-if scenario analysis
    - A/B testing
    - Performance comparison
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.rule_engine = RuleEngine(db)
        
    async def run_historical_simulation(
        self,
        start_date: datetime,
        end_date: datetime,
        rule_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Replay historical dispatches with current rules
        
        Args:
            start_date: Start date for historical data
            end_date: End date for historical data
            rule_ids: Optional list of specific rule IDs to test
            
        Returns:
            Simulation results with metrics
        """
        logger.info(f"Starting historical simulation from {start_date} to {end_date}")
        
        # Fetch historical dispatches
        dispatches = self.db.query(Dispatch).filter(
            Dispatch.created_at >= start_date,
            Dispatch.created_at <= end_date
        ).all()
        
        logger.info(f"Found {len(dispatches)} historical dispatches")
        
        results = {
            "total_dispatches": len(dispatches),
            "simulation_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "original_metrics": self._calculate_dispatch_metrics(dispatches),
            "simulated_metrics": {},
            "improvements": {},
            "dispatch_results": []
        }
        
        # Run simulation for each dispatch
        simulated_dispatches = []
        for dispatch in dispatches:
            context = self._build_dispatch_context(dispatch)
            
            # Execute rules in simulation mode
            if rule_ids:
                rule_results = []
                for rule_id in rule_ids:
                    rule = self.db.query(DispatchRule).filter_by(id=rule_id).first()
                    if rule:
                        result = self.rule_engine.execute_rule(rule, context, simulation=True)
                        rule_results.append(result)
            else:
                rule_results = self.rule_engine.execute_rules(context, simulation=True)
            
            # Apply simulated changes
            simulated_dispatch = self._apply_simulation_results(dispatch, rule_results)
            simulated_dispatches.append(simulated_dispatch)
            
            results["dispatch_results"].append({
                "original_dispatch_id": dispatch.id,
                "rules_applied": len([r for r in rule_results if r.get("matched")]),
                "changes": simulated_dispatch.get("changes", [])
            })
        
        # Calculate simulated metrics
        results["simulated_metrics"] = self._calculate_simulated_metrics(simulated_dispatches)
        
        # Calculate improvements
        results["improvements"] = self._calculate_improvements(
            results["original_metrics"],
            results["simulated_metrics"]
        )
        
        logger.info(f"Simulation complete. Improvements: {results['improvements']}")
        
        return results
        
    async def run_whatif_simulation(
        self,
        scenario: Dict[str, Any],
        sample_size: int = 100
    ) -> Dict[str, Any]:
        """
        Run what-if analysis with modified parameters
        
        Args:
            scenario: Dictionary with modified parameters
            sample_size: Number of recent dispatches to use
            
        Returns:
            Comparison of baseline vs scenario
        """
        logger.info(f"Running what-if simulation: {scenario.get('name', 'Unnamed')}")
        
        # Get recent dispatches as baseline
        dispatches = self.db.query(Dispatch).order_by(
            Dispatch.created_at.desc()
        ).limit(sample_size).all()
        
        results = {
            "scenario_name": scenario.get("name", "Unnamed Scenario"),
            "scenario_description": scenario.get("description", ""),
            "sample_size": len(dispatches),
            "baseline_metrics": {},
            "scenario_metrics": {},
            "comparison": {}
        }
        
        # Calculate baseline metrics
        baseline_dispatches = []
        for dispatch in dispatches:
            context = self._build_dispatch_context(dispatch)
            baseline_dispatches.append(dispatch)
        
        results["baseline_metrics"] = self._calculate_dispatch_metrics(baseline_dispatches)
        
        # Apply scenario modifications
        scenario_dispatches = []
        for dispatch in dispatches:
            context = self._build_dispatch_context(dispatch)
            
            # Apply scenario changes to context
            if "rule_modifications" in scenario:
                context.update(scenario["rule_modifications"])
            
            # Execute rules with modified context
            rule_results = self.rule_engine.execute_rules(context, simulation=True)
            
            # Apply results
            simulated = self._apply_simulation_results(dispatch, rule_results)
            scenario_dispatches.append(simulated)
        
        results["scenario_metrics"] = self._calculate_simulated_metrics(scenario_dispatches)
        
        # Compare scenarios
        results["comparison"] = self._calculate_improvements(
            results["baseline_metrics"],
            results["scenario_metrics"]
        )
        
        return results
        
    async def run_ab_test(
        self,
        rule_a_id: int,
        rule_b_id: int,
        test_duration_days: int = 7,
        traffic_split: float = 0.5
    ) -> Dict[str, Any]:
        """
        Run A/B test between two rules
        
        Args:
            rule_a_id: ID of rule A (control)
            rule_b_id: ID of rule B (treatment)
            test_duration_days: Duration of test in days
            traffic_split: Percentage of traffic for rule B (0.0-1.0)
            
        Returns:
            A/B test results with statistical significance
        """
        logger.info(f"Running A/B test: Rule {rule_a_id} vs Rule {rule_b_id}")
        
        rule_a = self.db.query(DispatchRule).filter_by(id=rule_a_id).first()
        rule_b = self.db.query(DispatchRule).filter_by(id=rule_b_id).first()
        
        if not rule_a or not rule_b:
            raise ValueError("Both rules must exist")
        
        # Get historical data for test period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=test_duration_days)
        
        dispatches = self.db.query(Dispatch).filter(
            Dispatch.created_at >= start_date,
            Dispatch.created_at <= end_date
        ).all()
        
        # Split traffic
        split_index = int(len(dispatches) * traffic_split)
        group_a_dispatches = dispatches[:split_index]
        group_b_dispatches = dispatches[split_index:]
        
        results = {
            "test_name": f"A/B Test: {rule_a.name} vs {rule_b.name}",
            "test_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "duration_days": test_duration_days
            },
            "traffic_split": traffic_split,
            "group_a": {
                "rule_id": rule_a_id,
                "rule_name": rule_a.name,
                "sample_size": len(group_a_dispatches),
                "metrics": {}
            },
            "group_b": {
                "rule_id": rule_b_id,
                "rule_name": rule_b.name,
                "sample_size": len(group_b_dispatches),
                "metrics": {}
            },
            "comparison": {},
            "winner": None
        }
        
        # Simulate group A with rule A
        group_a_results = []
        for dispatch in group_a_dispatches:
            context = self._build_dispatch_context(dispatch)
            result = self.rule_engine.execute_rule(rule_a, context, simulation=True)
            simulated = self._apply_simulation_results(dispatch, [result])
            group_a_results.append(simulated)
        
        results["group_a"]["metrics"] = self._calculate_simulated_metrics(group_a_results)
        
        # Simulate group B with rule B
        group_b_results = []
        for dispatch in group_b_dispatches:
            context = self._build_dispatch_context(dispatch)
            result = self.rule_engine.execute_rule(rule_b, context, simulation=True)
            simulated = self._apply_simulation_results(dispatch, [result])
            group_b_results.append(simulated)
        
        results["group_b"]["metrics"] = self._calculate_simulated_metrics(group_b_results)
        
        # Compare groups
        results["comparison"] = self._calculate_improvements(
            results["group_a"]["metrics"],
            results["group_b"]["metrics"]
        )
        
        # Determine winner (simplified - use more advanced statistics in production)
        if results["comparison"].get("distance_saved_km", 0) > 0:
            results["winner"] = "B"
        elif results["comparison"].get("distance_saved_km", 0) < 0:
            results["winner"] = "A"
        else:
            results["winner"] = "Tie"
        
        return results
        
    def _build_dispatch_context(self, dispatch: Dispatch) -> Dict[str, Any]:
        """Build context from dispatch for simulation"""
        # Fetch related data
        order = self.db.query(Order).filter_by(id=dispatch.order_id).first()
        
        context = {
            "dispatch": {
                "id": dispatch.id,
                "status": dispatch.status.value if hasattr(dispatch.status, 'value') else dispatch.status,
                "created_at": dispatch.created_at.isoformat() if dispatch.created_at else None,
                "driver_id": dispatch.driver_id,
                "vehicle_id": dispatch.vehicle_id
            },
            "order": {}
        }
        
        if order:
            context["order"] = {
                "id": order.id,
                "priority": order.priority if hasattr(order, 'priority') else "normal",
                "weight": order.weight if hasattr(order, 'weight') else 0,
                "volume": order.volume if hasattr(order, 'volume') else 0,
                "value": order.total_amount if hasattr(order, 'total_amount') else 0
            }
        
        return context
        
    def _apply_simulation_results(
        self,
        dispatch: Dispatch,
        rule_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply simulation results to create modified dispatch"""
        simulated = {
            "original_dispatch_id": dispatch.id,
            "changes": []
        }
        
        for result in rule_results:
            if result.get("matched"):
                for action in result.get("actions", []):
                    if action.get("type") == "assign_driver":
                        simulated["driver_id"] = action["params"].get("driver_id")
                        simulated["changes"].append("driver_changed")
                    elif action.get("type") == "assign_vehicle":
                        simulated["vehicle_id"] = action["params"].get("vehicle_id")
                        simulated["changes"].append("vehicle_changed")
        
        return simulated
        
    def _calculate_dispatch_metrics(self, dispatches: List[Dispatch]) -> Dict[str, Any]:
        """Calculate metrics from actual dispatches"""
        if not dispatches:
            return {}
        
        total_distance = sum(d.distance_km for d in dispatches if hasattr(d, 'distance_km') and d.distance_km)
        total_cost = sum(d.cost for d in dispatches if hasattr(d, 'cost') and d.cost)
        completed = len([d for d in dispatches if d.status == "completed"])
        
        return {
            "total_dispatches": len(dispatches),
            "completed_count": completed,
            "completion_rate": completed / len(dispatches) if dispatches else 0,
            "total_distance_km": total_distance,
            "avg_distance_km": total_distance / len(dispatches) if dispatches else 0,
            "total_cost": total_cost,
            "avg_cost": total_cost / len(dispatches) if dispatches else 0
        }
        
    def _calculate_simulated_metrics(self, simulated_dispatches: List[Dict]) -> Dict[str, Any]:
        """Calculate metrics from simulated dispatches"""
        if not simulated_dispatches:
            return {}
        
        changes_count = sum(len(d.get("changes", [])) for d in simulated_dispatches)
        
        return {
            "total_simulated": len(simulated_dispatches),
            "total_changes": changes_count,
            "change_rate": changes_count / len(simulated_dispatches) if simulated_dispatches else 0,
            # Add more simulated metrics here
        }
        
    def _calculate_improvements(
        self,
        baseline: Dict[str, Any],
        simulated: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate percentage improvements"""
        improvements = {}
        
        for key in baseline:
            if key in simulated and isinstance(baseline[key], (int, float)):
                baseline_val = baseline[key]
                simulated_val = simulated.get(key, baseline_val)
                
                if baseline_val != 0:
                    improvement_pct = ((simulated_val - baseline_val) / baseline_val) * 100
                    improvements[f"{key}_improvement_pct"] = round(improvement_pct, 2)
        
        return improvements
