from ..db import Base

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str]
    is_active: Mapped[bool]
