"""Fix enum columns to use proper types

Revision ID: ac0c5d849b15
Revises: f87654321098
Create Date: 2025-12-18 04:09:05.689155

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac0c5d849b15'
down_revision: Union[str, Sequence[str], None] = 'f87654321098'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - fix message_type and operation_status to use proper enum types."""

    # Drop existing columns
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS message_type")
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS operation_status")

    # Recreate columns using existing enum types with their actual values
    # Based on errors, the enums likely have uppercase values
    op.execute("ALTER TABLE messages ADD COLUMN message_type messagetype NOT NULL DEFAULT 'TEXT'")
    op.execute("ALTER TABLE messages ADD COLUMN operation_status operationstatus NOT NULL DEFAULT 'DELIVERED'")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop enum columns
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS message_type")
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS operation_status")

    # Recreate as VARCHAR (previous state)
    op.execute("ALTER TABLE messages ADD COLUMN message_type VARCHAR(50) NOT NULL DEFAULT 'text'")
    op.execute("ALTER TABLE messages ADD COLUMN operation_status VARCHAR(50) NOT NULL DEFAULT 'delivered'")
