"""make email nullable in users table

Revision ID: 20260228_155700
Revises: 20260228_133550
Create Date: 2026-02-28 15:57:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260228_155700'
down_revision = '20260228_133550'
branch_labels = None
depends_on = None


def upgrade():
    """Make email field nullable in users table"""
    # Drop unique constraint temporarily
    op.drop_constraint('users_email_key', 'users', type_='unique')
    
    # Alter column to be nullable
    op.alter_column('users', 'email',
                    existing_type=sa.String(length=100),
                    nullable=True,
                    existing_nullable=False)
    
    # Recreate unique constraint (but only for non-NULL values)
    # PostgreSQL allows multiple NULL values in unique columns
    op.create_unique_constraint('users_email_key', 'users', ['email'])


def downgrade():
    """Revert email field to non-nullable"""
    # This would require filling NULL emails with dummy values first
    # So we'll just raise an error
    raise NotImplementedError("Downgrade not supported - would require filling NULL emails")
