#!/bin/bash
cd /root/uvis

# Create Alembic migration file
cat > "backend/alembic/versions/$(date +%Y%m%d_%H%M%S)_add_user_approval_fields.py" << 'MIGRATION_EOF'
"""add user approval fields

Revision ID: $(date +%s | tail -c 8)
Revises: 
Create Date: $(date +"%Y-%m-%d %H:%M:%S")

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '$(openssl rand -hex 6)'
down_revision = None  # Update this with your latest revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add approval_status field
    op.add_column('users', sa.Column('approval_status', sa.String(20), nullable=False, server_default='pending', comment='승인 상태: pending, approved, rejected'))
    
    # Add approved_by field
    op.add_column('users', sa.Column('approved_by', sa.Integer(), nullable=True, comment='승인한 사용자 ID'))
    
    # Add approved_at field
    op.add_column('users', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True, comment='승인 일시'))
    
    # Update existing users to 'approved' status
    op.execute("UPDATE users SET approval_status = 'approved', approved_at = NOW() WHERE is_active = true")


def downgrade() -> None:
    op.drop_column('users', 'approved_at')
    op.drop_column('users', 'approved_by')
    op.drop_column('users', 'approval_status')
MIGRATION_EOF

echo "✅ Migration file created"
ls -lh backend/alembic/versions/*approval*
