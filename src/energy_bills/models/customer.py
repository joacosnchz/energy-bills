import os
from datetime import datetime
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
    move_in: Mapped[str]
    move_out_day: Mapped[Optional[int]]
    devices: Mapped[str]
    stripe_id: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(server_default=sa.func.current_timestamp())

    property_owner: Mapped["PropertyOwner"] = relationship(lazy=True)

    def get_device_list(self, active_devices: list[int]) -> list[int]:
        """Get list of active devices from customer"""
        customer_devices = [int(d) for d in self.devices.split(",")]

        return [d for d in customer_devices if d in active_devices]

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
