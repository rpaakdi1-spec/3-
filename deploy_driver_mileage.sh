#!/bin/bash
# 운전자별 주행거리 계산 기능 배포 스크립트
# 작성일: 2026-03-03
# 설명: 차량 테이블의 driver_name 기반 운전자별 주행거리 집계 기능 배포

set -e

echo "🚀 운전자별 주행거리 계산 기능 배포 시작..."
echo ""

# 1. 저장소 업데이트
echo "📥 1단계: 코드 업데이트"
cd /root/uvis
git stash  # 기존 변경사항 임시 저장
git pull origin main
echo "✅ 코드 업데이트 완료"
echo ""

# 2. 데이터베이스 마이그레이션 실행
echo "🗄️  2단계: 데이터베이스 마이그레이션"
echo "driver_id를 NULL 허용으로 변경 중..."

cat backend/migrations/fix_driver_daily_mileage_nullable.sql | \
docker compose exec -T db psql -U uvis_user -d uvis_db

if [ $? -eq 0 ]; then
    echo "✅ 데이터베이스 마이그레이션 완료"
else
    echo "⚠️  마이그레이션 실패 (이미 적용되었을 수 있음)"
fi
echo ""

# 3. 백엔드 재빌드 및 재시작
echo "🔧 3단계: 백엔드 서비스 재빌드"
docker compose build backend
echo "✅ 백엔드 빌드 완료"
echo ""

echo "♻️  4단계: 백엔드 서비스 재시작"
docker compose up -d backend
echo "⏳ 서비스 시작 대기 중 (20초)..."
sleep 20
echo "✅ 백엔드 재시작 완료"
echo ""

# 4. 서비스 상태 확인
echo "🔍 5단계: 서비스 상태 확인"
docker compose ps
echo ""

# 5. 운전자 주행거리 계산 테스트
echo "🧪 6단계: 운전자 주행거리 계산 테스트"
echo ""
docker compose exec -T backend python3 <<'EOF'
from datetime import date, timedelta
from app.core.database import get_db
from app.services.driver_mileage_service import DriverMileageService

db = next(get_db())
service = DriverMileageService(db)
yesterday = date.today() - timedelta(days=1)

print(f"🚗 {yesterday} 운전자별 주행거리 계산 시작...\n")
results = service.calculate_driver_mileage_from_vehicle(yesterday)

if results:
    print(f"✅ 총 {len(results)}명 운전자 계산 완료\n")
    print("="*110)
    print(f"{'운전자명':<12} | {'주행(km)':>10} | {'시간(분)':>9} | {'차량수':>7} | {'평균속도':>9} | {'최고속도':>9}")
    print("="*110)
    
    for m in sorted(results, key=lambda x: x.total_distance_km, reverse=True)[:15]:
        driver_name = m.notes.replace("차량기반:", "") if m.notes else "미지정"
        print(f"{driver_name:<12} | {m.total_distance_km:>10.2f} | {m.total_driving_minutes:>9} | "
              f"{m.vehicle_count:>7} | {m.avg_speed_kmh:>9.1f} | {m.max_speed_kmh:>9.1f}")
    
    print("="*110)
    print()
else:
    print("⚠️  계산된 운전자 없음 (GPS 데이터 또는 운전자 정보 확인 필요)")
    print()

db.close()
EOF

echo ""
echo "✅ 배포 완료!"
echo ""
echo "📊 API 사용법:"
echo "  # 일별 운전자 주행거리 조회"
echo "  curl \"http://localhost/api/v1/driver-mileage/daily?target_date=2026-03-02\""
echo ""
echo "  # 운전자명으로 검색"
echo "  curl \"http://localhost/api/v1/driver-mileage/daily?driver_name=박운송\""
echo ""
echo "  # 운전자 주행거리 재계산"
echo "  curl -X POST \"http://localhost/api/v1/driver-mileage/calculate?target_date=2026-03-02\""
echo ""
