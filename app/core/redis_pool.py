import redis.asyncio as aioredis
from app.core.config import settings
from contextlib import asynccontextmanager



class RedisConnectionPool:
    def __init__(self, redis_url):
        self.redis_url = redis_url
        self.pool: aioredis.Redis = None

    async def start(self):
        """Подключение к Redis при старте приложения."""
        self.pool = aioredis.from_url(self.redis_url, decode_responses=True, max_connections=300)

    async def get_redis_connection(self) -> aioredis.Redis:
        if not self.pool:
            raise ConnectionError("Redis соединение не инициализировано!")
        return self.pool

    async def close(self):
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def connection(self):
        redis = await self.get_redis_connection()
        try:
            yield redis
        finally:
            pass

redis_pool = RedisConnectionPool(settings.REDIS_URL)