#!/bin/bash

echo "======================================"
echo "GET /orders/ 500 ERROR DIAGNOSTICS"
echo "======================================"
echo ""

echo "1. Checking backend container status..."
docker ps | grep backend

echo ""
echo "2. Checking recent backend logs (last 100 lines)..."
docker logs uvis-backend-1 --tail 100

echo ""
echo "3. Testing GET /orders/ endpoint..."
curl -X GET "http://139.150.11.99/api/v1/orders/" \
     -H "accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n" \
     -v

echo ""
echo "4. Testing with limit=1 to see if it's a data volume issue..."
curl -X GET "http://139.150.11.99/api/v1/orders/?limit=1" \
     -H "accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "5. Checking database connection..."
docker exec uvis-backend-1 python3 -c "
from app.core.database import SessionLocal
from app.models.order import Order

try:
    db = SessionLocal()
    count = db.query(Order).count()
    print(f'✓ Database connection successful. Total orders: {count}')
    
    # Check for problematic data
    orders = db.query(Order).limit(5).all()
    for order in orders:
        print(f'Order {order.id}: temperature_zone={order.temperature_zone}, status={order.status}')
        print(f'  pickup_start_time type: {type(order.pickup_start_time)}, value: {order.pickup_start_time}')
        
except Exception as e:
    print(f'✗ Database error: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
"

echo ""
echo "6. Checking Python backend error logs..."
docker exec uvis-backend-1 cat /tmp/uvicorn.log 2>/dev/null || echo "Log file not found"

echo ""
echo "======================================"
echo "DIAGNOSTICS COMPLETE"
echo "======================================"
