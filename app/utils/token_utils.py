import os
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends
import jwt
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

load_dotenv()
oauth2_schema = OAuth2PasswordBearer("token")


def create_access_token(
    data: dict,
):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"))
    return encoded_jwt


def decode_access_token(token: Annotated[str, Depends(oauth2_schema)]):
    return jwt.decode(token, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"))
