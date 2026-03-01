"""add cargo_license_issue_date to employees

Revision ID: 20260301_cargo_issue
Revises: 
Create Date: 2026-03-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260301_cargo_issue'
down_revision = None  # Will be set to latest revision
branch_labels = None
depends_on = None


def upgrade():
    # Add cargo_license_issue_date column to employees table
    op.add_column('employees', sa.Column('cargo_license_issue_date', sa.Date(), nullable=True, comment='화물운송자격증 발급일'))


def downgrade():
    # Remove cargo_license_issue_date column
    op.drop_column('employees', 'cargo_license_issue_date')
