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

    @classmethod
    def upsert(cls, data: dict) -> None:
        """Creates customer if not exists, updates it otherwise"""

        engine = create_engine(os.getenv("DB_URI"))
        with Session(engine) as session:
            stmt = (
                select(cls)
                .where(cls.customer_id == data["customer_id"])
                .where(cls.usage_date == data["usage_date"])
            )
            existing = session.scalars(stmt).first()

            if not existing:
                session.add(cls(**data))
                session.commit()
            else:
                existing.updated_at = datetime.now()
                stmt = (
                    update(cls)
                    .where(cls.customer_id == data["customer_id"])
                    .where(cls.usage_date == data["usage_date"])
                    .values(**data)
                )
                session.execute(stmt)
                session.commit()
    
    @classmethod
    def compute_customer_usage(cls, customer_id: int, start: datetime, end: datetime) -> float:
        engine = create_engine(os.getenv("DB_URI"))
        session = Session(engine)

        return (
            session.query(sa.func.sum(cls.kwh_consumed).label("total"))
            .where(cls.customer_id == customer_id)
            .where(cls.usage_date >= start)
            .where(cls.usage_date <= end)
            .first()
            [0]
        )