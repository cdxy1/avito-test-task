from datetime import timedelta
from typing import Optional

from redis import ConnectionError, Redis
from redis import asyncio as aioredis


class RedisClient:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[Redis | None] = None

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def set_value(self, key: str, value: str, expire: timedelta):
        try:
            await self.redis.setex(f"refresh:{key}", expire, value)
        except ConnectionError:
            print("не работает")

    async def get_value(self, key) -> Optional[str]:
        try:
            return await self.redis.get(f"refresh:{key}")
        except ConnectionError:
            pass

    async def delete_value(self, key):
        try:
            await self.redis.delete(f"refresh:{key}")
        except ConnectionError:
            pass


redis_client = RedisClient()
