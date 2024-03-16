"""create property owners table

Revision ID: 59b58b66dc98
Revises: 
Create Date: 2024-02-18 11:56:26.107221

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence


# revision identifiers, used by Alembic.
revision: str = "59b58b66dc98"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

id_seq = sa.Sequence("property_owners_id_seq")


def upgrade() -> None:
    op.execute(CreateSequence(id_seq))

    op.create_table(
        "property_owners",
        sa.Column("id", sa.BigInteger, id_seq, server_default=id_seq.next_value(), nullable=False, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("park_id", sa.Integer, nullable=True),
        sa.Column("kwh_rate", sa.Integer, nullable=False),
        sa.Column("customers_list_id", sa.String(255), nullable=True),
        sa.Column("emporia_usr", sa.String(255), nullable=True),
        sa.Column("emporia_pwd", sa.String(255), nullable=True),
        sa.Column("stripe_id", sa.String(255), nullable=True),
        sa.Column("stripe_price_id", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("property_owners")
    op.execute(DropSequence(id_seq))
