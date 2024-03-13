import os
from datetime import datetime, date
from typing import List, Optional, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey, create_engine, select, update
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from energy_bills.models.base import Base

if TYPE_CHECKING:
    from energy_bills.models.property_owner import PropertyOwner


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    pad_id: Mapped[int]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    phone: Mapped[Optional[str]]
    property_owner_id: Mapped[int] = mapped_column(ForeignKey("property_owners.id"))
    aniversary_day: Mapped[int]
    move_in_date: Mapped[date]
    move_out_date: Mapped[Optional[date]]
    devices: Mapped[str]
    stripe_id: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(server_default=sa.func.current_timestamp())

    property_owner: Mapped["PropertyOwner"] = relationship(lazy=True)

    def filter_devices(self, active_devices: list) -> list:
        """Get list of active devices from customer"""
        customer_devices = self.devices.split(",")

        return [d for d in active_devices if str(d["deviceGid"]) in customer_devices]

    @classmethod
    def get_all(cls) -> List["Customer"]:
        engine = create_engine(os.getenv("DB_URI"))
        session = Session(engine)
        stmt = select(cls)

        return session.scalars(stmt).unique()

    @classmethod
    def upsert(cls, customer: dict) -> None:
        """Creates customer if not exists, updates it otherwise"""

        engine = create_engine(os.getenv("DB_URI"))
        with Session(engine) as session:
            stmt = select(cls).where(cls.email == customer["email"])
            existing = session.scalars(stmt).first()

            if not existing:
                session.add(Customer(**customer))
                session.commit()
            else:
                existing.updated_at = datetime.now()
                stmt = (
                    update(cls)
                    .where(cls.email == customer["email"])
                    .values(**customer)
                )
                session.execute(stmt)
                session.commit()

    @classmethod
    def get_active_customers(cls, interval_end: date) -> List["Customer"]:
        """Get customers using energy on a date"""

        engine = create_engine(os.getenv("DB_URI"))
        session = Session(engine)
        stmt = (
            select(cls)
            .where(cls.move_in_date <= interval_end)
            .where(sa.or_(
                cls.move_out_date.is_(None),
                cls.move_out_date >= interval_end,
            ))
        )

        return session.scalars(stmt).unique()

    @classmethod
    def get_active_billable_customers(cls, interval_end: date) -> List["Customer"]:
        """Get customers using energy on a date"""
        ts_day = int(interval_end.strftime("%d").replace("0", ""))

        engine = create_engine(os.getenv("DB_URI"))
        session = Session(engine)
        stmt = (
            select(cls)
            .where(cls.aniversary_day == ts_day)
            .where(cls.move_in_date <= interval_end)
            .where(sa.or_(
                cls.move_out_date.is_(None),
                cls.move_out_date >= interval_end,
            ))
        )

        return session.scalars(stmt).unique()
