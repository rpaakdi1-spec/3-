#!/bin/bash
# Production Startup Script
# Cold Chain Delivery Management System

set -e

echo "=========================================="
echo "Starting Cold Chain Delivery System"
echo "Environment: PRODUCTION"
echo "=========================================="

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z ${POSTGRES_HOST:-postgres} ${POSTGRES_PORT:-5432}; do
  sleep 1
done
echo "✓ PostgreSQL is ready"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
  sleep 1
done
echo "✓ Redis is ready"

# Run database migrations
echo "Running database migrations..."
cd /app/backend
python -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine)"
echo "✓ Database migrations completed"

# Create initial admin user if not exists
echo "Checking admin user..."
python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
if not admin:
    admin = User(
        username='admin',
        email='admin@coldchain.com',
        hashed_password=get_password_hash('admin123'),
        full_name='System Administrator',
        role='ADMIN',
        is_active=True
    )
    db.add(admin)
    db.commit()
    print('✓ Admin user created')
else:
    print('✓ Admin user exists')
db.close()
" || echo "⚠ Admin user check skipped"

# Warm up ML models (if enabled)
if [ "${FEATURE_ML_PREDICTION}" = "true" ]; then
    echo "Loading ML models..."
    python -c "
from app.services.eta_prediction import eta_predictor
from app.services.demand_forecasting import demand_forecaster
print('✓ ML models loaded')
    " || echo "⚠ ML model loading skipped"
fi

# Start Gunicorn with production config
echo "Starting Gunicorn server..."
echo "Workers: ${API_WORKERS:-4}"
echo "Port: ${API_PORT:-8000}"
echo "=========================================="

exec gunicorn app.main:app \
    --workers ${API_WORKERS:-4} \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${API_PORT:-8000} \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level ${LOG_LEVEL:-info} \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --worker-tmp-dir /dev/shm
