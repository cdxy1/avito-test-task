from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import database
from ..models.transaction import PurchaseModel, TransferModel
from ..utils.info_utils import (
    count_items,
    get_user_info,
    get_user_purchases,
    get_user_transfers,
    process_transfers,
)
from ..utils.security_utils import decode_access_token
from ..utils.transaction_utils import check_balance, get_item_by_name

router = APIRouter(prefix="/transaction", tags=["transaction"])


@router.post("/buy/{item}")
async def buy_item(
    item: str,
    current_user: Annotated[dict, Depends(decode_access_token)],
    session: Annotated[AsyncSession, Depends(database.get_session)],
):
    username = current_user.get("sub")
    if not username:
        raise HTTPException(status_code=400, detail="Username is missing")

    async with session.begin():
        user = await get_user_info(session, username)
        item = await get_item_by_name(session, item)

        await check_balance(user, item.price)

        purchase = PurchaseModel(from_user=user.username, item_name=item.name)
        user.balance -= item.price
        session.add(purchase)

    return {"username": user.username, "item": item.name, "balance": user.balance}


@router.post("/sendCoin")
async def send_coin(
    to_user: str,
    current_user: Annotated[dict, Depends(decode_access_token)],
    amount: int,
    session: Annotated[AsyncSession, Depends(database.get_session)],
):
    username = current_user.get("sub")
    if not username:
        raise HTTPException(status_code=400, detail="Username is missing")

    async with session.begin():
        from_user = await get_user_info(session, username)
        to_user_obj = await get_user_info(session, to_user)

        await check_balance(from_user, amount)

        transfer = TransferModel(
            from_user=from_user.username, to_user=to_user, amount=amount
        )
        from_user.balance -= amount
        to_user_obj.balance += amount
        session.add(transfer)

    return {"from_user": from_user.username, "to_user": to_user, "amount": amount}


@router.get("/info")
async def info(
    current_user: Annotated[dict, Depends(decode_access_token)],
    session: Annotated[AsyncSession, Depends(database.get_session)],
) -> dict:
    username = current_user.get("sub")
    if not username:
        raise HTTPException(status_code=400, detail="Username is missing")

    user = await get_user_info(session, username)
    transfers = await get_user_transfers(session, username)
    purchases = await get_user_purchases(session, username)

    item_counts = count_items(purchases)
    transfer_data = process_transfers(transfers, username)

    return {
        "coins": user.balance,
        "inventory": [
            {"type": item, "quantity": count} for item, count in item_counts.items()
        ],
        "CoinHistory": {
            "received": [
                {"fromUser": user, "amount": amount}
                for user, amount in transfer_data["received"].items()
            ],
            "sent": [
                {"toUser": user, "amount": amount}
                for user, amount in transfer_data["sent"].items()
            ],
        },
    }
