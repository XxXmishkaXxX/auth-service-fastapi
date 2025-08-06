from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.v1.auth import router
from core.redis_pool import redis_pool
from core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await redis_pool.start()
        logger.info("✅ Redis started.")
   
    except Exception as e:
        logger.warning(f"⚠️ Ошибка Kafka: {e}")

    yield
    
    await redis_pool.close()
    logger.info("🛑 Redis closed.")


app = FastAPI(title="Auth Service", lifespan=lifespan)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)