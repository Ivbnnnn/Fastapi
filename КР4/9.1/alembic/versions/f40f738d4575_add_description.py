"""add_description

Revision ID: f40f738d4575
Revises: 417b4c59c1de
Create Date: 2026-05-02 19:34:22.084521

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f40f738d4575'
down_revision: Union[str, Sequence[str], None] = '417b4c59c1de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE product ADD COLUMN description VARCHAR(255) NOT NULL DEFAULT 'not null'")
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
