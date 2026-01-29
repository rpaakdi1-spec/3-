"""make weight optional

Revision ID: 20260129115304
Revises: 20260129113751
Create Date: 2026-01-29 11:53:04.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260129115304'
down_revision = '20260129113751'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Make weight_kg optional in orders table"""
    # Make weight_kg nullable and set default to 0
    op.alter_column('orders', 'weight_kg',
                    existing_type=sa.Float(),
                    nullable=True,
                    server_default='0')


def downgrade() -> None:
    """Revert weight_kg to required"""
    # First update any NULL values to 0
    op.execute("UPDATE orders SET weight_kg = 0 WHERE weight_kg IS NULL")
    
    # Make weight_kg non-nullable again
    op.alter_column('orders', 'weight_kg',
                    existing_type=sa.Float(),
                    nullable=False,
                    server_default=None)
