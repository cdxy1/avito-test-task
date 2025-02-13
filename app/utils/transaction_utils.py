from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.item import ItemModel
from ..models.user import UserModel


async def get_item_by_name(session: AsyncSession, item_name: str) -> ItemModel:
    query = select(ItemModel).filter(ItemModel.name == item_name)
    result = await session.execute(query)
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


async def check_balance(user: UserModel, amount: int) -> None:
    if user.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
