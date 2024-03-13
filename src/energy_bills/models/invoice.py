import os
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, create_engine, select
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

    @classmethod
    def create(cls, data: dict) -> None:
        """Creates invoice only if not exists"""

        engine = create_engine(os.getenv("DB_URI"))
        with Session(engine) as session:
            stmt = (
                select(cls)
                .where(cls.invoice_date == data["invoice_date"])
                .where(cls.customer_id == data["customer_id"])
            )
            existing = session.scalars(stmt).first()

            if not existing:
                session.add(cls(**data))
                session.commit()
