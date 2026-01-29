"""Rename has_forklift to forklift_operator_available

Revision ID: 20260129140000
Revises: 20260129115304
Create Date: 2026-01-29 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260129140000'
down_revision = '20260129115304'
branch_labels = None
depends_on = None


def upgrade():
    # Rename column in clients table
    op.alter_column('clients', 'has_forklift',
                    new_column_name='forklift_operator_available',
                    existing_type=sa.Boolean(),
                    existing_nullable=False,
                    existing_server_default=sa.text('false'),
                    comment='지게차 운전능력 가능 여부')
    
    # Rename column in vehicles table
    op.alter_column('vehicles', 'has_forklift',
                    new_column_name='forklift_operator_available',
                    existing_type=sa.Boolean(),
                    existing_nullable=False,
                    existing_server_default=sa.text('false'),
                    comment='지게차 운전능력 가능 여부')


def downgrade():
    # Revert column name in vehicles table
    op.alter_column('vehicles', 'forklift_operator_available',
                    new_column_name='has_forklift',
                    existing_type=sa.Boolean(),
                    existing_nullable=False,
                    existing_server_default=sa.text('false'),
                    comment='지게차 가능 여부')
    
    # Revert column name in clients table
    op.alter_column('clients', 'forklift_operator_available',
                    new_column_name='has_forklift',
                    existing_type=sa.Boolean(),
                    existing_nullable=False,
                    existing_server_default=sa.text('false'),
                    comment='지게차 유무')
