"""create customers table

Revision ID: fa8e243e1251
Revises: 59b58b66dc98
Create Date: 2024-02-18 12:19:21.129719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence


# revision identifiers, used by Alembic.
revision: str = "fa8e243e1251"
down_revision: Union[str, None] = "59b58b66dc98"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

id_seq = sa.Sequence("customers_id_seq")

def upgrade() -> None:
    op.execute(CreateSequence(id_seq))

    op.create_table(
        "customers",
        sa.Column("id", sa.BigInteger, id_seq, server_default=id_seq.next_value(), nullable=False, primary_key=True),
        sa.Column("pad_id", sa.Integer, nullable=False),
        sa.Column("first_name", sa.String(255), nullable=False),
        sa.Column("last_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(255), nullable=True),
        sa.Column("property_owner_id", sa.BigInteger, nullable=False),
        sa.Column("aniversary_day", sa.Integer, nullable=False),
        sa.Column("move_in_date", sa.Date, nullable=False),
        sa.Column("move_out_date", sa.Date, nullable=True),
        sa.Column("devices", sa.String(255), nullable=False),
        sa.Column("stripe_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
    )

    op.create_foreign_key("fk_property_owner_customer", "customers", "property_owners", ["property_owner_id"], ["id"])


def downgrade() -> None:
    op.drop_table("customers")
    op.execute(DropSequence(id_seq))
