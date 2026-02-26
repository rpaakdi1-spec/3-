# Dispatch Rules API Fix Guide

## ✅ Current Status

### Backend API - **WORKING** ✅
All dispatch rules endpoints are functional:

```bash
# 1. List Rules
GET /api/v1/dispatch-rules/

# 2. Get Single Rule  
GET /api/v1/dispatch-rules/{id}

# 3. Create Rule
POST /api/v1/dispatch-rules/
Body: {
  "name": "규칙명",
  "description": "설명", 
  "rule_type": "assignment|constraint|optimization",
  "priority": 100,
  "conditions": {...},
  "actions": {...},
  "is_active": true
}

# 4. Update Rule - **REQUIRES WRAPPER** ⚠️
PUT /api/v1/dispatch-rules/{id}
Body: {
  "rule_update": {    # ← MUST wrap in rule_update
    "name": "수정된 이름",
    "priority": 999,
    "is_active": false
    # ... other fields
  }
}

# 5. Delete Rule
DELETE /api/v1/dispatch-rules/{id}

# 6. Test Rule
POST /api/v1/dispatch-rules/{id}/test
Body: {
  "test_data": {
    "order_priority": "urgent",
    "distance_km": 5
  }
}

# 7. Activate/Deactivate
POST /api/v1/dispatch-rules/{id}/activate
POST /api/v1/dispatch-rules/{id}/deactivate

# 8. Performance Stats
GET /api/v1/dispatch-rules/{id}/performance

# 9. Execution Logs
GET /api/v1/dispatch-rules/{id}/logs
```

### Verified Working Examples

```bash
# ✅ Update works with wrapper
curl -X PUT http://localhost:8000/api/v1/dispatch-rules/3 \
  -H "Content-Type: application/json" \
  -d '{"rule_update": {"name": "올바른형식", "priority": 999}}' | jq .
# Response: {"id": 3, "name": "올바른형식", "priority": 999, "version": 5}

# ✅ Delete works
curl -X DELETE http://localhost:8000/api/v1/dispatch-rules/4
# Response: 204 No Content

# ✅ Test works  
curl -X POST http://localhost:8000/api/v1/dispatch-rules/1/test \
  -H "Content-Type: application/json" \
  -d '{"test_data": {"order_priority": "urgent", "distance_km": 5}}' | jq .
# Response: {"rule_id": 1, "matched": true, ...}
```

## ❌ Frontend Issue

The frontend is sending **incorrect payload format** for PUT requests:

### Current (Wrong) ❌
```javascript
// Frontend sends:
{
  "name": "수정테스트",
  "priority": 999
}
// Result: 422 Unprocessable Entity
```

### Required (Correct) ✅  
```javascript
// Frontend must send:
{
  "rule_update": {
    "name": "수정테스트",
    "priority": 999
  }
}
// Result: 200 OK with updated rule
```

## 🔧 Frontend Fix Required

### Option 1: Fix Frontend API Client (Recommended)

Find the dispatch rules API service file (usually `src/services/api/dispatchRules.ts` or similar):

```typescript
// BEFORE (Wrong)
export const updateDispatchRule = async (id: number, data: DispatchRuleUpdate) => {
  const response = await api.put(`/api/v1/dispatch-rules/${id}`, data);
  return response.data;
};

// AFTER (Correct)
export const updateDispatchRule = async (id: number, data: DispatchRuleUpdate) => {
  const response = await api.put(`/api/v1/dispatch-rules/${id}`, {
    rule_update: data  // ← Wrap in rule_update
  });
  return response.data;
};
```

### Option 2: Fix in Component

If modifying the component directly:

```typescript
// BEFORE (Wrong)
const handleUpdate = async (ruleData) => {
  await fetch(`/api/v1/dispatch-rules/${ruleId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(ruleData)  // ← Missing wrapper
  });
};

// AFTER (Correct)
const handleUpdate = async (ruleData) => {
  await fetch(`/api/v1/dispatch-rules/${ruleId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rule_update: ruleData })  // ← Add wrapper
  });
};
```

## 🧪 Testing After Fix

### 1. Test in Browser Console

```javascript
// Open http://139.150.11.99/dispatch-rules
// Open Developer Tools (F12) > Console
// Run this test:

fetch('/api/v1/dispatch-rules/3', {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    rule_update: {
      name: '브라우저테스트',
      priority: 888
    }
  })
})
.then(r => r.json())
.then(data => console.log('Success:', data))
.catch(err => console.error('Error:', err));
```

### 2. Check Network Tab

1. Open http://139.150.11.99/dispatch-rules
2. Open Developer Tools (F12) > Network tab
3. Try to edit a rule
4. Find the PUT request
5. Check **Payload** section:
   - ❌ Wrong: `{"name":"...","priority":100}`
   - ✅ Correct: `{"rule_update":{"name":"...","priority":100}}`

### 3. Check Response

- ✅ Success: Status 200, JSON with `{"id": 3, "name": "...", "priority": 999, "version": 5}`
- ❌ Failure: Status 422, JSON with `{"detail": [{"type": "missing", "loc": ["body", "rule_update"], ...}]}`

## 📊 Backend Implementation Details

The backend expects a Pydantic model `DispatchRuleUpdate` wrapped in a `rule_update` field:

```python
# /app/app/api/v1/endpoints/dispatch_rules.py

@router.put("/{rule_id}", response_model=DispatchRuleResponse)
async def update_rule(
    rule_id: int,
    rule_update: DispatchRuleUpdate = Body(..., embed=True),  # ← embed=True requires wrapper
    db: Session = Depends(get_db),
    current_user: dict = None
):
    # ... implementation
    update_data = rule_update.dict(exclude_unset=True)
    # ... update database
    return db_rule
```

The `embed=True` parameter in FastAPI's `Body()` requires the payload to be wrapped with the parameter name.

## 🎯 Summary

| Endpoint | Method | Works? | Notes |
|----------|--------|--------|-------|
| List Rules | GET | ✅ | Returns array of rules |
| Get Rule | GET | ✅ | Returns single rule |
| Create Rule | POST | ✅ | Works correctly |
| **Update Rule** | **PUT** | ⚠️ | **Requires `{"rule_update": {...}}` wrapper** |
| Delete Rule | DELETE | ✅ | Returns 204 |
| Test Rule | POST | ✅ | Requires `{"test_data": {...}}` wrapper |
| Activate | POST | ✅ | Works correctly |
| Deactivate | POST | ✅ | Works correctly |
| Performance | GET | ✅ | Returns stats |
| Logs | GET | ✅ | Returns execution logs |

## 📝 Action Items

1. **Frontend Developer**: Update the dispatch rules API client to wrap PUT request body in `{"rule_update": {...}}`
2. **Testing**: Verify update/delete functionality in browser at http://139.150.11.99/dispatch-rules
3. **Documentation**: Update API documentation with correct request format

## 🔗 References

- Backend file: `/app/app/api/v1/endpoints/dispatch_rules.py`
- PR: https://github.com/rpaakdi1-spec/3-/pull/12
- Commit: `afc83e0` - "fix: Resolve dispatch rules API and database issues"

---
Generated: 2026-02-25
