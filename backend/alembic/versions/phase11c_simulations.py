"""add simulation tables

Revision ID: phase11c_simulations
Revises: phase10_001
Create Date: 2026-02-10 07:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'phase11c_simulations'
down_revision = 'phase10_001'
branch_labels = None
depends_on = None


def upgrade():
    # Create rule_simulations table
    op.create_table(
        'rule_simulations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False, comment='시뮬레이션 이름'),
        sa.Column('description', sa.Text(), nullable=True, comment='시뮬레이션 설명'),
        sa.Column('rule_id', sa.Integer(), nullable=True, comment='테스트할 규칙 ID'),
        sa.Column('rule_config', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='규칙 설정'),
        sa.Column('scenario_data', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='테스트 시나리오 데이터'),
        sa.Column('scenario_type', sa.String(length=50), nullable=True, server_default='custom', comment='시나리오 타입'),
        sa.Column('iterations', sa.Integer(), nullable=True, server_default='1', comment='반복 실행 횟수'),
        sa.Column('randomize_data', sa.Boolean(), nullable=True, server_default='false', comment='데이터 랜덤화 여부'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='pending', comment='상태'),
        sa.Column('total_matches', sa.Integer(), nullable=True, comment='총 매칭 수'),
        sa.Column('successful_matches', sa.Integer(), nullable=True, comment='성공한 매칭 수'),
        sa.Column('failed_matches', sa.Integer(), nullable=True, comment='실패한 매칭 수'),
        sa.Column('match_rate', sa.Float(), nullable=True, comment='매칭 성공률 (%)'),
        sa.Column('avg_response_time_ms', sa.Float(), nullable=True, comment='평균 응답 시간 (ms)'),
        sa.Column('min_response_time_ms', sa.Float(), nullable=True, comment='최소 응답 시간 (ms)'),
        sa.Column('max_response_time_ms', sa.Float(), nullable=True, comment='최대 응답 시간 (ms)'),
        sa.Column('estimated_cost', sa.Float(), nullable=True, comment='예상 비용'),
        sa.Column('estimated_distance_km', sa.Float(), nullable=True, comment='예상 총 거리 (km)'),
        sa.Column('estimated_time_minutes', sa.Float(), nullable=True, comment='예상 총 시간 (분)'),
        sa.Column('results', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='상세 시뮬레이션 결과'),
        sa.Column('errors', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='오류 내역'),
        sa.Column('created_by', sa.String(length=100), nullable=True, comment='생성자'),
        sa.Column('started_at', sa.DateTime(), nullable=True, comment='시작 시각'),
        sa.Column('completed_at', sa.DateTime(), nullable=True, comment='완료 시각'),
        sa.Column('duration_seconds', sa.Float(), nullable=True, comment='실행 시간 (초)'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='생성 시각'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='수정 시각'),
        sa.ForeignKeyConstraint(['rule_id'], ['dispatch_rules.id'], ),
        sa.PrimaryKeyConstraint('id'),
        comment='규칙 시뮬레이션 실행 기록'
    )
    op.create_index(op.f('ix_rule_simulations_id'), 'rule_simulations', ['id'], unique=False)
    op.create_index(op.f('ix_rule_simulations_rule_id'), 'rule_simulations', ['rule_id'], unique=False)
    op.create_index(op.f('ix_rule_simulations_status'), 'rule_simulations', ['status'], unique=False)
    op.create_index(op.f('ix_rule_simulations_created_at'), 'rule_simulations', ['created_at'], unique=False)

    # Create simulation_comparisons table
    op.create_table(
        'simulation_comparisons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False, comment='비교 테스트 이름'),
        sa.Column('description', sa.Text(), nullable=True, comment='비교 테스트 설명'),
        sa.Column('simulation_a_id', sa.Integer(), nullable=False, comment='시뮬레이션 A'),
        sa.Column('simulation_b_id', sa.Integer(), nullable=False, comment='시뮬레이션 B'),
        sa.Column('winner', sa.String(length=1), nullable=True, comment='승자: A, B, tie'),
        sa.Column('comparison_metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='비교 지표'),
        sa.Column('recommendation', sa.Text(), nullable=True, comment='AI 추천 내용'),
        sa.Column('confidence_score', sa.Float(), nullable=True, comment='추천 신뢰도 (0-1)'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='생성 시각'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='수정 시각'),
        sa.ForeignKeyConstraint(['simulation_a_id'], ['rule_simulations.id'], ),
        sa.ForeignKeyConstraint(['simulation_b_id'], ['rule_simulations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        comment='규칙 A/B 비교 테스트'
    )
    op.create_index(op.f('ix_simulation_comparisons_id'), 'simulation_comparisons', ['id'], unique=False)
    op.create_index(op.f('ix_simulation_comparisons_created_at'), 'simulation_comparisons', ['created_at'], unique=False)

    # Create simulation_templates table
    op.create_table(
        'simulation_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False, comment='템플릿 이름'),
        sa.Column('description', sa.Text(), nullable=True, comment='템플릿 설명'),
        sa.Column('category', sa.String(length=50), nullable=True, comment='카테고리'),
        sa.Column('scenario_data', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='시나리오 데이터'),
        sa.Column('expected_results', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='예상 결과'),
        sa.Column('difficulty', sa.String(length=20), nullable=True, server_default='medium', comment='난이도'),
        sa.Column('complexity_score', sa.Float(), nullable=True, comment='복잡도 점수 (1-10)'),
        sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0', comment='사용 횟수'),
        sa.Column('avg_success_rate', sa.Float(), nullable=True, comment='평균 성공률'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true', comment='활성 여부'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='생성 시각'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='수정 시각'),
        sa.PrimaryKeyConstraint('id'),
        comment='시뮬레이션 템플릿'
    )
    op.create_index(op.f('ix_simulation_templates_id'), 'simulation_templates', ['id'], unique=False)
    op.create_index(op.f('ix_simulation_templates_category'), 'simulation_templates', ['category'], unique=False)
    op.create_index(op.f('ix_simulation_templates_difficulty'), 'simulation_templates', ['difficulty'], unique=False)
    op.create_index(op.f('ix_simulation_templates_is_active'), 'simulation_templates', ['is_active'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_simulation_templates_is_active'), table_name='simulation_templates')
    op.drop_index(op.f('ix_simulation_templates_difficulty'), table_name='simulation_templates')
    op.drop_index(op.f('ix_simulation_templates_category'), table_name='simulation_templates')
    op.drop_index(op.f('ix_simulation_templates_id'), table_name='simulation_templates')
    op.drop_table('simulation_templates')
    
    op.drop_index(op.f('ix_simulation_comparisons_created_at'), table_name='simulation_comparisons')
    op.drop_index(op.f('ix_simulation_comparisons_id'), table_name='simulation_comparisons')
    op.drop_table('simulation_comparisons')
    
    op.drop_index(op.f('ix_rule_simulations_created_at'), table_name='rule_simulations')
    op.drop_index(op.f('ix_rule_simulations_status'), table_name='rule_simulations')
    op.drop_index(op.f('ix_rule_simulations_rule_id'), table_name='rule_simulations')
    op.drop_index(op.f('ix_rule_simulations_id'), table_name='rule_simulations')
    op.drop_table('rule_simulations')
