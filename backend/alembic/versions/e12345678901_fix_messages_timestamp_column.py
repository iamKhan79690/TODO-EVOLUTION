"""Fix messages timestamp column - simple approach

Revision ID: e12345678901
Revises: c51234567890
Create Date: 2025-12-18 03:44:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e12345678901'
down_revision: Union[str, Sequence[str], None] = 'c51234567890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - fix messages timestamp column using op.add_column."""
    # Use Alembic's built-in op.add_column for better transaction handling
    # First add the basic timestamp column
    op.add_column('messages', sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('messages', 'timestamp')