"""Database Performance Optimization - Add composite indexes

Revision ID: performance_001
Revises: a995c798829a
Create Date: 2026-01-28 18:21:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'performance_001'
down_revision = 'a995c798829a'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance optimization indexes"""
    
    # Orders table composite indexes
    op.create_index(
        'idx_orders_status_date',
        'orders',
        ['status', 'created_at'],
        postgresql_using='btree'
    )
    
    op.create_index(
        'idx_orders_client_temp',
        'orders',
        ['pickup_client_id', 'temperature_type'],
        postgresql_using='btree'
    )
    
    op.create_index(
        'idx_orders_delivery_client_temp',
        'orders',
        ['delivery_client_id', 'temperature_type'],
        postgresql_using='btree'
    )
    
    # Dispatches table composite indexes
    op.create_index(
        'idx_dispatches_vehicle_date',
        'dispatches',
        ['vehicle_id', 'dispatch_date'],
        postgresql_using='btree'
    )
    
    op.create_index(
        'idx_dispatches_driver_date',
        'dispatches',
        ['driver_id', 'dispatch_date'],
        postgresql_using='btree'
    )
    
    op.create_index(
        'idx_dispatches_status_date',
        'dispatches',
        ['status', 'dispatch_date'],
        postgresql_using='btree'
    )
    
    # Vehicles table indexes
    op.create_index(
        'idx_vehicles_type_status',
        'vehicles',
        ['vehicle_type', 'status'],
        postgresql_using='btree'
    )
    
    # Users table indexes
    op.create_index(
        'idx_users_role_active',
        'users',
        ['role', 'is_active'],
        postgresql_using='btree'
    )
    
    # Clients table indexes
    op.create_index(
        'idx_clients_location_type',
        'clients',
        ['location_type', 'is_active'],
        postgresql_using='btree'
    )


def downgrade():
    """Remove performance optimization indexes"""
    
    # Drop indexes in reverse order
    op.drop_index('idx_clients_location_type', table_name='clients')
    op.drop_index('idx_users_role_active', table_name='users')
    op.drop_index('idx_vehicles_type_status', table_name='vehicles')
    op.drop_index('idx_dispatches_status_date', table_name='dispatches')
    op.drop_index('idx_dispatches_driver_date', table_name='dispatches')
    op.drop_index('idx_dispatches_vehicle_date', table_name='dispatches')
    op.drop_index('idx_orders_delivery_client_temp', table_name='orders')
    op.drop_index('idx_orders_client_temp', table_name='orders')
    op.drop_index('idx_orders_status_date', table_name='orders')
