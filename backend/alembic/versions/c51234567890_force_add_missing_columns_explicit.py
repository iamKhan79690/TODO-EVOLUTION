"""Force add missing columns - explicit version

Revision ID: c51234567890
Revises: b21161491994
Create Date: 2025-12-18 03:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c51234567890'
down_revision: Union[str, Sequence[str], None] = 'b21161491994'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add missing columns without error handling."""
    # Add task.completed_at column if it doesn't exist
    op.execute("ALTER TABLE task ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP NULL")

    # Add conversations columns if they don't exist
    op.execute("ALTER TABLE conversations ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT true")
    op.execute("ALTER TABLE conversations ADD COLUMN IF NOT EXISTS messages_count INTEGER NOT NULL DEFAULT 0")
    op.execute("ALTER TABLE conversations ADD COLUMN IF NOT EXISTS last_message_at TIMESTAMP NULL")
    op.execute("ALTER TABLE conversations ADD COLUMN IF NOT EXISTS extra_data JSON NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns
    op.execute("ALTER TABLE task DROP COLUMN IF EXISTS completed_at")
    op.execute("ALTER TABLE conversations DROP COLUMN IF EXISTS is_active")
    op.execute("ALTER TABLE conversations DROP COLUMN IF EXISTS messages_count")
    op.execute("ALTER TABLE conversations DROP COLUMN IF EXISTS last_message_at")
    op.execute("ALTER TABLE conversations DROP COLUMN IF EXISTS extra_data")