import sys
sys.path.insert(0, '/home/user/webapp/backend')

from app.database import SessionLocal
from app.models.order import Order, TemperatureZone
from app.models.vehicle import Vehicle, VehicleType
from app.models.client import Client

def check_data():
    db = SessionLocal()
    try:
        # Check orders
        orders = db.query(Order).filter(Order.status == '배차대기').all()
        print(f"📦 배차대기 주문: {len(orders)}건\n")
        
        if orders:
            for i, order in enumerate(orders[:3], 1):
                print(f"주문 #{i} (ID: {order.id}):")
                print(f"  - 주문번호: {order.order_number}")
                print(f"  - 온도대: {order.temperature_zone.value if order.temperature_zone else 'N/A'}")
                print(f"  - 팔레트: {order.pallet_count}개")
                print(f"  - 중량: {order.weight_kg}kg")
                print(f"  - 상차지: {order.pickup_address or 'N/A'}")
                print(f"  - 상차 GPS: ({order.pickup_latitude}, {order.pickup_longitude})")
                print(f"  - 하차지: {order.delivery_address or 'N/A'}")
                print(f"  - 하차 GPS: ({order.delivery_latitude}, {order.delivery_longitude})")
                
                # Check related clients
                if order.pickup_client_id:
                    client = db.query(Client).filter(Client.id == order.pickup_client_id).first()
                    if client:
                        print(f"  - 상차 거래처: {client.name} (GPS: {client.latitude}, {client.longitude})")
                
                if order.delivery_client_id:
                    client = db.query(Client).filter(Client.id == order.delivery_client_id).first()
                    if client:
                        print(f"  - 하차 거래처: {client.name} (GPS: {client.latitude}, {client.longitude})")
                print()
        
        # Check vehicles
        vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).all()
        print(f"\n🚚 활성 차량: {len(vehicles)}대\n")
        
        if vehicles:
            # Group by type
            by_type = {}
            for v in vehicles:
                vtype = v.vehicle_type.value if v.vehicle_type else 'N/A'
                if vtype not in by_type:
                    by_type[vtype] = []
                by_type[vtype].append(v)
            
            for vtype, vlist in by_type.items():
                print(f"  {vtype}: {len(vlist)}대")
                if vlist:
                    v = vlist[0]
                    print(f"    예: {v.code} (팔레트: {v.max_pallets}, 중량: {v.max_weight_kg}kg)")
                    print(f"        차고지 GPS: ({v.garage_latitude}, {v.garage_longitude})")
        
        # Check temperature compatibility
        print(f"\n🌡️ 온도대별 호환 차량:")
        for temp_zone in TemperatureZone:
            compatible_types = []
            if temp_zone == TemperatureZone.FROZEN:
                compatible_types = [VehicleType.FROZEN, VehicleType.DUAL]
            elif temp_zone == TemperatureZone.REFRIGERATED:
                compatible_types = [VehicleType.REFRIGERATED, VehicleType.DUAL]
            elif temp_zone == TemperatureZone.AMBIENT:
                compatible_types = [VehicleType.AMBIENT, VehicleType.DUAL]
            
            compatible_vehicles = [v for v in vehicles if v.vehicle_type in compatible_types]
            print(f"  {temp_zone.value}: {len(compatible_vehicles)}대 ({', '.join([t.value for t in compatible_types])})")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
