"""empty message

Revision ID: 555a64706a39
Revises: 5065f2153eb2
Create Date: 2025-02-12 04:42:34.000454

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "555a64706a39"
down_revision: Union[str, None] = "5065f2153eb2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("balance")
    op.drop_table("users")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("username", sa.VARCHAR(), nullable=False),
        sa.Column("password", sa.VARCHAR(), nullable=False),
        sa.Column("role", sa.VARCHAR(), nullable=False),
        sa.Column("is_active", sa.BOOLEAN(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "balance",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("user_id", sa.INTEGER(), nullable=False),
        sa.Column("balance", sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###
