import os
from datetime import date, datetime

import sqlalchemy as sa
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Mapped, Session, mapped_column

from energy_bills.models.base import Base


class Usage(Base):
    __tablename__ = "usage"
    id: Mapped[int] = mapped_column(primary_key=True)
    usage_date: Mapped[date] = mapped_column(server_default=sa.func.current_date())
    kwh_consumed: Mapped[float]
    device_id: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(server_default=sa.func.current_timestamp())

    @classmethod
    def upsert(cls, data: dict) -> None:
        """Creates customer if not exists, updates it otherwise"""

        engine = create_engine(os.getenv("DB_URI"))
        with Session(engine) as session:
            stmt = (
                select(cls)
                .where(cls.device_id == data["device_id"])
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
                    .where(cls.device_id == data["device_id"])
                    .where(cls.usage_date == data["usage_date"])
                    .values(**data)
                )
                session.execute(stmt)
                session.commit()
    
    @classmethod
    def compute_device_usage(cls, device_id: int, start: datetime, end: datetime) -> float:
        engine = create_engine(os.getenv("DB_URI"))
        session = Session(engine)

        return (
            session.query(sa.func.sum(cls.kwh_consumed).label("total"))
            .where(cls.device_id == device_id)
            .where(cls.usage_date >= start)
            .where(cls.usage_date <= end)
            .first()
            [0]
        )
    
    @classmethod
    def find_device_last_date(cls, device_id: int) -> date | None:
        engine = create_engine(os.getenv("DB_URI"))
        session = Session(engine)

        return (
            session.query(sa.func.max(cls.usage_date).label("date"))
            .where(cls.device_id == device_id)
            .first()
            [0]
        )
