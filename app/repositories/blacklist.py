from datetime import datetime


class BlacklistRepository:
    def __init__(self, redis_pool):
        self.redis_pool = redis_pool

    async def add(self, token: str, expires_at: datetime) -> None:
        """Добавляет токен в blacklist с TTL до времени expires_at."""
        ttl = int((expires_at - datetime.utcnow()).total_seconds())
        if ttl > 0:
            async with self.redis_pool.connection() as redis:
                await redis.set(token, "blacklisted", ex=ttl)

    async def is_blacklisted(self, token: str) -> bool:
        """Проверяет, находится ли токен в blacklist."""
        async with self.redis_pool.connection() as redis:
            result = await redis.get(token)
            return result == "blacklisted"
