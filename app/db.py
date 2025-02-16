import os
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, database_url: Optional[str] = None):
        self.DATABASE_URL = (
            database_url if database_url is not None else os.getenv("DATABASE_URL")
        )
        self.engine = create_async_engine(self.DATABASE_URL)
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_session(self):
        async with self.async_session() as session:
            yield session

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


database = Database()
