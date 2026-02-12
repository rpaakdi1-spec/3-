"""
Unit tests for Rule Engine Core
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from app.services.rule_engine import RuleEngine
from app.models.dispatch_rule import DispatchRule


class TestRuleEngine:
    """Test cases for RuleEngine"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.db = Mock()
        self.engine = RuleEngine(self.db)
        
    def test_execute_single_rule(self):
        """Test executing a single rule"""
        rule = DispatchRule(
            id=1,
            name="Test Rule",
            rule_type="assignment",
            priority=1,
            is_active=True,
            conditions={
                "field": "order.priority",
                "operator": "eq",
                "value": "urgent"
            },
            actions={
                "type": "assign_driver",
                "params": {"driver_id": 123}
            }
        )
        
        context = {
            "order": {"priority": "urgent", "id": 1},
            "dispatch": {"id": 100}
        }
        
        result = self.engine.execute_rule(rule, context, simulation=True)
        
        assert result["matched"] is True
        assert result["rule_id"] == 1
        assert result["execution_time_ms"] > 0
        
    def test_execute_rules_by_priority(self):
        """Test executing multiple rules with priorities"""
        rules = [
            DispatchRule(
                id=1,
                name="High Priority Rule",
                rule_type="assignment",
                priority=1,
                is_active=True,
                conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
                actions={"type": "action1"}
            ),
            DispatchRule(
                id=2,
                name="Low Priority Rule",
                rule_type="assignment",
                priority=10,
                is_active=True,
                conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
                actions={"type": "action2"}
            ),
            DispatchRule(
                id=3,
                name="Medium Priority Rule",
                rule_type="assignment",
                priority=5,
                is_active=True,
                conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
                actions={"type": "action3"}
            )
        ]
        
        self.db.query.return_value.filter.return_value.order_by.return_value.all.return_value = rules
        
        context = {
            "order": {"priority": "urgent", "id": 1},
            "dispatch": {"id": 100}
        }
        
        results = self.engine.execute_rules(context, simulation=True)
        
        # Should execute in priority order: 1, 5, 10
        assert len(results) == 3
        assert results[0]["rule_id"] == 1  # Priority 1
        assert results[1]["rule_id"] == 3  # Priority 5
        assert results[2]["rule_id"] == 2  # Priority 10
        
    def test_execute_with_stop_on_match(self):
        """Test stopping execution after first match"""
        rules = [
            DispatchRule(
                id=1,
                name="First Rule",
                priority=1,
                is_active=True,
                conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
                actions={"type": "action1"}
            ),
            DispatchRule(
                id=2,
                name="Second Rule",
                priority=2,
                is_active=True,
                conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
                actions={"type": "action2"}
            )
        ]
        
        self.db.query.return_value.filter.return_value.order_by.return_value.all.return_value = rules
        
        context = {
            "order": {"priority": "urgent", "id": 1},
            "dispatch": {"id": 100}
        }
        
        results = self.engine.execute_rules(context, stop_on_first_match=True, simulation=True)
        
        # Should only execute first matching rule
        assert len(results) == 1
        assert results[0]["rule_id"] == 1
        
    def test_execute_skip_inactive_rules(self):
        """Test skipping inactive rules"""
        rules = [
            DispatchRule(
                id=1,
                name="Active Rule",
                priority=1,
                is_active=True,
                conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
                actions={"type": "action1"}
            ),
            DispatchRule(
                id=2,
                name="Inactive Rule",
                priority=2,
                is_active=False,
                conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
                actions={"type": "action2"}
            )
        ]
        
        self.db.query.return_value.filter.return_value.order_by.return_value.all.return_value = rules
        
        context = {
            "order": {"priority": "urgent", "id": 1},
            "dispatch": {"id": 100}
        }
        
        results = self.engine.execute_rules(context, simulation=True)
        
        # Should only execute active rule
        assert len(results) == 1
        assert results[0]["rule_id"] == 1
        
    def test_simulation_mode(self):
        """Test simulation mode doesn't save to database"""
        rule = DispatchRule(
            id=1,
            name="Test Rule",
            priority=1,
            is_active=True,
            conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
            actions={"type": "assign_driver"}
        )
        
        context = {
            "order": {"priority": "urgent", "id": 1},
            "dispatch": {"id": 100}
        }
        
        # Simulation mode
        result = self.engine.execute_rule(rule, context, simulation=True)
        
        # Database should not be called
        self.db.add.assert_not_called()
        self.db.commit.assert_not_called()
        
    def test_production_mode_logs(self):
        """Test production mode saves logs"""
        rule = DispatchRule(
            id=1,
            name="Test Rule",
            priority=1,
            is_active=True,
            conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
            actions={"type": "assign_driver"}
        )
        
        context = {
            "order": {"priority": "urgent", "id": 1},
            "dispatch": {"id": 100}
        }
        
        # Production mode
        result = self.engine.execute_rule(rule, context, simulation=False)
        
        # Database should be called to save log
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        
    def test_execute_with_rule_type_filter(self):
        """Test filtering rules by type"""
        rules = [
            DispatchRule(
                id=1,
                name="Assignment Rule",
                rule_type="assignment",
                priority=1,
                is_active=True,
                conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
                actions={"type": "assign"}
            ),
            DispatchRule(
                id=2,
                name="Optimization Rule",
                rule_type="optimization",
                priority=2,
                is_active=True,
                conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
                actions={"type": "optimize"}
            )
        ]
        
        self.db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [rules[0]]
        
        context = {
            "order": {"priority": "urgent", "id": 1},
            "dispatch": {"id": 100}
        }
        
        results = self.engine.execute_rules(
            context, 
            rule_type="assignment", 
            simulation=True
        )
        
        # Should only execute assignment rules
        assert len(results) == 1
        assert results[0]["rule_id"] == 1
        
    def test_error_handling(self):
        """Test error handling during rule execution"""
        rule = DispatchRule(
            id=1,
            name="Error Rule",
            priority=1,
            is_active=True,
            conditions={"field": "invalid", "operator": "invalid_op", "value": "test"},
            actions={"type": "test"}
        )
        
        context = {
            "order": {"priority": "urgent", "id": 1}
        }
        
        result = self.engine.execute_rule(rule, context, simulation=True)
        
        # Should return error result
        assert result["success"] is False
        assert "error" in result
        
    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        rule = DispatchRule(
            id=1,
            name="Test Rule",
            priority=1,
            is_active=True,
            conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
            actions={"type": "assign_driver"}
        )
        
        context = {
            "order": {"priority": "urgent", "id": 1},
            "dispatch": {"id": 100}
        }
        
        result = self.engine.execute_rule(rule, context, simulation=True)
        
        # Should include performance metrics
        assert "execution_time_ms" in result
        assert result["execution_time_ms"] > 0
        assert isinstance(result["execution_time_ms"], (int, float))
        
    def test_context_enrichment(self):
        """Test context enrichment with additional data"""
        rule = DispatchRule(
            id=1,
            name="Test Rule",
            priority=1,
            is_active=True,
            conditions={"field": "order.priority", "operator": "eq", "value": "urgent"},
            actions={"type": "assign_driver"}
        )
        
        context = {
            "order": {"priority": "urgent", "id": 1}
        }
        
        # Engine should enrich context with current time/day
        result = self.engine.execute_rule(rule, context, simulation=True)
        
        assert result["success"] is True
