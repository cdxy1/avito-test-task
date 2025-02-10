import os
from typing import Optional
from datetime import timedelta, datetime

import aioredis
from aioredis import Redis


class RedisСlient:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[Redis | None] = None

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def set_value(self, key: str, value: str):
        from_env_exp = os.getenv("REDIS_EXPIRE_DAYS")
        expire = (
            datetime.now() + timedelta(int(from_env_exp))
            if from_env_exp
            else timedelta(days=7)
        )

        try:
            self.redis.setex(key, expire, value)
        except:
            pass

    async def get_value(self, key):
        try:
            return self.redis.get(key)
        except:
            pass

    async def delete_value(self, key):
        try:
            self.redis.delete(key)
        except:
            pass


redis_client = RedisСlient()
