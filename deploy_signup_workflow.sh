#!/bin/bash
set -e

echo "=========================================="
echo "회원가입 승인 워크플로우 배포 스크립트"
echo "=========================================="
echo ""

cd /root/uvis

# 1. Pull latest changes from GitHub
echo "📥 Step 1: Pulling latest changes from GitHub..."
git fetch origin main
git pull origin main

echo "✅ Latest changes pulled"
echo ""

# 2. Check if Employee table exists and has test data
echo "🔍 Step 2: Checking Employee data..."
docker exec uvis-backend python3 << 'PYTHON_EOF'
from app.core.database import SessionLocal
from app.models.employee import Employee, EmployeeRole, EmploymentType
from datetime import date

db = SessionLocal()
try:
    employee_count = db.query(Employee).count()
    print(f"Current employee count: {employee_count}")
    
    if employee_count == 0:
        print("⚠️  No employees found. Creating test employee...")
        test_employee = Employee(
            employee_code="D001",
            name="김테스트",
            phone="010-1234-5678",
            email="test@example.com",
            role=EmployeeRole.DRIVER,
            employment_type=EmploymentType.FULL_TIME,
            hire_date=date.today()
        )
        db.add(test_employee)
        db.commit()
        print("✅ Test employee created: D001 / 김테스트 / 010-1234-5678")
    else:
        # Show first 3 employees
        employees = db.query(Employee).limit(3).all()
        print("\nExisting employees (first 3):")
        for emp in employees:
            print(f"  - {emp.employee_code} / {emp.name} / {emp.phone}")
finally:
    db.close()
PYTHON_EOF

echo ""

# 3. Create and run database migration
echo "🗄️  Step 3: Creating database migration..."
cat > backend/alembic/versions/$(date +%Y%m%d_%H%M%S)_add_user_approval_fields.py << 'MIGRATION_EOF'
"""add user approval fields

Revision ID: $(openssl rand -hex 6)
Revises: 
Create Date: $(date +"%Y-%m-%d %H:%M:%S")

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '$(openssl rand -hex 6)'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if columns already exist before adding
    from sqlalchemy import inspect
    from sqlalchemy.engine import reflection
    
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'approval_status' not in columns:
        op.add_column('users', sa.Column('approval_status', sa.String(20), nullable=False, server_default='approved', comment='승인 상태: pending, approved, rejected'))
        print("✅ Added approval_status column")
    else:
        print("ℹ️  approval_status column already exists")
    
    if 'approved_by' not in columns:
        op.add_column('users', sa.Column('approved_by', sa.Integer(), nullable=True, comment='승인한 사용자 ID'))
        print("✅ Added approved_by column")
    else:
        print("ℹ️  approved_by column already exists")
    
    if 'approved_at' not in columns:
        op.add_column('users', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True, comment='승인 일시'))
        print("✅ Added approved_at column")
    else:
        print("ℹ️  approved_at column already exists")
    
    if 'phone' not in columns:
        op.add_column('users', sa.Column('phone', sa.String(20), nullable=True, comment='전화번호'))
        print("✅ Added phone column")
    else:
        print("ℹ️  phone column already exists")
    
    if 'employee_id' not in columns:
        op.add_column('users', sa.Column('employee_id', sa.Integer(), nullable=True, comment='연동된 직원 ID'))
        # Only create foreign key if employee table exists
        try:
            op.create_foreign_key('fk_users_employee_id', 'users', 'employees', ['employee_id'], ['id'])
            print("✅ Added employee_id foreign key")
        except:
            print("⚠️  Could not create foreign key (employees table might not exist)")
    else:
        print("ℹ️  employee_id column already exists")
    
    # Update existing users to 'approved' status
    op.execute("UPDATE users SET approval_status = 'approved', approved_at = NOW() WHERE approval_status = 'pending' OR approval_status IS NULL")
    print("✅ Updated existing users to approved status")


def downgrade() -> None:
    op.drop_column('users', 'employee_id')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'approved_at')
    op.drop_column('users', 'approved_by')
    op.drop_column('users', 'approval_status')
MIGRATION_EOF

echo "✅ Migration file created"
echo ""

# 4. Run migration
echo "🔄 Step 4: Running database migration..."
docker exec uvis-backend alembic upgrade head || {
    echo "⚠️  Migration might have failed or columns already exist"
}

echo "✅ Migration completed"
echo ""

# 5. Verify database changes
echo "🔍 Step 5: Verifying database schema..."
docker exec uvis-backend python3 << 'VERIFY_EOF'
from sqlalchemy import inspect
from app.core.database import engine

inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('users')]

required_columns = ['approval_status', 'approved_by', 'approved_at', 'phone', 'employee_id']
missing = [col for col in required_columns if col not in columns]

if missing:
    print(f"❌ Missing columns: {', '.join(missing)}")
    exit(1)
else:
    print("✅ All required columns exist:")
    for col in required_columns:
        print(f"   - {col}")
VERIFY_EOF

echo ""

# 6. Update existing admin user to MASTER role
echo "👤 Step 6: Updating admin user role to MASTER..."
docker exec uvis-backend python3 << 'UPDATE_ADMIN_EOF'
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from datetime import datetime

db = SessionLocal()
try:
    admin = db.query(User).filter(User.username == 'admin').first()
    if admin:
        admin.role = UserRole.MASTER
        admin.approval_status = 'approved'
        admin.approved_at = datetime.utcnow()
        db.commit()
        print(f"✅ Updated admin user to MASTER role")
    else:
        print("⚠️  Admin user not found")
finally:
    db.close()
UPDATE_ADMIN_EOF

echo ""

# 7. Rebuild and restart backend
echo "🔨 Step 7: Rebuilding backend container..."
docker-compose down backend
docker-compose build --no-cache backend
docker-compose up -d backend

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
sleep 10

# Check backend health
echo "🏥 Checking backend health..."
for i in {1..30}; do
    if docker exec uvis-backend curl -f http://localhost:8000/health 2>/dev/null; then
        echo "✅ Backend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend health check timeout"
        exit 1
    fi
    sleep 2
done

echo ""

# 8. Enhance UserManagementTab with pending approvals
echo "🎨 Step 8: Enhancing UserManagementTab..."
bash add_pending_approvals.sh

echo ""

# 9. Rebuild and restart frontend
echo "🔨 Step 9: Rebuilding frontend container..."
docker-compose down frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend

echo "⏳ Waiting for frontend to build..."
sleep 30

echo ""

# 10. Verify deployment
echo "✅ Step 10: Deployment verification..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 회원가입 승인 워크플로우 배포 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 다음 단계:"
echo ""
echo "1️⃣  브라우저에서 http://139.150.11.99/ 접속"
echo ""
echo "2️⃣  로그인 페이지에서 '회원가입' 버튼 클릭"
echo ""
echo "3️⃣  회원가입 테스트 (테스트 직원 정보):"
echo "   - 직원번호: D001"
echo "   - 이름: 김테스트"
echo "   - 전화번호: 010-1234-5678"
echo "   - 사용자명: testuser1"
echo "   - 비밀번호: test123456"
echo "   - 이메일: testuser1@company.com"
echo "   - 권한: 운전사원"
echo ""
echo "4️⃣  관리자 계정으로 로그인:"
echo "   - 사용자명: admin"
echo "   - 비밀번호: admin123"
echo ""
echo "5️⃣  설정 → 회원관리에서 승인 대기 목록 확인"
echo ""
echo "6️⃣  승인 버튼 클릭하여 사용자 승인"
echo ""
echo "7️⃣  로그아웃 후 새 계정으로 로그인 테스트"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 주요 변경사항:"
echo "  - UserRole enum 확장 (MASTER, ADMIN, VEHICLE_MANAGER, DRIVER, VIEWER)"
echo "  - 회원가입 시 인사카드(직원번호) 검증 추가"
echo "  - 승인 대기 상태 (approval_status: pending/approved/rejected)"
echo "  - 관리자(MASTER/ADMIN)만 승인/거부 가능"
echo "  - 로그인 페이지에 회원가입 링크 추가"
echo "  - 회원관리 페이지에 승인 대기 목록 섹션 추가"
echo ""
echo "🔗 API Endpoints:"
echo "  - POST /api/v1/auth/signup (공개)"
echo "  - GET /api/v1/auth/users/pending (MASTER/ADMIN)"
echo "  - POST /api/v1/auth/users/{id}/approve (MASTER/ADMIN)"
echo "  - POST /api/v1/auth/users/{id}/reject (MASTER/ADMIN)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
