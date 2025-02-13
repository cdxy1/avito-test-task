from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import database
from ..models.user import UserModel
from ..schemas.token import TokenSchema
from ..schemas.user import ChangePasswordScheme, UserDBSchema, UserInSchema, UserSchema
from ..utils.redis_utlis import redis_client
from ..utils.security_utils import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    username_from_token,
    verify_password,
)

router = APIRouter(tags=["Auth"])


async def get_user_by_username(
    username: str, session: AsyncSession
) -> UserModel | None:
    select_result = select(UserModel).filter(UserModel.username == username)
    user = (await session.execute(select_result)).scalars().first()
    return user


@router.post("/register")
async def register(
    user: UserInSchema,
    session: Annotated[AsyncSession, Depends(database.get_session)],
) -> UserSchema:
    user_dict = user.model_dump()
    user_db_dict = UserDBSchema(**user_dict).model_dump()

    user_db_dict["password"] = hash_password(user.password)
    new_user = UserModel(**user_db_dict)
    session.add(new_user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    return UserSchema(**user_dict)


@router.post("/auth")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(database.get_session)],
) -> TokenSchema:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    )

    result = await session.execute(
        select(UserModel).where(UserModel.username == form_data.username)
    )
    user = result.scalars().first()
    if user and verify_password(form_data.password, user.password):
        token = create_access_token({"sub": user.username})
        refresh_token = await create_refresh_token(user.username)
        return TokenSchema(
            access_token=token, refresh_token=refresh_token, token_type="bearer"
        )
    else:
        raise credentials_exc


@router.post("/refresh")
async def refresh_access_token(
    current_user: Annotated[str, Depends(username_from_token)],
):
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    )

    if not current_user:
        raise exc

    refresh_token = await redis_client.get_value(current_user)
    if not refresh_token:
        raise exc

    payload = {"sub": current_user}

    return create_access_token(payload)


@router.get("/users/me")
async def get_user(current_user: Annotated[str, Depends(decode_access_token)]):
    return current_user


@router.patch("/users/change_password")
async def change_password(
    passwords: ChangePasswordScheme,
    current_user: Annotated[dict, Depends(decode_access_token)],
    session: Annotated[AsyncSession, Depends(database.get_session)],
) -> dict:
    username = current_user.get("sub")
    user = await get_user_by_username(username, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not verify_password(passwords.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )

    new_hashed_password = hash_password(passwords.new_password)
    update_result = (
        update(UserModel)
        .filter(UserModel.username == username)
        .values(password=new_hashed_password)
    )
    await session.execute(update_result)
    await session.commit()

    return {"status": "success"}


@router.delete("/logout")
async def logout(current_user: Annotated[dict, Depends(decode_access_token)]):
    user = current_user.get("sub")
    await redis_client.delete_value(user)
    return {"status": "success"}
