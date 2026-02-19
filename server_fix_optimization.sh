#!/bin/bash

# 서버 측 배차 최적화 수정 스크립트
# 서버에서 직접 실행: bash server_fix_optimization.sh

set -e

echo "=================================================="
echo "배차 최적화 엔드포인트 수정 (서버 측)"
echo "=================================================="
echo ""

BACKEND_DIR="/root/uvis/backend/app/api"
FILE="$BACKEND_DIR/dispatches.py"
BACKUP="$FILE.backup_$(date +%Y%m%d_%H%M%S)"

# 현재 디렉토리 확인
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ 에러: $BACKEND_DIR 디렉토리를 찾을 수 없습니다."
    exit 1
fi

cd "$BACKEND_DIR"
echo "✓ 작업 디렉토리: $BACKEND_DIR"
echo ""

# 백업
echo "📦 원본 파일 백업..."
cp "$FILE" "$BACKUP"
echo "✓ 백업 완료: $BACKUP"
echo ""

# 현재 파일 상태 확인
echo "📋 현재 파일 상태 (29-56번 라인):"
sed -n '29,56p' "$FILE"
echo ""

# Import 확인
echo "📋 Import 상태:"
grep -n "AdvancedDispatchOptimizationService" "$FILE" || echo "⚠️ AdvancedDispatchOptimizationService import 없음"
grep -n "DispatchOptimizationService" "$FILE" || echo "⚠️ DispatchOptimizationService import 없음"
echo ""

echo "=================================================="
echo "수정 방법 선택"
echo "=================================================="
echo ""
echo "현재 파일 상태를 확인하고 아래 방법 중 하나를 선택하세요:"
echo ""
echo "방법 1: 자동 수정 (sed 사용)"
echo "방법 2: 수동 수정 (vi 편집기)"
echo "방법 3: 파일 전체 교체"
echo ""

read -p "선택 (1/2/3): " -n 1 -r
echo ""
echo ""

case $REPLY in
    1)
        echo "🔧 자동 수정 시작..."
        echo ""
        
        # Import 추가 (없으면)
        if ! grep -q "from app.services.cvrptw_service import AdvancedDispatchOptimizationService" "$FILE"; then
            echo "1. Import 추가..."
            sed -i '22a from app.services.cvrptw_service import AdvancedDispatchOptimizationService' "$FILE"
            echo "✓ Import 추가 완료"
        else
            echo "✓ Import 이미 존재"
        fi
        echo ""
        
        # 44번 라인 수정 (optimizer.optimize_dispatch -> optimizer.optimize_dispatch_cvrptw)
        echo "2. 함수 호출 수정 (44번 라인)..."
        sed -i '44s/optimizer\.optimize_dispatch(/optimizer.optimize_dispatch_cvrptw(/' "$FILE"
        echo "✓ 함수 호출 수정 완료"
        echo ""
        
        # 47번 라인 수정 (dispatch_date 뒤에 콤마)
        echo "3. dispatch_date 콤마 추가 (47번 라인)..."
        sed -i '47s/dispatch_date=request\.dispatch_date$/dispatch_date=request.dispatch_date,/' "$FILE"
        echo "✓ 콤마 추가 완료"
        echo ""
        
        # 파라미터 추가 확인
        if ! grep -q "time_limit_seconds=15" "$FILE"; then
            echo "4. 추가 파라미터 삽입..."
            sed -i '47a\        time_limit_seconds=15,\n        use_time_windows=False,\n        use_real_routing=False' "$FILE"
            echo "✓ 파라미터 추가 완료"
        else
            echo "✓ 파라미터 이미 존재"
        fi
        echo ""
        
        echo "✅ 자동 수정 완료!"
        ;;
        
    2)
        echo "📝 수동 수정 안내..."
        echo ""
        echo "vi 편집기로 파일을 엽니다. 다음을 수정하세요:"
        echo ""
        echo "1. 22-23번 라인 (Import):"
        echo "   from app.services.dispatch_optimization_service import DispatchOptimizationService"
        echo "   from app.services.cvrptw_service import AdvancedDispatchOptimizationService"
        echo ""
        echo "2. 44번 라인 (Optimizer 인스턴스):"
        echo "   optimizer = AdvancedDispatchOptimizationService(db)"
        echo ""
        echo "3. 46-52번 라인 (함수 호출):"
        echo "   result = await optimizer.optimize_dispatch_cvrptw("
        echo "       order_ids=request.order_ids,"
        echo "       vehicle_ids=request.vehicle_ids,"
        echo "       dispatch_date=request.dispatch_date,"
        echo "       time_limit_seconds=15,"
        echo "       use_time_windows=False,"
        echo "       use_real_routing=False"
        echo "   )"
        echo ""
        read -p "vi 편집기를 열까요? (y/n): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            vi "$FILE"
        fi
        ;;
        
    3)
        echo "📥 파일 전체 교체..."
        echo ""
        echo "로컬에서 다음 명령어를 실행하세요:"
        echo ""
        echo "scp /home/user/webapp/backend/app/api/dispatches.py root@139.150.11.99:/root/uvis/backend/app/api/"
        echo ""
        echo "파일을 업로드한 후 이 스크립트를 다시 실행하세요."
        exit 0
        ;;
        
    *)
        echo "❌ 잘못된 선택"
        exit 1
        ;;
esac

# 수정 결과 확인
echo ""
echo "=================================================="
echo "📋 수정 결과 확인 (29-56번 라인)"
echo "=================================================="
sed -n '29,56p' "$FILE"
echo ""

# Import 재확인
echo "=================================================="
echo "📋 Import 확인"
echo "=================================================="
grep -n "from app.services" "$FILE" | head -5
echo ""

# Docker 재시작 확인
read -p "Docker 컨테이너를 재시작할까요? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔄 Docker 컨테이너 재시작 중..."
    cd /root/uvis
    docker restart uvis-backend
    echo "⏳ 10초 대기..."
    sleep 10
    echo ""
    
    echo "✓ 컨테이너 상태:"
    docker ps | grep uvis-backend
    echo ""
    
    echo "📋 최근 로그 (에러 확인):"
    docker logs uvis-backend --tail 20
    echo ""
    
    echo "=================================================="
    echo "✅ 배포 완료!"
    echo "=================================================="
    echo ""
    echo "🧪 테스트 명령어:"
    echo ""
    echo "curl -X POST \"http://localhost:8000/api/v1/dispatches/optimize\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{ \"order_ids\": [1, 2], \"vehicle_ids\": [], \"dispatch_date\": \"2026-02-19\" }' | jq ."
    echo ""
else
    echo ""
    echo "⚠️ 수동으로 재시작하세요:"
    echo "   cd /root/uvis && docker restart uvis-backend"
    echo ""
fi

echo "=================================================="
echo "백업 파일: $BACKUP"
echo "=================================================="
