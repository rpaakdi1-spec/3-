# Phase 10 Rule Engine - Quick Start Examples

## Basic Rule Examples

### 1. VIP Customer Rule
Assign best drivers to VIP customers:

```json
{
  "name": "VIP Customer Priority Assignment",
  "description": "Automatically assign 5-star rated drivers to VIP customers",
  "rule_type": "assignment",
  "priority": 1,
  "is_active": true,
  "conditions": {
    "field": "customer.is_vip",
    "operator": "eq",
    "value": true
  },
  "actions": [
    {
      "type": "assign_driver",
      "params": {
        "min_rating": 5.0,
        "prefer_available": true
      }
    },
    {
      "type": "notify",
      "params": {
        "recipient": "dispatcher",
        "message": "VIP customer order assigned"
      }
    }
  ]
}
```

### 2. Urgent Order Rule
Prioritize urgent orders:

```json
{
  "name": "Urgent Order Fast Assignment",
  "description": "Assign nearest available driver to urgent orders",
  "rule_type": "assignment",
  "priority": 1,
  "is_active": true,
  "conditions": {
    "field": "order.priority",
    "operator": "eq",
    "value": "urgent"
  },
  "actions": [
    {
      "type": "optimize",
      "params": {
        "objective": "minimize_distance",
        "max_computation_time": 10
      }
    }
  ]
}
```

### 3. Temperature-Controlled Shipment
Route refrigerated goods correctly:

```json
{
  "name": "Refrigerated Transport Required",
  "description": "Assign refrigerated vehicles to temperature-sensitive orders",
  "rule_type": "assignment",
  "priority": 2,
  "is_active": true,
  "conditions": {
    "and": [
      {
        "field": "order.temperature_controlled",
        "operator": "eq",
        "value": true
      },
      {
        "field": "order.temperature_range_min",
        "operator": "lte",
        "value": 4
      }
    ]
  },
  "actions": [
    {
      "type": "assign_vehicle",
      "params": {
        "has_refrigeration": true,
        "temperature_range": [-10, 4]
      }
    },
    {
      "type": "optimize",
      "params": {
        "objective": "minimize_time",
        "max_duration_hours": 4
      }
    }
  ]
}
```

### 4. Heavy Load Rule
Assign appropriate vehicles for heavy shipments:

```json
{
  "name": "Heavy Load Vehicle Assignment",
  "description": "Assign trucks for orders over 1000kg",
  "rule_type": "assignment",
  "priority": 2,
  "is_active": true,
  "conditions": {
    "or": [
      {
        "field": "order.weight",
        "operator": "gt",
        "value": 1000
      },
      {
        "field": "order.volume",
        "operator": "gt",
        "value": 50
      }
    ]
  },
  "actions": [
    {
      "type": "assign_vehicle",
      "params": {
        "vehicle_type": "truck_large",
        "min_capacity_kg": 1500
      }
    }
  ]
}
```

### 5. Business Hours Rule
Different handling during business hours:

```json
{
  "name": "Business Hours Standard Dispatch",
  "description": "Standard dispatch rules for business hours",
  "rule_type": "assignment",
  "priority": 5,
  "is_active": true,
  "apply_time_start": "09:00",
  "apply_time_end": "18:00",
  "apply_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
  "conditions": {
    "field": "order.priority",
    "operator": "eq",
    "value": "normal"
  },
  "actions": [
    {
      "type": "optimize",
      "params": {
        "objective": "minimize_cost",
        "allow_batching": true
      }
    }
  ]
}
```

### 6. Weekend Emergency Rule
Special handling for weekend emergencies:

```json
{
  "name": "Weekend Emergency Dispatch",
  "description": "Premium service for weekend emergencies",
  "rule_type": "assignment",
  "priority": 1,
  "is_active": true,
  "apply_days": ["saturday", "sunday"],
  "conditions": {
    "field": "order.priority",
    "operator": "eq",
    "value": "emergency"
  },
  "actions": [
    {
      "type": "assign_driver",
      "params": {
        "on_weekend_duty": true,
        "max_response_time_minutes": 30
      }
    },
    {
      "type": "notify",
      "params": {
        "recipient": "manager",
        "urgency": "high",
        "message": "Weekend emergency dispatch"
      }
    }
  ]
}
```

## Complex Rule Examples

### 7. Multi-Condition Premium Service
```json
{
  "name": "Premium Service Eligibility",
  "description": "Multiple criteria for premium service",
  "rule_type": "assignment",
  "priority": 1,
  "is_active": true,
  "conditions": {
    "and": [
      {
        "or": [
          {
            "field": "customer.is_vip",
            "operator": "eq",
            "value": true
          },
          {
            "field": "order.value",
            "operator": "gt",
            "value": 10000
          }
        ]
      },
      {
        "field": "order.priority",
        "operator": "in",
        "value": ["urgent", "emergency"]
      },
      {
        "not": {
          "field": "customer.has_late_payments",
          "operator": "eq",
          "value": true
        }
      }
    ]
  },
  "actions": [
    {
      "type": "assign_driver",
      "params": {
        "service_level": "premium",
        "min_rating": 4.8
      }
    },
    {
      "type": "optimize",
      "params": {
        "objective": "minimize_time",
        "priority_weight": 10
      }
    }
  ]
}
```

### 8. Dynamic Route Optimization
```json
{
  "name": "Multi-Stop Route Optimization",
  "description": "Optimize routes for multiple delivery stops",
  "rule_type": "optimization",
  "priority": 3,
  "is_active": true,
  "conditions": {
    "and": [
      {
        "field": "order.has_multiple_stops",
        "operator": "eq",
        "value": true
      },
      {
        "field": "order.total_stops",
        "operator": "gte",
        "value": 3
      }
    ]
  },
  "actions": [
    {
      "type": "optimize",
      "params": {
        "objective": "minimize_distance",
        "algorithm": "clarke_wright",
        "consider_traffic": true,
        "time_windows": true
      }
    }
  ]
}
```

## API Usage Examples

### Create Rule via API

```python
import requests

url = "http://localhost:8000/api/v1/dispatch-rules"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}

rule_data = {
    "name": "Test Rule",
    "rule_type": "assignment",
    "priority": 1,
    "is_active": True,
    "conditions": {
        "field": "order.priority",
        "operator": "eq",
        "value": "urgent"
    },
    "actions": {
        "type": "assign_driver",
        "params": {"prefer_available": True}
    }
}

response = requests.post(url, json=rule_data, headers=headers)
print(response.json())
```

### Test Rule

```python
rule_id = 1
test_context = {
    "order": {
        "id": 123,
        "priority": "urgent",
        "weight": 500
    },
    "available_drivers": [
        {"id": 1, "name": "Driver A", "rating": 5.0},
        {"id": 2, "name": "Driver B", "rating": 4.5}
    ]
}

response = requests.post(
    f"http://localhost:8000/api/v1/dispatch-rules/{rule_id}/test",
    json={"context": test_context},
    headers=headers
)
print(response.json())
```

### Run Historical Simulation

```python
simulation_data = {
    "start_date": "2026-01-01",
    "end_date": "2026-01-07",
    "rule_ids": [1, 2, 3]  # Optional: test specific rules
}

response = requests.post(
    "http://localhost:8000/api/v1/dispatch-rules/simulation/historical",
    json=simulation_data,
    headers=headers
)

result = response.json()
print(f"Original distance: {result['original_metrics']['total_distance_km']} km")
print(f"Simulated distance: {result['simulated_metrics']['total_distance_km']} km")
print(f"Improvement: {result['improvements']['distance_saved_pct']}%")
```

### A/B Test Two Rules

```python
ab_test_data = {
    "rule_a_id": 1,  # Control
    "rule_b_id": 2,  # Treatment
    "test_duration_days": 7,
    "traffic_split": 0.5
}

response = requests.post(
    "http://localhost:8000/api/v1/dispatch-rules/simulation/ab-test",
    json=ab_test_data,
    headers=headers
)

result = response.json()
print(f"Winner: Rule {result['winner']}")
print(f"Improvement: {result['comparison']}")
```

## Frontend Usage Examples

### Using Rule Builder Canvas

```tsx
import { RuleBuilderCanvas } from '@/components/RuleBuilderCanvas';

function RuleEditorPage() {
  const handleSaveRule = (ruleData: any) => {
    // Save rule to backend
    fetch('/api/v1/dispatch-rules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ruleData)
    });
  };

  return (
    <div>
      <h1>Visual Rule Builder</h1>
      <RuleBuilderCanvas onSave={handleSaveRule} />
    </div>
  );
}
```

### Using Simulation Dashboard

```tsx
import { SimulationDashboard } from '@/pages/SimulationDashboard';

function SimulationPage() {
  return (
    <div>
      <h1>Rule Simulation & Testing</h1>
      <SimulationDashboard />
    </div>
  );
}
```

## Common Patterns

### Pattern 1: Customer Tier-Based Dispatch
```json
{
  "conditions": {
    "field": "customer.tier",
    "operator": "in",
    "value": ["gold", "platinum"]
  },
  "actions": [{"type": "assign_driver", "params": {"min_rating": 4.8}}]
}
```

### Pattern 2: Time-Critical Delivery
```json
{
  "conditions": {
    "and": [
      {"field": "order.delivery_window_hours", "operator": "lte", "value": 2},
      {"field": "order.distance_km", "operator": "lte", "value": 20}
    ]
  },
  "actions": [{"type": "optimize", "params": {"objective": "minimize_time"}}]
}
```

### Pattern 3: Geographic Zone Restrictions
```json
{
  "conditions": {
    "field": "order.delivery_zone",
    "operator": "regex",
    "value": "^ZONE-(A|B|C)$"
  },
  "actions": [{"type": "assign_driver", "params": {"authorized_zones": ["A", "B", "C"]}}]
}
```

---

**Need Help?**
- API Documentation: http://localhost:8000/docs#/dispatch-rules
- Full Guide: See PHASE10_COMPLETE_REPORT.md
- Support: support@your-company.com
