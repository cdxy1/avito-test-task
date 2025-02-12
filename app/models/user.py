from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str]
    balance: Mapped[int] = mapped_column(default=1000, nullable=False)
    is_active: Mapped[bool]
