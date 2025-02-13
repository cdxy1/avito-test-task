from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class TransferModel(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    from_user: Mapped[str]
    to_user: Mapped[str]
    amount: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class PurchaseModel(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_user: Mapped[str]
    item_name: Mapped[str]
    pub_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
