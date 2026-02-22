#!/bin/bash
# 🚨 긴급 배포: 배차 번호 중복 오류 수정
# 실행: bash deploy_dispatch_number_fix.sh

echo "=================================================="
echo "🚨 긴급 배포: 배차 번호 중복 오류 수정"
echo "=================================================="
echo ""

# 1. 백엔드 디렉터리로 이동
echo "📂 Step 1: 백엔드 디렉터리로 이동..."
cd /root/uvis/backend || { echo "❌ 디렉터리 이동 실패"; exit 1; }
echo "✅ 현재 위치: $(pwd)"
echo ""

# 2. 최신 코드 가져오기
echo "📥 Step 2: 최신 코드 가져오기..."
git fetch origin main
git stash  # 로컬 변경사항 임시 저장
git pull origin main
if [ $? -eq 0 ]; then
    echo "✅ 코드 업데이트 성공"
else
    echo "❌ 코드 업데이트 실패"
    exit 1
fi
echo ""

# 3. 변경사항 확인
echo "🔍 Step 3: 변경사항 확인..."
echo "최근 커밋:"
git log --oneline -1
echo ""
echo "변경된 부분:"
grep -A 2 "배차 번호 생성" app/services/cvrptw_service.py
echo ""

# 4. 파일 백업
echo "💾 Step 4: 현재 파일 백업..."
BACKUP_FILE="app/services/cvrptw_service.py.backup_$(date +%Y%m%d_%H%M%S)"
docker cp uvis-backend:/app/app/services/cvrptw_service.py "$BACKUP_FILE"
echo "✅ 백업 완료: $BACKUP_FILE"
echo ""

# 5. 파일 복사
echo "📤 Step 5: 수정된 파일을 컨테이너로 복사..."
docker cp app/services/cvrptw_service.py uvis-backend:/app/app/services/cvrptw_service.py
if [ $? -eq 0 ]; then
    echo "✅ 파일 복사 성공"
else
    echo "❌ 파일 복사 실패"
    exit 1
fi
echo ""

# 6. 컨테이너 재시작
echo "🔄 Step 6: 컨테이너 재시작..."
docker restart uvis-backend
sleep 10
echo "✅ 재시작 완료"
echo ""

# 7. 컨테이너 상태 확인
echo "🔍 Step 7: 컨테이너 상태 확인..."
if docker ps | grep -q uvis-backend; then
    echo "✅ 컨테이너 실행 중"
else
    echo "❌ 컨테이너 실행 실패"
    exit 1
fi
echo ""

# 8. 로그 확인
echo "📋 Step 8: 컨테이너 로그 확인..."
docker logs uvis-backend --tail 20
echo ""

echo "=================================================="
echo "✅ 배포 완료!"
echo "=================================================="
echo ""
echo "📋 다음 단계:"
echo "1. 브라우저에서 배차 최적화 페이지 이동"
echo "2. 주문 선택 (예: 27, 28, 30번)"
echo "3. '배차 최적화' 버튼 클릭"
echo "4. 에러 없이 배차가 생성되는지 확인"
echo ""
echo "🔍 확인할 사항:"
echo "   ✅ UniqueViolation 에러 없음"
echo "   ✅ 모든 배차가 정상 생성됨"
echo "   ✅ dispatch_number에 20자리 숫자 포함 (마이크로초)"
echo ""
echo "📞 문제 발생 시:"
echo "   docker cp $BACKUP_FILE uvis-backend:/app/app/services/cvrptw_service.py"
echo "   docker restart uvis-backend"
echo ""
echo "=================================================="
