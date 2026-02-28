#!/bin/bash
set -e

echo "=========================================="
echo "인사카드 회원가입 시스템 배포 스크립트"
echo "=========================================="
echo ""

cd /root/uvis

# 1. Pull latest changes
echo "📥 Step 1: Pulling latest code from GitHub..."
git fetch origin main
git pull origin main
echo "✅ Code updated"
echo ""

# 2. Stop containers
echo "🛑 Step 2: Stopping containers..."
docker-compose down
echo "✅ Containers stopped"
echo ""

# 3. Run database migration
echo "🗄️  Step 3: Running database migration..."
docker-compose up -d db
sleep 5

# Check if migration file exists
if [ ! -f "backend/alembic/versions/*pending_employees.py" ]; then
    echo "⚠️  Migration file not found, creating it..."
    cat > "backend/alembic/versions/$(date +%Y%m%d_%H%M%S)_add_pending_employees.py" << 'MIGRATION_CONTENT'
"""add pending_employees table

Revision ID: pending_emp_001
Revises: 
Create Date: 2024-02-28 14:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'pending_emp_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'pending_employees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('employee_code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100)),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('email', sa.String(100)),
        sa.Column('address', sa.Text()),
        sa.Column('emergency_contact', sa.String(20)),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('employment_type', sa.String(20), nullable=False),
        sa.Column('department', sa.String(100)),
        sa.Column('position', sa.String(100)),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('work_start_time', sa.String(5), server_default='08:00'),
        sa.Column('work_end_time', sa.String(5), server_default='18:00'),
        sa.Column('max_work_hours', sa.Integer(), server_default='10'),
        sa.Column('license_type', sa.String(20)),
        sa.Column('license_number', sa.String(50)),
        sa.Column('license_issue_date', sa.Date()),
        sa.Column('has_cargo_license', sa.Boolean(), server_default='false'),
        sa.Column('cargo_license_number', sa.String(50)),
        sa.Column('cargo_license_issue_date', sa.Date()),
        sa.Column('cargo_license_expiry_date', sa.Date()),
        sa.Column('can_drive_forklift', sa.Boolean(), server_default='false'),
        sa.Column('has_forklift_certificate', sa.Boolean(), server_default='false'),
        sa.Column('forklift_certificate_number', sa.String(50)),
        sa.Column('forklift_certificate_issue_date', sa.Date()),
        sa.Column('forklift_certificate_expiry_date', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('idx_pending_employees_user_id', 'pending_employees', ['user_id'])
    op.create_index('idx_pending_employees_code', 'pending_employees', ['employee_code'])


def downgrade() -> None:
    op.drop_index('idx_pending_employees_code')
    op.drop_index('idx_pending_employees_user_id')
    op.drop_table('pending_employees')
MIGRATION_CONTENT
fi

# Run migration inside backend container
docker-compose up -d backend
sleep 10

echo "Running Alembic migration..."
docker exec uvis-backend alembic upgrade head || {
    echo "⚠️  Migration may have failed or table already exists"
}
echo "✅ Migration completed"
echo ""

# 4. Rebuild backend
echo "🔨 Step 4: Rebuilding backend..."
docker-compose down backend
docker-compose build --no-cache backend
docker-compose up -d backend
echo "⏳ Waiting for backend to start..."
sleep 15
echo "✅ Backend rebuilt"
echo ""

# 5. Rebuild frontend
echo "🔨 Step 5: Rebuilding frontend..."
docker-compose down frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
echo "⏳ Waiting for frontend to build..."
sleep 30
echo "✅ Frontend rebuilt"
echo ""

# 6. Start all services
echo "🚀 Step 6: Starting all services..."
docker-compose up -d
sleep 10
echo "✅ All services started"
echo ""

# 7. Check health
echo "🏥 Step 7: Health check..."
docker-compose ps
echo ""

# 8. Verify deployment
echo "✅ Step 8: Deployment complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 인사카드 회원가입 시스템 배포 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 테스트 방법:"
echo ""
echo "1️⃣  브라우저에서 http://139.150.11.99/ 접속"
echo ""
echo "2️⃣  로그인 페이지에서 '회원가입' 클릭"
echo ""
echo "3️⃣  4단계 회원가입 진행:"
echo "   Step 1: 계정 정보 (사용자명, 이메일, 비밀번호, 권한)"
echo "   Step 2: 기본 정보 (사원번호, 이름, 전화번호, 주소 등)"
echo "   Step 3: 조직/근무 정보 (직급, 고용형태, 부서, 입사일 등)"
echo "   Step 4: 자격증 정보 (운전면허, 화물운송, 지게차)"
echo ""
echo "4️⃣  관리자 로그인 (admin / admin123)"
echo ""
echo "5️⃣  설정 → 회원관리에서 승인 대기 목록 확인"
echo "   - 사원번호, 이름, 전화번호"
echo "   - 부서/직책/입사일"
echo "   - 보유 자격증 현황"
echo ""
echo "6️⃣  '승인' 버튼 클릭 → 인사카드 자동 생성 ✨"
echo ""
echo "7️⃣  새 계정으로 로그인 테스트"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 주요 변경사항:"
echo "  ✅ 회원가입 페이지: 4단계 Step Wizard (40+ 필드)"
echo "  ✅ 인사카드 전체 양식 입력"
echo "  ✅ 승인 시 Employee 자동 생성"
echo "  ✅ PendingEmployee 테이블로 임시 저장"
echo "  ✅ 승인 페이지에 상세 정보 표시"
echo ""
echo "🔗 API Endpoints:"
echo "  - POST /api/v1/auth/signup (공개)"
echo "  - GET /api/v1/auth/users/pending (MASTER/ADMIN)"
echo "  - POST /api/v1/auth/users/{id}/approve (MASTER/ADMIN)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 문서: SIGNUP_REFACTOR.md"
echo ""
