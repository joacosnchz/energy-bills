import os
from datetime import date, datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey, create_engine, select, update
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from energy_bills.models.base import Base

if TYPE_CHECKING:
    from energy_bills.models.customer import Customer


class Usage(Base):
    __tablename__ = "usage"
    id: Mapped[int] = mapped_column(primary_key=True)
    usage_date: Mapped[date] = mapped_column(server_default=sa.func.current_date())
    kwh_consumed: Mapped[float]
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(server_default=sa.func.current_timestamp())

    customer: Mapped["Customer"] = relationship(lazy=True)
