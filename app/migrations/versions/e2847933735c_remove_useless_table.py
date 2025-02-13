"""remove useless table

Revision ID: e2847933735c
Revises: 1fc57012ebb8
Create Date: 2025-02-13 11:57:41.201824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2847933735c'
down_revision: Union[str, None] = '1fc57012ebb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('inventories')
    op.drop_table('transactions')
    op.drop_table('items')
    op.drop_table('purchases')
    op.drop_table('users')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(), nullable=False),
    sa.Column('password', sa.VARCHAR(), nullable=False),
    sa.Column('role', sa.VARCHAR(), nullable=False),
    sa.Column('balance', sa.INTEGER(), nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('purchases',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('from_user', sa.VARCHAR(), nullable=False),
    sa.Column('item_name', sa.VARCHAR(), nullable=False),
    sa.Column('pub_date', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('items',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('price', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('from_user', sa.VARCHAR(), nullable=False),
    sa.Column('to_user', sa.VARCHAR(), nullable=False),
    sa.Column('amount', sa.INTEGER(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('inventories',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('belongs_to_name', sa.VARCHAR(), nullable=False),
    sa.Column('item_name', sa.VARCHAR(), nullable=False),
    sa.Column('quantity', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
