from typing import Optional

from redis import Redis
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

    async def set_value(self, key: str, value: str):
        try:
            await self.redis.set(f"refresh:{key}", value)
        except:
            print("нихуя не работает")

    async def get_value(self, key):
        try:
            print(key)
            return await self.redis.get(key)
        except:
            pass

    async def delete_value(self, key):
        try:
            await self.redis.delete(key)
        except:
            pass


redis_client = RedisClient()
