"""Add dispatch rules tables

Revision ID: phase10_001
Revises: 
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'phase10_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # dispatch_rules 테이블
    op.create_table(
        'dispatch_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rule_type', sa.String(50), nullable=False, comment='assignment, constraint, optimization'),
        sa.Column('priority', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        
        # JSON 필드
        sa.Column('conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('actions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        
        # 적용 시간
        sa.Column('apply_time_start', sa.Time(), nullable=True),
        sa.Column('apply_time_end', sa.Time(), nullable=True),
        sa.Column('apply_days', sa.String(20), nullable=True, comment='MON,TUE,WED or WEEKEND'),
        
        # 메타데이터
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        
        # 성능 추적
        sa.Column('execution_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('avg_execution_time_ms', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL')
    )
    
    # 인덱스
    op.create_index('idx_dispatch_rules_active', 'dispatch_rules', ['is_active'])
    op.create_index('idx_dispatch_rules_priority', 'dispatch_rules', [sa.text('priority DESC')])
    op.create_index('idx_dispatch_rules_type', 'dispatch_rules', ['rule_type'])
    
    # rule_constraints 테이블
    op.create_table(
        'rule_constraints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.Column('constraint_type', sa.String(50), nullable=False, comment='hard, soft'),
        sa.Column('constraint_name', sa.String(200), nullable=False),
        sa.Column('constraint_definition', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('penalty_weight', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['rule_id'], ['dispatch_rules.id'], ondelete='CASCADE')
    )
    
    # rule_execution_logs 테이블
    op.create_table(
        'rule_execution_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.Integer(), nullable=True),
        sa.Column('dispatch_id', sa.Integer(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('distance_saved_km', sa.Float(), nullable=True),
        sa.Column('cost_saved', sa.Float(), nullable=True),
        sa.Column('time_saved_minutes', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['rule_id'], ['dispatch_rules.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['dispatch_id'], ['dispatches.id'], ondelete='SET NULL')
    )
    
    op.create_index('idx_rule_logs_rule_id', 'rule_execution_logs', ['rule_id'])
    op.create_index('idx_rule_logs_executed_at', 'rule_execution_logs', [sa.text('executed_at DESC')])
    
    # optimization_configs 테이블
    op.create_table(
        'optimization_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('objective', sa.String(50), nullable=False, comment='minimize_distance, minimize_cost, minimize_time, balanced'),
        sa.Column('weights', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('algorithm', sa.String(50), server_default='or_tools', nullable=False),
        sa.Column('max_computation_time_seconds', sa.Integer(), server_default='60', nullable=False),
        sa.Column('is_default', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('optimization_configs')
    op.drop_index('idx_rule_logs_executed_at', 'rule_execution_logs')
    op.drop_index('idx_rule_logs_rule_id', 'rule_execution_logs')
    op.drop_table('rule_execution_logs')
    op.drop_table('rule_constraints')
    op.drop_index('idx_dispatch_rules_type', 'dispatch_rules')
    op.drop_index('idx_dispatch_rules_priority', 'dispatch_rules')
    op.drop_index('idx_dispatch_rules_active', 'dispatch_rules')
    op.drop_table('dispatch_rules')
