"""
Unit tests for Rule Parser
"""
import pytest
from datetime import datetime
from app.services.rule_parser import RuleParser, ParseError


class TestRuleParser:
    """Test cases for RuleParser"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.parser = RuleParser()
        
    def test_parse_simple_condition(self):
        """Test parsing simple condition"""
        condition = {
            "field": "order.priority",
            "operator": "eq",
            "value": "urgent"
        }
        
        context = {"order": {"priority": "urgent"}}
        result = self.parser.parse_condition(condition, context)
        assert result is True
        
    def test_parse_numeric_comparison(self):
        """Test numeric comparison operators"""
        conditions = [
            ({"field": "order.weight", "operator": "gt", "value": 100}, 
             {"order": {"weight": 150}}, True),
            ({"field": "order.weight", "operator": "lt", "value": 100}, 
             {"order": {"weight": 50}}, True),
            ({"field": "order.weight", "operator": "gte", "value": 100}, 
             {"order": {"weight": 100}}, True),
            ({"field": "order.weight", "operator": "lte", "value": 100}, 
             {"order": {"weight": 100}}, True),
        ]
        
        for condition, context, expected in conditions:
            result = self.parser.parse_condition(condition, context)
            assert result == expected
            
    def test_parse_in_operator(self):
        """Test IN operator"""
        condition = {
            "field": "order.status",
            "operator": "in",
            "value": ["pending", "confirmed"]
        }
        
        context = {"order": {"status": "pending"}}
        result = self.parser.parse_condition(condition, context)
        assert result is True
        
        context = {"order": {"status": "completed"}}
        result = self.parser.parse_condition(condition, context)
        assert result is False
        
    def test_parse_and_condition(self):
        """Test AND logical operator"""
        condition = {
            "and": [
                {"field": "order.priority", "operator": "eq", "value": "urgent"},
                {"field": "order.weight", "operator": "gt", "value": 100}
            ]
        }
        
        context = {"order": {"priority": "urgent", "weight": 150}}
        result = self.parser.parse_condition(condition, context)
        assert result is True
        
        context = {"order": {"priority": "urgent", "weight": 50}}
        result = self.parser.parse_condition(condition, context)
        assert result is False
        
    def test_parse_or_condition(self):
        """Test OR logical operator"""
        condition = {
            "or": [
                {"field": "order.priority", "operator": "eq", "value": "urgent"},
                {"field": "order.weight", "operator": "gt", "value": 1000}
            ]
        }
        
        context = {"order": {"priority": "normal", "weight": 1500}}
        result = self.parser.parse_condition(condition, context)
        assert result is True
        
        context = {"order": {"priority": "normal", "weight": 500}}
        result = self.parser.parse_condition(condition, context)
        assert result is False
        
    def test_parse_not_condition(self):
        """Test NOT logical operator"""
        condition = {
            "not": {
                "field": "order.is_cancelled",
                "operator": "eq",
                "value": True
            }
        }
        
        context = {"order": {"is_cancelled": False}}
        result = self.parser.parse_condition(condition, context)
        assert result is True
        
    def test_parse_nested_conditions(self):
        """Test deeply nested logical conditions"""
        condition = {
            "and": [
                {"field": "order.priority", "operator": "eq", "value": "urgent"},
                {
                    "or": [
                        {"field": "order.weight", "operator": "gt", "value": 1000},
                        {"field": "customer.is_vip", "operator": "eq", "value": True}
                    ]
                }
            ]
        }
        
        context = {
            "order": {"priority": "urgent", "weight": 500},
            "customer": {"is_vip": True}
        }
        result = self.parser.parse_condition(condition, context)
        assert result is True
        
    def test_parse_missing_field(self):
        """Test handling of missing fields"""
        condition = {
            "field": "order.nonexistent",
            "operator": "eq",
            "value": "test"
        }
        
        context = {"order": {"priority": "normal"}}
        result = self.parser.parse_condition(condition, context)
        assert result is False
        
    def test_parse_invalid_operator(self):
        """Test handling of invalid operator"""
        condition = {
            "field": "order.priority",
            "operator": "invalid_op",
            "value": "urgent"
        }
        
        context = {"order": {"priority": "urgent"}}
        with pytest.raises(ParseError):
            self.parser.parse_condition(condition, context)
            
    def test_parse_action(self):
        """Test parsing action"""
        action = {
            "type": "assign_driver",
            "params": {
                "driver_id": 123,
                "priority": 1
            }
        }
        
        result = self.parser.parse_action(action)
        assert result["type"] == "assign_driver"
        assert result["params"]["driver_id"] == 123
        
    def test_get_nested_value(self):
        """Test getting nested values from context"""
        context = {
            "order": {
                "customer": {
                    "name": "Test Customer",
                    "address": {
                        "city": "Seoul"
                    }
                }
            }
        }
        
        value = self.parser.get_value(context, "order.customer.address.city")
        assert value == "Seoul"
        
    def test_contains_operator(self):
        """Test contains operator for strings"""
        condition = {
            "field": "order.notes",
            "operator": "contains",
            "value": "fragile"
        }
        
        context = {"order": {"notes": "Handle with care - fragile items"}}
        result = self.parser.parse_condition(condition, context)
        assert result is True
        
    def test_regex_operator(self):
        """Test regex operator"""
        condition = {
            "field": "order.tracking_code",
            "operator": "regex",
            "value": "^TRACK-\\d{6}$"
        }
        
        context = {"order": {"tracking_code": "TRACK-123456"}}
        result = self.parser.parse_condition(condition, context)
        assert result is True
        
        context = {"order": {"tracking_code": "INVALID-CODE"}}
        result = self.parser.parse_condition(condition, context)
        assert result is False
