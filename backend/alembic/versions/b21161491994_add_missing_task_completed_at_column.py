"""Add missing task.completed_at column

Revision ID: b21161491994
Revises: fc63459e144e
Create Date: 2025-12-18 03:30:07.188375

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b21161491994'
down_revision: Union[str, Sequence[str], None] = 'fc63459e144e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add missing task.completed_at column if it doesn't exist
    try:
        op.add_column('task', sa.Column('completed_at', sa.DateTime(), nullable=True))
    except Exception:
        # Column already exists, ignore error
        pass

    # Add missing conversations columns if they don't exist
    try:
        op.add_column('conversations', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    except Exception:
        pass

    try:
        op.add_column('conversations', sa.Column('messages_count', sa.Integer(), nullable=False, server_default='0'))
    except Exception:
        pass

    try:
        op.add_column('conversations', sa.Column('last_message_at', sa.DateTime(), nullable=True))
    except Exception:
        pass

    try:
        op.add_column('conversations', sa.Column('extra_data', sa.JSON(), nullable=True))
    except Exception:
        pass


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns if they exist
    try:
        op.drop_column('task', 'completed_at')
    except Exception:
        pass

    try:
        op.drop_column('conversations', 'is_active')
    except Exception:
        pass

    try:
        op.drop_column('conversations', 'messages_count')
    except Exception:
        pass

    try:
        op.drop_column('conversations', 'last_message_at')
    except Exception:
        pass

    try:
        op.drop_column('conversations', 'extra_data')
    except Exception:
        pass
