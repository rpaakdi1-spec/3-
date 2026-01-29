# Testing Guide

Complete testing documentation for the Cold Chain Dispatch System.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [E2E Testing](#e2e-testing)
- [Load Testing](#load-testing)
- [Performance Testing](#performance-testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Test Coverage](#test-coverage)
- [Running Tests](#running-tests)

---

## 🎯 Overview

The Cold Chain System employs comprehensive testing at multiple levels:

- **Unit Tests**: 130+ tests (Backend: pytest, Frontend: Jest)
- **Integration Tests**: API endpoint tests
- **E2E Tests**: 100+ Cypress test cases
- **Load Tests**: 10+ Locust scenarios
- **Performance Tests**: k6 scripts
- **Code Coverage**: 80%+ target

---

## 🧪 Unit Testing

### Backend (pytest)

**Location**: `backend/tests/`

**Framework**: pytest + pytest-asyncio + pytest-cov

**Running Tests**:
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_orders.py

# Run specific test
pytest tests/test_orders.py::test_create_order

# Run with verbose output
pytest -v -s

# Run failed tests only
pytest --lf
```

**Test Structure**:
```
backend/tests/
├── conftest.py           # Fixtures and configuration
├── test_auth.py          # Authentication tests
├── test_orders.py        # Order management tests
├── test_dispatches.py    # Dispatch tests
├── test_vehicles.py      # Vehicle tests
├── test_analytics.py     # Analytics tests
├── test_ml_models.py     # ML model tests
└── test_websocket.py     # WebSocket tests
```

**Example Test**:
```python
import pytest
from fastapi.testclient import TestClient

def test_create_order(client: TestClient, auth_headers):
    """Test order creation"""
    order_data = {
        "client_id": 1,
        "temperature_type": "냉동",
        "pallets": 5,
        "weight_kg": 500.0
    }
    
    response = client.post(
        "/api/v1/orders",
        json=order_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json()["pallets"] == 5
```

### Frontend (Jest + React Testing Library)

**Location**: `frontend/src/__tests__/`

**Running Tests**:
```bash
cd frontend

# Run all tests
npm run test

# Run with coverage
npm run test -- --coverage

# Run in watch mode
npm run test -- --watch

# Run specific test file
npm run test -- hooks/useRealtimeData.test.ts
```

---

## 🔗 Integration Testing

### API Integration Tests

**Purpose**: Test API endpoints with real database

**Running**:
```bash
cd backend
pytest tests/integration/
```

**Example**:
```python
@pytest.mark.asyncio
async def test_complete_dispatch_workflow(async_client, db_session):
    """Test complete workflow: order -> dispatch -> completion"""
    
    # 1. Create order
    order = await create_test_order(db_session)
    
    # 2. Optimize dispatch
    response = await async_client.post(
        "/api/v1/dispatches/optimize",
        json={"order_ids": [order.id]}
    )
    assert response.status_code == 200
    
    # 3. Create dispatch
    dispatch = await create_dispatch_from_optimization(
        db_session, 
        response.json()
    )
    
    # 4. Complete dispatch
    response = await async_client.patch(
        f"/api/v1/dispatches/{dispatch.id}/status",
        json={"status": "completed"}
    )
    assert response.status_code == 200
```

---

## 🌐 E2E Testing (Cypress)

### Running Cypress Tests

**Interactive Mode**:
```bash
cd frontend
npm run cypress:open
```

**Headless Mode**:
```bash
cd frontend
npm run cypress:run
```

**Specific Spec**:
```bash
npx cypress run --spec "cypress/e2e/complete-workflow.cy.ts"
```

### Test Categories

#### 1. Complete Workflow Tests
**File**: `cypress/e2e/complete-workflow.cy.ts`

- Order creation to dispatch completion
- Authentication flow
- Form validation
- Search and filter

**Coverage**: 100+ test cases

#### 2. Authentication Tests
- User registration
- Login/logout
- Token expiration
- Password reset

#### 3. CRUD Operations
- Create, Read, Update, Delete for all entities
- Form validation
- Error handling

#### 4. Real-time Features
- WebSocket connections
- Live updates
- Alert notifications

### Cypress Best Practices

```typescript
// ✅ Good: Use data-cy attributes
cy.get('[data-cy=submit-btn]').click();

// ❌ Bad: Use classes or IDs
cy.get('.submit-button').click();
cy.get('#submit').click();

// ✅ Good: Custom commands
cy.login('username', 'password');

// ✅ Good: Proper waits
cy.intercept('POST', '/api/v1/orders').as('createOrder');
cy.get('[data-cy=submit-btn]').click();
cy.wait('@createOrder');
```

---

## 🚀 Load Testing (Locust)

### Running Load Tests

**Basic Run**:
```bash
cd backend
locust -f tests/load/advanced_load_test.py --host=http://localhost:8000
```

**Headless Mode**:
```bash
locust -f tests/load/advanced_load_test.py \
  --host=http://localhost:8000 \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --html tests/load/report.html
```

**Distributed Mode** (Multiple Workers):
```bash
# Master
locust -f tests/load/advanced_load_test.py --master

# Workers (run on multiple machines)
locust -f tests/load/advanced_load_test.py --worker --master-host=<master-ip>
```

### Load Test Scenarios

1. **AdvancedColdChainUser** (70% of traffic)
   - Dashboard viewing (10x weight)
   - Order management (8x weight)
   - Dispatch operations (7x weight)
   - ML predictions (3x weight)

2. **AdminUser** (20% of traffic)
   - System performance monitoring
   - Audit logs
   - Cache management

3. **MobileUser** (10% of traffic)
   - GPS location updates
   - Dispatch status changes
   - FCM token registration

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Concurrent Users | 1000 | Simultaneous connections |
| RPS | 500+ | Requests per second |
| Avg Response Time | <200ms | Mean latency |
| 95th Percentile | <500ms | p95 latency |
| 99th Percentile | <1s | p99 latency |
| Error Rate | <0.1% | Failed requests |

---

## ⚡ Performance Testing (k6)

### Running k6 Tests

**Installation**:
```bash
# macOS
brew install k6

# Linux
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

**Run Tests**:
```bash
cd backend

# Basic run
k6 run tests/performance/k6-performance-test.js

# With custom options
k6 run --vus 100 --duration 5m tests/performance/k6-performance-test.js

# With environment variable
k6 run --env API_URL=https://api.production.com tests/performance/k6-performance-test.js
```

### k6 Test Stages

1. **Ramp Up** (2 min): 0 → 50 users
2. **Steady Load** (5 min): 50 users
3. **Scale Up** (2 min): 50 → 100 users
4. **High Load** (5 min): 100 users
5. **Spike** (2 min): 100 → 200 users
6. **Peak Load** (3 min): 200 users
7. **Ramp Down** (2 min): 200 → 0 users

### k6 Metrics

- `http_req_duration`: Request duration
- `http_req_failed`: Failed requests
- `http_reqs`: Total requests
- `vus`: Virtual users
- `iterations`: Completed iterations

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

**File**: `.github/workflows/test.yml`

**Triggers**:
- Push to `main` or `genspark_ai_developer` branches
- Pull requests to `main`

**Jobs**:

1. **backend-tests**
   - Python 3.11
   - PostgreSQL 15
   - Redis 7
   - pytest with coverage

2. **frontend-tests**
   - Node.js 18
   - Jest with coverage

3. **e2e-tests**
   - Cypress E2E tests
   - Chrome browser
   - Full stack (backend + frontend)

4. **load-tests** (conditional)
   - Triggered by `load-test` label
   - Locust 3-minute run

5. **code-quality**
   - flake8, black, mypy (Python)
   - ESLint (TypeScript/React)

6. **security-scan**
   - Trivy vulnerability scanner
   - Snyk security scan

### Running Locally

```bash
# Simulate CI environment
docker-compose -f docker-compose.test.yml up -d
pytest
npm run test
npm run cypress:run
docker-compose -f docker-compose.test.yml down
```

---

## 📊 Test Coverage

### Current Coverage

- **Backend**: 80%+ (target: 80%)
- **Frontend**: 70%+ (target: 75%)
- **E2E**: 100+ scenarios

### Coverage Reports

**Backend**:
```bash
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

**Frontend**:
```bash
cd frontend
npm run test -- --coverage
open coverage/lcov-report/index.html
```

### Coverage Goals

| Component | Current | Target |
|-----------|---------|--------|
| Models | 90% | 90% |
| Services | 85% | 85% |
| API Endpoints | 80% | 80% |
| Utils | 75% | 75% |
| Frontend Components | 70% | 75% |
| Frontend Hooks | 80% | 80% |

---

## 🏃 Running Tests

### Quick Test Commands

```bash
# Backend: All tests with coverage
cd backend && pytest --cov=app --cov-report=term

# Frontend: All tests with coverage
cd frontend && npm run test -- --coverage

# E2E: Headless mode
cd frontend && npm run cypress:run

# Load: 5-minute test with 100 users
cd backend && locust -f tests/load/advanced_load_test.py --headless --users 100 --spawn-rate 10 --run-time 5m

# Performance: k6 test
cd backend && k6 run tests/performance/k6-performance-test.js
```

### Pre-commit Checks

```bash
# Format code
cd backend && black app
cd frontend && npm run format

# Lint code
cd backend && flake8 app
cd frontend && npm run lint

# Type check
cd backend && mypy app
cd frontend && npm run type-check

# Run quick tests
cd backend && pytest -x --ff
cd frontend && npm run test -- --bail
```

---

## 🎯 Test Strategy

### Testing Pyramid

```
        /\
       /  \       E2E Tests (10%)
      /____\      100+ Cypress scenarios
     /      \
    /        \    Integration Tests (20%)
   /__________\   API + DB tests
  /            \
 /              \ Unit Tests (70%)
/________________\ 130+ pytest + Jest tests
```

### When to Write Tests

- **Unit Tests**: For all business logic, utilities, models
- **Integration Tests**: For API endpoints, database operations
- **E2E Tests**: For critical user flows
- **Load Tests**: For performance validation
- **Performance Tests**: For SLA verification

---

## 📚 Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [Cypress Documentation](https://docs.cypress.io/)
- [Locust Documentation](https://docs.locust.io/)
- [k6 Documentation](https://k6.io/docs/)

---

**Last Updated**: 2026-01-28  
**Maintained by**: Cold Chain Development Team
