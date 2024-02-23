import os
from typing import Optional

from sqlalchemy import ForeignKey, create_engine, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from energy_bills.models.base import Base
from energy_bills.models.property_owner import PropertyOwner
from datetime import datetime
import sqlalchemy as sa


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

    @classmethod
    def create(cls, customer: "Customer") -> None:
        engine = create_engine(os.getenv("DB_URI"))
        with Session(engine) as session:
            stmt = select(Customer).where(cls.email == customer.email)
            existing = session.scalars(stmt).first()

            if not existing:
                session.add(customer)
                session.commit()
