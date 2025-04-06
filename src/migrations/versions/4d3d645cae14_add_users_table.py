"""Add users table

Revision ID: 4d3d645cae14
Revises: a1be75c7e0e1
Create Date: 2025-03-29 18:25:39.954628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d3d645cae14'
down_revision: Union[str, None] = 'a1be75c7e0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=150), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.drop_constraint('contacts_birthday_key', 'contacts', type_='unique')
    op.drop_constraint('contacts_first_name_key', 'contacts', type_='unique')
    op.drop_constraint('contacts_last_name_key', 'contacts', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('contacts_last_name_key', 'contacts', ['last_name'])
    op.create_unique_constraint('contacts_first_name_key', 'contacts', ['first_name'])
    op.create_unique_constraint('contacts_birthday_key', 'contacts', ['birthday'])
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
