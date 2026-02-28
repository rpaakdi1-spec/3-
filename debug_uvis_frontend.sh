#!/bin/bash

echo "=== UVIS Frontend Debugging Script ==="
echo ""

# Check current date/time
echo "1. Current Server Date/Time:"
date
echo ""

# Test API with various date ranges
echo "2. Testing API Endpoints:"
echo ""

echo "a) Today (2026-02-28):"
curl -s "http://localhost:8000/api/v1/vehicles/analytics/fleet?start_date=2026-02-28&end_date=2026-02-28" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"  Total: {data['total_vehicles']}, Active: {data['active_vehicles']}, Distance: {data['total_distance_km']} km, Vehicle Stats Count: {len(data['vehicle_stats'])}\")"
echo ""

echo "b) Yesterday (2026-02-27):"
curl -s "http://localhost:8000/api/v1/vehicles/analytics/fleet?start_date=2026-02-27&end_date=2026-02-27" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"  Total: {data['total_vehicles']}, Active: {data['active_vehicles']}, Distance: {data['total_distance_km']} km, Vehicle Stats Count: {len(data['vehicle_stats'])}\")"
echo ""

echo "c) Last 7 days (2026-02-21 to 2026-02-28):"
curl -s "http://localhost:8000/api/v1/vehicles/analytics/fleet?start_date=2026-02-21&end_date=2026-02-28" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"  Total: {data['total_vehicles']}, Active: {data['active_vehicles']}, Distance: {data['total_distance_km']} km, Vehicle Stats Count: {len(data['vehicle_stats'])}\")"
echo ""

echo "3. Checking GPS Data:"
docker exec -it uvis-db psql -U uvis_user -d uvis_db -t -c "
SELECT 
  COUNT(*) AS total_logs,
  COUNT(DISTINCT tid_id) AS unique_devices,
  MAX(created_at) AS latest_log,
  MIN(created_at) AS earliest_log,
  COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) AS logs_last_24h,
  COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) AS logs_last_7d
FROM vehicle_gps_logs;
"
echo ""

echo "4. Checking Vehicle UVIS Assignments:"
docker exec -it uvis-db psql -U uvis_user -d uvis_db -t -c "
SELECT 
  COUNT(*) AS total_vehicles,
  COUNT(CASE WHEN uvis_device_id IS NOT NULL THEN 1 END) AS with_device,
  COUNT(CASE WHEN uvis_device_id IS NULL THEN 1 END) AS without_device
FROM vehicles
WHERE is_active = true;
"
echo ""

echo "5. Sample Vehicle Stats from API:"
curl -s "http://localhost:8000/api/v1/vehicles/analytics/fleet?start_date=2026-02-21&end_date=2026-02-28" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'  Total Vehicles: {data[\"total_vehicles\"]}')
print(f'  Active Vehicles: {data[\"active_vehicles\"]}')
print(f'  Total Distance: {data[\"total_distance_km\"]} km')
print(f'  Vehicle Stats Count: {len(data[\"vehicle_stats\"])}')
print()
if data['vehicle_stats']:
    print('  Sample Vehicle Stats (first 3):')
    for v in data['vehicle_stats'][:3]:
        print(f'    - Vehicle {v[\"vehicle_id\"]} ({v[\"vehicle_plate\"]}):')
        print(f'      Distance: {v[\"total_distance_km\"]} km, Max Speed: {v[\"max_speed_kmh\"]} km/h')
        print(f'      Avg Speed: {v[\"avg_speed_kmh\"]} km/h, Engine On: {v[\"engine_on_ratio\"]}%')
else:
    print('  No vehicle stats returned')
"
echo ""

echo "6. Frontend Container Status:"
docker ps --filter name=uvis-frontend --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "7. Frontend Build Time:"
docker exec -it uvis-frontend stat /usr/share/nginx/html/index.html | grep Modify
echo ""

echo "8. Test Frontend API Endpoint (as browser would see it):"
curl -s "http://139.150.11.99/api/v1/vehicles/analytics/fleet?start_date=2026-02-21&end_date=2026-02-28" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"  Active Vehicles: {data['active_vehicles']}, Vehicle Stats: {len(data['vehicle_stats'])}\")"
echo ""

echo "=== Debug Complete ==="
