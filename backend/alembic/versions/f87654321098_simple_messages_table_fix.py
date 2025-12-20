"""Simple fix for messages table - avoid enum conflicts

Revision ID: f87654321098
Revises: e12345678901
Create Date: 2025-12-18 04:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f87654321098'
down_revision: Union[str, Sequence[str], None] = 'e12345678901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add missing columns as VARCHAR to avoid enum conflicts."""

    # Add all missing columns as VARCHAR first to ensure they exist
    op.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS message_type VARCHAR(50) NOT NULL DEFAULT 'text'")
    op.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS operation_status VARCHAR(50) NOT NULL DEFAULT 'delivered'")
    op.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS operation_type VARCHAR(100) NULL")
    op.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS operation_result JSON NULL")
    op.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS error_details JSON NULL")
    op.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS extra_data JSON NOT NULL DEFAULT '{}'")
    op.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS processing_started_at TIMESTAMP NULL")
    op.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS processing_completed_at TIMESTAMP NULL")
    op.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS retry_count")
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS processing_completed_at")
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS processing_started_at")
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS extra_data")
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS error_details")
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS operation_result")
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS operation_type")
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS operation_status")
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS message_type")