from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import database
from ..models.item import ItemModel
from ..models.transaction import PurchaseModel, TransferModel
from ..models.user import UserModel
from ..utils.security_utils import decode_access_token

router = APIRouter(prefix="/transaction", tags=["transaction"])


@router.post("/buy/{item}")
async def buy_item(
    item: str,
    current_user: Annotated[dict, Depends(decode_access_token)],
    session: Annotated[AsyncSession, Depends(database.get_session)],
):
    username = current_user.get("sub")

    if username is None:
        raise HTTPException(status_code=400, detail="Username is missing")

    query_user = select(UserModel).filter(UserModel.username == username)
    query_item = select(ItemModel).filter(ItemModel.name == item)
    result_user = await session.execute(query_user)
    result_item = await session.execute(query_item)
    res_user = result_user.scalars().first()
    res_item = result_item.scalars().first()

    if res_user is None or res_item is None:
        raise HTTPException(status_code=404, detail="User or item not found")

    if res_user.balance < res_item.price:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    purchase = PurchaseModel(from_user=res_user.username, item_name=res_item.name)

    res_user.balance -= res_item.price
    session.add(purchase)
    await session.commit()

    return {res_user.username: res_item.name, res_user.balance: res_item.price}


@router.post("/sendCoin")
async def send_coin(
    to_user: str,
    current_user: Annotated[dict, Depends(decode_access_token)],
    amount: int,
    session: Annotated[AsyncSession, Depends(database.get_session)],
):
    username = current_user.get("sub")
    if username is None:
        raise HTTPException(status_code=400, detail="Username is missing")
    query_user = select(UserModel).filter(UserModel.username == username)
    query_user2 = select(UserModel).filter(UserModel.username == to_user)
    result_user = await session.execute(query_user)
    result_user2 = await session.execute(query_user2)
    res_user = result_user.scalars().first()
    res_user2 = result_user2.scalars().first()
    if res_user is None or res_user2 is None:
        raise HTTPException(status_code=404, detail="User or item not found")
    if res_user.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    transfer = TransferModel(
        from_user=res_user.username, to_user=to_user, amount=amount
    )
    res_user.balance -= amount
    res_user2.balance += amount
    session.add(transfer)
    await session.commit()


@router.get("/info")
async def info(
    current_user: Annotated[dict, Depends(decode_access_token)],
    session: Annotated[AsyncSession, Depends(database.get_session)],
):
    user = current_user.get("sub")
    user_query = select(UserModel).filter(UserModel.username == user)
    transfer_query = select(TransferModel).filter(
        or_(TransferModel.to_user == user, TransferModel.from_user == user)
    )
    purchase_query = select(PurchaseModel).filter(PurchaseModel.from_user == user)
    result_user = await session.execute(user_query)
    result_transfer = await session.execute(transfer_query)
    result_purchase = await session.execute(purchase_query)

    res_user = result_user.scalars().first()
    res_transfer = result_transfer.scalars().all()
    res_purchase = result_purchase.scalars().all()

    temp_dict = {}
    for i in res_purchase:
        temp_var = i.__dict__["item_name"]
        if temp_var in temp_dict:
            temp_dict[temp_var] += 1
        else:
            temp_dict[temp_var] = 1

    temp_dict1 = {}
    for i in res_transfer:
        temp_var1 = i.__dict__["to_user"]
        if temp_var1 == user:
            if i.__dict__["from_user"] not in temp_dict1:
                temp_dict1[i.__dict__["from_user"]] = i.__dict__["amount"]
            else:
                temp_dict1[i.__dict__["from_user"]] += i.__dict__["amount"]

    temp_dict2 = {}
    for i in res_transfer:
        temp_var2 = i.__dict__["from_user"]
        if temp_var2 == user:
            if i.__dict__["to_user"] not in temp_dict2:
                temp_dict2[i.__dict__["to_user"]] = i.__dict__["amount"]
            else:
                temp_dict2[i.__dict__["to_user"]] += i.__dict__["amount"]

    return {
        "coins": res_user.balance,
        "inventory": [{"type": i, "quantity": j} for i, j in temp_dict.items()],
        "CoinHistory": {
            "received": [{"fromUser": i, "amount": j} for i, j in temp_dict1.items()],
            "sent": [{"toUser": i, "amount": j} for i, j in temp_dict2.items()],
        },
    }
