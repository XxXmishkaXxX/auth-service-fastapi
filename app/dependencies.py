from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession 


from services.auth import AuthService
from services.jwt_tokens import JWTService
from core.db import get_db
from core.redis_pool import redis_pool
from repositories.user import UserRepository
from repositories.blacklist import BlacklistRepository

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(db)
    blacklist_repo = BlacklistRepository(redis_pool)
    return AuthService(user_repo=user_repo, blacklist_repo=blacklist_repo)

def get_jwt_service() -> JWTService: return JWTService()