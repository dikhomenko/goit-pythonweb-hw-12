"""Add user-roles Enum and role column to the User table

Revision ID: ff0ef6b3ae2b
Revises: 4a3acf42b916
Create Date: 2025-04-12 11:52:52.203912

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# Define the enum type
userrole_enum = ENUM("user", "admin", name="userrole")

# revision identifiers, used by Alembic.
revision: str = "ff0ef6b3ae2b"
down_revision: Union[str, None] = "4a3acf42b916"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create the enum type
    userrole_enum.create(op.get_bind())

    # Add the role column to the users table
    op.add_column(
        "users", sa.Column("role", userrole_enum, server_default="user", nullable=False)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    # Drop the role column
    op.drop_column("users", "role")

    # Drop the enum type
    userrole_enum.drop(op.get_bind())
