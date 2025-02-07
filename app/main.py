from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import database
from .routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.create_tables()
    yield


app = FastAPI(lifespan=lifespan, root_path="/api/v1")


app.include_router(auth_router)
