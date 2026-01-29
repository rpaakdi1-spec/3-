#!/bin/bash

###############################################################################
# Cold Chain Dispatch System - Deployment Script
# 
# 이 스크립트는 로컬에서 AWS ECS로 애플리케이션을 수동 배포합니다.
# GitHub Actions CI/CD 파이프라인이 없을 때 사용하거나 긴급 배포 시 사용합니다.
###############################################################################

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수: 로그 출력
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 설정
AWS_REGION="${AWS_REGION:-ap-northeast-2}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID}"
ECS_CLUSTER="${ECS_CLUSTER:-coldchain-production-cluster}"
ECS_BACKEND_SERVICE="${ECS_BACKEND_SERVICE:-coldchain-production-backend}"
ECS_FRONTEND_SERVICE="${ECS_FRONTEND_SERVICE:-coldchain-production-frontend}"
ECR_BACKEND_REPO="${ECR_BACKEND_REPO:-coldchain-production/backend}"
ECR_FRONTEND_REPO="${ECR_FRONTEND_REPO:-coldchain-production/frontend}"

# 배너 출력
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   Cold Chain Dispatch System - Deployment Script            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# AWS 계정 ID 자동 감지
if [ -z "$AWS_ACCOUNT_ID" ]; then
    log_info "AWS 계정 ID를 감지하는 중..."
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    log_success "AWS 계정 ID: $AWS_ACCOUNT_ID"
fi

# ECR URI 구성
ECR_BACKEND_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_BACKEND_REPO"
ECR_FRONTEND_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_FRONTEND_REPO"

# 배포할 서비스 선택
echo ""
log_info "배포할 서비스를 선택하세요:"
echo "  1) Backend만"
echo "  2) Frontend만"
echo "  3) 둘 다"
read -p "선택 (1-3): " service_choice

DEPLOY_BACKEND=false
DEPLOY_FRONTEND=false

case $service_choice in
    1)
        DEPLOY_BACKEND=true
        ;;
    2)
        DEPLOY_FRONTEND=true
        ;;
    3)
        DEPLOY_BACKEND=true
        DEPLOY_FRONTEND=true
        ;;
    *)
        log_error "잘못된 선택입니다."
        exit 1
        ;;
esac

# 이미지 태그 입력
echo ""
read -p "이미지 태그를 입력하세요 (기본값: latest): " IMAGE_TAG
IMAGE_TAG="${IMAGE_TAG:-latest}"

log_info "배포 설정:"
log_info "  - AWS Region: $AWS_REGION"
log_info "  - ECS Cluster: $ECS_CLUSTER"
log_info "  - Image Tag: $IMAGE_TAG"
log_info "  - Deploy Backend: $DEPLOY_BACKEND"
log_info "  - Deploy Frontend: $DEPLOY_FRONTEND"

echo ""
read -p "배포를 계속하시겠습니까? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    log_warning "배포가 취소되었습니다."
    exit 0
fi

# ECR 로그인
echo ""
log_info "ECR에 로그인하는 중..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
log_success "ECR 로그인 완료"

# Backend 배포
if [ "$DEPLOY_BACKEND" = true ]; then
    echo ""
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "Backend 배포 시작"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Docker 이미지 빌드
    log_info "Backend Docker 이미지 빌드 중..."
    docker build -t $ECR_BACKEND_REPO:$IMAGE_TAG ./backend
    log_success "Backend 이미지 빌드 완료"
    
    # 이미지 태그
    log_info "이미지 태그 설정 중..."
    docker tag $ECR_BACKEND_REPO:$IMAGE_TAG $ECR_BACKEND_URI:$IMAGE_TAG
    docker tag $ECR_BACKEND_REPO:$IMAGE_TAG $ECR_BACKEND_URI:latest
    
    # 이미지 푸시
    log_info "Backend 이미지를 ECR로 푸시 중..."
    docker push $ECR_BACKEND_URI:$IMAGE_TAG
    docker push $ECR_BACKEND_URI:latest
    log_success "Backend 이미지 푸시 완료"
    
    # ECS 서비스 업데이트
    log_info "Backend ECS 서비스 업데이트 중..."
    aws ecs update-service \
        --cluster $ECS_CLUSTER \
        --service $ECS_BACKEND_SERVICE \
        --force-new-deployment \
        --region $AWS_REGION \
        > /dev/null
    log_success "Backend 서비스 업데이트 시작"
    
    # 배포 대기
    log_info "Backend 서비스가 안정화될 때까지 대기 중... (최대 10분)"
    aws ecs wait services-stable \
        --cluster $ECS_CLUSTER \
        --services $ECS_BACKEND_SERVICE \
        --region $AWS_REGION
    log_success "Backend 배포 완료!"
fi

# Frontend 배포
if [ "$DEPLOY_FRONTEND" = true ]; then
    echo ""
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "Frontend 배포 시작"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Docker 이미지 빌드
    log_info "Frontend Docker 이미지 빌드 중..."
    docker build -t $ECR_FRONTEND_REPO:$IMAGE_TAG ./frontend
    log_success "Frontend 이미지 빌드 완료"
    
    # 이미지 태그
    log_info "이미지 태그 설정 중..."
    docker tag $ECR_FRONTEND_REPO:$IMAGE_TAG $ECR_FRONTEND_URI:$IMAGE_TAG
    docker tag $ECR_FRONTEND_REPO:$IMAGE_TAG $ECR_FRONTEND_URI:latest
    
    # 이미지 푸시
    log_info "Frontend 이미지를 ECR로 푸시 중..."
    docker push $ECR_FRONTEND_URI:$IMAGE_TAG
    docker push $ECR_FRONTEND_URI:latest
    log_success "Frontend 이미지 푸시 완료"
    
    # ECS 서비스 업데이트
    log_info "Frontend ECS 서비스 업데이트 중..."
    aws ecs update-service \
        --cluster $ECS_CLUSTER \
        --service $ECS_FRONTEND_SERVICE \
        --force-new-deployment \
        --region $AWS_REGION \
        > /dev/null
    log_success "Frontend 서비스 업데이트 시작"
    
    # 배포 대기
    log_info "Frontend 서비스가 안정화될 때까지 대기 중... (최대 10분)"
    aws ecs wait services-stable \
        --cluster $ECS_CLUSTER \
        --services $ECS_FRONTEND_SERVICE \
        --region $AWS_REGION
    log_success "Frontend 배포 완료!"
fi

# 헬스 체크
echo ""
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "헬스 체크 수행 중"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ALB DNS 가져오기
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --query 'LoadBalancers[?contains(LoadBalancerName, `coldchain-production`)].DNSName' \
    --output text \
    --region $AWS_REGION)

if [ -z "$ALB_DNS" ]; then
    log_warning "ALB DNS를 찾을 수 없습니다. 헬스 체크를 건너뜁니다."
else
    log_info "ALB DNS: $ALB_DNS"
    
    if [ "$DEPLOY_BACKEND" = true ]; then
        log_info "Backend 헬스 체크 중..."
        response=$(curl -s -o /dev/null -w "%{http_code}" "https://$ALB_DNS/health" || echo "000")
        
        if [ "$response" = "200" ]; then
            log_success "Backend 헬스 체크 통과 ✓"
        else
            log_warning "Backend 헬스 체크 실패 (HTTP $response)"
        fi
    fi
    
    if [ "$DEPLOY_FRONTEND" = true ]; then
        log_info "Frontend 헬스 체크 중..."
        response=$(curl -s -o /dev/null -w "%{http_code}" "https://$ALB_DNS/" || echo "000")
        
        if [ "$response" = "200" ]; then
            log_success "Frontend 헬스 체크 통과 ✓"
        else
            log_warning "Frontend 헬스 체크 실패 (HTTP $response)"
        fi
    fi
fi

# 배포 완료
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  🎉 배포 완료! 🎉                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
log_success "모든 서비스가 성공적으로 배포되었습니다!"
log_info "애플리케이션 URL: https://$ALB_DNS"
echo ""
