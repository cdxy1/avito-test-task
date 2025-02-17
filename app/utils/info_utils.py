from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.transaction import PurchaseModel, TransferModel
from ..models.user import UserModel


async def get_user_info(user_id: int, session: AsyncSession) -> UserModel:
    query = select(UserModel).filter(UserModel.id == int(user_id))
    result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
    return user


async def get_user_by_username(username: str, session: AsyncSession) -> UserModel:
    query = select(UserModel).where(UserModel.username == username)
    result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user_transfers(
    user_id: int, session: AsyncSession
) -> list[TransferModel]:
    query = (
        select(TransferModel)
        .where(
            (TransferModel.from_user_id == user_id)
            | (TransferModel.to_user_id == user_id)
        )
        .options(
            selectinload(TransferModel.sender),
            selectinload(TransferModel.receiver),
        )
        .order_by(TransferModel.created_at.desc())
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_user_purchases(
    user_id: int, session: AsyncSession
) -> list[PurchaseModel]:
    query = (
        select(PurchaseModel)
        .where(PurchaseModel.user_id == user_id)
        .options(selectinload(PurchaseModel.item))
        .order_by(PurchaseModel.pub_date.desc())
    )
    result = await session.execute(query)
    return result.scalars().all()


def count_items(purchases: list[PurchaseModel]) -> dict[str, int]:
    if not purchases:
        return {}
    item_counts = {}
    for purchase in purchases:
        item_name = purchase.item.name
        item_counts[item_name] = item_counts.get(item_name, 0) + 1
    return item_counts


def process_transfers(
    transfers: list[TransferModel], user_id: int
) -> dict[str, dict[str, int]]:
    if not transfers:
        return {"received": {}, "sent": {}}
    received = {}
    sent = {}
    for transfer in transfers:
        if transfer.to_user_id == user_id:
            received[transfer.sender.username] = (
                received.get(transfer.sender.username, 0) + transfer.amount
            )
        elif transfer.from_user_id == user_id:
            sent[transfer.receiver.username] = (
                sent.get(transfer.receiver.username, 0) + transfer.amount
            )
    return {"received": received, "sent": sent}
