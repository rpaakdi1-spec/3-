"""merge heads

Revision ID: 20260129150000
Revises: 20260129140000, db_optimization_001
Create Date: 2026-01-29 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260129150000'
down_revision = ('20260129140000', 'db_optimization_001')
branch_labels = None
depends_on = None


def upgrade():
    # Merge migration - no operations needed
    pass


def downgrade():
    # Merge migration - no operations needed
    pass
