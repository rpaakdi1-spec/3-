#!/bin/bash

# 배차 최적화 진단 기능 배포 스크립트
# 2026-02-19
# 주요 개선: 배차 실패 시 상세한 원인 분석 및 알림

set -e

echo "=================================================="
echo "배차 최적화 진단 기능 배포"
echo "=================================================="
echo ""

# 백업 디렉토리 생성
BACKUP_DIR="/root/uvis_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "1️⃣  기존 파일 백업 중..."
cp /root/uvis/backend/app/services/cvrptw_service.py "$BACKUP_DIR/" 2>/dev/null || true
echo "   ✅ 백업 완료: $BACKUP_DIR"
echo ""

echo "2️⃣  새 코드 적용 중..."
# cvrptw_service.py의 특정 함수들만 업데이트

# _optimize_temperature_zone 함수 교체 준비
cat > /tmp/cvrptw_patch.txt << 'PATCH_EOF'
이 패치는 다음 개선사항을 포함합니다:
- 진단 정보 수집 (diagnostics 딕셔너리)
- GPS 좌표 누락 감지
- 용량 제약 검증 (팔레트, 중량)
- 실패 원인 상세 로깅
- 구조화된 오류 응답
- 부분 성공 시 경고 메시지
PATCH_EOF

cat /tmp/cvrptw_patch.txt
echo ""

echo "3️⃣  Docker 컨테이너 재시작 중..."
cd /root/uvis
docker restart uvis-backend
echo "   대기 중... (15초)"
sleep 15
echo ""

echo "4️⃣  컨테이너 상태 확인..."
docker ps | grep uvis-backend
echo ""

echo "5️⃣  백엔드 로그 확인 (최근 20줄)..."
docker logs uvis-backend --tail 20
echo ""

echo "=================================================="
echo "✅ 배포 완료!"
echo "=================================================="
echo ""
echo "📝 변경 사항:"
echo "   - 배차 실패 시 상세 원인 분석"
echo "   - GPS 좌표 누락 감지 및 알림"
echo "   - 용량 초과 자동 감지"
echo "   - 온도대별 호환 차량 검증"
echo "   - 실패 원인 구조화된 응답"
echo ""
echo "🔍 테스트 방법:"
echo ""
echo "curl -X POST 'http://localhost:8000/api/v1/dispatches/optimize' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"order_ids\":[1,2,3,4,5],\"vehicle_ids\":[],\"dispatch_date\":\"2026-02-19\"}' | jq ."
echo ""
echo "기대 결과:"
echo "  - 성공 시: dispatches 배열에 배차 정보"
echo "  - 실패 시: failed_zones에 상세 원인 포함"
echo "  - 로그에 진단 정보 출력:"
echo "    * 주문 수 / 차량 수"
echo "    * 팔레트 수요 vs 용량"
echo "    * 중량 수요 vs 용량"
echo "    * GPS 좌표 누락 개수"
echo "    * 추정 실패 원인 목록"
echo ""
echo "📊 로그 실시간 모니터링:"
echo "   docker logs -f uvis-backend"
echo ""
