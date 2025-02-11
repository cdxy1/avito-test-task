import os
from datetime import datetime, timedelta
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError

from .redis_utlis import redis_client

load_dotenv()
oauth2_schema = OAuth2PasswordBearer("/auth/token")


def create_access_token(
    data: dict,
) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"))
    return encoded_jwt


async def create_refresh_token(
    username: str,
) -> str:
    expire = timedelta(days=30)
    encoded_jwt = jwt.encode(
        {"sub": username},
        os.getenv("SECRET_KEY"),
        os.getenv("ALGORITHM"),
    )
    await redis_client.set_value(username, encoded_jwt, expire)
    return encoded_jwt


def decode_access_token(token: Annotated[str, Depends(oauth2_schema)]) -> dict:
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"))
        exp = payload.get("exp")

        if not exp or datetime.now() >= datetime.utcfromtimestamp(exp):
            raise HTTPException(status_code=401, detail="Token expired or invalid")
        return payload

    except DecodeError:
        raise HTTPException(status_code=401, detail="Token decode error")


def username_from_token(token: Annotated[str, Depends(oauth2_schema)]) -> dict:
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"))
        user = payload.get("sub")

        return user

    except DecodeError:
        raise HTTPException(status_code=401, detail="Token decode error")
