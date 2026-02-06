#!/bin/bash

##############################################################################
# UVIS 빠른 수정 메뉴
# 목적: 일반적인 문제를 빠르게 수정
##############################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO_DIR="/root/uvis"

clear
echo "=================================================================="
echo -e "${BLUE}UVIS 빠른 수정 메뉴${NC}"
echo "=================================================================="
echo ""
echo "무엇을 수정하시겠습니까?"
echo ""
echo "1) 백엔드 재시작"
echo "2) 프론트엔드 재빌드 및 재시작"
echo "3) 데이터베이스 재시작"
echo "4) 모든 컨테이너 재시작"
echo "5) Git 저장소 최신 코드로 업데이트"
echo "6) 환경 설정 파일 수정"
echo "7) 전체 시스템 완전 재설치"
echo "8) 시스템 진단만 실행"
echo "0) 종료"
echo ""
read -p "선택 (0-8): " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}백엔드 재시작 중...${NC}"
        cd "$REPO_DIR"
        docker-compose restart backend
        sleep 3
        
        # 헬스 체크
        BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
        if [ "$BACKEND_STATUS" == "200" ]; then
            echo -e "${GREEN}✓ 백엔드 재시작 완료: $BACKEND_STATUS OK${NC}"
        else
            echo -e "${RED}✗ 백엔드 상태: $BACKEND_STATUS${NC}"
        fi
        ;;
        
    2)
        echo ""
        echo -e "${BLUE}프론트엔드 재빌드 및 재시작 중...${NC}"
        cd "$REPO_DIR/frontend" || exit 1
        
        # 이전 빌드 삭제
        if [ -d "dist" ]; then
            echo "이전 빌드 삭제 중..."
            rm -rf dist
        fi
        
        # 빌드
        echo "빌드 중... (시간이 걸릴 수 있습니다)"
        if npm run build; then
            echo -e "${GREEN}✓ 빌드 성공${NC}"
            
            # 재시작
            cd "$REPO_DIR" || exit 1
            echo "Docker 이미지 재빌드 중..."
            docker-compose build --no-cache frontend
            echo "프론트엔드 컨테이너 시작 중..."
            docker-compose up -d frontend
            
            echo "서비스 시작 대기 중... (5초)"
            sleep 5
            
            # 헬스 체크
            FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null)
            if [ "$FRONTEND_STATUS" == "200" ]; then
                echo -e "${GREEN}✓ 프론트엔드 재시작 완료: $FRONTEND_STATUS OK${NC}"
                echo ""
                echo "접속 URL: http://139.150.11.99/"
                echo "브라우저 캐시 삭제: Ctrl + Shift + R"
            else
                echo -e "${RED}✗ 프론트엔드 상태: $FRONTEND_STATUS${NC}"
                echo "로그 확인: docker logs uvis-frontend --tail 50"
            fi
        else
            echo -e "${RED}✗ 빌드 실패${NC}"
            echo "오류를 확인하고 다시 시도하세요."
        fi
        ;;
        
    3)
        echo ""
        echo -e "${BLUE}데이터베이스 재시작 중...${NC}"
        cd "$REPO_DIR"
        docker-compose restart uvis-db
        sleep 5
        
        # 헬스 체크
        if docker exec uvis-db pg_isready -U postgres > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 데이터베이스 재시작 완료${NC}"
        else
            echo -e "${RED}✗ 데이터베이스 연결 실패${NC}"
        fi
        ;;
        
    4)
        echo ""
        echo -e "${BLUE}모든 컨테이너 재시작 중...${NC}"
        cd "$REPO_DIR"
        docker-compose restart
        sleep 10
        
        # 헬스 체크
        echo "헬스 체크 중..."
        BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
        FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null)
        
        echo ""
        if [ "$BACKEND_STATUS" == "200" ]; then
            echo -e "${GREEN}✓ 백엔드: $BACKEND_STATUS OK${NC}"
        else
            echo -e "${RED}✗ 백엔드: $BACKEND_STATUS${NC}"
        fi
        
        if [ "$FRONTEND_STATUS" == "200" ]; then
            echo -e "${GREEN}✓ 프론트엔드: $FRONTEND_STATUS OK${NC}"
        else
            echo -e "${RED}✗ 프론트엔드: $FRONTEND_STATUS${NC}"
        fi
        ;;
        
    5)
        echo ""
        echo -e "${BLUE}Git 저장소 최신 코드로 업데이트 중...${NC}"
        cd "$REPO_DIR"
        
        # 로컬 변경사항 백업
        if [[ -n $(git status -s) ]]; then
            BACKUP_DIR="/root/uvis_backup_$(date +%Y%m%d_%H%M%S)"
            echo "백업 생성 중: $BACKUP_DIR"
            cp -r "$REPO_DIR" "$BACKUP_DIR"
            echo -e "${GREEN}✓ 백업 완료${NC}"
        fi
        
        # 최신 코드 가져오기
        git fetch origin genspark_ai_developer
        git reset --hard origin/genspark_ai_developer
        git clean -fd
        
        echo -e "${GREEN}✓ 최신 코드 업데이트 완료${NC}"
        echo ""
        echo "현재 커밋: $(git rev-parse --short HEAD)"
        echo ""
        echo "이제 프론트엔드를 재빌드하고 컨테이너를 재시작하세요:"
        echo "  ./quick_fix.sh 선택 2번"
        ;;
        
    6)
        echo ""
        echo -e "${BLUE}환경 설정 파일 수정 중...${NC}"
        
        # 프론트엔드 .env 확인 및 수정
        if [ ! -f "$REPO_DIR/frontend/.env" ]; then
            echo "프론트엔드 .env 생성 중..."
            cat > "$REPO_DIR/frontend/.env" << 'EOF'
# API Configuration
VITE_API_URL=/api/v1
EOF
            echo -e "${GREEN}✓ 프론트엔드 .env 생성 완료${NC}"
        else
            # VITE_API_URL 확인 및 수정
            if grep -q "VITE_API_URL=http" "$REPO_DIR/frontend/.env"; then
                echo "VITE_API_URL을 상대 경로로 수정 중..."
                sed -i 's|VITE_API_URL=.*|VITE_API_URL=/api/v1|g' "$REPO_DIR/frontend/.env"
                echo -e "${GREEN}✓ VITE_API_URL 수정 완료${NC}"
            else
                echo -e "${GREEN}✓ 환경 설정이 이미 올바릅니다${NC}"
            fi
        fi
        
        echo ""
        echo "현재 프론트엔드 .env 내용:"
        cat "$REPO_DIR/frontend/.env"
        ;;
        
    7)
        echo ""
        echo -e "${RED}경고: 전체 시스템을 완전히 재설치합니다${NC}"
        read -p "계속하시겠습니까? (yes/no): " confirm
        
        if [ "$confirm" == "yes" ]; then
            echo ""
            echo -e "${BLUE}전체 시스템 재설치 중...${NC}"
            
            # fix_all_errors.sh 실행
            if [ -f "$REPO_DIR/fix_all_errors.sh" ]; then
                chmod +x "$REPO_DIR/fix_all_errors.sh"
                "$REPO_DIR/fix_all_errors.sh"
            else
                echo -e "${RED}✗ fix_all_errors.sh 파일을 찾을 수 없습니다${NC}"
            fi
        else
            echo "취소되었습니다."
        fi
        ;;
        
    8)
        echo ""
        # diagnose_system.sh 실행
        if [ -f "$REPO_DIR/diagnose_system.sh" ]; then
            chmod +x "$REPO_DIR/diagnose_system.sh"
            "$REPO_DIR/diagnose_system.sh"
        else
            echo -e "${RED}✗ diagnose_system.sh 파일을 찾을 수 없습니다${NC}"
        fi
        ;;
        
    0)
        echo "종료합니다."
        exit 0
        ;;
        
    *)
        echo -e "${RED}잘못된 선택입니다.${NC}"
        ;;
esac

echo ""
echo "=================================================================="
read -p "계속하려면 Enter를 누르세요..."
