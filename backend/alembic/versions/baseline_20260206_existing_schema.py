"""Baseline migration for existing database schema

Revision ID: baseline_20260206
Revises: 
Create Date: 2026-02-06 20:05:00.000000

This is a baseline migration that represents the existing database schema.
All tables already exist, so this migration does nothing but marks the starting point.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'baseline_20260206'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    No-op upgrade. All tables already exist in the database.
    This migration just marks the baseline for future migrations.
    """
    pass


def downgrade() -> None:
    """
    Cannot downgrade from baseline.
    """
    pass
