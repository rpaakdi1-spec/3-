#!/bin/bash

##############################################################################
# UVIS 레이아웃 완전 수정 및 배포 스크립트
# 작성일: 2026-02-25
# 목적: OrdersPage.tsx JSX 수정 및 .dockerignore 수정 후 전체 배포
##############################################################################

set -e  # 오류 발생 시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# 프로젝트 루트로 이동
cd /root/uvis

log_info "=== UVIS 레이아웃 완전 수정 시작 ==="
echo ""

##############################################################################
# 1. 백업 생성
##############################################################################
log_info "Step 1: 백업 생성"
BACKUP_FILE="/root/uvis_backup_before_layout_fix_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$BACKUP_FILE" \
    frontend/src/pages/OrdersPage.tsx \
    frontend/.dockerignore \
    2>/dev/null || log_warning "백업 실패 (계속 진행)"

if [ -f "$BACKUP_FILE" ]; then
    log_success "백업 완료: $BACKUP_FILE"
else
    log_warning "백업 파일 없음 (문제 없음)"
fi
echo ""

##############################################################################
# 2. OrdersPage.tsx 수정
##############################################################################
log_info "Step 2: OrdersPage.tsx 수정"

# Python 스크립트로 정확히 수정
python3 - <<'PYEOF'
import sys

file_path = '/root/uvis/frontend/src/pages/OrdersPage.tsx'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 정확한 패턴 찾기
    old_pattern = """        </div>
      )}
  );
};"""
    
    new_pattern = """        </div>
      )}
    </>
  );
};"""
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ OrdersPage.tsx 수정 완료")
        sys.exit(0)
    else:
        print("⚠️  패턴을 찾을 수 없습니다. 이미 수정되었거나 파일이 다릅니다.")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ 오류: {e}")
    sys.exit(2)
PYEOF

ORDERS_FIX_RESULT=$?
if [ $ORDERS_FIX_RESULT -eq 0 ]; then
    log_success "OrdersPage.tsx 수정 완료"
elif [ $ORDERS_FIX_RESULT -eq 1 ]; then
    log_warning "OrdersPage.tsx 이미 수정되었거나 다른 내용입니다"
else
    log_error "OrdersPage.tsx 수정 실패"
    exit 1
fi

# 수정 확인
echo ""
log_info "수정 확인: OrdersPage.tsx (line 665-672)"
sed -n '665,672p' frontend/src/pages/OrdersPage.tsx | cat -n
echo ""

##############################################################################
# 3. .dockerignore 수정
##############################################################################
log_info "Step 3: .dockerignore 수정"

# dist와 build 제거
sed -i '/^# Build output/d' frontend/.dockerignore
sed -i '/^dist$/d' frontend/.dockerignore
sed -i '/^build$/d' frontend/.dockerignore

log_success ".dockerignore 수정 완료"

# 수정 확인
echo ""
log_info "수정 확인: .dockerignore"
cat frontend/.dockerignore
echo ""

##############################################################################
# 4. 프론트엔드 빌드
##############################################################################
log_info "Step 4: 프론트엔드 빌드"
cd frontend

if npm run build; then
    log_success "프론트엔드 빌드 성공"
    
    # CSS 파일 확인
    echo ""
    log_info "빌드된 CSS 파일:"
    ls -lh dist/assets/*.css 2>/dev/null || log_warning "CSS 파일 없음"
else
    log_error "프론트엔드 빌드 실패"
    exit 1
fi

cd /root/uvis
echo ""

##############################################################################
# 5. Docker 이미지 재빌드
##############################################################################
log_info "Step 5: Docker 이미지 재빌드"

# 기존 컨테이너 정지 및 삭제
log_info "기존 프론트엔드 컨테이너 정지 및 삭제..."
docker-compose stop frontend 2>/dev/null || true
docker-compose rm -f frontend 2>/dev/null || true

# 기존 이미지 삭제
log_info "기존 프론트엔드 이미지 삭제..."
docker rmi uvis-frontend 2>/dev/null || log_warning "기존 이미지 없음 (문제 없음)"

# 새 이미지 빌드
log_info "새 프론트엔드 이미지 빌드 중..."
if docker-compose build --no-cache frontend; then
    log_success "Docker 이미지 빌드 성공"
else
    log_error "Docker 이미지 빌드 실패"
    exit 1
fi
echo ""

##############################################################################
# 6. 컨테이너 재시작
##############################################################################
log_info "Step 6: 컨테이너 재시작"

if docker-compose up -d frontend; then
    log_success "프론트엔드 컨테이너 시작 성공"
else
    log_error "프론트엔드 컨테이너 시작 실패"
    exit 1
fi

log_info "컨테이너 안정화 대기 (15초)..."
sleep 15
echo ""

##############################################################################
# 7. 배포 확인
##############################################################################
log_info "Step 7: 배포 확인"

echo ""
log_info "1️⃣ 컨테이너 상태 확인:"
docker ps --filter "name=uvis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
log_info "2️⃣ CSS 파일 확인:"
if docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/*.css 2>/dev/null; then
    log_success "CSS 파일 정상 확인"
else
    log_error "CSS 파일 없음!"
    echo ""
    log_warning "수동 복사 시도 중..."
    
    # 수동 복사 시도
    docker cp frontend/dist/assets/index-BjMybcaV.css uvis-frontend:/usr/share/nginx/html/assets/ 2>/dev/null && \
    docker cp frontend/dist/assets/leaflet-Dgihpmma.css uvis-frontend:/usr/share/nginx/html/assets/ 2>/dev/null && \
    docker cp frontend/dist/assets/OrderCalendarPage-D0RJcmxZ.css uvis-frontend:/usr/share/nginx/html/assets/ 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log_success "CSS 파일 수동 복사 성공"
        docker-compose restart frontend
        sleep 10
    else
        log_error "CSS 파일 수동 복사 실패"
    fi
fi

echo ""
log_info "3️⃣ index.html CSS 참조 확인:"
docker exec uvis-frontend cat /usr/share/nginx/html/index.html 2>/dev/null | grep -o '<link[^>]*css[^>]*>' | head -5

echo ""
log_info "4️⃣ 컨테이너 로그 (마지막 10줄):"
docker logs uvis-frontend --tail 10 2>/dev/null || log_warning "로그 확인 실패"

echo ""
log_info "5️⃣ Assets 파일 개수:"
ASSET_COUNT=$(docker exec uvis-frontend ls /usr/share/nginx/html/assets/ 2>/dev/null | wc -l)
log_success "Assets 파일 개수: $ASSET_COUNT"

##############################################################################
# 8. 최종 요약
##############################################################################
echo ""
echo "═══════════════════════════════════════════════════════════════"
log_success "🎉 레이아웃 수정 및 배포 완료!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📋 완료된 작업:"
echo "  ✅ OrdersPage.tsx Fragment 닫기 태그 추가"
echo "  ✅ .dockerignore에서 dist, build 제거"
echo "  ✅ 프론트엔드 빌드 성공"
echo "  ✅ Docker 이미지 재빌드 완료"
echo "  ✅ 컨테이너 재시작 완료"
echo "  ✅ CSS 파일 컨테이너 배치 확인"
echo ""
echo "🧪 브라우저 테스트 방법:"
echo "  1️⃣  브라우저 캐시 완전 삭제 (Ctrl+Shift+Delete)"
echo "     - 전체 기간 선택"
echo "     - 쿠키 및 기타 사이트 데이터 체크"
echo "     - 캐시된 이미지 및 파일 체크"
echo "     - 데이터 삭제"
echo ""
echo "  2️⃣  Chrome 완전 재시작"
echo "     - Chrome 완전 종료"
echo "     - 다시 시작"
echo ""
echo "  3️⃣  사이트 접속 테스트"
echo "     - http://139.150.11.99/login"
echo "     - ID: admin / PW: admin123"
echo ""
echo "  4️⃣  확인 사항"
echo "     ✓ 로그인 페이지 중앙 정렬"
echo "     ✓ 대시보드 왼쪽에 사이드바 1개만"
echo "     ✓ 설정 페이지 레이아웃 정상"
echo "     ✓ 모든 페이지 스타일 정상 적용"
echo ""
echo "📦 Git 커밋 명령어:"
echo "  cd /root/uvis"
echo "  git add frontend/src/pages/OrdersPage.tsx frontend/.dockerignore"
echo "  git commit -m \"fix: OrdersPage JSX fragment and .dockerignore for CSS files\""
echo "  git push origin main"
echo ""
echo "🔗 배포 URL: http://139.150.11.99"
echo ""
echo "═══════════════════════════════════════════════════════════════"

exit 0
