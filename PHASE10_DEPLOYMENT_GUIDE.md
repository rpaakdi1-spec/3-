# Phase 10 Deployment Guide

## Prerequisites

- PostgreSQL 15+ with JSONB support
- Python 3.11+ with OR-Tools
- Node.js 18+ with npm
- React 18+
- Docker (optional, for containerized deployment)

## Backend Deployment

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Add to `requirements.txt` if not present:
```
ortools==9.8.3296
```

### 2. Run Database Migration

```bash
cd backend
alembic upgrade head
```

This will create the following tables:
- `dispatch_rules`
- `rule_constraints`
- `rule_execution_logs`
- `optimization_configs`

### 3. Verify Backend

```bash
# Start backend server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Test API
curl http://localhost:8000/api/v1/dispatch-rules
```

### 4. Initialize Sample Rules (Optional)

```bash
cd backend
python scripts/init_sample_rules.py
```

## Frontend Deployment

### 1. Install Dependencies

```bash
cd frontend
npm install
```

New packages added:
- `reactflow@^11.10.1` - Visual rule builder
- `react-flow-renderer@^10.3.17` - Flow renderer

### 2. Build Frontend

```bash
cd frontend
npm run build
```

### 3. Preview Build

```bash
cd frontend
npm run preview
```

## Docker Deployment (Recommended)

### 1. Update docker-compose.yml

```yaml
services:
  backend:
    # ... existing config ...
    environment:
      - ENABLE_RULE_ENGINE=true
    volumes:
      - ./backend:/app
    
  frontend:
    # ... existing config ...
    environment:
      - VITE_API_URL=http://localhost:8000
```

### 2. Rebuild and Restart

```bash
docker-compose down
docker-compose build backend frontend
docker-compose up -d
```

### 3. Run Migration in Container

```bash
docker-compose exec backend alembic upgrade head
```

## Production Deployment

### 1. Environment Variables

Create `.env` file:
```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Rule Engine
ENABLE_RULE_ENGINE=true
MAX_RULE_EXECUTION_TIME=10000  # milliseconds
RULE_CACHE_TTL=300             # seconds

# Optimization
OR_TOOLS_SOLVER_TIME_LIMIT=60  # seconds
ENABLE_PARALLEL_OPTIMIZATION=true

# Simulation
MAX_SIMULATION_DISPATCHES=10000
SIMULATION_CACHE_TTL=3600      # seconds
```

### 2. Nginx Configuration

Add to nginx.conf:
```nginx
# Rule Builder UI
location /rules {
    proxy_pass http://frontend:80;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# Rule API
location /api/v1/dispatch-rules {
    proxy_pass http://backend:8000;
    proxy_read_timeout 300s;      # Allow long simulations
    proxy_connect_timeout 300s;
}
```

### 3. Database Indexes

Run these queries for better performance:
```sql
-- Index on active rules
CREATE INDEX idx_dispatch_rules_active 
ON dispatch_rules(is_active, priority) 
WHERE is_active = true;

-- Index on execution logs
CREATE INDEX idx_rule_execution_logs_rule_id 
ON rule_execution_logs(rule_id, executed_at DESC);

-- Index on JSONB conditions (GIN)
CREATE INDEX idx_dispatch_rules_conditions 
ON dispatch_rules USING GIN (conditions);
```

### 4. Monitoring Setup

Add to Prometheus config:
```yaml
scrape_configs:
  - job_name: 'rule_engine'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

Add Grafana dashboard:
```bash
cp grafana/dashboards/rule_engine_dashboard.json /var/lib/grafana/dashboards/
```

## Post-Deployment Verification

### 1. Health Checks

```bash
# Backend health
curl http://your-domain.com/health

# Rule engine status
curl http://your-domain.com/api/v1/dispatch-rules
```

### 2. Create Test Rule

```bash
curl -X POST http://your-domain.com/api/v1/dispatch-rules \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Test Rule",
    "rule_type": "assignment",
    "priority": 1,
    "is_active": true,
    "conditions": {
      "field": "order.priority",
      "operator": "eq",
      "value": "urgent"
    },
    "actions": {
      "type": "assign_driver",
      "params": {"prefer_available": true}
    }
  }'
```

### 3. Run Simulation Test

```bash
curl -X POST http://your-domain.com/api/v1/dispatch-rules/simulation/historical \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "start_date": "2026-01-01",
    "end_date": "2026-01-07"
  }'
```

## Rollback Plan

If issues occur:

### 1. Rollback Database

```bash
cd backend
alembic downgrade -1  # Rollback last migration
```

### 2. Restore Previous Docker Images

```bash
docker-compose down
git checkout main
docker-compose up -d
```

### 3. Disable Rule Engine

Set in `.env`:
```env
ENABLE_RULE_ENGINE=false
```

## Troubleshooting

### Issue: Rules Not Executing
```bash
# Check logs
docker-compose logs backend | grep "rule_engine"

# Verify rules are active
docker-compose exec backend python -c "
from app.database import SessionLocal
from app.models.dispatch_rule import DispatchRule
db = SessionLocal()
print(db.query(DispatchRule).filter_by(is_active=True).count())
"
```

### Issue: Simulation Timeout
```bash
# Increase timeout in nginx.conf
proxy_read_timeout 600s;

# Reduce sample size
# Or use smaller date range
```

### Issue: OR-Tools Not Installed
```bash
pip install --upgrade ortools==9.8.3296
```

## Performance Tuning

### 1. Rule Execution
- Keep rules simple (< 10 conditions)
- Use indexes on frequently accessed fields
- Cache rule results when possible

### 2. Simulation
- Limit historical date range (< 30 days)
- Use sampling for large datasets
- Run simulations during off-peak hours

### 3. Database
- Regular VACUUM ANALYZE
- Monitor JSONB query performance
- Consider materialized views for metrics

## Security Considerations

1. **API Authorization**
   - All rule endpoints require authentication
   - Admin-only access for rule creation/deletion
   - Audit log all rule modifications

2. **Input Validation**
   - Validate all rule conditions
   - Sanitize JSONB inputs
   - Limit rule complexity

3. **Rate Limiting**
   - Limit simulation requests (5 per hour per user)
   - Throttle rule execution (1000 per minute)

## Support

- **Documentation**: `/docs/phase10/`
- **API Docs**: `http://your-domain.com/docs#/dispatch-rules`
- **Issues**: GitHub Issues
- **Email**: support@your-company.com

## Maintenance

### Weekly Tasks
- Review rule execution logs
- Check simulation performance
- Monitor disk usage (logs)

### Monthly Tasks
- Archive old execution logs (> 90 days)
- Review and optimize slow rules
- Update documentation

### Quarterly Tasks
- Performance audit
- Security review
- User feedback collection

---

**Deployment Checklist**
- [ ] Database migration completed
- [ ] Backend dependencies installed
- [ ] Frontend built and deployed
- [ ] Environment variables configured
- [ ] Database indexes created
- [ ] Monitoring configured
- [ ] Health checks passing
- [ ] Test rule created
- [ ] Simulation test passed
- [ ] Documentation updated
- [ ] Team trained
- [ ] Support channel ready

**Deployed By**: _____________  
**Date**: _____________  
**Version**: 2.0.0
