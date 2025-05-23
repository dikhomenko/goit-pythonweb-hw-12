"""add emal field to the user

Revision ID: fca877170cb3
Revises: 4d3d645cae14
Create Date: 2025-03-30 16:55:53.250304

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fca877170cb3"
down_revision: Union[str, None] = "4d3d645cae14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
            unique=True,
            server_default="user-1@user.com",
        ),
    )
    op.create_unique_constraint(None, "users", ["email"])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "users", type_="unique")
    op.drop_column("users", "email")
    # ### end Alembic commands ###
