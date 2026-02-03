#!/bin/bash

echo "================================================================================"
echo "🔧 백엔드 코드 Hot-Fix 적용 스크립트"
echo "================================================================================"
echo ""
echo "문제: Docker 컨테이너가 이전 코드를 캐싱하고 있어 새 코드가 반영되지 않음"
echo "해결: 컨테이너 내부 코드를 직접 업데이트"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "${BLUE}1️⃣ 현재 컨테이너 상태 확인${NC}"
docker ps | grep uvis-backend

echo ""
echo "${BLUE}2️⃣ backend/app/api/orders.py 파일 업데이트${NC}"
echo "   → GET /{order_id} 엔드포인트를 dict 반환으로 수정"

# Create the updated orders.py content
cat > /tmp/orders_get_endpoint_fix.py << 'EOF'
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """주문 상세 조회"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    
    # Convert to dict to avoid SQLAlchemy relationship serialization issues
    order_dict = {
        'id': order.id,
        'order_number': order.order_number,
        'order_date': order.order_date,
        'temperature_zone': order.temperature_zone,
        'pickup_client_id': order.pickup_client_id,
        'delivery_client_id': order.delivery_client_id,
        'pickup_address': order.pickup_address,
        'pickup_address_detail': order.pickup_address_detail,
        'delivery_address': order.delivery_address,
        'delivery_address_detail': order.delivery_address_detail,
        'pallet_count': order.pallet_count,
        'weight_kg': order.weight_kg,
        'volume_cbm': order.volume_cbm,
        'product_name': order.product_name,
        'product_code': order.product_code,
        'pickup_start_time': order.pickup_start_time,
        'pickup_end_time': order.pickup_end_time,
        'delivery_start_time': order.delivery_start_time,
        'delivery_end_time': order.delivery_end_time,
        'requested_delivery_date': order.requested_delivery_date,
        'priority': order.priority,
        'is_reserved': order.is_reserved,
        'reserved_at': order.reserved_at,
        'confirmed_at': order.confirmed_at,
        'recurring_type': order.recurring_type,
        'recurring_end_date': order.recurring_end_date,
        'requires_forklift': order.requires_forklift,
        'is_stackable': order.is_stackable,
        'notes': order.notes,
        'status': order.status,
        'created_at': order.created_at,
        'updated_at': order.updated_at,
        'pickup_latitude': order.pickup_latitude,
        'pickup_longitude': order.pickup_longitude,
        'delivery_latitude': order.delivery_latitude,
        'delivery_longitude': order.delivery_longitude,
        # Add client names
        'pickup_client_name': order.pickup_client.name if order.pickup_client else None,
        'delivery_client_name': order.delivery_client.name if order.delivery_client else None,
    }
    
    return order_dict
EOF

echo "${GREEN}✓ 수정된 코드 준비 완료${NC}"
echo ""

echo "${BLUE}3️⃣ 컨테이너 내부 파일 백업${NC}"
docker exec uvis-backend cp /app/app/api/orders.py /app/app/api/orders.py.backup
echo "${GREEN}✓ 백업 완료: /app/app/api/orders.py.backup${NC}"
echo ""

echo "${BLUE}4️⃣ 컨테이너 내부 Python 스크립트로 파일 수정${NC}"
echo "   (sed/vi가 없을 수 있으므로 Python으로 수정)"

docker exec uvis-backend python3 << 'PYTHON_EOF'
import re

# Read the current file
with open('/app/app/api/orders.py', 'r') as f:
    content = f.read()

# Find and replace the get_order function
old_pattern = r'@router\.get\("/\{order_id\}", response_model=OrderWithClientsResponse\)[\s\S]*?def get_order\(order_id: int, db: Session = Depends\(get_db\)\):[\s\S]*?return order'

new_code = '''@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """주문 상세 조회"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    
    # Convert to dict to avoid SQLAlchemy relationship serialization issues
    order_dict = {
        'id': order.id,
        'order_number': order.order_number,
        'order_date': order.order_date,
        'temperature_zone': order.temperature_zone,
        'pickup_client_id': order.pickup_client_id,
        'delivery_client_id': order.delivery_client_id,
        'pickup_address': order.pickup_address,
        'pickup_address_detail': order.pickup_address_detail,
        'delivery_address': order.delivery_address,
        'delivery_address_detail': order.delivery_address_detail,
        'pallet_count': order.pallet_count,
        'weight_kg': order.weight_kg,
        'volume_cbm': order.volume_cbm,
        'product_name': order.product_name,
        'product_code': order.product_code,
        'pickup_start_time': order.pickup_start_time,
        'pickup_end_time': order.pickup_end_time,
        'delivery_start_time': order.delivery_start_time,
        'delivery_end_time': order.delivery_end_time,
        'requested_delivery_date': order.requested_delivery_date,
        'priority': order.priority,
        'is_reserved': order.is_reserved,
        'reserved_at': order.reserved_at,
        'confirmed_at': order.confirmed_at,
        'recurring_type': order.recurring_type,
        'recurring_end_date': order.recurring_end_date,
        'requires_forklift': order.requires_forklift,
        'is_stackable': order.is_stackable,
        'notes': order.notes,
        'status': order.status,
        'created_at': order.created_at,
        'updated_at': order.updated_at,
        'pickup_latitude': order.pickup_latitude,
        'pickup_longitude': order.pickup_longitude,
        'delivery_latitude': order.delivery_latitude,
        'delivery_longitude': order.delivery_longitude,
        # Add client names
        'pickup_client_name': order.pickup_client.name if order.pickup_client else None,
        'delivery_client_name': order.delivery_client.name if order.delivery_client else None,
    }
    
    return order_dict'''

# Try to replace
if 'OrderWithClientsResponse' in content:
    # Replace the function
    content = re.sub(old_pattern, new_code, content, count=1)
    print("✓ Found and replaced get_order function")
else:
    print("⚠ OrderWithClientsResponse not found, function may already be updated")

# Also fix the import
content = content.replace(
    'from app.schemas.order import (\n    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse, OrderWithClientsResponse\n)',
    'from app.schemas.order import (\n    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse\n)'
)

# Write back
with open('/app/app/api/orders.py', 'w') as f:
    f.write(content)

print("✓ File updated successfully")
PYTHON_EOF

echo ""
echo "${GREEN}✓ 파일 수정 완료${NC}"
echo ""

echo "${BLUE}5️⃣ 백엔드 재시작 (코드 리로드)${NC}"
docker-compose -f docker-compose.prod.yml restart backend
sleep 30
echo "${GREEN}✓ 재시작 완료${NC}"
echo ""

echo "${BLUE}6️⃣ 테스트 실행${NC}"
echo "   GET /api/v1/orders/3"
curl -s http://localhost:8000/api/v1/orders/3 | jq '{id, order_number, pickup_start_time, pickup_end_time}'

echo ""
echo "================================================================================"
echo "${YELLOW}📊 결과 확인${NC}"
echo "================================================================================"
echo ""
echo "✅ 예상 결과: id, order_number, pickup_start_time이 모두 표시되어야 함"
echo "❌ 실패 시: null 값이나 에러 메시지 표시"
echo ""
echo "다음 명령어로 에러 확인:"
echo "  docker logs uvis-backend --tail 50 | grep ERROR"
echo ""
echo "================================================================================"
