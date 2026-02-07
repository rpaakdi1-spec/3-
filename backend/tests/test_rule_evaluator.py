"""
Unit tests for Rule Evaluator
"""
import pytest
from datetime import datetime, time
from app.services.rule_evaluator import RuleEvaluator
from app.models.dispatch_rule import DispatchRule


class TestRuleEvaluator:
    """Test cases for RuleEvaluator"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.evaluator = RuleEvaluator()
        
    def test_evaluate_simple_rule(self):
        """Test evaluating a simple rule"""
        rule = DispatchRule(
            id=1,
            name="Urgent Order Rule",
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
            "available_drivers": [{"id": 123, "name": "Driver 1"}]
        }
        
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is True
        assert result["actions"][0]["type"] == "assign_driver"
        
    def test_evaluate_rule_not_matched(self):
        """Test rule that doesn't match"""
        rule = DispatchRule(
            id=1,
            name="VIP Customer Rule",
            rule_type="assignment",
            priority=1,
            is_active=True,
            conditions={
                "field": "customer.is_vip",
                "operator": "eq",
                "value": True
            },
            actions={
                "type": "assign_driver",
                "params": {"driver_id": 456}
            }
        )
        
        context = {
            "customer": {"is_vip": False, "id": 1},
            "order": {"id": 1}
        }
        
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is False
        assert len(result["actions"]) == 0
        
    def test_evaluate_time_constraints(self):
        """Test time-based constraints"""
        rule = DispatchRule(
            id=1,
            name="Business Hours Rule",
            rule_type="assignment",
            priority=1,
            is_active=True,
            apply_time_start=time(9, 0),  # 9 AM
            apply_time_end=time(18, 0),   # 6 PM
            conditions={
                "field": "order.priority",
                "operator": "eq",
                "value": "normal"
            },
            actions={
                "type": "assign_driver",
                "params": {"prefer_shift": "day"}
            }
        )
        
        context = {
            "order": {"priority": "normal", "id": 1},
            "current_time": time(10, 0)  # 10 AM - within range
        }
        
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is True
        
        context["current_time"] = time(20, 0)  # 8 PM - outside range
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is False
        
    def test_evaluate_day_constraints(self):
        """Test day-of-week constraints"""
        rule = DispatchRule(
            id=1,
            name="Weekday Rule",
            rule_type="assignment",
            priority=1,
            is_active=True,
            apply_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
            conditions={
                "field": "order.priority",
                "operator": "eq",
                "value": "normal"
            },
            actions={
                "type": "standard_dispatch"
            }
        )
        
        # Monday
        context = {
            "order": {"priority": "normal", "id": 1},
            "current_day": "monday"
        }
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is True
        
        # Sunday
        context["current_day"] = "sunday"
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is False
        
    def test_evaluate_complex_conditions(self):
        """Test complex nested conditions"""
        rule = DispatchRule(
            id=1,
            name="Premium Service Rule",
            rule_type="assignment",
            priority=1,
            is_active=True,
            conditions={
                "and": [
                    {"field": "customer.is_vip", "operator": "eq", "value": True},
                    {
                        "or": [
                            {"field": "order.priority", "operator": "eq", "value": "urgent"},
                            {"field": "order.value", "operator": "gt", "value": 10000}
                        ]
                    }
                ]
            },
            actions={
                "type": "premium_dispatch",
                "params": {"service_level": "premium"}
            }
        )
        
        # VIP + urgent
        context = {
            "customer": {"is_vip": True, "id": 1},
            "order": {"priority": "urgent", "value": 5000, "id": 1}
        }
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is True
        
        # VIP + high value
        context["order"]["priority"] = "normal"
        context["order"]["value"] = 15000
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is True
        
        # Not VIP
        context["customer"]["is_vip"] = False
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is False
        
    def test_evaluate_inactive_rule(self):
        """Test that inactive rules are not evaluated"""
        rule = DispatchRule(
            id=1,
            name="Inactive Rule",
            rule_type="assignment",
            priority=1,
            is_active=False,
            conditions={
                "field": "order.priority",
                "operator": "eq",
                "value": "urgent"
            },
            actions={
                "type": "assign_driver"
            }
        )
        
        context = {
            "order": {"priority": "urgent", "id": 1}
        }
        
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is False
        
    def test_evaluate_multiple_actions(self):
        """Test rule with multiple actions"""
        rule = DispatchRule(
            id=1,
            name="Multi-Action Rule",
            rule_type="assignment",
            priority=1,
            is_active=True,
            conditions={
                "field": "order.priority",
                "operator": "eq",
                "value": "urgent"
            },
            actions=[
                {"type": "assign_driver", "params": {"driver_id": 123}},
                {"type": "notify", "params": {"recipient": "dispatcher"}},
                {"type": "set_priority", "params": {"priority": 1}}
            ]
        )
        
        context = {
            "order": {"priority": "urgent", "id": 1}
        }
        
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is True
        assert len(result["actions"]) == 3
        assert result["actions"][0]["type"] == "assign_driver"
        assert result["actions"][1]["type"] == "notify"
        assert result["actions"][2]["type"] == "set_priority"
        
    def test_evaluate_with_weights(self):
        """Test evaluation with constraint weights"""
        rule = DispatchRule(
            id=1,
            name="Weighted Rule",
            rule_type="optimization",
            priority=1,
            is_active=True,
            conditions={
                "field": "order.temperature_sensitive",
                "operator": "eq",
                "value": True
            },
            actions={
                "type": "optimize",
                "params": {
                    "objective": "minimize_distance",
                    "constraint_weight": 10
                }
            }
        )
        
        context = {
            "order": {"temperature_sensitive": True, "id": 1}
        }
        
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is True
        assert result["actions"][0]["params"]["constraint_weight"] == 10
        
    def test_evaluate_error_handling(self):
        """Test error handling in evaluation"""
        rule = DispatchRule(
            id=1,
            name="Error Test Rule",
            rule_type="assignment",
            priority=1,
            is_active=True,
            conditions={
                "field": "order.invalid_field",
                "operator": "unknown_operator",  # Invalid operator
                "value": "test"
            },
            actions={"type": "test_action"}
        )
        
        context = {"order": {"id": 1}}
        
        # Should handle error gracefully
        result = self.evaluator.evaluate(rule, context)
        assert result["matched"] is False
        assert "error" in result
