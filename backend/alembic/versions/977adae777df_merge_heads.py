"""merge heads

Revision ID: 977adae777df
Revises: a6eb2e22dbd2, phase11c_templates_data
Create Date: 2026-02-28 00:10:50.744162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '977adae777df'
down_revision: Union[str, Sequence[str], None] = ('a6eb2e22dbd2', 'phase11c_templates_data')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
