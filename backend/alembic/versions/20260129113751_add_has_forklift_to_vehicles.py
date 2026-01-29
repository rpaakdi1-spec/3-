"""add has_forklift to vehicles

Revision ID: 20260129113751
Revises: a995c798829a
Create Date: 2026-01-29 11:37:51.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260129113751'
down_revision = 'a995c798829a'
branch_labels = None
depends_on = None


def upgrade():
    # Add has_forklift column to vehicles table
    op.add_column('vehicles', 
        sa.Column('has_forklift', sa.Boolean(), nullable=False, server_default='false', comment='지게차 가능 여부')
    )


def downgrade():
    # Remove has_forklift column from vehicles table
    op.drop_column('vehicles', 'has_forklift')
