"""create invoices table

Revision ID: 2ead63bf3591
Revises: fa8e243e1251
Create Date: 2024-02-18 13:04:54.363075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence


# revision identifiers, used by Alembic.
revision: str = '2ead63bf3591'
down_revision: Union[str, None] = 'fa8e243e1251'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

id_seq = sa.Sequence("invoices_id_seq")


def upgrade() -> None:
    op.execute(CreateSequence(id_seq))

    op.create_table(
        "invoices",
        sa.Column("id", sa.BigInteger, id_seq, server_default=id_seq.next_value(), nullable=False, primary_key=True),
        sa.Column("invoice_date", sa.Date, nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("kwh_consumed", sa.Float, nullable=False),
        sa.Column("customer_id", sa.BigInteger, nullable=False),
        sa.Column("stripe_id", sa.String(255), nullable=True),
        sa.Column("link", sa.String(255), nullable=True),
    )

    op.create_foreign_key("fk_customer_invoice", "invoices", "customers", ["customer_id"], ["id"])


def downgrade() -> None:
    op.drop_table("invoices")
    op.execute(DropSequence(id_seq))
