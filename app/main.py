from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import database
from .routes.auth import router as auth_router
from .utils.redis_utlis import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.create_tables()
    await redis_client.connect()

    yield

    await redis_client.close()


app = FastAPI(lifespan=lifespan, root_path="/api/v1")


app.include_router(auth_router)
