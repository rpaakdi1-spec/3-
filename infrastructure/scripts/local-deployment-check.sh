#!/bin/bash

# 🔍 Local Deployment Readiness Check
# UVIS GPS Fleet Management System
# Version: 1.0.0

# Don't use set -e to allow checks to continue even if some fail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  UVIS GPS Fleet Management System                        ║"
echo "║  배포 준비 상태 검증                                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Counters
total_checks=0
passed_checks=0
failed_checks=0
warning_checks=0

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((passed_checks++))
    ((total_checks++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((failed_checks++))
    ((total_checks++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((warning_checks++))
    ((total_checks++))
}

print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ==================== 1. 코드 저장소 검증 ====================
print_section "1. 코드 저장소 검증"

if [ -d "${PROJECT_ROOT}/.git" ]; then
    check_pass "Git 저장소 존재"
    
    # Check branch
    current_branch=$(git -C "${PROJECT_ROOT}" branch --show-current)
    if [ -n "$current_branch" ]; then
        check_pass "현재 브랜치: $current_branch"
    else
        check_warn "브랜치 정보 없음"
    fi
    
    # Check uncommitted changes
    if git -C "${PROJECT_ROOT}" diff-index --quiet HEAD -- 2>/dev/null; then
        check_pass "커밋되지 않은 변경사항 없음"
    else
        check_warn "커밋되지 않은 변경사항 존재"
    fi
    
    # Check latest commit
    latest_commit=$(git -C "${PROJECT_ROOT}" log -1 --format="%h - %s" 2>/dev/null || echo "N/A")
    check_pass "최신 커밋: $latest_commit"
else
    check_fail "Git 저장소 없음"
fi

# ==================== 2. 프로젝트 구조 검증 ====================
print_section "2. 프로젝트 구조 검증"

# Backend
if [ -d "${PROJECT_ROOT}/backend" ]; then
    check_pass "backend/ 디렉토리 존재"
    
    if [ -f "${PROJECT_ROOT}/backend/main.py" ]; then
        check_pass "backend/main.py 존재"
    else
        check_fail "backend/main.py 없음"
    fi
    
    if [ -f "${PROJECT_ROOT}/backend/requirements.txt" ]; then
        check_pass "requirements.txt 존재"
        req_count=$(wc -l < "${PROJECT_ROOT}/backend/requirements.txt")
        check_pass "패키지 수: $req_count"
    else
        check_fail "requirements.txt 없음"
    fi
else
    check_fail "backend/ 디렉토리 없음"
fi

# Frontend
if [ -d "${PROJECT_ROOT}/frontend" ]; then
    check_pass "frontend/ 디렉토리 존재"
    
    if [ -f "${PROJECT_ROOT}/frontend/package.json" ]; then
        check_pass "package.json 존재"
    else
        check_fail "package.json 없음"
    fi
else
    check_fail "frontend/ 디렉토리 없음"
fi

# Infrastructure
if [ -d "${PROJECT_ROOT}/infrastructure" ]; then
    check_pass "infrastructure/ 디렉토리 존재"
    
    if [ -d "${PROJECT_ROOT}/infrastructure/terraform" ]; then
        check_pass "Terraform 디렉토리 존재"
        tf_files=$(find "${PROJECT_ROOT}/infrastructure/terraform" -name "*.tf" | wc -l)
        check_pass "Terraform 파일 수: $tf_files"
    else
        check_fail "Terraform 디렉토리 없음"
    fi
else
    check_fail "infrastructure/ 디렉토리 없음"
fi

# ==================== 3. Docker 설정 검증 ====================
print_section "3. Docker 설정 검증"

if [ -f "${PROJECT_ROOT}/Dockerfile.production" ]; then
    check_pass "Dockerfile.production 존재"
else
    check_fail "Dockerfile.production 없음"
fi

if [ -f "${PROJECT_ROOT}/docker-compose.production.yml" ]; then
    check_pass "docker-compose.production.yml 존재"
else
    check_warn "docker-compose.production.yml 없음 (선택 사항)"
fi

if [ -f "${PROJECT_ROOT}/.dockerignore" ]; then
    check_pass ".dockerignore 존재"
else
    check_warn ".dockerignore 없음"
fi

# ==================== 4. 환경 설정 파일 검증 ====================
print_section "4. 환경 설정 파일 검증"

if [ -f "${PROJECT_ROOT}/.env.example" ]; then
    check_pass ".env.example 존재"
    env_vars=$(grep -c "^[A-Z_]" "${PROJECT_ROOT}/.env.example" || echo 0)
    check_pass "환경 변수 수: $env_vars"
else
    check_fail ".env.example 없음"
fi

if [ -f "${PROJECT_ROOT}/.env.production" ]; then
    check_pass ".env.production 존재"
else
    check_warn ".env.production 없음 (배포 시 필요)"
fi

if [ -f "${PROJECT_ROOT}/infrastructure/terraform/terraform.tfvars.example" ]; then
    check_pass "terraform.tfvars.example 존재"
else
    check_fail "terraform.tfvars.example 없음"
fi

# ==================== 5. 테스트 파일 검증 ====================
print_section "5. 테스트 파일 검증"

if [ -d "${PROJECT_ROOT}/backend/tests" ]; then
    check_pass "backend/tests 디렉토리 존재"
    test_files=$(find "${PROJECT_ROOT}/backend/tests" -name "test_*.py" 2>/dev/null | wc -l)
    check_pass "테스트 파일 수: $test_files"
else
    check_warn "테스트 디렉토리 없음"
fi

if [ -f "${PROJECT_ROOT}/backend/pytest.ini" ] || [ -f "${PROJECT_ROOT}/backend/pyproject.toml" ]; then
    check_pass "Pytest 설정 파일 존재"
else
    check_warn "Pytest 설정 파일 없음"
fi

# ==================== 6. 문서 검증 ====================
print_section "6. 문서 검증"

docs=(
    "README.md"
    "DEPLOYMENT_QUICKSTART.md"
    "PROJECT_COMPLETION_REPORT.md"
    "PHASE11-20_CHECKLIST.md"
)

for doc in "${docs[@]}"; do
    if [ -f "${PROJECT_ROOT}/${doc}" ]; then
        check_pass "$doc 존재"
    else
        check_warn "$doc 없음"
    fi
done

# Count all markdown files
md_count=$(find "${PROJECT_ROOT}" -maxdepth 1 -name "*.md" | wc -l)
check_pass "총 문서 수: $md_count"

# ==================== 7. 배포 스크립트 검증 ====================
print_section "7. 배포 스크립트 검증"

scripts=(
    "infrastructure/scripts/production-deploy.sh"
    "infrastructure/scripts/backup.sh"
    "infrastructure/scripts/restore.sh"
)

for script in "${scripts[@]}"; do
    if [ -f "${PROJECT_ROOT}/${script}" ]; then
        check_pass "$(basename $script) 존재"
        if [ -x "${PROJECT_ROOT}/${script}" ]; then
            check_pass "$(basename $script) 실행 권한 있음"
        else
            check_warn "$(basename $script) 실행 권한 없음"
        fi
    else
        check_fail "$(basename $script) 없음"
    fi
done

# ==================== 8. ML 모델 파일 검증 ====================
print_section "8. ML/Analytics 검증"

if [ -d "${PROJECT_ROOT}/backend/app/ml" ]; then
    check_pass "ML 모듈 디렉토리 존재"
    
    if [ -d "${PROJECT_ROOT}/backend/app/ml/models" ]; then
        check_pass "ML models 디렉토리 존재"
        model_files=$(find "${PROJECT_ROOT}/backend/app/ml/models" -name "*.py" | wc -l)
        check_pass "ML 모델 파일 수: $model_files"
    fi
    
    if [ -d "${PROJECT_ROOT}/backend/app/ml/services" ]; then
        check_pass "ML services 디렉토리 존재"
    fi
else
    check_warn "ML 모듈 없음"
fi

# ==================== 9. API 엔드포인트 검증 ====================
print_section "9. API 엔드포인트 검증"

if [ -d "${PROJECT_ROOT}/backend/app/api" ]; then
    check_pass "API 디렉토리 존재"
    api_files=$(find "${PROJECT_ROOT}/backend/app/api" -name "*.py" | wc -l)
    check_pass "API 파일 수: $api_files"
else
    check_fail "API 디렉토리 없음"
fi

# ==================== 10. 데이터베이스 마이그레이션 검증 ====================
print_section "10. 데이터베이스 마이그레이션 검증"

if [ -d "${PROJECT_ROOT}/backend/alembic" ]; then
    check_pass "Alembic 디렉토리 존재"
    
    if [ -f "${PROJECT_ROOT}/backend/alembic.ini" ]; then
        check_pass "alembic.ini 존재"
    else
        check_warn "alembic.ini 없음"
    fi
    
    if [ -d "${PROJECT_ROOT}/backend/alembic/versions" ]; then
        migration_count=$(find "${PROJECT_ROOT}/backend/alembic/versions" -name "*.py" ! -name "__init__.py" | wc -l)
        check_pass "마이그레이션 파일 수: $migration_count"
    fi
else
    check_warn "Alembic 디렉토리 없음"
fi

# ==================== 11. 보안 설정 검증 ====================
print_section "11. 보안 설정 검증"

# Check for sensitive files in .gitignore
if [ -f "${PROJECT_ROOT}/.gitignore" ]; then
    check_pass ".gitignore 존재"
    
    if grep -q ".env" "${PROJECT_ROOT}/.gitignore"; then
        check_pass ".env 파일 Git 제외됨"
    else
        check_fail ".env 파일이 .gitignore에 없음"
    fi
    
    if grep -q "*.pem" "${PROJECT_ROOT}/.gitignore" || grep -q "*.key" "${PROJECT_ROOT}/.gitignore"; then
        check_pass "키 파일 Git 제외됨"
    else
        check_warn "키 파일이 .gitignore에 없음"
    fi
else
    check_fail ".gitignore 없음"
fi

# ==================== 12. 모니터링 설정 검증 ====================
print_section "12. 모니터링 설정 검증"

if [ -d "${PROJECT_ROOT}/infrastructure/monitoring" ]; then
    check_pass "모니터링 디렉토리 존재"
    
    if [ -f "${PROJECT_ROOT}/infrastructure/monitoring/prometheus.yml" ]; then
        check_pass "Prometheus 설정 존재"
    fi
    
    if [ -d "${PROJECT_ROOT}/infrastructure/monitoring/grafana" ]; then
        check_pass "Grafana 디렉토리 존재"
    fi
else
    check_warn "모니터링 디렉토리 없음"
fi

# ==================== 최종 결과 ====================
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  최종 검증 결과                           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ 통과: $passed_checks${NC}"
echo -e "${RED}❌ 실패: $failed_checks${NC}"
echo -e "${YELLOW}⚠️  경고: $warning_checks${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "   총계: $total_checks"

# Calculate percentage
if [ $total_checks -gt 0 ]; then
    percentage=$((passed_checks * 100 / total_checks))
    echo ""
    echo -e "배포 준비도: ${GREEN}${percentage}%${NC}"
    echo ""
    
    if [ $percentage -ge 90 ]; then
        echo -e "${GREEN}🎉 프로덕션 배포 준비 완료!${NC}"
        echo ""
        echo "다음 단계:"
        echo "1. AWS CLI 설정: aws configure"
        echo "2. Terraform 변수 설정: cd infrastructure/terraform && cp terraform.tfvars.example terraform.tfvars"
        echo "3. 배포 실행: ./infrastructure/scripts/production-deploy.sh"
        exit 0
    elif [ $percentage -ge 75 ]; then
        echo -e "${YELLOW}⚠️  거의 준비 완료 - 일부 항목 확인 필요${NC}"
        exit 0
    else
        echo -e "${RED}❌ 배포 준비 불충분 - 실패 항목 수정 필요${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ 검증 실패${NC}"
    exit 1
fi
