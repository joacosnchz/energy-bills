import os
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from energy_bills.models.base import Base

if TYPE_CHECKING:
    from energy_bills.models.customer import Customer


class PropertyOwner(Base):
    __tablename__ = "property_owners"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    park_id: Mapped[Optional[int]]
    kwh_rate: Mapped[float]
    customers_list_id: Mapped[Optional[str]]
    emporia_usr: Mapped[Optional[str]]
    emporia_pwd: Mapped[Optional[str]]
    stripe_id: Mapped[Optional[str]]

    customers: Mapped[List["Customer"]] = relationship(back_populates="property_owner", lazy=True)

    @classmethod
    def get_all(cls) -> List["PropertyOwner"]:
        engine = create_engine(os.getenv("DB_URI"))
        session = Session(engine)
        stmt = select(PropertyOwner)

        return session.scalars(stmt).unique()
