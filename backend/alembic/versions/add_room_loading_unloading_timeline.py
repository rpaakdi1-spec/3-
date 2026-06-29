"""add room loading/unloading fields and timeline columns

Revision ID: add_room_loading_unloading_timeline
Revises: 
Create Date: 2026-06-29

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_room_loading_unloading_timeline'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 상차지 필드
    op.add_column('location_rooms', sa.Column('loading_name', sa.String(200), nullable=True))
    op.add_column('location_rooms', sa.Column('loading_address', sa.String(500), nullable=True))
    op.add_column('location_rooms', sa.Column('loading_lat', sa.Float(), nullable=True))
    op.add_column('location_rooms', sa.Column('loading_lng', sa.Float(), nullable=True))
    # 하차지 필드
    op.add_column('location_rooms', sa.Column('unloading_name', sa.String(200), nullable=True))
    op.add_column('location_rooms', sa.Column('unloading_address', sa.String(500), nullable=True))
    op.add_column('location_rooms', sa.Column('unloading_lat', sa.Float(), nullable=True))
    op.add_column('location_rooms', sa.Column('unloading_lng', sa.Float(), nullable=True))
    # 타임라인
    op.add_column('location_rooms', sa.Column('arrived_at_loading', sa.DateTime(timezone=True), nullable=True))
    op.add_column('location_rooms', sa.Column('departed_loading', sa.DateTime(timezone=True), nullable=True))
    op.add_column('location_rooms', sa.Column('arrived_at_unloading', sa.DateTime(timezone=True), nullable=True))
    op.add_column('location_rooms', sa.Column('departed_unloading', sa.DateTime(timezone=True), nullable=True))
    # 내부 geofence 플래그
    op.add_column('location_rooms', sa.Column('in_loading_zone', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('location_rooms', sa.Column('in_unloading_zone', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('location_rooms', 'in_unloading_zone')
    op.drop_column('location_rooms', 'in_loading_zone')
    op.drop_column('location_rooms', 'departed_unloading')
    op.drop_column('location_rooms', 'arrived_at_unloading')
    op.drop_column('location_rooms', 'departed_loading')
    op.drop_column('location_rooms', 'arrived_at_loading')
    op.drop_column('location_rooms', 'unloading_lng')
    op.drop_column('location_rooms', 'unloading_lat')
    op.drop_column('location_rooms', 'unloading_address')
    op.drop_column('location_rooms', 'unloading_name')
    op.drop_column('location_rooms', 'loading_lng')
    op.drop_column('location_rooms', 'loading_lat')
    op.drop_column('location_rooms', 'loading_address')
    op.drop_column('location_rooms', 'loading_name')
