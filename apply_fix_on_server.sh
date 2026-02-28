#!/bin/bash
# 서버에서 이 명령어를 실행하세요

cd /root/uvis

# Line 199 수정: hours=1 → hours=24
sed -i '199s/timedelta(hours=1)/timedelta(hours=24)  # 1시간 → 24시간으로 완화/' backend/app/services/vehicle_analytics_service.py

# Line 247 수정: hours=1 → hours=24  
sed -i '247s/timedelta(hours=1)/timedelta(hours=24)  # 1시간 → 24시간으로 완화/' backend/app/services/vehicle_analytics_service.py

# 수정 확인
echo "=== 수정된 내용 확인 ==="
grep -n "timedelta(hours=" backend/app/services/vehicle_analytics_service.py

# Backend 재시작
echo ""
echo "=== Backend 재시작 ==="
docker-compose restart backend

echo ""
echo "✅ 수정 완료! 30초 후 API 테스트..."
sleep 30

echo ""
echo "=== API 테스트 ==="
curl "http://localhost:8000/api/v1/vehicles/analytics/fleet?start_date=2026-02-27&end_date=2026-02-27" | jq '.active_vehicles'
