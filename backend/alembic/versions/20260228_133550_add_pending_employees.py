"""add pending_employees table

Revision ID: pending_emp_001
Revises: 
Create Date: 2024-02-28 14:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'pending_emp_001'
down_revision = None  # Update with your latest revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create pending_employees table
    op.create_table(
        'pending_employees',
        sa.Column('id', sa.Integer(), nullable=False, comment='ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='연결된 사용자 ID'),
        
        # 기본 식별 정보
        sa.Column('employee_code', sa.String(50), nullable=False, comment='사원번호'),
        
        # 개인 정보
        sa.Column('name', sa.String(100), nullable=False, comment='이름'),
        sa.Column('name_en', sa.String(100), nullable=True, comment='영문명'),
        sa.Column('phone', sa.String(20), nullable=False, comment='전화번호'),
        sa.Column('email', sa.String(100), nullable=True, comment='이메일'),
        sa.Column('address', sa.Text(), nullable=True, comment='주소'),
        sa.Column('emergency_contact', sa.String(20), nullable=True, comment='비상연락처'),
        
        # 조직 정보
        sa.Column('role', sa.String(20), nullable=False, comment='직급'),
        sa.Column('employment_type', sa.String(20), nullable=False, comment='고용 형태'),
        sa.Column('department', sa.String(100), nullable=True, comment='부서'),
        sa.Column('position', sa.String(100), nullable=True, comment='직책'),
        
        # 근무 정보
        sa.Column('hire_date', sa.Date(), nullable=False, comment='입사일'),
        
        # 운전면허 정보
        sa.Column('license_type', sa.String(20), nullable=True, comment='운전면허 종류'),
        sa.Column('license_number', sa.String(50), nullable=True, comment='운전면허 번호'),
        sa.Column('license_issue_date', sa.Date(), nullable=True, comment='운전면허 발급일'),
        
        # 화물운송자격증
        sa.Column('has_cargo_license', sa.Boolean(), server_default='false', comment='화물운송자격증 보유'),
        sa.Column('cargo_license_number', sa.String(50), nullable=True, comment='화물운송자격증 번호'),
        sa.Column('cargo_license_issue_date', sa.Date(), nullable=True, comment='화물운송자격증 발급일'),
        sa.Column('cargo_license_expiry_date', sa.Date(), nullable=True, comment='화물운송자격증 만료일'),
        
        # 지게차 자격
        sa.Column('can_drive_forklift', sa.Boolean(), server_default='false', comment='지게차 운전 가능'),
        sa.Column('has_forklift_certificate', sa.Boolean(), server_default='false', comment='지게차 자격증 보유'),
        sa.Column('forklift_certificate_number', sa.String(50), nullable=True, comment='지게차 자격증 번호'),
        sa.Column('forklift_certificate_issue_date', sa.Date(), nullable=True, comment='지게차 자격증 발급일'),
        sa.Column('forklift_certificate_expiry_date', sa.Date(), nullable=True, comment='지게차 자격증 만료일'),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), comment='생성일시'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('user_id')
    )
    
    # Create indexes
    op.create_index('idx_pending_employees_user_id', 'pending_employees', ['user_id'])
    op.create_index('idx_pending_employees_code', 'pending_employees', ['employee_code'])
    
    print("✅ Created pending_employees table")


def downgrade() -> None:
    op.drop_index('idx_pending_employees_code', table_name='pending_employees')
    op.drop_index('idx_pending_employees_user_id', table_name='pending_employees')
    op.drop_table('pending_employees')
    print("✅ Dropped pending_employees table")
