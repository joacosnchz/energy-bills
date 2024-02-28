"""create usage table

Revision ID: 3470a90fb575
Revises: 2ead63bf3591
Create Date: 2024-02-27 19:42:59.201604

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence


# revision identifiers, used by Alembic.
revision: str = "3470a90fb575"
down_revision: Union[str, None] = "2ead63bf3591"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

id_seq = sa.Sequence("usage_id_seq")


def upgrade() -> None:
    op.execute(CreateSequence(id_seq))

    op.create_table(
        "usage",
        sa.Column("id", sa.BigInteger, id_seq, server_default=id_seq.next_value(), nullable=False, primary_key=True),
        sa.Column("usage_date", sa.Date, nullable=False, server_default=sa.func.current_date()),
        sa.Column("kwh_consumed", sa.Float, nullable=False),
        sa.Column("customer_id", sa.BigInteger, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
    )

    op.create_foreign_key("fk_customer_usage", "usage", "customers", ["customer_id"], ["id"])


def downgrade() -> None:
    op.drop_table("usage")
    op.execute(DropSequence(id_seq))
