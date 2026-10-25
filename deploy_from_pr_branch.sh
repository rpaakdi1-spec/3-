#!/bin/bash
# 운전자별 주행거리 계산 - PR 브랜치에서 직접 배포
# genspark_ai_developer 브랜치의 코드를 서버에 적용

set -e

echo "🚀 운전자별 주행거리 계산 기능 배포 (PR 브랜치)"
echo ""

cd /root/uvis

# 1. 변경사항 백업
echo "📦 1단계: 현재 변경사항 백업"
git stash
echo ""

# 2. PR 브랜치 가져오기 및 체크아웃
echo "📥 2단계: PR 브랜치 가져오기"
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer
echo "✅ 코드 업데이트 완료"
echo ""

# 3. 데이터베이스 마이그레이션
echo "🗄️  3단계: 데이터베이스 마이그레이션"
if [ -f backend/migrations/fix_driver_daily_mileage_nullable.sql ]; then
    cat backend/migrations/fix_driver_daily_mileage_nullable.sql | \
    docker compose exec -T db psql -U uvis_user -d uvis_db
    echo "✅ 마이그레이션 완료"
else
    echo "⚠️  마이그레이션 파일 없음"
fi
echo ""

# 4. 백엔드 재빌드
echo "🔧 4단계: 백엔드 재빌드"
docker compose build backend
echo ""

# 5. 백엔드 재시작
echo "♻️  5단계: 백엔드 재시작"
docker compose up -d backend
sleep 20
echo ""

# 6. 서비스 상태 확인
echo "🔍 6단계: 서비스 상태 확인"
docker compose ps | grep backend
echo ""

# 7. 테스트
echo "🧪 7단계: 기능 테스트"
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
else:
    print("⚠️  계산된 운전자 없음")

db.close()
EOF

echo ""
echo "✅ 배포 완료!"
echo ""
echo "⚠️  참고: 현재 genspark_ai_developer 브랜치를 사용 중입니다."
echo "   main 브랜치로 돌아가려면: git checkout main"
echo ""
