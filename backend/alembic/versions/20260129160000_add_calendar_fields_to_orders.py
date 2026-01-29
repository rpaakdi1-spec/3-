"""add calendar fields to orders

Revision ID: 20260129160000
Revises: 20260129150000
Create Date: 2026-01-29 16:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260129160000'
down_revision: Union[str, None] = '20260129150000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add calendar-related fields to orders table
    op.add_column('orders', sa.Column('is_reserved', sa.Boolean(), nullable=False, server_default='false', comment='예약 오더 여부'))
    op.add_column('orders', sa.Column('reserved_at', sa.Date(), nullable=True, comment='예약 생성일'))
    op.add_column('orders', sa.Column('confirmed_at', sa.Date(), nullable=True, comment='오더 확정일'))
    op.add_column('orders', sa.Column('recurring_type', sa.String(20), nullable=True, comment='반복 유형 (DAILY, WEEKLY, MONTHLY)'))
    op.add_column('orders', sa.Column('recurring_end_date', sa.Date(), nullable=True, comment='반복 종료일'))


def downgrade() -> None:
    # Remove calendar-related fields
    op.drop_column('orders', 'recurring_end_date')
    op.drop_column('orders', 'recurring_type')
    op.drop_column('orders', 'confirmed_at')
    op.drop_column('orders', 'reserved_at')
    op.drop_column('orders', 'is_reserved')
