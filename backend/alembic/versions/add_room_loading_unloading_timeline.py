"""add room loading/unloading fields and timeline columns

Revision ID: add_room_loading_unloading_timeline
Revises: 20260228_155700
Create Date: 2026-06-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.exc import OperationalError

# revision identifiers
revision = 'add_room_loading_unloading_timeline'
down_revision = '20260228_155700'
branch_labels = None
depends_on = None


def _add_column_if_not_exists(table, column_def):
    """컬럼이 없을 때만 추가 (idempotent)"""
    try:
        op.add_column(table, column_def)
    except Exception:
        pass  # 이미 존재하면 무시


def upgrade():
    # 상차지 필드
    _add_column_if_not_exists('location_rooms', sa.Column('loading_name', sa.String(200), nullable=True))
    _add_column_if_not_exists('location_rooms', sa.Column('loading_address', sa.String(500), nullable=True))
    _add_column_if_not_exists('location_rooms', sa.Column('loading_lat', sa.Float(), nullable=True))
    _add_column_if_not_exists('location_rooms', sa.Column('loading_lng', sa.Float(), nullable=True))
    # 하차지 필드
    _add_column_if_not_exists('location_rooms', sa.Column('unloading_name', sa.String(200), nullable=True))
    _add_column_if_not_exists('location_rooms', sa.Column('unloading_address', sa.String(500), nullable=True))
    _add_column_if_not_exists('location_rooms', sa.Column('unloading_lat', sa.Float(), nullable=True))
    _add_column_if_not_exists('location_rooms', sa.Column('unloading_lng', sa.Float(), nullable=True))
    # 타임라인
    _add_column_if_not_exists('location_rooms', sa.Column('arrived_at_loading', sa.DateTime(timezone=True), nullable=True))
    _add_column_if_not_exists('location_rooms', sa.Column('departed_loading', sa.DateTime(timezone=True), nullable=True))
    _add_column_if_not_exists('location_rooms', sa.Column('arrived_at_unloading', sa.DateTime(timezone=True), nullable=True))
    _add_column_if_not_exists('location_rooms', sa.Column('departed_unloading', sa.DateTime(timezone=True), nullable=True))
    # 내부 geofence 플래그
    _add_column_if_not_exists('location_rooms', sa.Column('in_loading_zone', sa.Boolean(), nullable=False, server_default='false'))
    _add_column_if_not_exists('location_rooms', sa.Column('in_unloading_zone', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    # 필요 시 수동으로 컬럼 제거
    pass
