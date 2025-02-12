from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class ItemModel(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[int]


class InventoryModel(Base):
    __tablename__ = "inventories"

    id: Mapped[int] = mapped_column(primary_key=True)
    belongs_to_name: Mapped[str]
    item_name: Mapped[str]
    quantity: Mapped[int]
