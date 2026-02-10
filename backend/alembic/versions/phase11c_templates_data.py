"""insert simulation templates

Revision ID: phase11c_templates_data
Revises: phase11c_simulations
Create Date: 2026-02-10 07:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
import json

# revision identifiers, used by Alembic.
revision = 'phase11c_templates_data'
down_revision = 'phase11c_simulations'
branch_labels = None
depends_on = None


def upgrade():
    # Define table structure for bulk insert
    simulation_templates = table(
        'simulation_templates',
        column('name', sa.String),
        column('description', sa.Text),
        column('category', sa.String),
        column('scenario_data', sa.Text),
        column('expected_results', sa.Text),
        column('difficulty', sa.String),
        column('complexity_score', sa.Float),
        column('is_active', sa.Boolean),
    )
    
    # Template data
    templates_data = [
        {
            'name': '기본 거리 우선 배차',
            'description': '5km 이내 가까운 기사에게 우선 배정하는 시나리오',
            'category': 'distance',
            'difficulty': 'easy',
            'complexity_score': 2.0,
            'is_active': True,
            'scenario_data': json.dumps({
                "orders": [
                    {"id": 1, "distance_km": 3, "priority": "normal", "cargo_temp": "냉동"},
                    {"id": 2, "distance_km": 7, "priority": "normal", "cargo_temp": "냉장"},
                    {"id": 3, "distance_km": 2, "priority": "high", "cargo_temp": "냉동"}
                ],
                "drivers": [
                    {"id": 1, "rating": 4.5, "available": True, "vehicle_type": "냉동차"},
                    {"id": 2, "rating": 4.2, "available": True, "vehicle_type": "냉장차"},
                    {"id": 3, "rating": 4.8, "available": True, "vehicle_type": "냉동차"}
                ]
            }),
            'expected_results': json.dumps({
                "expected_match_rate": 100,
                "expected_avg_distance": 4.0,
                "description": "모든 주문이 5km 이내 기사에게 배정되어야 함"
            })
        },
        {
            'name': '고평점 기사 우선',
            'description': '평점 4.5 이상 고평점 기사 우선 배정',
            'category': 'quality',
            'difficulty': 'easy',
            'complexity_score': 2.5,
            'is_active': True,
            'scenario_data': json.dumps({
                "orders": [
                    {"id": 1, "distance_km": 5, "priority": "normal", "cargo_temp": "냉동"},
                    {"id": 2, "distance_km": 6, "priority": "high", "cargo_temp": "냉장"},
                    {"id": 3, "distance_km": 4, "priority": "normal", "cargo_temp": "냉동"}
                ],
                "drivers": [
                    {"id": 1, "rating": 4.8, "available": True, "vehicle_type": "냉동차"},
                    {"id": 2, "rating": 4.3, "available": True, "vehicle_type": "냉장차"},
                    {"id": 3, "rating": 4.7, "available": True, "vehicle_type": "냉동차"},
                    {"id": 4, "rating": 4.1, "available": True, "vehicle_type": "냉장차"}
                ]
            }),
            'expected_results': json.dumps({
                "expected_match_rate": 100,
                "expected_min_rating": 4.5,
                "description": "고평점 기사에게 우선 배정"
            })
        },
        {
            'name': '피크 시간대 시뮬레이션',
            'description': '주문 10건, 기사 5명 - 피크 시간 상황',
            'category': 'peak_hours',
            'difficulty': 'medium',
            'complexity_score': 5.0,
            'is_active': True,
            'scenario_data': json.dumps({
                "orders": [
                    {"id": i, "distance_km": 3 + i * 0.5, "priority": "high" if i % 3 == 0 else "normal", "cargo_temp": "냉동" if i % 2 == 0 else "냉장"}
                    for i in range(1, 11)
                ],
                "drivers": [
                    {"id": i, "rating": 4.0 + i * 0.1, "available": True, "vehicle_type": "냉동차" if i % 2 == 0 else "냉장차"}
                    for i in range(1, 6)
                ]
            }),
            'expected_results': json.dumps({
                "expected_match_rate": 50,
                "description": "기사 부족 상황에서 우선순위 높은 주문 먼저 배정"
            })
        },
        {
            'name': '복합 조건 테스트',
            'description': '거리 + 평점 + 차량 타입 복합 조건',
            'category': 'complex',
            'difficulty': 'hard',
            'complexity_score': 7.5,
            'is_active': True,
            'scenario_data': json.dumps({
                "orders": [
                    {"id": 1, "distance_km": 3, "priority": "high", "cargo_temp": "냉동", "weight_kg": 500},
                    {"id": 2, "distance_km": 8, "priority": "normal", "cargo_temp": "냉장", "weight_kg": 300},
                    {"id": 3, "distance_km": 5, "priority": "high", "cargo_temp": "냉동", "weight_kg": 700},
                    {"id": 4, "distance_km": 2, "priority": "normal", "cargo_temp": "냉장", "weight_kg": 200}
                ],
                "drivers": [
                    {"id": 1, "rating": 4.8, "available": True, "vehicle_type": "냉동차", "capacity_kg": 1000},
                    {"id": 2, "rating": 4.5, "available": True, "vehicle_type": "냉장차", "capacity_kg": 800},
                    {"id": 3, "rating": 4.2, "available": False, "vehicle_type": "냉동차", "capacity_kg": 1000},
                    {"id": 4, "rating": 4.7, "available": True, "vehicle_type": "냉장차", "capacity_kg": 500}
                ]
            }),
            'expected_results': json.dumps({
                "expected_match_rate": 75,
                "description": "복합 조건 만족하는 최적 기사 매칭"
            })
        },
        {
            'name': '긴급 주문 우선 처리',
            'description': '긴급(high priority) 주문 최우선 배정',
            'category': 'priority',
            'difficulty': 'medium',
            'complexity_score': 4.0,
            'is_active': True,
            'scenario_data': json.dumps({
                "orders": [
                    {"id": 1, "distance_km": 10, "priority": "high", "cargo_temp": "냉동"},
                    {"id": 2, "distance_km": 3, "priority": "normal", "cargo_temp": "냉장"},
                    {"id": 3, "distance_km": 5, "priority": "high", "cargo_temp": "냉동"},
                    {"id": 4, "distance_km": 2, "priority": "normal", "cargo_temp": "냉장"}
                ],
                "drivers": [
                    {"id": 1, "rating": 4.5, "available": True, "vehicle_type": "냉동차"},
                    {"id": 2, "rating": 4.3, "available": True, "vehicle_type": "냉장차"}
                ]
            }),
            'expected_results': json.dumps({
                "expected_match_rate": 50,
                "description": "긴급 주문 2건이 우선 배정되어야 함"
            })
        },
        {
            'name': '차량 타입 매칭',
            'description': '냉동/냉장 화물에 맞는 차량 타입 매칭',
            'category': 'vehicle_type',
            'difficulty': 'easy',
            'complexity_score': 3.0,
            'is_active': True,
            'scenario_data': json.dumps({
                "orders": [
                    {"id": 1, "distance_km": 5, "priority": "normal", "cargo_temp": "냉동"},
                    {"id": 2, "distance_km": 4, "priority": "normal", "cargo_temp": "냉장"},
                    {"id": 3, "distance_km": 6, "priority": "normal", "cargo_temp": "냉동"}
                ],
                "drivers": [
                    {"id": 1, "rating": 4.5, "available": True, "vehicle_type": "냉동차"},
                    {"id": 2, "rating": 4.3, "available": True, "vehicle_type": "냉장차"},
                    {"id": 3, "rating": 4.6, "available": True, "vehicle_type": "냉동차"}
                ]
            }),
            'expected_results': json.dumps({
                "expected_match_rate": 100,
                "description": "각 화물이 적절한 차량 타입에 배정"
            })
        }
    ]
    
    # Bulk insert
    op.bulk_insert(simulation_templates, templates_data)


def downgrade():
    # Delete all template data
    op.execute("DELETE FROM simulation_templates WHERE category IN ('distance', 'quality', 'peak_hours', 'complex', 'priority', 'vehicle_type')")
