"""baseline

Revision ID: ceea6fda39d0
Revises:
Create Date: 2026-03-21 01:17:02.363804

"""

from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = "ceea6fda39d0"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
