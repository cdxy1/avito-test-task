from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models.user import UserModel
from ..db import database
from ..schemas.user import UserSchema, UserInSchema
from ..schemas.token import TokenSchema
from ..utils.hasher import hash_password, verify_password
from ..utils.token_utils import create_access_token, decode_access_token

router = APIRouter()


@router.post("/register")
async def register(
    user: UserInSchema,
    session: Annotated[AsyncSession, Depends(database.get_session)],
):
    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user.password)
    new_user = UserModel(**user_dict)
    session.add(new_user)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    return UserSchema(**user_dict)


@router.post("/token")
async def login(
    from_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(database.get_session)],
):
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentails"
    )

    result = await session.execute(
        select(UserModel).where(UserModel.username == from_data.username)
    )
    user = result.scalars().first()
    if user and verify_password(from_data.password, user.password):
        token = create_access_token({"sub": user.username})
        return TokenSchema(access_token=token, token_type="bearer")
    else:
        raise credentials_exc


@router.get("/users/me")
async def get_user(current_user: Annotated[str, Depends(decode_access_token)]):
    return current_user
