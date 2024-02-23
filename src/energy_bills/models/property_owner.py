import os
from typing import List

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from energy_bills.models.base import Base


class PropertyOwner(Base):
    __tablename__ = "property_owners"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    park_id: Mapped[int]
    kwh_rate: Mapped[float]
    customers_list_id: Mapped[str]
    emporia_usr: Mapped[str]
    emporia_pwd: Mapped[str]
    stripe_id: Mapped[str]

    @classmethod
    def get_all(cls) -> List["PropertyOwner"]:
        engine = create_engine(os.getenv("DB_URI"))
        session = Session(engine)
        stmt = select(PropertyOwner)

        return session.scalars(stmt).unique()
