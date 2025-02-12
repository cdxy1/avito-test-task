from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import database
from ..models.item import ItemModel
from ..utils.security_utils import decode_access_token

router = APIRouter(prefix="/transaction", tags=["transaction"])


@router.post("/buy/{item}")
async def buy_item(
    item: str,
    current_user: Annotated[dict, Depends(decode_access_token)],
    session: Annotated[AsyncSession, Depends(database.get_session)],
):
    user = current_user.get("sub")
    item = ItemModel(name=item, price=1000)

    session.add(item)
    return {"item": item}
