"""add emergency maintenance fields to vehicles

Revision ID: 20260130140000
Revises: 20260129160000
Create Date: 2026-01-30 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260130140000'
down_revision = '20260129160000'
branch_labels = None
depends_on = None


def upgrade():
    # 1. VehicleStatus enum에 새로운 값 추가
    op.execute("ALTER TYPE vehiclestatus ADD VALUE IF NOT EXISTS 'EMERGENCY_MAINTENANCE'")
    op.execute("ALTER TYPE vehiclestatus ADD VALUE IF NOT EXISTS 'BREAKDOWN'")
    
    # 2. 긴급정비 관련 필드 추가
    op.add_column('vehicles', sa.Column('is_emergency', sa.Boolean(), nullable=True, comment='긴급 상황 여부'))
    op.add_column('vehicles', sa.Column('emergency_type', sa.String(length=50), nullable=True, comment='긴급 유형'))
    op.add_column('vehicles', sa.Column('emergency_severity', sa.String(length=20), nullable=True, comment='긴급도'))
    op.add_column('vehicles', sa.Column('emergency_reported_at', sa.DateTime(), nullable=True, comment='신고 시각'))
    op.add_column('vehicles', sa.Column('emergency_location', sa.String(length=500), nullable=True, comment='발생 위치'))
    op.add_column('vehicles', sa.Column('emergency_description', sa.Text(), nullable=True, comment='상황 설명'))
    op.add_column('vehicles', sa.Column('estimated_repair_time', sa.Integer(), nullable=True, comment='예상 수리 시간(분)'))
    op.add_column('vehicles', sa.Column('replacement_vehicle_id', sa.Integer(), nullable=True, comment='대체 차량 ID'))
    
    # 3. 기존 데이터에 대해 기본값 설정
    op.execute("UPDATE vehicles SET is_emergency = FALSE WHERE is_emergency IS NULL")
    
    # 4. is_emergency 필드를 NOT NULL로 변경
    op.alter_column('vehicles', 'is_emergency', nullable=False)
    
    # 5. 인덱스 추가 (긴급 상황 조회 성능 향상)
    op.create_index('idx_vehicles_is_emergency', 'vehicles', ['is_emergency'])
    op.create_index('idx_vehicles_emergency_reported_at', 'vehicles', ['emergency_reported_at'])


def downgrade():
    # 인덱스 삭제
    op.drop_index('idx_vehicles_emergency_reported_at', table_name='vehicles')
    op.drop_index('idx_vehicles_is_emergency', table_name='vehicles')
    
    # 컬럼 삭제
    op.drop_column('vehicles', 'replacement_vehicle_id')
    op.drop_column('vehicles', 'estimated_repair_time')
    op.drop_column('vehicles', 'emergency_description')
    op.drop_column('vehicles', 'emergency_location')
    op.drop_column('vehicles', 'emergency_reported_at')
    op.drop_column('vehicles', 'emergency_severity')
    op.drop_column('vehicles', 'emergency_type')
    op.drop_column('vehicles', 'is_emergency')
    
    # Note: PostgreSQL enum 값 제거는 복잡하므로 생략
    # 필요시 enum 타입을 재생성해야 함
