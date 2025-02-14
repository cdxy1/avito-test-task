from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from ..db import database
from ..models.transaction import PurchaseModel, TransferModel
from ..schemas.response import (
    CoinHistory,
    InventoryItem,
    ReceivedCoin,
    ResponseSchema,
    SentCoin,
    UserInfoResponse,
)
from ..utils.info_utils import (
    count_items,
    get_user_info,
    get_user_purchases,
    get_user_transfers,
    process_transfers,
)
from ..utils.security_utils import decode_access_token
from ..utils.transaction_utils import check_balance, get_item_by_name

router = APIRouter(tags=["Transaction"])


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
        user = await get_user_info(
            username,
            session,
        )
        item = await get_item_by_name(
            item,
            session,
        )

        await check_balance(user, item.price)

        purchase = PurchaseModel(from_user=user.username, item_name=item.name)
        user.balance -= item.price
        session.add(purchase)

    response = ResponseSchema(detail="Успешный ответ.")
    return JSONResponse(status_code=200, content=response.model_dump())


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
        from_user = await get_user_info(username, session)
        to_user_obj = await get_user_info(to_user, session)

        await check_balance(from_user, amount)

        transfer = TransferModel(
            from_user=from_user.username, to_user=to_user, amount=amount
        )

        from_user.balance -= amount
        to_user_obj.balance += amount
        session.add(transfer)

    response = ResponseSchema(detail="Успешный ответ.")
    return JSONResponse(status_code=200, content=response.model_dump())


@router.get("/info")
async def info(
    current_user: Annotated[dict, Depends(decode_access_token)],
    session: Annotated[AsyncSession, Depends(database.get_session)],
) -> JSONResponse:
    username = current_user.get("sub")

    if not username:
        raise HTTPException(status_code=400, detail="Username is missing")

    user = await get_user_info(username, session)

    transfers = await get_user_transfers(
        username,
        session,
    )
    purchases = await get_user_purchases(
        username,
        session,
    )

    item_counts = count_items(purchases)
    transfer_data = process_transfers(transfers, username)

    response = UserInfoResponse(
        coins=user.balance,
        inventory=[
            InventoryItem(type=item, quantity=count)
            for item, count in item_counts.items()
        ],
        CoinHistory=CoinHistory(
            received=[
                ReceivedCoin(fromUser=user, amount=amount)
                for user, amount in transfer_data["received"].items()
            ],
            sent=[
                SentCoin(toUser=user, amount=amount)
                for user, amount in transfer_data["sent"].items()
            ],
        ),
    )
    return JSONResponse(status_code=200, content=response.model_dump())
