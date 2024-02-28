import os
from datetime import datetime, date
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, create_engine, select, update
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from energy_bills.models.base import Base

if TYPE_CHECKING:
    from energy_bills.models.customer import Customer

class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_date: Mapped[date]
    amount: Mapped[float]
    kwh_consumed: Mapped[float]
    kwh_rate: Mapped[float]
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    stripe_id: Mapped[str]
    link: Mapped[str]
    sent_at: Mapped[Optional[datetime]]

    customer: Mapped["Customer"] = relationship(lazy=True)
