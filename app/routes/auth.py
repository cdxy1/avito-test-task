from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from ..db import database
from ..models.user import UserModel
from ..schemas.response import (
    AccessTokenResponseSchema,
    AuthResponseSchema,
    ResponseSchema,
)
from ..schemas.user import ChangePasswordScheme, UserDBSchema, UserInSchema
from ..utils.info_utils import get_user_info
from ..utils.redis_utils import redis_client
from ..utils.security_utils import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    username_from_token,
    verify_password,
)

router = APIRouter(tags=["Auth"])


@router.post("/register")
async def register(
    user: UserInSchema,
    session: Annotated[AsyncSession, Depends(database.get_session)],
) -> JSONResponse:
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
    response = ResponseSchema(detail="Пользователь зарегистрирован.")
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=response.model_dump()
    )


@router.post("/auth")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(database.get_session)],
) -> JSONResponse:
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
        response = AuthResponseSchema(
            detail="Успешная аутентификация.",
            access_token=token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=response.model_dump()
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

    token = create_access_token(payload)
    response = AccessTokenResponseSchema(detail="Успешный ответ.", access_token=token)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())


@router.patch("/change_password")
async def change_password(
    passwords: ChangePasswordScheme,
    current_user: Annotated[dict, Depends(decode_access_token)],
    session: Annotated[AsyncSession, Depends(database.get_session)],
) -> JSONResponse:
    username = current_user.get("sub")
    user = await get_user_info(username, session)

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

    response = ResponseSchema(detail="Успешный ответ.")
    return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())


@router.delete("/logout")
async def logout(
    current_user: Annotated[dict, Depends(decode_access_token)],
) -> JSONResponse:
    user = current_user.get("sub")
    await redis_client.delete_value(user)
    response = ResponseSchema(detail="Успешный ответ.")
    return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())
