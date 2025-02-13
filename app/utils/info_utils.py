from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.transaction import PurchaseModel, TransferModel
from ..models.user import UserModel


async def get_user_info(session: AsyncSession, username: str) -> UserModel:
    query = select(UserModel).filter(UserModel.username == username)
    result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user_transfers(session: AsyncSession, username: str):
    query = select(TransferModel).filter(
        or_(TransferModel.to_user == username, TransferModel.from_user == username)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_user_purchases(session: AsyncSession, username: str):
    query = select(PurchaseModel).filter(PurchaseModel.from_user == username)
    result = await session.execute(query)
    return result.scalars().all()


def count_items(purchases: list) -> dict:
    item_counts = {}
    for purchase in purchases:
        item_name = purchase.item_name
        item_counts[item_name] = item_counts.get(item_name, 0) + 1
    return item_counts


def process_transfers(transfers: list, username: str) -> dict:
    received = {}
    sent = {}
    for transfer in transfers:
        if transfer.to_user == username:
            received[transfer.from_user] = (
                received.get(transfer.from_user, 0) + transfer.amount
            )
        elif transfer.from_user == username:
            sent[transfer.to_user] = sent.get(transfer.to_user, 0) + transfer.amount
    return {"received": received, "sent": sent}
